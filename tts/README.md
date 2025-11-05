# 🎵 Cartesia TTS Integration

High-quality voice synthesis for Concya restaurant responses using Cartesia Sonic-3.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   ```bash
   export CARTESIA_API_KEY="sk_car_89jTmTuqUSb2ZjCoAa96TP"
   ```

3. **Test the setup:**
   ```bash
   python cartesia_tts.py
   ```

## 🎛️ Configuration

### Voice Selection
The default voice is: `9f0b0e13-f0c3-4c0b-94d7-1b64dc1e9c29`

To see all available voices:
```python
from cartesia_tts import CartesiaTTS
tts = CartesiaTTS()
tts.list_voices()
```

### Quality Settings
- **Model:** `sonic-3` (highest quality)
- **Sample Rate:** 44.1kHz
- **Format:** WAV with 32-bit float PCM

## 🔧 Integration

The TTS is automatically integrated into the LLM bridge (`stt_llm_bridge_enhanced.py`). Every assistant response is spoken aloud using Cartesia.

### Pipeline Flow:
1. 🎤 User speaks → STT
2. 🧠 Intent parsing → LLM response
3. 🎵 Cartesia TTS → Audio playback
4. 🔊 Speaker output

## 🎚️ Customization

### Change Voice:
```python
tts = CartesiaTTS()
tts.set_voice("your-voice-id-here")
```

### Adjust Quality:
Edit `cartesia_tts.py` and modify the `output_format` parameters.

## 🔐 Security Notes

- Never commit API keys to git
- Use environment variables for sensitive data
- The API key is only used for TTS generation

## 🐛 Troubleshooting

**"API key not found"**
- Make sure `CARTESIA_API_KEY` is set
- Check the key format (should start with `sk_car_`)

**"Voice not found"**
- Use `list_voices()` to see available voices
- Update `voice_id` in the code

**"Audio doesn't play"**
- Make sure `afplay` is available (macOS built-in)
- Check system audio settings
