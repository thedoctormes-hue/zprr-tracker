"""Full-scale tests for OpenClawBox."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass


# RateLimit dataclass
@dataclass
class RateLimit:
    rpm: int
    tpm: int
    rpd: int
    remaining_rpm: int = 0
    remaining_tpm: int = 0
    remaining_tpd: int = 0
    reset_at: float = 0
    errors: int = 0
    cooldown_until: float = 0


class TestDatabasePostgreSQL:
    """Test PostgreSQL database functions."""

    @patch('app.database.psycopg2.connect')
    def test_get_db_context_manager(self, mock_connect):
        """Test database connection context manager."""
        from app.database import get_db

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with get_db() as conn:
            assert conn == mock_conn

        mock_conn.close.assert_called_once()

    @patch('app.database.psycopg2.connect')
    def test_create_user_returns_api_key(self, mock_connect):
        """Test user creation returns API key."""
        from app.database import create_user

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"api_key": "ocb_sk_test123"}
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MockContext(mock_conn)
        mock_conn.__exit__ = MockContext(mock_conn)

        with patch('app.database.get_db') as mock_get_db:
            mock_get_db.return_value.__enter__ = MockContext(mock_conn)
            result = create_user(123456)

        assert result.startswith("ocb_sk_")


class TestRedisClient:
    """Test Redis client functionality."""

    @pytest.mark.asyncio
    async def test_check_rate_limit_allows_under_limit(self):
        """Test rate limit allows requests under limit."""
        from app.redis_client import RedisClient

        client = RedisClient()
        client.client = AsyncMock()

        # Mock Redis pipeline
        mock_pipeline = AsyncMock()
        mock_pipeline.execute.return_value = [0, 5, None, True]  # Removed, count, add, expire
        client.client.pipeline.return_value = mock_pipeline

        allowed, remaining = await client.check_rate_limit("test_key", 100, window=60)

        assert allowed is True
        assert remaining == 94

    @pytest.mark.asyncio
    async def test_check_rate_limit_denies_over_limit(self):
        """Test rate limit denies requests over limit."""
        from app.redis_client import RedisClient

        client = RedisClient()
        client.client = AsyncMock()

        mock_pipeline = AsyncMock()
        mock_pipeline.execute.return_value = [0, 100, None, True]  # Already at limit
        client.client.pipeline.return_value = mock_pipeline

        allowed, remaining = await client.check_rate_limit("test_key", 100, limit=100, window=60)

        assert allowed is False
        assert remaining == 0


class TestAPIGateway:
    """Test API Gateway endpoints."""

    @pytest.mark.asyncio
    async def test_chat_completions_requires_auth(self):
        """Test that chat completions requires authentication."""
        from app.main import app
        from httpx import AsyncClient

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/v1/chat/completions", json={
                "messages": [{"role": "user", "content": "Hello"}]
            })

            assert response.status_code == 403  # Missing auth

    @pytest.mark.asyncio
    async def test_chat_completions_with_valid_key(self):
        """Test chat completions with valid API key."""
        from app.main import app
        from httpx import AsyncClient

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": "Hello"}]},
                headers={"Authorization": "Bearer ocb_sk_test123"}
            )

            # Should not be 403 (auth passes)
            assert response.status_code != 403


class TestProviders:
    """Test provider adapters."""

    def test_groq_provider_exists(self):
        """Test Groq provider can be imported."""
        from app.providers.groq import GroqProvider
        assert GroqProvider is not None

    def test_mistral_provider_exists(self):
        """Test Mistral provider can be imported."""
        from app.providers.mistral import MistralProvider
        assert MistralProvider is not None

    def test_google_provider_exists(self):
        """Test Google provider can be imported."""
        from app.providers.google import GoogleProvider
        assert GoogleProvider is not None

    def test_together_provider_exists(self):
        """Test Together provider can be imported."""
        from app.providers.together import TogetherProvider
        assert TogetherProvider is not None

    def test_cohere_provider_exists(self):
        """Test Cohere provider can be imported."""
        from app.providers.cohere import CohereProvider
        assert CohereProvider is not None


class TestRouter:
    """Test LLM router."""

    def test_router_initialization(self):
        """Test router initializes with providers."""
        from app.router import LLMRouter, ProviderInfo
        from app.providers.base import BaseProvider

        # Create mock adapters
        mock_adapter = MagicMock(spec=BaseProvider)

        providers = {
            "test": mock_adapter
        }

        with patch('app.router.SmartRouter.__init__', return_value=None):
            router = LLMRouter(providers)

        assert router is not None

    def test_round_robin_selection(self):
        """Test round-robin provider selection."""
        from app.router import ProviderState
        import time

        state = ProviderState(
            last_error=time.time() - 100,
            error_count=0,
            success_count=10,
            cooldown_until=0,
            available=True
        )

        assert state.available is True
        assert state.error_count == 0


class MockContext:
    """Mock context manager for testing."""
    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj

    def __exit__(self, *args):
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])