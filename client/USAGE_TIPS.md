# Concya STT Client - Usage Tips

## Understanding JSON Output Behavior

### How JSON Output Works

The JSON output mode uses **Voice Activity Detection (VAD)** to detect natural pauses in speech. Here's how it behaves:

#### **Utterance-Based Output**
- Words are **buffered** as you speak
- JSON is output when the VAD detects a **pause** (2+ seconds of silence)
- You get **one JSON object per utterance**, not per word

#### **What You'll See**

When you run:
```bash
python stt_client.py --url ws://34.138.105.85:8080 --json
```

1. **While speaking:** No output (words are being buffered)
2. **After pause:** JSON object appears with complete utterance
3. **After Ctrl+C:** Any buffered words are flushed as final JSON

### Example Flow

```bash
# Start client
python stt_client.py --url ws://34.138.105.85:8080 --json

# You speak: "Hello how are you"
# (no output yet - buffering)

# You pause for 2 seconds...
{"timestamp": 1730940001.25, "text": "hello how are you", "speaker": "user", "confidence": 0.95}

# You speak: "I'd like to make a reservation"
# (no output yet - buffering)

# You pause for 2 seconds...
{"timestamp": 1730940005.12, "text": "i'd like to make a reservation", "speaker": "user", "confidence": 0.95}

# You press Ctrl+C
# Any remaining words are output before exit
```

## Common Issues & Solutions

### Issue 1: No JSON Output Appears

**Symptom:** You see "Starting the transcription" but no JSON

**Causes:**
1. You haven't spoken yet
2. You're still speaking (haven't paused)
3. Microphone isn't picking up audio
4. Background noise is preventing VAD from detecting pause

**Solutions:**
```bash
# Verify microphone is working (standard mode)
python stt_client.py --url ws://34.138.105.85:8080

# If text appears, try JSON mode with pauses
python stt_client.py --url ws://34.138.105.85:8080 --json

# Speak a short phrase, then PAUSE for 2-3 seconds
# JSON should appear after the pause
```

### Issue 2: Want Immediate Word-by-Word Output

**Current behavior:** Words are buffered until pause

**Workaround:** Use standard text mode for real-time word output
```bash
python stt_client.py --url ws://34.138.105.85:8080
# Words appear immediately as spoken
```

**Future enhancement:** Add `--streaming-json` flag for word-level JSON output

### Issue 3: JSON Not Appearing Until Ctrl+C

**Cause:** Not pausing long enough between utterances

**Solution:** Pause for **2-3 seconds** after each phrase to trigger VAD

```bash
# Speak: "Hello" → PAUSE 3 seconds → JSON appears
# Speak: "How are you" → PAUSE 3 seconds → JSON appears
```

## Tips for Best Results

### 1. Pause Between Utterances
```
✅ GOOD: "Hello" [pause 2s] "How are you" [pause 2s] "Nice weather"
❌ BAD:  "Hello how are you nice weather" [no pauses]
```

### 2. Check Microphone First
```bash
# Test in standard mode first
python stt_client.py --url ws://34.138.105.85:8080

# If you see text appearing, JSON mode will work too
```

### 3. Use VAD Visualization for Debugging
```bash
# See when pauses are detected
python stt_client.py --url ws://34.138.105.85:8080 --show-vad

# Output: "hello how are you | nice weather |"
# The "|" shows where VAD detected pauses
```

### 4. Quiet Environment
- Minimize background noise
- Speak clearly at normal volume
- Keep microphone at consistent distance

### 5. Save to File
```bash
# Capture all JSON output
python stt_client.py --url ws://34.138.105.85:8080 --json > transcripts.jsonl

# Press Ctrl+C when done - all utterances saved
```

## Advanced Usage

### Real-Time Processing
```python
# process_realtime.py
import subprocess
import json
import sys

process = subprocess.Popen(
    ["python", "stt_client.py", "--url", "ws://34.138.105.85:8080", "--json"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

print("Listening... (speak in short phrases with pauses)")

try:
    for line in process.stdout:
        if line.strip():
            data = json.loads(line)
            print(f"✓ Transcribed: {data['text']}")
            
            # Your processing here
            if "reservation" in data['text'].lower():
                print("  → Booking intent detected!")
                
except KeyboardInterrupt:
    process.terminate()
```

### Timeout Handler
```python
# For situations where you need output even without pauses
import subprocess
import json
import threading
import time

def timeout_handler(process):
    """Force flush after 10 seconds of no output"""
    time.sleep(10)
    process.send_signal(signal.SIGTERM)

# Start with timeout
process = subprocess.Popen([...])
timer = threading.Timer(10.0, timeout_handler, [process])
timer.start()

# Process output...
```

## Comparison: Standard vs JSON Mode

| Feature | Standard Mode | JSON Mode |
|---------|---------------|-----------|
| **Output** | Words as spoken | Complete utterances |
| **Timing** | Immediate | After pause detected |
| **Format** | Plain text | Structured JSON |
| **Use Case** | Live demo/debugging | Application integration |
| **Buffering** | No | Yes (until pause) |
| **Timestamps** | No | Yes (per utterance) |

## Quick Reference

```bash
# Standard text output (immediate)
python stt_client.py --url ws://34.138.105.85:8080

# JSON output (pause-based)
python stt_client.py --url ws://34.138.105.85:8080 --json

# JSON with VAD visualization
python stt_client.py --url ws://34.138.105.85:8080 --json --show-vad

# List microphones
python stt_client.py --list-devices

# Use specific mic with JSON
python stt_client.py --url ws://34.138.105.85:8080 --device 1 --json

# Save to file
python stt_client.py --url ws://34.138.105.85:8080 --json > output.jsonl
```

## Need Help?

See [README.md](README.md) for complete documentation.

**Remember:** In JSON mode, pause for 2-3 seconds after speaking to see output! 🎤⏸️

