#!/usr/bin/env python3
"""
Example consumer for Concya STT JSON output.
Demonstrates how to process real-time transcriptions.
"""

import json
import subprocess
import sys
from datetime import datetime


def process_transcription(data):
    """Process a single transcription event."""
    timestamp = datetime.fromtimestamp(data['timestamp']).strftime('%H:%M:%S')
    text = data['text']
    confidence = data['confidence']
    
    print(f"[{timestamp}] {text} (confidence: {confidence:.2f})")
    
    # Example: Detect reservation intent
    if any(word in text.lower() for word in ['book', 'reserve', 'reservation', 'table']):
        print("  → 🍽️  RESERVATION INTENT DETECTED")
    
    # Example: Detect party size
    if any(word in text.lower() for word in ['people', 'person', 'party']):
        print("  → 👥 PARTY SIZE MENTIONED")
    
    # Example: Detect time
    if any(word in text.lower() for word in ['pm', 'am', "o'clock", 'tonight', 'tomorrow']):
        print("  → 🕐 TIME MENTIONED")


def main():
    """Run the STT client and process JSON output."""
    server_url = sys.argv[1] if len(sys.argv) > 1 else "ws://34.26.22.244:8080/api/asr-streaming"
    
    print(f"Starting Concya STT client connected to {server_url}")
    print("Speak into your microphone. Press Ctrl+C to stop.\n")
    
    # Start the STT client as a subprocess
    process = subprocess.Popen(
        ["python", "stt_client.py", "--url", server_url, "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    try:
        # Process each line of JSON output
        for line in process.stdout:
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    data = json.loads(line)
                    process_transcription(data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}", file=sys.stderr)
                    
    except KeyboardInterrupt:
        print("\n\nStopping...")
        process.terminate()
        process.wait()


if __name__ == "__main__":
    main()

