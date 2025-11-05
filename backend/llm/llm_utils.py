"""
LLM Utilities for Concya Voice AI Backend
Based on Unmute's LLM integration
"""
import asyncio
from logging import getLogger
from typing import Any, AsyncIterator

import openai
from openai import AsyncOpenAI

logger = getLogger(__name__)

# Special tokens for interruption handling
INTERRUPTION_CHAR = "\x00"
USER_SILENCE_MARKER = "[USER_SILENCE]"


def preprocess_messages_for_llm(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Preprocess messages before sending to LLM"""
    return messages


def get_openai_client(api_base: str, api_key: str) -> AsyncOpenAI:
    """Create OpenAI client with custom base URL"""
    return AsyncOpenAI(
        api_key=api_key,
        base_url=api_base,
    )


async def rechunk_to_words(iterator: AsyncIterator[str]) -> AsyncIterator[str]:
    """
    Rechunk text stream into word-by-word output
    Based on Unmute's implementation
    """
    buffer = ""
    async for chunk in iterator:
        buffer += chunk
        while " " in buffer:
            space_idx = buffer.index(" ")
            word = buffer[:space_idx + 1]  # Include the space
            buffer = buffer[space_idx + 1:]
            yield word

    # Yield remaining buffer
    if buffer.strip():
        yield buffer


class VLLMStream:
    """Streaming LLM interface compatible with OpenAI API"""

    def __init__(self, client: AsyncOpenAI, temperature: float = 0.7):
        self.client = client
        self.temperature = temperature

    async def chat_completion(
        self, messages: list[dict[str, Any]]
    ) -> AsyncIterator[str]:
        """Stream chat completion responses"""
        try:
            stream = await self.client.chat.completions.create(
                model="local-model",  # This will be overridden by the server
                messages=messages,
                temperature=self.temperature,
                stream=True,
                max_tokens=1024,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield content

        except Exception as e:
            logger.error(f"VLLM Stream error: {e}")
            yield f"Error: {str(e)}"


class Timer:
    """Simple timer for measuring latency"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = asyncio.get_event_loop().time()

    def stop(self):
        self.end_time = asyncio.get_event_loop().time()

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            return asyncio.get_event_loop().time() - self.start_time
        return self.end_time - self.start_time


# Test functions
async def test_llm_utils():
    """Test LLM utilities"""
    print("Testing LLM Utils...")

    # Test rechunk_to_words
    async def mock_stream():
        yield "Hello "
        yield "world "
        yield "this "
        yield "is "
        yield "a "
        yield "test"

    print("Testing rechunk_to_words:")
    async for word in rechunk_to_words(mock_stream()):
        print(f"'{word}'", end="")
    print("\n")

    # Test client creation
    try:
        client = get_openai_client("http://localhost:8091", "test-key")
        print("✅ OpenAI client created successfully")
    except Exception as e:
        print(f"❌ OpenAI client creation failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_llm_utils())
