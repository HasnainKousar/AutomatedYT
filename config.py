# ============================================================
#  config.py — All API keys and settings in one place
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # default: Rachel

# --- YouTube OAuth ---
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# --- Video Settings ---
VIDEO_WIDTH       = 1920
VIDEO_HEIGHT      = 1080
VIDEO_FPS         = 24
CLIP_DURATION     = 5          # seconds per image clip (FFmpeg mode)
FADE_DURATION     = 0.5        # seconds for crossfade between clips (FFmpeg mode)

# --- Output Folders ---
OUTPUT_DIR        = "output"
AUDIO_DIR         = f"{OUTPUT_DIR}/audio"
IMAGES_DIR        = f"{OUTPUT_DIR}/images"   # drop Meta AI videos/images here
VIDEO_CLIPS_DIR   = f"{OUTPUT_DIR}/clips"
FINAL_VIDEO_DIR   = f"{OUTPUT_DIR}/final"

# --- ChatGPT ---
GPT_MODEL         = "gpt-4o"
VIDEO_DURATION    = 60         # target video length in seconds
NUM_IMAGE_PROMPTS = 8          # how many image prompts to generate

# --- CapCut / VectCutAPI ---
# Start VectCutAPI server first:  cd VectCutAPI && python capcut_server.py
CAPCUT_SERVER_URL = os.getenv("CAPCUT_SERVER_URL", "http://localhost:9001")
