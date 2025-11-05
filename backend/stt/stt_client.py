# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "msgpack",
#     "numpy",
#     "sounddevice",
#     "websockets",
# ]
# ///
import argparse
import asyncio
import json
import signal
import time

import msgpack
import numpy as np
import sounddevice as sd
import websockets

SAMPLE_RATE = 24000

# The VAD has several prediction heads, each of which tries to determine whether there
# has been a pause of a given length. The lengths are 0.5, 1.0, 2.0, and 3.0 seconds.
# Lower indices predict pauses more aggressively. In Unmute, we use 2.0 seconds = index 2.
PAUSE_PREDICTION_HEAD_INDEX = 2


async def receive_messages(websocket, show_vad: bool = False, json_output: bool = False, show_latency: bool = False):
    """Receive and process messages from the WebSocket server."""
    try:
        speech_started = False
        current_utterance = []
        utterance_start_time = None
        first_word_time = None
        last_audio_sent_time = None
        word_latencies = []
        
        async for message in websocket:
            receive_time = time.time()
            data = msgpack.unpackb(message, raw=False)

            # The Step message only gets sent if the model has semantic VAD available
            if data["type"] == "Step":
                pause_prediction = data["prs"][PAUSE_PREDICTION_HEAD_INDEX]
                if pause_prediction > 0.5 and speech_started:
                    if json_output and current_utterance:
                        # Calculate average latency for this utterance
                        avg_latency = sum(word_latencies) / len(word_latencies) if word_latencies else 0
                        
                        # Output complete utterance as JSON
                        output = {
                            "timestamp": utterance_start_time,
                            "text": " ".join(current_utterance),
                            "speaker": "user",
                            "confidence": 0.95  # Default confidence (server doesn't provide this yet)
                        }
                        
                        if show_latency:
                            output["latency_ms"] = round(avg_latency * 1000, 1)
                            output["words_count"] = len(current_utterance)
                        
                        print(json.dumps(output), flush=True)
                        current_utterance = []
                        utterance_start_time = None
                        word_latencies = []
                    elif show_vad and not json_output:
                        print("| ", end="", flush=True)
                    
                    # Show latency summary for standard mode
                    if show_latency and not json_output and word_latencies:
                        avg_latency = sum(word_latencies) / len(word_latencies)
                        print(f" [⚡ {avg_latency*1000:.0f}ms]", end="", flush=True)
                        word_latencies = []
                    
                    # Reset for next utterance
                    speech_started = False
                    utterance_start_time = None

            elif data["type"] == "Word":
                # Set utterance start time on first word
                if utterance_start_time is None:
                    utterance_start_time = receive_time
                    first_word_time = receive_time
                
                # Calculate latency: time elapsed since utterance started
                word_latency = receive_time - utterance_start_time
                word_latencies.append(word_latency)
                
                if json_output:
                    current_utterance.append(data["text"])
                else:
                    if show_latency:
                        # Show word with latency in standard mode
                        print(f"{data['text']}⚡{word_latency*1000:.0f} ", end="", flush=True)
                    else:
                        print(data["text"], end=" ", flush=True)
                speech_started = True
                
        # Output any remaining utterance
        if json_output and current_utterance:
            output = {
                "timestamp": utterance_start_time,
                "text": " ".join(current_utterance),
                "speaker": "user",
                "confidence": 0.95
            }
            print(json.dumps(output), flush=True)
            
    except websockets.ConnectionClosed:
        print("Connection closed while receiving messages.")


async def send_messages(websocket, audio_queue):
    """Send audio data from microphone to WebSocket server."""
    try:
        # Start by draining the queue to avoid lags
        while not audio_queue.empty():
            await audio_queue.get()

        print("Starting the transcription")

        while True:
            audio_data = await audio_queue.get()
            chunk = {"type": "Audio", "pcm": [float(x) for x in audio_data]}
            msg = msgpack.packb(chunk, use_bin_type=True, use_single_float=True)
            await websocket.send(msg)

    except websockets.ConnectionClosed:
        print("Connection closed while sending messages.")


async def stream_audio(url: str, api_key: str, show_vad: bool, json_output: bool, show_latency: bool):
    """Stream audio data to a WebSocket server."""
    if not json_output:
        print("Starting microphone recording...")
        print("Press Ctrl+C to stop recording")
        if show_latency:
            print("⚡ Latency monitoring enabled")
    audio_queue = asyncio.Queue()

    loop = asyncio.get_event_loop()

    def audio_callback(indata, frames, time, status):
        loop.call_soon_threadsafe(
            audio_queue.put_nowait, indata[:, 0].astype(np.float32).copy()
        )

    # Start audio stream
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback,
        blocksize=1920,  # 80ms blocks
    ):
        headers = {"kyutai-api-key": api_key}
        # Instead of using the header, you can authenticate by adding `?auth_id={api_key}` to the URL
        async with websockets.connect(url, additional_headers=headers) as websocket:
            send_task = asyncio.create_task(send_messages(websocket, audio_queue))
            receive_task = asyncio.create_task(
                receive_messages(websocket, show_vad=show_vad, json_output=json_output, show_latency=show_latency)
            )
            await asyncio.gather(send_task, receive_task)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time microphone transcription")
    parser.add_argument(
        "--url",
        help="The URL of the server to which to send the audio",
        default="ws://34.26.22.244:8080/api/asr-streaming",
    )
    parser.add_argument("--api-key", default="public_token")
    parser.add_argument(
        "--list-devices", action="store_true", help="List available audio devices"
    )
    parser.add_argument(
        "--device", type=int, help="Input device ID (use --list-devices to see options)"
    )
    parser.add_argument(
        "--show-vad",
        action="store_true",
        help="Visualize the predictions of the semantic voice activity detector with a '|' symbol",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON format with timestamp, text, speaker, and confidence",
    )
    parser.add_argument(
        "--latency",
        action="store_true",
        help="Show latency metrics (processing time per word/utterance)",
    )

    args = parser.parse_args()

    def handle_sigint(signum, frame):
        print("Interrupted by user")  # Don't complain about KeyboardInterrupt
        exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    if args.list_devices:
        print("Available audio devices:")
        print(sd.query_devices())
        exit(0)

    if args.device is not None:
        sd.default.device[0] = args.device  # Set input device

    url = args.url
    asyncio.run(stream_audio(url, args.api_key, args.show_vad, args.json, args.latency))
