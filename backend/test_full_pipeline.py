#!/usr/bin/env python3
"""
Test the Complete Concya Backend Pipeline
STT → LLM → TTS Integration Test
"""
import asyncio
import os
import sys
import subprocess
import time
import threading
import signal

# Add backend to path
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

from llm.llm_service import get_llm_service
from llm.chatbot import Chatbot

def start_mock_llm_server():
    """Start the mock LLM server in a separate process"""
    print("🔄 Starting Mock LLM Server...")

    # Change to LLM directory and start server
    os.chdir(os.path.join(os.path.dirname(__file__), 'llm'))

    # Start server in background
    process = subprocess.Popen([
        sys.executable, 'mock_llm_server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait a moment for server to start
    time.sleep(2)

    # Check if server is running
    if process.poll() is None:
        print("✅ Mock LLM Server started successfully")
        return process
    else:
        print("❌ Failed to start Mock LLM Server")
        stdout, stderr = process.communicate()
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return None

def stop_mock_llm_server(process):
    """Stop the mock LLM server"""
    if process and process.poll() is None:
        print("🛑 Stopping Mock LLM Server...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Mock LLM Server stopped")

async def test_stt_connection():
    """Test STT connection to GCP server"""
    print("\n🧪 Testing STT Connection...")

    try:
        # Import here to avoid issues if websockets not installed
        import websockets
        import msgpack

        # Test connection to GCP STT server
        uri = "ws://34.26.22.244:8080/api/asr-streaming"
        headers = {"kyutai-api-key": "public_token"}

        async with websockets.connect(uri, additional_headers=headers) as websocket:
            # Send ready message
            await websocket.send(msgpack.packb({"type": "Audio", "pcm": [0.0] * 1920}))

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = msgpack.unpackb(response)

            if data.get("type") == "Ready":
                print("✅ STT Server connection successful")
                return True
            else:
                print(f"❌ Unexpected STT response: {data}")
                return False

    except Exception as e:
        print(f"❌ STT Connection failed: {e}")
        return False

async def test_llm_integration():
    """Test LLM integration with chatbot"""
    print("\n🧪 Testing LLM Integration...")

    try:
        # Test LLM service
        service = get_llm_service()
        healthy = await service.health_check()

        if not healthy:
            print("❌ LLM Service not healthy")
            return False

        print("✅ LLM Service health check passed")

        # Test chatbot integration
        chatbot = Chatbot()
        await chatbot.add_chat_message_delta("Hello", "user")

        messages = chatbot.preprocess_messages()
        print(f"✅ Prepared {len(messages)} messages for LLM")

        # Test streaming response
        full_response = ""
        chunk_count = 0

        async for chunk in service.generate_response(messages):
            full_response += chunk
            chunk_count += 1

        print(f"✅ Received {chunk_count} chunks, {len(full_response)} characters")
        print(f"📝 Response: {full_response[:100]}{'...' if len(full_response) > 100 else ''}")

        # Add response to chatbot
        await chatbot.add_chat_message_delta(full_response, "assistant")
        print(f"✅ Added response to conversation history")

        return True

    except Exception as e:
        print(f"❌ LLM Integration failed: {e}")
        return False

async def test_full_pipeline():
    """Test the complete STT → LLM pipeline"""
    print("\n🧪 Testing Full Pipeline (STT → LLM)...")

    try:
        # Simulate STT transcription
        chatbot = Chatbot()
        stt_transcription = "I'd like to make a reservation"

        print(f"🎤 Simulating STT input: '{stt_transcription}'")

        # Add to chatbot (simulating STT → LLM)
        await chatbot.add_chat_message_delta(stt_transcription, "user")
        print("✅ Added STT transcription to chatbot")

        # Get LLM response
        messages = chatbot.preprocess_messages()
        service = get_llm_service()

        print("🤖 Getting LLM response...")
        full_response = ""

        async for chunk in service.generate_response(messages):
            full_response += chunk

        print(f"✅ LLM Response: '{full_response}'")

        # Add response back to chatbot
        await chatbot.add_chat_message_delta(full_response, "assistant")
        print("✅ Added LLM response to conversation")

        # Check conversation state
        state = chatbot.conversation_state()
        print(f"📊 Final conversation state: {state}")

        return True

    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False

async def run_all_tests():
    """Run all backend tests"""
    print("🚀 Concya Backend Full Pipeline Test")
    print("=" * 50)

    results = []

    # Start mock LLM server
    llm_process = start_mock_llm_server()
    if not llm_process:
        print("❌ Cannot proceed without LLM server")
        return

    try:
        # Test 1: STT Connection
        results.append(await test_stt_connection())

        # Test 2: LLM Integration
        results.append(await test_llm_integration())

        # Test 3: Full Pipeline
        results.append(await test_full_pipeline())

    finally:
        # Always stop the server
        stop_mock_llm_server(llm_process)

    # Report results
    print("\n" + "=" * 50)
    print("📊 Test Results:")

    test_names = ["STT Connection", "LLM Integration", "Full Pipeline"]
    passed = 0

    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {i+1}. {name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! Your backend is ready for voice integration!")
        print("\n📋 Next Steps:")
        print("   1. Replace mock LLM with real vLLM server")
        print("   2. Add TTS integration")
        print("   3. Create voice handler (UnmuteHandler)")
        print("   4. Test real-time STT → LLM → TTS pipeline")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
