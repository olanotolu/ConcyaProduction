#!/usr/bin/env python3
"""
Cartesia TTS Module for Concya
High-quality voice synthesis for restaurant responses
"""

import os
from typing import Optional
from cartesia import Cartesia


class CartesiaTTS:
    """Cartesia Text-to-Speech client for Concya"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Cartesia TTS client"""
        self.api_key = api_key or os.getenv("CARTESIA_API_KEY")
        if not self.api_key:
            raise ValueError("CARTESIA_API_KEY environment variable is required")

        self.client = Cartesia(api_key=self.api_key)

        # Default voice - you can change this
        self.voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091"  # More common Cartesia voice
        self.model_id = "sonic-english"  # Try sonic-english first

    def list_voices(self):
        """List available voices"""
        try:
            voices = self.client.voices.list()
            print("Available Cartesia Voices:")
            print("=" * 50)
            for voice in voices:
                # Handle both dict and object responses
                if hasattr(voice, 'id'):
                    voice_id = voice.id
                    voice_name = getattr(voice, 'name', 'Unknown')
                    voice_lang = getattr(voice, 'language', 'Unknown')
                else:
                    voice_id = voice.get('id', 'Unknown')
                    voice_name = voice.get('name', 'Unknown')
                    voice_lang = voice.get('language', 'Unknown')

                print(f"ID: {voice_id}")
                print(f"Name: {voice_name}")
                print(f"Language: {voice_lang}")
                print("-" * 30)
            return voices
        except Exception as e:
            print(f"Error listing voices: {e}")
            return []

    def set_voice(self, voice_id: str):
        """Set the voice to use"""
        self.voice_id = voice_id

    def speak(self, text: str, play_immediately: bool = True) -> str:
        """
        Generate and optionally play TTS audio

        Args:
            text: Text to convert to speech
            play_immediately: Whether to play the audio immediately

        Returns:
            Path to generated audio file
        """
        try:
            # Generate audio chunks
            chunks = self.client.tts.bytes(
                model_id=self.model_id,
                transcript=text,
                voice={"mode": "id", "id": self.voice_id},
                output_format={
                    "container": "wav",
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100
                },
                language="en"
            )

            # Write to file
            audio_file = "/tmp/concya_response.wav"
            with open(audio_file, "wb") as f:
                for chunk in chunks:
                    f.write(chunk)

            if play_immediately:
                self._play_audio(audio_file)

            return audio_file

        except Exception as e:
            print(f"[TTS Error] {e}")
            return None

    def _play_audio(self, audio_file: str):
        """Play audio file (macOS specific)"""
        try:
            os.system(f"afplay {audio_file} &>/dev/null")
        except Exception as e:
            print(f"[Audio Playback Error] {e}")


def test_cartesia():
    """Test function to verify Cartesia setup"""
    try:
        print("🔑 Testing Cartesia API key...")
        tts = CartesiaTTS()
        print("✅ Cartesia TTS initialized successfully!")

        # Test with sample text
        print("🎵 Testing TTS with sample text...")
        result = tts.speak("Hello! Welcome to Concya restaurant. How can I help you today?", play_immediately=False)

        if result:
            print(f"✅ Audio generated: {result}")
            print("🎧 Audio file created (playback disabled for testing)")
        else:
            print("❌ Audio generation failed")

        print("✅ TTS test completed!")

    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        print("💡 Make sure CARTESIA_API_KEY is set correctly")
        print("💡 Try: export CARTESIA_API_KEY='your_key_here'")


if __name__ == "__main__":
    test_cartesia()
