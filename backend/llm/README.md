# Concya Backend - LLM Module

This module provides LLM (Large Language Model) integration for the Concya voice AI backend, based on Unmute's architecture.

## 🎯 Step 1: Basic LLM Service Setup ✅

### What's Been Implemented

#### 1. **LLM Service** (`llm_service.py`)
- Connects to external LLM APIs (OpenAI-compatible)
- Provides streaming text generation
- Health check functionality
- Configurable model and API settings

#### 2. **LLM Utilities** (`llm_utils.py`)
- `VLLMStream`: Streaming LLM interface
- `rechunk_to_words()`: Converts token streams to word streams
- OpenAI client factory
- Message preprocessing utilities

#### 3. **System Prompt** (`system_prompt.py`)
- Defines Concya's personality and behavior
- Configurable instructions system
- Voice-optimized conversation guidelines

#### 4. **Chatbot** (`chatbot.py`)
- Manages conversation state (`waiting_for_user`, `user_speaking`, `bot_speaking`)
- Handles incremental message building
- Interruption and silence handling

#### 5. **Testing** (`test_llm_integration.py`)
- Comprehensive test suite
- Verifies all components work together
- Mock responses for offline testing

## 🚀 Configuration

Set these environment variables:

```bash
export KYUTAI_LLM_URL="http://localhost:8091"        # LLM API base URL
export KYUTAI_LLM_MODEL="meta-llama/Llama-3.2-3B-Instruct"  # Model name
export KYUTAI_LLM_API_KEY="your-api-key-here"       # API key
```

## 🧪 Testing

Run the integration tests:

```bash
cd backend/llm
python test_llm_integration.py
```

Expected output:
```
🚀 Starting LLM Integration Tests for Concya Backend
============================================================
🧪 Testing LLM Service...
   Health check: ✅ PASS
   (or ⚠️ if service unavailable)

🧪 Testing Chatbot...
   Initial state: waiting_for_user ✅
   Added user message: True ✅
   State after user msg: user_speaking ✅
   Added assistant msg: True ✅
   Final state: bot_speaking ✅

🧪 Testing Streaming Integration...
   Prepared 2 messages for LLM
   Streaming response:
   [LLM response appears here]
   ✅ Received X chunks, Y characters

📊 Test Results:
   1. LLM Service: ✅ PASS
   2. Chatbot: ✅ PASS
   3. Streaming Integration: ✅ PASS

🎯 Overall: 3/3 tests passed
🎉 All tests passed! LLM integration is ready for Step 2.
```

## 📁 File Structure

```
backend/llm/
├── llm_service.py          # Main LLM service
├── llm_utils.py           # Utilities and streaming
├── system_prompt.py       # AI personality & instructions
├── chatbot.py             # Conversation management
├── test_llm_integration.py # Integration tests
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## 🎯 Next Steps

**Step 2**: Service discovery and WebSocket server setup
- Create LLM WebSocket server for real-time connections
- Implement service discovery patterns
- Add connection pooling and error handling

Ready to proceed to Step 2? Run the tests first to verify everything works!
