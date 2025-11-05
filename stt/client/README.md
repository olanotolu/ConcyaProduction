# Concya STT Client

Real-time speech-to-text client that connects to GCP STT server.

## Usage

```bash
# Standard text output
python stt_client.py --url ws://34.138.105.85:8080

# JSON structured output (for LLM integration)
python stt_client.py --url ws://34.138.105.85:8080 --json

# With latency monitoring
python stt_client.py --url ws://34.138.105.85:8080 --latency
```

## Files

- `stt_client.py` - Main client script
- `example_json_consumer.py` - Example integration
- `requirements.txt` - Python dependencies

