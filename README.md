# Concya - Restaurant Voice Agent

Production-ready Speech-to-Text system for restaurant reservations.

## Architecture

- **Client**: Python WebSocket client (runs on local machine)
- **Server**: Rust-based Moshi STT server (deployed on GCP with GPU)
- **Model**: Kyutai STT-1B (English/French support)

## Quick Start

### Client Setup
```bash
cd client
pip install -r requirements.txt
python stt_client.py --url ws://YOUR_GCP_IP:8080
```

### Server Deployment
See `server/deployment/deploy.md` for GCP deployment instructions.

## Current Status

✅ STT Server: Running on GCP at 34.138.105.85:8080
✅ Client: Tested and working
✅ Latency: Real-time streaming with 80ms chunks

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [API Reference](docs/API.md)
