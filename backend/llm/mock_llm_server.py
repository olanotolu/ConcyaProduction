#!/usr/bin/env python3
"""
Mock LLM Server for Testing Concya Backend
Simulates OpenAI-compatible API for development/testing
"""
import asyncio
import json
import time
from typing import Dict, List, Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI(title="Mock Concya LLM Server")

# Sample responses for testing
MOCK_RESPONSES = {
    "hello": "Hello! I'm Concya, your voice AI assistant. How can I help you today?",
    "reservation": "I'd be happy to help you make a reservation. What type of reservation would you like to make?",
    "joke": "Why don't scientists trust atoms? Because they make up everything! 🤣",
    "default": "I understand. Can you tell me more about what you'd like to discuss?"
}

def get_mock_response(user_message: str) -> str:
    """Get a mock response based on user input"""
    user_lower = user_message.lower()

    for key, response in MOCK_RESPONSES.items():
        if key in user_lower:
            return response

    return MOCK_RESPONSES["default"]

async def stream_mock_response(response_text: str):
    """Stream the response token by token"""
    words = response_text.split()

    for i, word in enumerate(words):
        # Simulate realistic token timing
        await asyncio.sleep(0.1)  # 100ms per word

        chunk = {
            "id": f"chatcmpl-mock-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "mock-concya-llm",
            "choices": [{
                "index": 0,
                "delta": {
                    "content": word + (" " if i < len(words) - 1 else "")
                },
                "finish_reason": None
            }]
        }

        yield f"data: {json.dumps(chunk)}\n\n"

    # Send final chunk
    final_chunk = {
        "id": f"chatcmpl-mock-{int(time.time())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "mock-concya-llm",
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }

    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Mock OpenAI chat completions endpoint"""
    data = await request.json()
    messages = data.get("messages", [])

    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    response_text = get_mock_response(user_message)

    return StreamingResponse(
        stream_mock_response(response_text),
        media_type="text/plain"
    )

@app.get("/v1/models")
async def list_models():
    """Mock models endpoint"""
    return {
        "object": "list",
        "data": [{
            "id": "mock-concya-llm",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "concya"
        }]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mock-llm-server"}

if __name__ == "__main__":
    print("🚀 Starting Mock LLM Server for Concya Backend Testing")
    print("📍 Server will run on: http://localhost:8091")
    print("🔧 Endpoints:")
    print("   POST /v1/chat/completions - Chat completions")
    print("   GET  /v1/models - List models")
    print("   GET  /health - Health check")
    print("🛑 Press Ctrl+C to stop")

    uvicorn.run(
        "mock_llm_server:app",
        host="0.0.0.0",
        port=8091,
        reload=False,
        log_level="info"
    )
