#!/bin/bash

# Simple STT Client - Just Speech to Text
# No LLM, No TTS - Clean transcription only

echo "🎤 Simple STT Client"
echo "==================="
echo "Just speech-to-text transcription"
echo "Server: ws://34.26.22.244:8080/api/asr-streaming"
echo

# Install basic dependencies (no TTS/LLM stuff)
pip install -q websockets msgpack sounddevice

# Run the simple STT client
python llm/stt_simple_client.py
