# 🎬 AutomatedYT — Automated YouTube Channel Pipeline

Automates script → audio → video assembly → YouTube upload.

## 📁 Project Structure
```
├── main.py               # Run this — orchestrates everything
├── script_generator.py   # ChatGPT script + image prompts
├── audio_generator.py    # ElevenLabs voiceover
├── video_assembler.py    # FFmpeg video assembly
├── youtube_uploader.py   # YouTube Data API upload
├── media_uploader.py     # GUI to upload your Meta AI videos
├── config.py             # All settings
├── .env                  # Your API keys (never commit this)
├── .env.example          # Template for .env
├── requirements.txt
└── output/
    ├── images/           # ← Drop your Meta AI videos/images here (or use media_uploader.py)
    ├── audio/
    ├── clips/
    └── final/
```

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone git@github.com:HasnainKousar/AutomatedYT.git
cd AutomatedYT
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg
- **Windows**: Download from https://ffmpeg.org → add to PATH
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 4. Set up API keys
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 5. Set up YouTube API
1. Go to https://console.cloud.google.com
2. Create a project → Enable **YouTube Data API v3**
3. Create OAuth 2.0 credentials (Desktop App)
4. Download `client_secrets.json` → place in project root

## 🚀 Usage

```bash
# Full pipeline (with YouTube upload)
python main.py "5 Shocking Facts About Black Holes"

# Skip YouTube upload (just generate video locally)
python main.py "Top 10 AI Tools 2024" --no-upload

# Open the Media Uploader GUI standalone
python media_uploader.py
```

## 🔄 Workflow

| Step | Tool | Auto? |
|------|------|-------|
| Script + prompts | ChatGPT API | ✅ Auto |
| Voiceover | ElevenLabs API | ✅ Auto |
| Image generation | Google Flow | 👋 Manual |
| Image to video | Meta AI | 👋 Manual |
| HD download | VerseVidSaver | 👋 Manual |
| Add files to pipeline | `media_uploader.py` GUI | 🖱️ 1 click |
| Video assembly | FFmpeg | ✅ Auto |
| YouTube upload | YouTube API | ✅ Auto |

## 📌 Manual Steps (~15 min per video)
1. Pipeline generates script and image prompts automatically
2. Go to **labs.google/flow** → generate images from the prompts
3. Upload images to **meta.ai** → animate them
4. Download HD versions via **VerseVidSaver**
5. Use the **Media Uploader GUI** that opens automatically to add files
6. Pipeline takes over — assembles and uploads to YouTube!

## 🔑 API Keys Needed

| Key | Where to get it |
|-----|-----------------|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `ELEVENLABS_API_KEY` | https://elevenlabs.io → Profile |
| `ELEVENLABS_VOICE_ID` | ElevenLabs → Pick a voice → copy ID from URL |
| YouTube credentials | https://console.cloud.google.com → YouTube Data API v3 → OAuth Desktop |
