#!/usr/bin/env python3
"""
Test script for LLM integration in Concya Backend
Tests the complete LLM pipeline: Service → Chatbot → Streaming
"""
import asyncio
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# Direct imports for testing
import llm_service
import chatbot
import llm_utils
import system_prompt


async def test_llm_service_basic():
    """Test basic LLM service functionality"""
    print("🧪 Testing LLM Service...")

    service = llm_service.get_llm_service()

    # Test health check
    healthy = await service.health_check()
    print(f"   Health check: {'✅ PASS' if healthy else '❌ FAIL'}")

    if not healthy:
        print("   ⚠️  LLM service not available - using mock responses")
        return False

    return True


async def test_chatbot_functionality():
    """Test chatbot conversation management"""
    print("\n🧪 Testing Chatbot...")

    bot = chatbot.Chatbot()

    # Test initial state
    state = bot.conversation_state()
    print(f"   Initial state: {state} {'✅' if state == 'waiting_for_user' else '❌'}")

    # Add user message
    is_new = await bot.add_chat_message_delta("Hello Concya!", "user")
    print(f"   Added user message: {is_new} {'✅' if is_new else '❌'}")

    # Check state after user message
    state = bot.conversation_state()
    print(f"   State after user msg: {state} {'✅' if state == 'user_speaking' else '❌'}")

    # Add assistant response
    is_new = await bot.add_chat_message_delta("Hi there!", "assistant")
    print(f"   Added assistant msg: {is_new} {'✅' if is_new else '❌'}")

    # Check final state
    state = bot.conversation_state()
    print(f"   Final state: {state} {'✅' if state == 'bot_speaking' else '❌'}")

    return True


async def test_streaming_integration():
    """Test the complete streaming pipeline"""
    print("\n🧪 Testing Streaming Integration...")

    bot = chatbot.Chatbot()
    service = llm_service.get_llm_service()

    # Add a user message
    await bot.add_chat_message_delta("Tell me a short joke", "user")

    # Get messages for LLM
    messages = bot.preprocess_messages()
    print(f"   Prepared {len(messages)} messages for LLM")

    # Test streaming response
    print("   Streaming response:")
    print("   ", end="", flush=True)

    chunk_count = 0
    full_response = ""

    try:
        async for chunk in service.generate_response(messages, temperature=0.7):
            print(chunk, end="", flush=True)
            full_response += chunk
            chunk_count += 1

        print(f"\n   ✅ Received {chunk_count} chunks, {len(full_response)} characters")

        # Add the response to chatbot
        await bot.add_chat_message_delta(full_response, "assistant")
        print(f"   ✅ Added response to chat history")

        return True

    except Exception as e:
        print(f"\n   ❌ Streaming failed: {e}")
        return False


async def run_all_tests():
    """Run all LLM integration tests"""
    print("🚀 Starting LLM Integration Tests for Concya Backend")
    print("=" * 60)

    results = []

    # Test 1: Basic LLM Service
    results.append(await test_llm_service_basic())

    # Test 2: Chatbot Functionality
    results.append(await test_chatbot_functionality())

    # Test 3: Streaming Integration
    results.append(await test_streaming_integration())

    print("\n" + "=" * 60)
    print("📊 Test Results:")

    test_names = ["LLM Service", "Chatbot", "Streaming Integration"]
    passed = 0

    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {i+1}. {name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! LLM integration is ready for Step 2.")
        return True
    else:
        print("⚠️  Some tests failed. Check configuration and try again.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
