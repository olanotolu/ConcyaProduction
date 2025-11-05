#!/bin/bash
# Concya STT → LLM Runner
# Quick start script for connecting speech to OpenAI

# Your OpenAI API key (set as environment variable)
# export OPENAI_API_KEY="your-key-here"
OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}"

# STT Server URL (your GCP server)
STT_URL="ws://34.26.22.244:8080"

# Model to use (gpt-4, gpt-3.5-turbo, etc.)
MODEL="gpt-4"

# System prompt
SYSTEM_PROMPT="You are a helpful restaurant reservation assistant for Concya restaurant. Be concise, friendly, and professional. Help customers book tables, answer questions about the menu, and provide restaurant information."

echo "🍽️  Starting Concya Voice Agent..."
echo ""

python stt_llm_bridge.py \
  --stt-url "$STT_URL" \
  --openai-key "$OPENAI_API_KEY" \
  --model "$MODEL" \
  --system-prompt "$SYSTEM_PROMPT"

