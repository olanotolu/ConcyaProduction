# Concya STT Client Updates

## ✅ Completed: Structured JSON Output

### What Changed

Modified `client/stt_client.py` to support structured JSON output format for easier integration with downstream applications.

### New Features

#### 1. JSON Output Mode (`--json` flag)

The client now outputs structured JSON instead of plain text when using the `--json` flag:

```bash
python client/stt_client.py --url ws://34.138.105.85:8080 --json
```

**Output Format:**
```json
{"timestamp": 1730940001.25, "text": "hello can you hear me", "speaker": "user", "confidence": 0.95}
{"timestamp": 1730940005.12, "text": "awesome this is working", "speaker": "user", "confidence": 0.95}
```

**JSON Fields:**
- `timestamp`: Unix timestamp when utterance started (float)
- `text`: Complete transcribed utterance (string)
- `speaker`: Speaker identifier, currently always "user" (string)
- `confidence`: Transcription confidence score 0.0-1.0 (float, currently fixed at 0.95)

#### 2. Utterance-Based Output

In JSON mode, the client now:
- Groups words into complete utterances
- Detects pauses using Voice Activity Detection (VAD)
- Outputs one JSON object per utterance (not per word)
- Timestamps each utterance at the start of speech

### Files Added

1. **`client/README.md`** - Comprehensive documentation with:
   - Installation instructions
   - Usage examples for both standard and JSON output
   - Integration examples (Python, Node.js)
   - Troubleshooting guide
   - Technical specifications

2. **`example_json_consumer.py`** - Example script demonstrating:
   - How to consume JSON output in Python
   - Real-time transcription processing
   - Intent detection (reservations, party size, time)
   - Subprocess integration pattern

### Code Changes

**Modified:** `client/stt_client.py`

1. Added imports:
   - `json` - for JSON serialization
   - `time` - for timestamps

2. Modified `receive_messages()` function:
   - Added `json_output` parameter
   - Added utterance buffering logic
   - Added timestamp tracking
   - Outputs JSON when utterance completes (pause detected)

3. Modified `stream_audio()` function:
   - Added `json_output` parameter
   - Suppresses startup messages in JSON mode
   - Passes `json_output` to `receive_messages()`

4. Added command-line argument:
   - `--json` flag to enable JSON output mode

### Backward Compatibility

✅ **Fully backward compatible**

- Default behavior unchanged (human-readable text output)
- All existing flags work as before
- JSON mode is opt-in via `--json` flag

### Usage Examples

#### Basic JSON Output
```bash
python client/stt_client.py --url ws://34.138.105.85:8080 --json
```

#### JSON Output with VAD Visualization
```bash
python client/stt_client.py --url ws://34.138.105.85:8080 --json --show-vad
```

#### Save to File
```bash
python client/stt_client.py --url ws://34.138.105.85:8080 --json > transcriptions.jsonl
```

#### Process with Example Consumer
```bash
python client/example_json_consumer.py ws://34.138.105.85:8080
```

#### Integrate in Python
```python
import subprocess
import json

process = subprocess.Popen(
    ["python", "client/stt_client.py", "--url", "ws://34.138.105.85:8080", "--json"],
    stdout=subprocess.PIPE,
    text=True
)

for line in process.stdout:
    data = json.loads(line)
    print(f"Transcribed: {data['text']}")
```

### Testing

To test the new JSON output:

```bash
# Terminal 1: Start JSON output
cd /Users/term_/Desktop/Concya
python client/stt_client.py --url ws://34.138.105.85:8080 --json

# Speak into microphone and observe JSON output

# Terminal 2: Run example consumer (alternative)
python client/example_json_consumer.py ws://34.138.105.85:8080
```

### Next Steps / Future Enhancements

Potential improvements for the JSON output:

1. **Real Confidence Scores**
   - Currently fixed at 0.95
   - Requires server-side confidence information
   - Would need updates to Moshi server protocol

2. **Word-Level Timestamps**
   - Output individual words with their timing
   - Useful for alignment and analysis

3. **Speaker Diarization**
   - Distinguish between multiple speakers
   - Populate `speaker` field with actual identifiers

4. **Partial Results**
   - Stream incomplete utterances as they're being spoken
   - Add `is_partial: true/false` field

5. **Metadata Fields**
   - Audio quality indicators
   - Language detection
   - Emotion/sentiment scores

### Files Structure

```
Concya/
├── CHANGES.md (NEW)
├── client/
│   ├── stt_client.py (MODIFIED)
│   ├── README.md (NEW)
│   ├── example_json_consumer.py (NEW)
│   └── requirements.txt
└── ...
```

---

**Status:** ✅ Complete and tested
**Date:** November 4, 2025
**Version:** 1.1.0

