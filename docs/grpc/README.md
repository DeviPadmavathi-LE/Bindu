# gRPC Language-Agnostic Agent Support

Bindu's gRPC adapter enables agents written in **any programming language** to become full Bindu microservices with DID identity, A2A protocol, x402 payments, and more.

## Documentation Structure

### Core Documentation
- **[Overview](./overview.md)** - Architecture diagrams, message flow, and visual guides
- **[API Reference](./api-reference.md)** - Complete gRPC service definitions and methods
- **[Client Implementation](./client.md)** - GrpcAgentClient and how the core calls remote agents
- **[Limitations](./limitations.md)** - Known gaps and workarounds

### SDK Documentation
- **[TypeScript SDK](./sdk-typescript.md)** - Complete guide for building TypeScript agents
- **[SDK Development](./sdk-development.md)** - Guide for building SDKs in new languages

### Advanced Topics
- **[Registry](./registry.md)** - Agent registry and lifecycle management
- **[Testing](./testing.md)** - How to test gRPC with grpcurl, Postman, and unit tests
- **[Proto Generation](./proto-generation.md)** - How to regenerate proto stubs

## Quick Start

### For SDK Users

```typescript
import { bindufy } from "@bindu/sdk";

bindufy({
  author: "dev@example.com",
  name: "my-agent",
}, async (messages) => {
  return "Hello from TypeScript!";
});
```

### For Core Developers

```bash
# Start gRPC server
uv run bindu serve --grpc

# Test with grpcurl
grpcurl -plaintext localhost:3774 list
```

## Current Limitations

⚠️ **Streaming Not Fully Implemented**

While `HandleMessagesStream` is defined in the proto, the `GrpcAgentClient` does not currently implement streaming support. This means:

- Remote agents can only use unary (non-streaming) responses
- The `message/stream` A2A endpoint won't work with gRPC agents
- SDKs cannot yield incremental responses

**Status:** Planned for future release. Track progress in issue #XXX.

## Port Layout

```
Bindu Core Process
├── :3773  HTTP (A2A protocol, agent card, DID, health, metrics)
└── :3774  gRPC (RegisterAgent, Heartbeat, UnregisterAgent)

SDK Process
└── :XXXXX  gRPC (HandleMessages, GetCapabilities, HealthCheck)
```
