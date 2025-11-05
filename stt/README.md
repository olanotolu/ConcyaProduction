# Concya Speech-to-Text System

Production-ready Speech-to-Text system for Concya restaurant voice agent.

## Components

### 1. Client (`client/`)
Python WebSocket client for real-time STT from microphone to cloud server.

**Features:**
- Real-time audio streaming
- JSON output with timestamps
- Latency monitoring
- Voice Activity Detection

**Quick Start:**
```bash
cd client
pip install -r requirements.txt
python stt_client.py --url ws://34.26.22.244:8080
```

See [client/README.md](client/README.md) for complete documentation.

### 2. Server (`server/`)
Configuration files for the GCP-deployed Rust STT server.

**Contains:**
- `configs/` - Moshi server configuration files
- `deployment/` - Deployment instructions

**Current Deployment:**
- **URL:** ws://34.138.105.85:8080
- **GPU:** NVIDIA L4 with CUDA
- **Model:** Kyutai STT-1B (English/French)
- **Latency:** ~180ms average

### 3. Source Code (`stt-rs/`)
Rust source code for building the STT server binary.

**Note:** This is for reference/rebuilding only. The actual production server runs on GCP.

**Build:**
```bash
cd stt-rs
cargo build --release --features cuda
```

## Architecture

```
┌─────────────┐         WebSocket          ┌─────────────┐
│  Your Mac   │ ───────────────────────────> │  GCP Server │
│  (Client)   │  Audio Chunks (80ms)        │  (STT-RS)   │
│             │                              │             │
│ stt_client  │ <─────────────────────────── │ moshi-      │
│   .py       │  JSON Transcriptions        │  server     │
└─────────────┘                              └─────────────┘
                                                    │
                                                    ▼
                                             ┌─────────────┐
                                             │  NVIDIA L4  │
                                             │  GPU/CUDA   │
                                             └─────────────┘
```

## Performance

- **Latency:** ~180ms average (excellent)
- **Chunk Size:** 80ms audio blocks
- **Sample Rate:** 24kHz
- **Channels:** Mono
- **Protocol:** WebSocket + MessagePack
- **Languages:** English, French

## Usage

### Standard Text Output
```bash
cd client
python stt_client.py --url ws://34.26.22.244:8080
```

### JSON Output (For Integration)
```bash
python stt_client.py --url ws://34.26.22.244:8080 --json
```

**Output:**
```json
{"timestamp": 1730940001.25, "text": "hello can you hear me", "speaker": "user", "confidence": 0.95}
```

### With Latency Monitoring
```bash
python stt_client.py --url ws://34.26.22.244:8080 --latency
```

**Output:**
```
hello⚡0 world⚡150 this⚡280 is⚡420 awesome⚡580  [⚡ 286ms]
```

## Integration Example

```python
import subprocess
import json

# Start STT client
process = subprocess.Popen(
    ["python", "client/stt_client.py", 
     "--url", "ws://34.138.105.85:8080", 
     "--json"],
    stdout=subprocess.PIPE,
    text=True
)

# Process transcriptions
for line in process.stdout:
    data = json.loads(line)
    print(f"Heard: {data['text']}")
    
    # Your restaurant logic here
    if "reservation" in data['text'].lower():
        handle_reservation(data['text'])
```

## Files

```
stt/
├── client/
│   ├── stt_client.py              # Main client
│   ├── example_json_consumer.py   # Integration example
│   ├── requirements.txt           # Dependencies
│   └── README.md                  # Client docs
├── server/
│   ├── configs/
│   │   └── config-stt-en_fr-hf.toml  # Server config
│   └── deployment/                # Deploy guides
├── stt-rs/
│   ├── Cargo.toml                 # Rust build config
│   └── src/main.rs                # Server source
└── README.md                      # This file
```

## Maintenance

### Check Server Status
```bash
# From your Mac
python client/stt_client.py --url ws://34.138.105.85:8080 --latency
```

### Update Server (on GCP)
```bash
# SSH to GCP
cd ~/delayed-streams-modeling/stt-rs
cargo update
cargo build --release --features cuda
cargo install --features cuda moshi-server
```

### Monitor Performance
```bash
# Run with latency monitoring
python client/stt_client.py --url ws://34.138.105.85:8080 --json --latency
```

## Status

✅ **Production Ready**
- Server: Running on GCP
- Client: Tested and working
- Latency: < 200ms (excellent)
- Quality: High accuracy

## Next Steps

1. Build NLU layer for intent detection
2. Add reservation-specific vocabulary
3. Integrate with restaurant database
4. Add error handling for unclear speech
5. Deploy full restaurant voice agent

---

For questions or issues, see the main [Concya README](../README.md).

