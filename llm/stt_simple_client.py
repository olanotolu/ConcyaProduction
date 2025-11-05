#!/usr/bin/env python3
"""
Simple STT Client - Just Speech to Text
No LLM, No TTS - Just clean transcription
"""

import subprocess
import signal
import sys
import os

def main():
    print("🎤 Simple STT Client")
    print("=" * 40)
    print("Just speech-to-text transcription")
    print("Press Ctrl+C to stop")
    print()

    # Path to STT client
    stt_client_path = os.path.join(os.path.dirname(__file__), "..", "stt", "client", "stt_client.py")
    
    # Default server URL
    server_url = "ws://34.26.22.244:8080/api/asr-streaming"
    
    # Allow custom URL from command line
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    print(f"Connecting to: {server_url}")
    print("-" * 40)

    # Start STT client subprocess
    stt_process = subprocess.Popen(
        ["python", stt_client_path, "--url", server_url, "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def handle_sigint(signum, frame):
        print("\n\nStopping STT client...")
        stt_process.terminate()
        exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        # Read and display transcription
        for line in stt_process.stdout:
            line = line.strip()
            if line:
                # Parse JSON if it's valid, otherwise show raw
                try:
                    import json
                    data = json.loads(line)
                    text = data.get('text', '').strip()
                    if text:
                        print(f"🎤 {text}")
                except json.JSONDecodeError:
                    # Show raw output if not JSON
                    if "Starting the transcription" not in line:
                        print(f"📝 {line}")

        # Check for errors
        stderr_output = stt_process.stderr.read()
        if stderr_output:
            print(f"⚠️  STT Error: {stderr_output}")

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        stt_process.terminate()

if __name__ == "__main__":
    main()
