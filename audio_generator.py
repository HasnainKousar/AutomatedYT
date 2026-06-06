# ============================================================
#  audio_generator.py — ElevenLabs text-to-speech
# ============================================================

import os
import requests
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, AUDIO_DIR

os.makedirs(AUDIO_DIR, exist_ok=True)

ELEVENLABS_URL = (
    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
)

HEADERS = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY,
}


def generate_audio(script: str, filename: str = "voiceover.mp3") -> str:
    """
    Sends the script to ElevenLabs and saves the MP3.
    Returns the full path to the saved audio file.
    """
    payload = {
        "text": script,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,
            "use_speaker_boost": True,
        },
    }

    print("🎙️  Generating audio with ElevenLabs...")
    response = requests.post(ELEVENLABS_URL, json=payload, headers=HEADERS)
    response.raise_for_status()

    output_path = os.path.join(AUDIO_DIR, filename)
    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"✅ Audio saved → {output_path}")
    return output_path


def get_audio_duration(audio_path: str) -> float:
    """
    Returns duration of audio file in seconds using mutagen (no FFmpeg needed).
    """
    from mutagen.mp3 import MP3
    audio = MP3(audio_path)
    return audio.info.length
