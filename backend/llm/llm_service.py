"""
LLM Service for Concya Voice AI Backend
Based on Unmute's LLM integration pattern
"""
import asyncio
import os
from logging import getLogger
from typing import Any, AsyncIterator, Literal

import openai
from openai import AsyncOpenAI

try:
    from .llm_utils import VLLMStream, get_openai_client, rechunk_to_words
except ImportError:
    from llm_utils import VLLMStream, get_openai_client, rechunk_to_words

logger = getLogger(__name__)

# Default LLM configuration
DEFAULT_LLM_URL = os.environ.get("KYUTAI_LLM_URL", "http://localhost:8091")
DEFAULT_LLM_MODEL = os.environ.get("KYUTAI_LLM_MODEL", "mock-concya-llm")
DEFAULT_LLM_API_KEY = os.environ.get("KYUTAI_LLM_API_KEY", "mock-key")


class LLMService:
    """LLM Service that connects to external LLM APIs"""

    def __init__(
        self,
        api_base: str = DEFAULT_LLM_URL,
        model: str = DEFAULT_LLM_MODEL,
        api_key: str = DEFAULT_LLM_API_KEY,
    ):
        self.api_base = api_base
        self.model = model
        self.api_key = api_key
        self.client = get_openai_client(api_base, api_key)
        logger.info(f"Initialized LLM Service with model: {model}")

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        stream: bool = True,
    ) -> AsyncIterator[str]:
        """
        Generate a response from the LLM
        Yields text chunks for streaming
        """
        try:
            llm_stream = VLLMStream(self.client, temperature=temperature)

            async for chunk in rechunk_to_words(llm_stream.chat_completion(messages)):
                yield chunk

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            yield f"Error: {str(e)}"

    async def health_check(self) -> bool:
        """Check if LLM service is available"""
        try:
            # Simple HTTP health check
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/health", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            # Fallback: try models endpoint
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.api_base}/v1/models",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=5.0
                    )
                    return response.status_code == 200
            except Exception as e2:
                logger.error(f"LLM models check also failed: {e2}")
                return False


# Global LLM service instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


async def test_llm_service():
    """Test function for LLM service"""
    service = get_llm_service()

    # Test health check
    healthy = await service.health_check()
    print(f"LLM Service Health: {healthy}")

    if healthy:
        # Test simple generation
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]

        print("Testing LLM generation:")
        async for chunk in service.generate_response(messages):
            print(chunk, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(test_llm_service())
