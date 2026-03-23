# gRPC Architecture Overview

Visual guide to how Bindu's gRPC layer works.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Developer's Code (Any Language)"
        TS["TypeScript Agent<br/>(OpenAI, LangChain, etc.)"]
        KT["Kotlin Agent<br/>(any framework)"]
        RS["Rust Agent<br/>(any framework)"]
    end

    subgraph "Language SDKs (Thin Wrappers)"
        TS_SDK["@bindu/sdk<br/>bindufy(config, handler)"]
        KT_SDK["bindu-sdk (Kotlin)<br/>bindufy(config, handler)"]
        RS_SDK["bindu-sdk (Rust)<br/>bindufy(config, handler)"]
    end

    subgraph "Bindu Core (Python)"
        GRPC_SERVER["gRPC Server<br/>:3774<br/>BinduService"]
        BINDUFY["_bindufy_core()<br/>DID, Auth, x402<br/>Manifest, Scheduler, Storage"]
        HTTP["HTTP/A2A Server<br/>:3773<br/>BinduApplication"]
        WORKER["ManifestWorker<br/>manifest.run(messages)"]
        GRPC_CLIENT["GrpcAgentClient<br/>(callable)"]
    end

    TS --> TS_SDK
    KT --> KT_SDK
    RS --> RS_SDK

    TS_SDK -->|"RegisterAgent<br/>(gRPC)"| GRPC_SERVER
    KT_SDK -->|"RegisterAgent<br/>(gRPC)"| GRPC_SERVER
    RS_SDK -->|"RegisterAgent<br/>(gRPC)"| GRPC_SERVER

    GRPC_SERVER --> BINDUFY
    BINDUFY --> HTTP
    BINDUFY --> WORKER

    WORKER -->|"manifest.run()"| GRPC_CLIENT
    GRPC_CLIENT -->|"HandleMessages<br/>(gRPC)"| TS_SDK
    GRPC_CLIENT -->|"HandleMessages<br/>(gRPC)"| KT_SDK
    GRPC_CLIENT -->|"HandleMessages<br/>(gRPC)"| RS_SDK

    CLIENT["External Client<br/>(A2A Protocol)"] -->|"POST /"| HTTP
```

## Complete Message Flow

```mermaid
sequenceDiagram
    participant Dev as Developer's Code
    participant SDK as Language SDK
    participant Core as Bindu Core (:3774)
    participant HTTP as A2A Server (:3773)
    participant Worker as ManifestWorker
    participant Client as External Client

    Note over Dev,SDK: 1. Agent Startup

    Dev->>SDK: bindufy(config, handler)
    SDK->>SDK: Read skill files locally
    SDK->>SDK: Start AgentHandler gRPC server (random port)
    SDK->>Core: RegisterAgent(config_json, skills, callback_address)

    Note over Core: Core runs full bindufy logic

    Core->>Core: Validate config
    Core->>Core: Generate agent ID (SHA256)
    Core->>Core: Setup DID (Ed25519 keys)
    Core->>Core: Setup x402 payments (if configured)
    Core->>Core: Create manifest (manifest.run = GrpcAgentClient)
    Core->>Core: Create BinduApplication (Starlette + middleware)
    Core->>HTTP: Start uvicorn (background thread)

    Core-->>SDK: RegisterAgentResponse {agent_id, did, agent_url}
    SDK-->>Dev: "Agent registered! A2A URL: http://localhost:3773"

    Note over SDK,Core: 2. Heartbeat Loop (every 30s)

    loop Every 30 seconds
        SDK->>Core: Heartbeat(agent_id, timestamp)
        Core-->>SDK: HeartbeatResponse(acknowledged)
    end

    Note over Client,Dev: 3. Runtime — Message Execution

    Client->>HTTP: POST / (A2A message/send)
    HTTP->>Worker: TaskManager → Scheduler → Worker
    Worker->>Worker: Build message history
    Worker->>Worker: manifest.run(messages)

    Note over Worker,SDK: manifest.run is GrpcAgentClient

    Worker->>SDK: HandleMessages(messages) via gRPC
    SDK->>Dev: handler(messages) — developer's function
    Dev-->>SDK: response (string or {state, prompt})
    SDK-->>Worker: HandleResponse

    Note over Worker: ResultProcessor → ResponseDetector

    Worker->>Worker: Normalize result, detect state
    Worker->>HTTP: Update storage, create artifacts
    HTTP-->>Client: A2A JSON-RPC response

    Note over Client,Dev: 4. Shutdown

    Dev->>SDK: Ctrl+C
    SDK->>Core: UnregisterAgent(agent_id)
    SDK->>SDK: Kill Python core child process
```

## SDK Internal Flow

When a developer calls `bindufy()` from a language SDK:

```mermaid
flowchart TD
    A["SDK: bindufy(config, handler)"] --> B["1. Read skill files from disk"]
    B --> C["2. Start AgentHandler gRPC server\n(random port, e.g., :57139)"]
    C --> D["3. Detect & spawn Python core\nas child process"]
    D --> E{"bindu CLI found?"}
    E -->|"pip installed"| F["bindu serve --grpc"]
    E -->|"uv available"| G["uv run bindu serve --grpc"]
    E -->|"fallback"| H["python -m bindu.cli serve --grpc"]
    F --> I["4. Wait for :3774 to be ready"]
    G --> I
    H --> I
    I --> J["5. Call RegisterAgent on :3774\n(config JSON + skills + callback)"]
    J --> K["6. Core runs bindufy logic\n(DID, auth, x402, manifest)"]
    K --> L["7. Core starts uvicorn on :3773\n(background thread)"]
    L --> M["8. Return {agent_id, did, url}"]
    M --> N["9. Start heartbeat loop (30s)"]
    N --> O["10. Wait for HandleMessages calls"]

    style A fill:#e1f5fe
    style O fill:#e8f5e9
```

## Port Layout

```
Bindu Core Process
├── :3773  Uvicorn (HTTP)  — A2A protocol, agent card, DID, health, x402, metrics
└── :3774  gRPC Server     — RegisterAgent, Heartbeat, UnregisterAgent

SDK Process
└── :XXXXX  gRPC Server (dynamic port) — HandleMessages, GetCapabilities, HealthCheck
```

## Two-Way Communication

The gRPC layer enables **bidirectional** communication:

**SDK → Core (BinduService)**
- Register agent
- Send heartbeats
- Unregister

**Core → SDK (AgentHandler)**
- Execute handler
- Query capabilities
- Health check

This is different from traditional HTTP where only the client initiates requests. With gRPC, both sides can initiate calls.

## Key Components

### 1. GrpcAgentClient (Core Side)

Replaces `manifest.run` for remote agents. When ManifestWorker calls it:

```python
# In ManifestWorker
raw_results = self.manifest.run(message_history)

# For gRPC agents, this becomes:
# 1. Convert messages to proto
# 2. Call SDK's HandleMessages via gRPC
# 3. Convert response back to Python
# 4. Return to ManifestWorker
```

### 2. AgentRegistry (Core Side)

Thread-safe in-memory database tracking registered agents:

```python
registry.register(agent_id, callback_address, manifest)
entry = registry.get(agent_id)
# entry.grpc_callback_address → where to call SDK
```

### 3. BinduServiceImpl (Core Side)

Handles SDK registration requests:

```python
def RegisterAgent(self, request, context):
    # 1. Parse config JSON
    # 2. Run full bindufy logic
    # 3. Create GrpcAgentClient
    # 4. Start HTTP server
    # 5. Return agent_id, DID, URL
```

### 4. SDK AgentHandler (SDK Side)

Receives execution requests from core:

```typescript
// TypeScript SDK
async function HandleMessages(request: HandleRequest): Promise<HandleResponse> {
  const messages = request.messages;
  const result = await developerHandler(messages);
  return { content: result };
}
```

## Data Flow Example

**User sends message to agent:**

```
1. External Client
   ↓ HTTP POST / (A2A message/send)
2. Bindu HTTP Server (:3773)
   ↓ TaskManager.send_message()
3. ManifestWorker
   ↓ manifest.run(messages)
4. GrpcAgentClient
   ↓ gRPC HandleMessages(messages)
5. SDK AgentHandler (:50052)
   ↓ developerHandler(messages)
6. Developer's Code
   ↓ return "response"
7. SDK AgentHandler
   ↓ HandleResponse{content: "response"}
8. GrpcAgentClient
   ↓ return "response"
9. ManifestWorker
   ↓ ResultProcessor → ResponseDetector
10. Bindu HTTP Server
    ↓ A2A JSON-RPC response
11. External Client
```

## Comparison: Python vs gRPC Agents

| Aspect | Python Agent | gRPC Agent |
|--------|-------------|------------|
| **Process** | Single Python process | Two processes (Core + SDK) |
| **Communication** | In-process function call | gRPC over localhost |
| **Latency** | ~0ms | ~1-5ms |
| **Language** | Python only | Any language |
| **Setup** | `bindufy(config, handler)` | SDK spawns core as child |
| **Debugging** | Python debugger | Requires gRPC tools |
| **Streaming** | ✅ Supported | ❌ Not implemented |

## Why This Architecture?

**Benefits:**
- **Language agnostic** - Write agents in any language
- **Zero changes** to core - ManifestWorker doesn't know about gRPC
- **Transparent** - Developers just call `bindufy()`
- **Full feature parity** - DID, x402, skills, auth all work

**Trade-offs:**
- Extra process overhead
- Slightly higher latency
- More complex debugging
- Streaming not yet implemented
