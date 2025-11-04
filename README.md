# Concya - Restaurant Voice Agent

Production-ready Speech-to-Text system for restaurant reservations.

## Architecture

- **Client**: Python WebSocket client (runs on local machine)
- **Server**: Rust-based Moshi STT server (deployed on GCP with GPU)
- **Model**: Kyutai STT-1B (English/French support)

## Quick Start

### Standard Text Output
```bash
cd client
pip install -r requirements.txt
python stt_client.py --url ws://34.138.105.85:8080
```

### Structured JSON Output (NEW!)
```bash
python stt_client.py --url ws://34.138.105.85:8080 --json
```

**Output:**
```json
{"timestamp": 1730940001.25, "text": "hello can you hear me", "speaker": "user", "confidence": 0.95}
```

See [client/README.md](client/README.md) for complete documentation and integration examples.

### Server Deployment
See `server/deployment/deploy.md` for GCP deployment instructions.

## Features

✅ **Real-time streaming** - 80ms audio chunks for low latency
✅ **GPU-accelerated** - CUDA inference on GCP L4 GPU
✅ **Bilingual support** - English and French
✅ **WebSocket protocol** - Efficient real-time communication
✅ **Voice Activity Detection** - Automatic pause detection
✅ **JSON output** - Structured data for easy integration
✅ **Production-ready** - Deployed and tested on GCP

## Current Status

- **STT Server**: Running on GCP at 34.138.105.85:8080
- **Client**: Tested and working (v1.1.0)
- **Latency**: Real-time streaming with 80ms chunks
- **Uptime**: Active and ready for development

## Documentation

- [Client README](client/README.md) - Client usage and integration
- [Changes Log](CHANGES.md) - Recent updates and new features
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Setup Guide](docs/SETUP.md) - Deployment instructions
- [API Reference](docs/API.md) - API documentation

## Project Structure

```
Concya/
├── client/              # STT client application
│   ├── stt_client.py   # Main client script
│   ├── example_json_consumer.py  # Integration example
│   ├── requirements.txt
│   └── README.md       # Detailed client documentation
├── server/             # Server configuration
│   ├── configs/       # Moshi server configs
│   └── deployment/    # Deployment guides
├── docs/              # Documentation
├── tests/             # Test files and data
└── README.md          # This file
```

## Usage Examples

See [client/README.md](client/README.md) for detailed examples, or try:

```bash
# List available microphones
python client/stt_client.py --list-devices

# Use specific microphone with JSON output
python client/stt_client.py --url ws://34.138.105.85:8080 --device 1 --json

# Run example consumer
python client/example_json_consumer.py
```
