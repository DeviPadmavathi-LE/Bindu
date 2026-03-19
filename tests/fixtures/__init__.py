"""Organized test fixtures for Bindu test suite.

This module provides centralized fixture management, split into logical categories:
- auth_fixtures: Authentication and authorization fixtures
- storage_fixtures: Storage layer fixtures (memory, postgres)
- payment_fixtures: Payment and x402 extension fixtures
- mock_fixtures: Mock objects and services
"""

from tests.fixtures.auth_fixtures import *
from tests.fixtures.mock_fixtures import *
from tests.fixtures.payment_fixtures import *
from tests.fixtures.storage_fixtures import *

__all__ = [
    # Auth fixtures
    "mock_hydra_client",
    "mock_auth_middleware",
    # Storage fixtures
    "memory_storage",
    "memory_scheduler",
    # Payment fixtures
    "mock_payment_requirements",
    "mock_payment_payload",
    # Mock fixtures
    "mock_agent",
    "mock_agent_input_required",
    "mock_agent_auth_required",
    "mock_agent_error",
    "mock_manifest",
    "mock_did_extension",
    "mock_notification_service",
]
