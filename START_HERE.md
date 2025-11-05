# 🍽️ Concya - Quick Start Guide

**Restaurant Voice Agent for Reservations**

---

## 📋 What You Have

- **STT Server**: Running on GCP (Google Cloud Platform) at `34.26.22.244:8080`
- **Local Client**: Python scripts on your Mac to capture audio and interact with the LLM
- **LLM Integration**: OpenAI GPT for conversation management

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Start the GCP Server

**SSH into your GCP VM:**
```bash
gcloud compute ssh concya --zone=us-central1-a --project=concyaproduction
```

**Navigate to project directory:**
```bash
cd ~/ConcyaProduction
source ~/stt_env/bin/activate
```

**Start the STT server:**
```bash
moshi-server worker --config stt/configs/config-stt-en-hf.toml
```

**You should see:**
```
listening on http://0.0.0.0:8080
```

**⚠️ Keep this terminal open! The server runs in the foreground.**

---

### Step 2: Test the Connection (Optional)

**On your Mac, open a new terminal:**
```bash
nc -zv 34.26.22.244 8080
```

**Expected output:**
```
Connection to 34.26.22.244 port 8080 [tcp/*] succeeded!
```

---

### Step 3: Run the Voice Agent

**On your Mac:**

```bash
cd /Users/term_/Desktop/Concya/llm

# Set your OpenAI API key (REQUIRED)
export OPENAI_API_KEY="your-api-key-here"

# Run the voice agent
./run_concya_enhanced.sh
```

**Expected output:**
```
🍽️  Concya Enhanced Voice Agent
============================================================
Mode: Intent-Based Structured Parsing
Speak naturally to make a reservation...
Press Ctrl+C to stop
```

---

## 🎤 How to Use

**Just speak naturally!** Examples:

- "Hi, I'd like to make a reservation"
- "Table for 4 people"
- "Tomorrow at 7 PM"
- "The name is John Smith"

The system will:
1. 🎙️ Capture your speech via microphone
2. 📡 Send audio to GCP for transcription
3. 🧠 Parse your intent (party size, date, time, name)
4. 💬 Generate restaurant responses via GPT
5. ✅ Confirm reservation details

---

## 🛠️ Troubleshooting

### Issue: "HTTP 404" or "Connection refused"

**Solution:** Restart the GCP server
```bash
# SSH into GCP (if not already connected)
gcloud compute ssh concya --zone=us-central1-a --project=concyaproduction

# Kill existing server
pkill -f moshi-server

# Restart server
cd ~/ConcyaProduction
source ~/stt_env/bin/activate
moshi-server worker --config stt/configs/config-stt-en-hf.toml
```

---

### Issue: "No transcription output"

**Check microphone permissions:**
- macOS: System Settings → Privacy & Security → Microphone
- Grant access to Terminal/iTerm

**Test microphone:**
```bash
cd /Users/term_/Desktop/Concya/stt/client
python stt_client.py --list-devices
```

---

### Issue: "OPENAI_API_KEY not set"

**Set the environment variable:**
```bash
export OPENAI_API_KEY="sk-proj-..."
```

Or add it to your `~/.zshrc`:
```bash
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.zshrc
source ~/.zshrc
```

---

## 📁 Project Structure

```
Concya/
├── START_HERE.md          ← You are here!
├── README.md              ← Full documentation
├── stt/                   ← Speech-to-Text components
│   ├── client/            ← Local Python client
│   │   └── stt_client.py  ← Microphone capture script
│   └── server/            ← GCP server configs
│       └── configs/       ← moshi-server configuration
└── llm/                   ← LLM integration
    ├── run_concya_enhanced.sh  ← Main entry point
    ├── stt_llm_bridge_enhanced.py
    ├── intent_parser.py
    └── openai_connector.py
```

---

## 🔑 Important Files

| File | Location | Purpose |
|------|----------|---------|
| **moshi-server** | GCP VM | STT inference engine (Rust) |
| **stt_client.py** | Your Mac | Captures mic audio, sends to GCP |
| **run_concya_enhanced.sh** | Your Mac | Main script to run voice agent |
| **stt_llm_bridge_enhanced.py** | Your Mac | Connects STT → LLM |
| **intent_parser.py** | Your Mac | Extracts reservation details |

---

## 🌐 What's Running Where?

### On GCP (34.26.22.244:8080):
- ✅ `moshi-server` - STT inference with CUDA acceleration
- ✅ Listens on WebSocket: `ws://34.26.22.244:8080/api/asr-streaming`
- ✅ Processes audio → returns text transcriptions

### On Your Mac:
- ✅ `stt_client.py` - Captures microphone audio
- ✅ `stt_llm_bridge_enhanced.py` - Orchestrates STT → LLM flow
- ✅ `intent_parser.py` - Extracts reservation data
- ✅ `openai_connector.py` - Talks to GPT API

---

## 🎯 Testing Individual Components

### Test STT Only (No LLM):
```bash
cd /Users/term_/Desktop/Concya/stt/client
python stt_client.py --json --device 1
```

Speak into your microphone. You should see:
```json
{"timestamp": 1730940123.45, "text": "hello can you hear me", "speaker": "user", "confidence": 0.95}
```

---

### Test Intent Parser:
```bash
cd /Users/term_/Desktop/Concya/llm
python intent_parser.py
```

Try test phrases like:
- "Table for 4"
- "Tomorrow at 7 PM"
- "My name is John"

---

## 💰 Cost Estimates

| Component | Provider | Estimated Cost |
|-----------|----------|----------------|
| GCP VM (L4 GPU) | Google Cloud | ~$1.20/hour |
| OpenAI API (GPT-3.5-turbo) | OpenAI | ~$0.002 per conversation |

**💡 Tip:** Stop the GCP VM when not in use to save costs!

```bash
gcloud compute instances stop concya --zone=us-central1-a
```

---

## 🚦 Server Management

### Start GCP VM:
```bash
gcloud compute instances start concya --zone=us-central1-a
```

### Stop GCP VM:
```bash
gcloud compute instances stop concya --zone=us-central1-a
```

### Check Server Status:
```bash
# On GCP VM:
ps aux | grep moshi-server

# From your Mac:
nc -zv 34.26.22.244 8080
```

---

## 📝 Next Steps

1. ✅ Start the GCP server
2. ✅ Run the voice agent on your Mac
3. ✅ Test with sample reservations
4. 📈 Monitor latency and accuracy
5. 🎨 Customize conversation prompts in `stt_llm_bridge_enhanced.py`
6. 🔧 Adjust intent parsing rules in `intent_parser.py`

---

## 📚 More Information

- Full documentation: `README.md`
- STT details: `stt/README.md`
- LLM integration: `llm/README.md`

---

## 🆘 Need Help?

**Common commands at a glance:**

```bash
# Start everything:
./llm/run_concya_enhanced.sh

# Test STT only:
./stt/client/stt_client.py --json

# Restart GCP server:
gcloud compute ssh concya --command "pkill -f moshi-server && cd ~/ConcyaProduction && moshi-server serve --config stt/configs/config-stt-en-hf.toml"
```

---

**🎉 You're ready to take restaurant reservations with voice! 🎉**

