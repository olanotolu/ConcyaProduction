# 🚀 Quick Start - Concya STT Client

## TL;DR - Get Running in 30 Seconds

```bash
cd /Users/term_/Desktop/Concya/client

# Install (first time only)
pip install -r requirements.txt

# Run standard mode
python stt_client.py --url ws://34.138.105.85:8080

# Speak → See text appear immediately
```

## JSON Mode (For Integration)

```bash
# Run JSON mode
python stt_client.py --url ws://34.138.105.85:8080 --json

# Speak a phrase, then PAUSE for 2-3 seconds
# JSON will appear after the pause
```

**Example:**
```
You: "Hello, I'd like to make a reservation" [pause 3 seconds]
Output: {"timestamp": 1730940001.25, "text": "hello i'd like to make a reservation", "speaker": "user", "confidence": 0.95}
```

## ⚠️ Important: JSON Output Requires Pauses!

The JSON mode uses Voice Activity Detection (VAD) to group words into utterances.

**You MUST pause 2-3 seconds after speaking** to trigger the JSON output.

```
✅ CORRECT:
"Hello" → [PAUSE 3s] → JSON appears
"How are you" → [PAUSE 3s] → JSON appears

❌ WRONG:
"Hello how are you nice weather" → [no pause] → No JSON output yet
```

## Test It Right Now

### Test 1: Standard Mode (Immediate Output)
```bash
python stt_client.py --url ws://34.138.105.85:8080
```
Speak: "Testing one two three"
See: `testing one two three` (appears word by word)

### Test 2: JSON Mode (Pause-Based)
```bash
python stt_client.py --url ws://34.138.105.85:8080 --json
```
1. Speak: "Hello world"
2. **PAUSE for 3 seconds** 
3. See: `{"timestamp": ..., "text": "hello world", ...}`
4. Speak: "This is awesome"
5. **PAUSE for 3 seconds**
6. See: `{"timestamp": ..., "text": "this is awesome", ...}`

## Common First-Time Issues

### "I don't see any JSON output"
**Solution:** You need to **pause for 2-3 seconds** after speaking. The JSON appears after the pause, not during speech.

### "Microphone permission error"
**Solution (macOS):** System Preferences → Security & Privacy → Microphone → Allow Terminal

### "Connection refused"
**Solution:** Check that server is running at `34.138.105.85:8080`

## Next Steps

- 📖 [Full README](README.md) - Complete documentation
- 💡 [Usage Tips](USAGE_TIPS.md) - Understanding JSON behavior
- 🔧 [Example Integration](example_json_consumer.py) - Python example

## Need Help?

Run with standard mode first to verify everything works:
```bash
python stt_client.py --url ws://34.138.105.85:8080
```

If you see text appearing as you speak, then JSON mode will work too (remember to pause!).

