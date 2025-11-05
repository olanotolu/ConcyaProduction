#!/bin/bash

# Concya Enhanced STT to LLM Bridge with Intent Parsing
# This version uses structured intent parsing for better accuracy

# --- Configuration ---
# Your OpenAI API Key (NEVER COMMIT THIS TO GIT!)
# Set this environment variable: export OPENAI_API_KEY="your-key-here"
OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}"

# Your GCP STT Server URL
STT_SERVER_URL="ws://34.26.22.244:8080"

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

# Run the enhanced STT-LLM bridge script
python stt_llm_bridge_enhanced.py \
  --stt-url "$STT_SERVER_URL" \
  --openai-key "$OPENAI_API_KEY" \
  --model "$LLM_MODEL" \
  --mode "$MODE"
