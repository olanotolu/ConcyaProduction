#!/bin/bash

# Concya Enhanced STT to LLM Bridge with Intent Parsing
# This version uses structured intent parsing for better accuracy

# --- Configuration ---
# API keys are loaded from .env file automatically (create .env in project root)
# See .env.example for the format

# Your GCP STT Server URL
STT_SERVER_URL="ws://34.26.22.244:8080/api/asr-streaming"

# OpenAI Model to use
LLM_MODEL="gpt-3.5-turbo" # Faster and cheaper than gpt-4

# Mode: "structured" for intent parsing, "llm" for pure LLM
MODE="structured"

# --- Script Logic ---

echo "🍽️  Starting Concya Enhanced Voice Agent..."
echo "------------------------------------------------------------"
echo "STT Server: $STT_SERVER_URL"
echo "LLM Model: $LLM_MODEL"
echo "Mode: $MODE (Intent-based parsing)"
echo "------------------------------------------------------------"

# Ensure Python dependencies are installed
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Run the enhanced STT-LLM bridge script (API keys loaded from .env)
python stt_llm_bridge_enhanced.py \
  --stt-url "$STT_SERVER_URL" \
  --model "$LLM_MODEL" \
  --mode "$MODE"
