# Known Limitations

Current limitations and gaps in Bindu's gRPC implementation.

## ❌ Streaming Not Implemented

### The Gap

While `HandleMessagesStream` is defined in the proto specification, the `GrpcAgentClient` does **not** implement streaming support.

**What's Missing:**

```python
# In bindu/grpc/client.py
class GrpcAgentClient:
    def __call__(self, messages):
        # ✅ Implemented - calls HandleMessages (unary)
        response = self._stub.HandleMessages(request, timeout=self._timeout)
        return self._response_to_result(response)
    
    # ❌ NOT IMPLEMENTED
    def stream_messages(self, messages):
        """This method doesn't exist!"""
        # Should call HandleMessagesStream and yield responses
        for response in self._stub.HandleMessagesStream(request):
            yield self._response_to_result(response)
```

### Impact

**For Remote Agents:**
- Cannot use `message/stream` A2A endpoint
- Cannot yield incremental responses
- Cannot support real-time streaming use cases
- Must return complete responses only

**For SDK Developers:**
- TypeScript/Kotlin/Rust agents limited to unary responses
- No support for streaming LLM outputs
- No support for progressive data processing

**For End Users:**
- No streaming responses from non-Python agents
- Worse UX for long-running tasks (no progress updates)

### Misleading Documentation

The main gRPC doc (line 72) states:

> `HandleMessagesStream` | Core → SDK | Same as HandleMessages but with server-side streaming. SDK yields chunks, core collects them via `ResultProcessor.collect_results()`. **Enable with `use_streaming=True` on `GrpcAgentClient`.**

This is **incorrect**:
- `GrpcAgentClient` has no `use_streaming` parameter
- No way to enable streaming
- The method is not implemented

### Workaround

Use unary `HandleMessages` and return complete responses:

```typescript
// SDK handler - must return complete response
async function handler(messages: ChatMessage[]): Promise<string> {
  const response = await llm.complete(messages);
  return response; // Cannot yield chunks
}
```

### Status

**Planned for future release.** Track progress in issue #XXX.

**Implementation needed:**
1. Add `stream_messages()` method to `GrpcAgentClient`
2. Update `ManifestWorker` to detect streaming handlers
3. Integrate with existing `ResultProcessor.collect_results()`
4. Add streaming tests
5. Update SDK examples

---

## ⚠️ Other Limitations

### No Bidirectional Streaming

Only server-side streaming (SDK → Core) is planned. Client-side streaming (Core → SDK) and bidirectional streaming are not in scope.

### No Connection Pooling

Each `GrpcAgentClient` creates a single channel. For high-throughput scenarios, consider implementing connection pooling.

### No Automatic Reconnection

If the SDK crashes, the client doesn't automatically reconnect. The agent must be re-registered.

### No Load Balancing

If multiple SDK instances run the same agent, there's no built-in load balancing. Each registration creates a separate agent.

### No Metrics for gRPC Calls

The `/metrics` endpoint doesn't expose gRPC-specific metrics (call duration, error rates, etc.).

### No TLS Support

Current implementation uses insecure channels (`grpc.insecure_channel`). TLS/mTLS is not configured.

**Security Note:** Only use gRPC on localhost or in trusted networks.

---

## Comparison: What Works vs What Doesn't

| Feature | Python Agents | gRPC Agents | Status |
|---------|--------------|-------------|--------|
| **Unary responses** | ✅ | ✅ | Works |
| **Streaming responses** | ✅ | ❌ | Not implemented |
| **DID identity** | ✅ | ✅ | Works |
| **x402 payments** | ✅ | ✅ | Works |
| **Skills** | ✅ | ✅ | Works |
| **State transitions** | ✅ | ✅ | Works |
| **Health checks** | ✅ | ✅ | Works |
| **Capabilities query** | ✅ | ✅ | Works |
| **Heartbeat** | N/A | ✅ | Works |
| **Multi-language** | ❌ | ✅ | Works |

---

## Feedback

If you're blocked by any of these limitations, please:
1. Open an issue on GitHub
2. Describe your use case
3. Vote on existing issues

This helps prioritize which limitations to address first.
