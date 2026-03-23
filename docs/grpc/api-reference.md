# gRPC API Reference

Complete reference for Bindu's gRPC services.

## Two gRPC Services

### 1. BinduService (SDK → Core, Port 3774)

SDKs call this service on the Bindu core to register and manage agents.

#### RegisterAgent

Register an agent with the core. Runs full bindufy logic (DID, auth, x402, manifest, HTTP server).

**Request:**
```protobuf
message RegisterAgentRequest {
  string config_json = 1;              // Full config as JSON string
  repeated SkillDefinition skills = 2; // Skills with content
  string grpc_callback_address = 3;    // SDK's AgentHandler address
}
```

**Response:**
```protobuf
message RegisterAgentResponse {
  bool success = 1;
  string agent_id = 2;    // UUID
  string did = 3;         // did:bindu:...
  string agent_url = 4;   // http://localhost:3773
  string error = 5;
}
```

**Example:**
```bash
grpcurl -plaintext -d '{
  "config_json": "{\"author\":\"dev@example.com\",\"name\":\"my-agent\"}",
  "skills": [],
  "grpc_callback_address": "localhost:50052"
}' localhost:3774 bindu.grpc.BinduService.RegisterAgent
```

#### Heartbeat

Periodic keep-alive signal. SDKs should send every 30 seconds.

**Request:**
```protobuf
message HeartbeatRequest {
  string agent_id = 1;
  int64 timestamp = 2;
}
```

**Response:**
```protobuf
message HeartbeatResponse {
  bool acknowledged = 1;      // true if agent is registered
  int64 server_timestamp = 2;
}
```

#### UnregisterAgent

Disconnect and clean up. Core stops the agent's HTTP server.

**Request:**
```protobuf
message UnregisterAgentRequest {
  string agent_id = 1;
}
```

**Response:**
```protobuf
message UnregisterAgentResponse {
  bool success = 1;
  string error = 2;
}
```

---

### 2. AgentHandler (Core → SDK, Dynamic Port)

The core calls this service on the SDK to execute tasks.

#### HandleMessages

Execute the developer's handler with conversation history. Called for every A2A request.

**Request:**
```protobuf
message HandleRequest {
  repeated ChatMessage messages = 1;
  string task_id = 2;      // Optional
  string context_id = 3;   // Optional
}

message ChatMessage {
  string role = 1;     // "user", "agent", "system"
  string content = 2;
}
```

**Response:**
```protobuf
message HandleResponse {
  string content = 1;                // Response text
  string state = 2;                  // "", "input-required", "auth-required"
  string prompt = 3;                 // Prompt for state transitions
  bool is_final = 4;                 // Reserved for streaming
  map<string, string> metadata = 5;  // Extra metadata
}
```

**Response Behavior:**

| SDK Returns | Task State | Description |
|------------|------------|-------------|
| `{content: "Hello"}` | `completed` | Normal completion |
| `{state: "input-required", prompt: "Clarify?"}` | `input-required` | Task stays open |
| `{state: "auth-required"}` | `auth-required` | Requires authentication |

#### HandleMessagesStream

⚠️ **Not Currently Implemented in GrpcAgentClient**

Server-side streaming version of HandleMessages. SDK yields chunks, core collects them.

**Request:** Same as HandleMessages

**Response:** Stream of HandleResponse messages

**Status:** Defined in proto but not implemented in `bindu/grpc/client.py`. Planned for future release.

#### GetCapabilities

Query agent capabilities (skills, supported modes).

**Request:**
```protobuf
message GetCapabilitiesRequest {}
```

**Response:**
```protobuf
message GetCapabilitiesResponse {
  string name = 1;
  string description = 2;
  string version = 3;
  bool supports_streaming = 4;
  repeated SkillDefinition skills = 5;
}
```

#### HealthCheck

Verify the SDK process is responsive.

**Request:**
```protobuf
message HealthCheckRequest {}
```

**Response:**
```protobuf
message HealthCheckResponse {
  bool healthy = 1;
  string message = 2;
}
```

---

## Complete Method Summary

| Service | Method | Direction | Implemented | Purpose |
|---------|--------|-----------|-------------|---------|
| **BinduService** | RegisterAgent | SDK → Core | ✅ | Register agent |
| | Heartbeat | SDK → Core | ✅ | Keep-alive |
| | UnregisterAgent | SDK → Core | ✅ | Disconnect |
| **AgentHandler** | HandleMessages | Core → SDK | ✅ | Execute handler (unary) |
| | HandleMessagesStream | Core → SDK | ❌ | Execute handler (streaming) |
| | GetCapabilities | Core → SDK | ✅ | Query capabilities |
| | HealthCheck | Core → SDK | ✅ | Health check |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRPC__ENABLED` | `false` | Enable gRPC server |
| `GRPC__HOST` | `0.0.0.0` | gRPC server bind host |
| `GRPC__PORT` | `3774` | gRPC server port |
| `GRPC__MAX_WORKERS` | `10` | Thread pool size |
| `GRPC__MAX_MESSAGE_LENGTH` | `4194304` | Max message size (4MB) |
| `GRPC__HANDLER_TIMEOUT` | `30.0` | HandleMessages timeout (seconds) |
| `GRPC__HEALTH_CHECK_INTERVAL` | `30` | Health check interval (seconds) |

### Python Settings

```python
from bindu.settings import app_settings

app_settings.grpc.enabled     # bool
app_settings.grpc.host         # str
app_settings.grpc.port         # int
app_settings.grpc.max_workers  # int
```
