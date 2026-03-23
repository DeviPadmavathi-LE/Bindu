"""Tests for GrpcAgentClient — the callable that replaces manifest.run."""

from unittest.mock import MagicMock, patch


from bindu.grpc.client import GrpcAgentClient
from bindu.grpc.generated import agent_handler_pb2


class TestGrpcAgentClient:
    """Test GrpcAgentClient behavior as a manifest.run replacement."""

    def test_init(self):
        """Test client initialization stores address and timeout."""
        client = GrpcAgentClient("localhost:50052", timeout=15.0)
        assert client._address == "localhost:50052"
        assert client._timeout == 15.0
        assert client._channel is None
        assert client._stub is None

    def test_repr(self):
        """Test string representation."""
        client = GrpcAgentClient("localhost:50052", timeout=30.0)
        assert "localhost:50052" in repr(client)
        assert "30.0" in repr(client)

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_plain_string_response(self, mock_stub_class, mock_channel):
        """Test that plain text response returns str (maps to 'completed')."""
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HandleMessages.return_value = agent_handler_pb2.HandleResponse(
            content="Hello from agent",
            state="",
            prompt="",
        )

        client = GrpcAgentClient("localhost:50052")
        result = client([{"role": "user", "content": "Hi"}])

        assert isinstance(result, str)
        assert result == "Hello from agent"

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_input_required_response(self, mock_stub_class, mock_channel):
        """Test that input-required state returns dict with state key."""
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HandleMessages.return_value = agent_handler_pb2.HandleResponse(
            content="",
            state="input-required",
            prompt="Can you clarify?",
        )

        client = GrpcAgentClient("localhost:50052")
        result = client([{"role": "user", "content": "Do something"}])

        assert isinstance(result, dict)
        assert result["state"] == "input-required"
        assert result["prompt"] == "Can you clarify?"

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_auth_required_response(self, mock_stub_class, mock_channel):
        """Test that auth-required state returns dict with state key."""
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HandleMessages.return_value = agent_handler_pb2.HandleResponse(
            content="",
            state="auth-required",
            prompt="Please authenticate",
        )

        client = GrpcAgentClient("localhost:50052")
        result = client([{"role": "user", "content": "Secret data"}])

        assert isinstance(result, dict)
        assert result["state"] == "auth-required"
        assert result["prompt"] == "Please authenticate"

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_response_with_metadata(self, mock_stub_class, mock_channel):
        """Test that metadata from response is included in result dict."""
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub

        response = agent_handler_pb2.HandleResponse(
            content="Processing",
            state="input-required",
            prompt="Which format?",
        )
        response.metadata["source"] = "test"
        mock_stub.HandleMessages.return_value = response

        client = GrpcAgentClient("localhost:50052")
        result = client([{"role": "user", "content": "Convert"}])

        assert isinstance(result, dict)
        assert result["source"] == "test"

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_messages_converted_to_proto(self, mock_stub_class, mock_channel):
        """Test that input messages are correctly converted to proto format."""
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HandleMessages.return_value = agent_handler_pb2.HandleResponse(
            content="ok", state=""
        )

        client = GrpcAgentClient("localhost:50052")
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        client(messages)

        # Verify the proto request was constructed correctly
        call_args = mock_stub.HandleMessages.call_args
        request = call_args[0][0]
        assert len(request.messages) == 3
        assert request.messages[0].role == "system"
        assert request.messages[0].content == "You are helpful"
        assert request.messages[1].role == "user"
        assert request.messages[2].role == "assistant"

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_lazy_connection(self, mock_stub_class, mock_channel):
        """Test that gRPC channel is not created until first call."""
        client = GrpcAgentClient("localhost:50052")
        assert client._channel is None

        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HandleMessages.return_value = agent_handler_pb2.HandleResponse(
            content="ok", state=""
        )

        client([{"role": "user", "content": "test"}])
        mock_channel.assert_called_once()

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_health_check_healthy(self, mock_stub_class, mock_channel):
        """Test health check returns True for healthy agent."""
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HealthCheck.return_value = agent_handler_pb2.HealthCheckResponse(
            healthy=True, message="OK"
        )

        client = GrpcAgentClient("localhost:50052")
        assert client.health_check() is True

    @patch("bindu.grpc.client.grpc.insecure_channel")
    @patch("bindu.grpc.client.agent_handler_pb2_grpc.AgentHandlerStub")
    def test_health_check_unhealthy(self, mock_stub_class, mock_channel):
        """Test health check returns False on gRPC error."""
        import grpc as grpc_module

        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub
        mock_stub.HealthCheck.side_effect = grpc_module.RpcError()

        client = GrpcAgentClient("localhost:50052")
        assert client.health_check() is False

    def test_close(self):
        """Test close cleans up channel and stub."""
        client = GrpcAgentClient("localhost:50052")
        mock_channel = MagicMock()
        client._channel = mock_channel
        client._stub = MagicMock()

        client.close()

        mock_channel.close.assert_called_once()
        assert client._channel is None
        assert client._stub is None

    def test_close_when_not_connected(self):
        """Test close is safe when not connected."""
        client = GrpcAgentClient("localhost:50052")
        client.close()  # Should not raise
