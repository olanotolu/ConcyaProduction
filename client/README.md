# Concya STT Client

Real-time Speech-to-Text client for Concya restaurant voice agent system.

## Installation

```bash
cd client
pip install -r requirements.txt
```

## Basic Usage

### Standard Output (Human-Readable)

```bash
python stt_client.py --url ws://34.138.105.85:8080
```

**Output:**
```
Starting microphone recording...
Press Ctrl+C to stop recording
Starting the transcription
Hello can you hear me awesome this is working
```

### JSON Output (Structured)

```bash
python stt_client.py --url ws://34.138.105.85:8080 --json
```

**Output:**
```json
{"timestamp": 1730940001.25, "text": "hello can you hear me", "speaker": "user", "confidence": 0.95}
{"timestamp": 1730940005.12, "text": "awesome this is working", "speaker": "user", "confidence": 0.95}
```

## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--url` | WebSocket server URL | `--url ws://34.138.105.85:8080` |
| `--api-key` | Authentication key | `--api-key public_token` (default) |
| `--json` | Enable structured JSON output | `--json` |
| `--show-vad` | Show voice activity detection | `--show-vad` |
| `--list-devices` | List available microphones | `--list-devices` |
| `--device N` | Use specific microphone | `--device 1` |

## Output Formats

### 1. Standard Output (Default)

Real-time text streaming to console:
```
Hello can you hear me | awesome this is working |
```

The `|` symbol indicates detected pauses (when using `--show-vad`).

### 2. JSON Output (`--json`)

Each utterance is output as a JSON object with:

```json
{
  "timestamp": 1730940001.25,
  "text": "hello can you hear me",
  "speaker": "user",
  "confidence": 0.95
}
```

**Fields:**
- `timestamp`: Unix timestamp (seconds since epoch) when utterance started
- `text`: Transcribed text (complete utterance)
- `speaker`: Always "user" (for future multi-speaker support)
- `confidence`: Transcription confidence score (0.0-1.0, currently fixed at 0.95)

## Examples

### Connect to Production Server
```bash
python stt_client.py --url ws://34.138.105.85:8080
```

### Connect to Local Development Server
```bash
python stt_client.py --url ws://127.0.0.1:8080
```

### JSON Output with VAD Visualization
```bash
python stt_client.py --url ws://34.138.105.85:8080 --json --show-vad
```

### Select Specific Microphone
```bash
# List available microphones
python stt_client.py --list-devices

# Use device #1
python stt_client.py --url ws://34.138.105.85:8080 --device 1
```

### Pipe JSON Output to File
```bash
python stt_client.py --url ws://34.138.105.85:8080 --json > transcriptions.jsonl
```

### Process JSON Output with jq
```bash
python stt_client.py --url ws://34.138.105.85:8080 --json | jq -r '.text'
```

## Integration Examples

### Python Integration

```python
import subprocess
import json

# Start client as subprocess
process = subprocess.Popen(
    ["python", "stt_client.py", "--url", "ws://34.138.105.85:8080", "--json"],
    stdout=subprocess.PIPE,
    text=True
)

# Process real-time transcriptions
for line in process.stdout:
    data = json.loads(line)
    print(f"[{data['timestamp']}] {data['text']}")
    
    # Your application logic here
    if "reservation" in data['text'].lower():
        print("→ Detected reservation intent!")
```

### Node.js Integration

```javascript
const { spawn } = require('child_process');

const client = spawn('python', [
  'stt_client.py',
  '--url', 'ws://34.138.105.85:8080',
  '--json'
]);

client.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  lines.forEach(line => {
    if (line.trim()) {
      const transcription = JSON.parse(line);
      console.log(`[${transcription.timestamp}] ${transcription.text}`);
      // Your application logic here
    }
  });
});
```

## Troubleshooting

### Connection Refused
```
Error: Connection refused
```
**Solution:** Check that the server is running and firewall rules are configured.

### No Audio Input
```
Error: No audio input device found
```
**Solution:** 
1. Check microphone permissions in System Preferences (macOS)
2. List devices with `--list-devices`
3. Specify device with `--device N`

### Poor Transcription Quality
**Solutions:**
- Speak clearly and avoid background noise
- Check microphone quality and placement
- Use `--show-vad` to see if speech is being detected
- Increase microphone volume in system settings

### High Latency
**Solutions:**
- Check network connection to GCP server
- Ensure server has adequate GPU resources
- Monitor server logs for processing bottlenecks

## Technical Details

- **Sample Rate:** 24kHz
- **Channels:** Mono (1 channel)
- **Chunk Size:** 1920 samples (80ms blocks)
- **Protocol:** WebSocket with MessagePack encoding
- **Authentication:** Via `kyutai-api-key` header or `?auth_id=` query parameter

## Future Enhancements

- [ ] Real confidence scores from server
- [ ] Speaker diarization (multiple speakers)
- [ ] Partial/streaming results (word-by-word)
- [ ] Audio quality metrics
- [ ] Automatic reconnection on disconnect
- [ ] Buffering for network interruptions

