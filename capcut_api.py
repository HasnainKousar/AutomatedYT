# ============================================================
#  capcut_api.py — CapCut/Jianying automation via VectCutAPI
#
#  Requires: VectCutAPI server running on localhost:9001
#  Install:  git clone https://github.com/sun-guannan/VectCutAPI.git
#            cd VectCutAPI && pip install -r requirements.txt
#  Start:    python capcut_server.py
# ============================================================

import os
import glob
import requests
from pathlib import Path
from config import (
    IMAGES_DIR, FINAL_VIDEO_DIR,
    VIDEO_WIDTH, VIDEO_HEIGHT,
    CAPCUT_SERVER_URL,
)

SUPPORTED_VIDEO = (".mp4", ".mov", ".avi", ".webm", ".mkv")
SUPPORTED_IMAGE = (".jpg", ".jpeg", ".png", ".webp")


# ── Helpers ──────────────────────────────────────────────────

def _local_url(path: str) -> str:
    """Convert a local file path to a file:// URL for VectCutAPI."""
    return Path(os.path.abspath(path)).as_uri()


def _get_media_files() -> list[str]:
    """Returns sorted list of all video/image files in IMAGES_DIR."""
    files = []
    for ext in SUPPORTED_VIDEO + SUPPORTED_IMAGE:
        files += glob.glob(os.path.join(IMAGES_DIR, f"*{ext}"))
    return sorted(files)


# ── Server health check ──────────────────────────────────────

def check_server(server_url: str = CAPCUT_SERVER_URL) -> bool:
    """
    Returns True if VectCutAPI server is reachable.
    Run `python capcut_server.py` in the VectCutAPI folder first.
    """
    try:
        r = requests.get(f"{server_url}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


# ── Draft management ─────────────────────────────────────────

def create_draft(
    title: str = "AutomatedYT Draft",
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT,
    server_url: str = CAPCUT_SERVER_URL,
) -> str:
    """
    Creates a new CapCut/Jianying draft.
    Returns the draft_id string.
    """
    res = requests.post(f"{server_url}/create_draft", json={
        "title": title,
        "width": width,
        "height": height,
    })
    res.raise_for_status()
    data = res.json()
    draft_id = (
        data.get("draft_id")
        or data.get("result", {}).get("draft_id")
    )
    if not draft_id:
        raise ValueError(f"No draft_id returned by server: {data}")
    print(f"  ✅ Draft created → ID: {draft_id}")
    return draft_id


def save_draft(
    draft_id: str,
    server_url: str = CAPCUT_SERVER_URL,
) -> str:
    """
    Saves the completed draft.
    Returns the draft URL or a confirmation string.
    """
    res = requests.post(f"{server_url}/save_draft", json={"draft_id": draft_id})
    res.raise_for_status()
    data = res.json()
    return (
        data.get("draft_url")
        or data.get("result", {}).get("draft_url")
        or "Draft saved — open CapCut/Jianying to review."
    )


# ── Media tracks ─────────────────────────────────────────────

def add_media_tracks(
    draft_id: str,
    audio_duration: float,
    server_url: str = CAPCUT_SERVER_URL,
) -> None:
    """
    Adds all videos/images from output/images/ to the draft.
    Clips are evenly distributed across the full audio duration.
    Original clip audio is muted (ElevenLabs voiceover is used instead).
    """
    files = _get_media_files()
    if not files:
        raise FileNotFoundError(
            f"No media found in {IMAGES_DIR}.\n"
            "Use the Media Uploader to add your files first."
        )

    clip_duration = audio_duration / len(files)
    current_time  = 0.0

    print(f"  📂 Adding {len(files)} media file(s) "
          f"({clip_duration:.1f}s each, total {audio_duration:.1f}s)...")

    for i, path in enumerate(files):
        ext      = os.path.splitext(path)[1].lower()
        file_url = _local_url(path)
        start    = round(current_time, 3)
        end      = round(current_time + clip_duration, 3)

        if ext in SUPPORTED_VIDEO:
            print(f"    🎬 [{i+1}/{len(files)}] Video: {os.path.basename(path)}")
            res = requests.post(f"{server_url}/add_video", json={
                "draft_id":  draft_id,
                "video_url": file_url,
                "start":     start,
                "end":       end,
                "volume":    0.0,          # mute — ElevenLabs audio handles narration
                "transition": "dissolve" if i > 0 else "fade_in",
            })
        else:
            print(f"    🖼️  [{i+1}/{len(files)}] Image: {os.path.basename(path)}")
            res = requests.post(f"{server_url}/add_image", json={
                "draft_id":  draft_id,
                "image_url": file_url,
                "start":     start,
                "end":       end,
            })

        try:
            res.raise_for_status()
        except Exception as e:
            print(f"    ⚠️  Warning ({os.path.basename(path)}): {e}")

        current_time += clip_duration


def add_voiceover(
    draft_id: str,
    audio_path: str,
    server_url: str = CAPCUT_SERVER_URL,
) -> None:
    """
    Adds the ElevenLabs voiceover MP3 to the draft audio track.
    """
    from audio_generator import get_audio_duration

    audio_url = _local_url(audio_path)
    duration  = get_audio_duration(audio_path)

    print(f"  🎙️  Adding voiceover ({duration:.1f}s): {os.path.basename(audio_path)}")
    res = requests.post(f"{server_url}/add_audio", json={
        "draft_id":  draft_id,
        "audio_url": audio_url,
        "start":     0,
        "end":       duration,
        "volume":    1.0,
    })
    try:
        res.raise_for_status()
    except Exception as e:
        print(f"  ⚠️  Warning on voiceover: {e}")


def add_title_text(
    draft_id: str,
    title: str,
    server_url: str = CAPCUT_SERVER_URL,
) -> None:
    """
    Adds an animated title text overlay at the start of the video.
    """
    print(f"  📝 Adding title text: '{title[:40]}...' ")
    res = requests.post(f"{server_url}/add_text", json={
        "draft_id":         draft_id,
        "text":             title,
        "start":            0.5,
        "end":              4.5,
        "font":             "Source Han Sans",
        "font_color":       "#FFFFFF",
        "font_size":        52,
        "shadow_enabled":   True,
        "background_color": "#00000088",
    })
    try:
        res.raise_for_status()
    except Exception as e:
        print(f"  ⚠️  Warning on title text: {e}")


def add_end_card_text(
    draft_id: str,
    audio_duration: float,
    cta: str = "Like & Subscribe for more!",
    server_url: str = CAPCUT_SERVER_URL,
) -> None:
    """
    Adds a call-to-action text overlay at the end of the video.
    """
    start = max(0.0, audio_duration - 5.0)
    end   = audio_duration

    print(f"  📣 Adding end-card CTA text...")
    res = requests.post(f"{server_url}/add_text", json={
        "draft_id":         draft_id,
        "text":             cta,
        "start":            start,
        "end":              end,
        "font":             "Source Han Sans",
        "font_color":       "#FFD700",
        "font_size":        44,
        "shadow_enabled":   True,
        "background_color": "#00000099",
    })
    try:
        res.raise_for_status()
    except Exception as e:
        print(f"  ⚠️  Warning on CTA text: {e}")


# ── Main orchestration ───────────────────────────────────────

def build_capcut_video(
    audio_path: str,
    title: str = "AutomatedYT Video",
    server_url: str = CAPCUT_SERVER_URL,
) -> str:
    """
    Full CapCut assembly pipeline:
      1. Checks VectCutAPI server is running
      2. Creates a new draft
      3. Adds all media from output/images/
      4. Adds ElevenLabs voiceover
      5. Adds animated title text
      6. Adds end-card CTA
      7. Saves the draft

    Returns the draft URL/path.
    Open CapCut/Jianying to preview, make final tweaks, and export.
    """
    from audio_generator import get_audio_duration

    # ── Pre-flight: server check ──────────────────────────
    print("\n🎬 Building CapCut draft via VectCutAPI...")
    if not check_server(server_url):
        raise ConnectionError(
            f"\n❌ VectCutAPI server not reachable at {server_url}\n"
            "   Start it first:\n"
            "   cd VectCutAPI && python capcut_server.py\n"
            "   Repo: https://github.com/sun-guannan/VectCutAPI"
        )
    print(f"  ✅ VectCutAPI server online at {server_url}")

    audio_duration = get_audio_duration(audio_path)
    print(f"  🎵 Audio duration: {audio_duration:.1f}s")

    # ── Step 1: Create draft ──────────────────────────────
    draft_id = create_draft(title=title, server_url=server_url)

    # ── Step 2: Add media (videos/images) ─────────────────
    add_media_tracks(draft_id, audio_duration, server_url)

    # ── Step 3: Add voiceover ─────────────────────────────
    add_voiceover(draft_id, audio_path, server_url)

    # ── Step 4: Add title overlay ─────────────────────────
    add_title_text(draft_id, title, server_url)

    # ── Step 5: Add end-card CTA ──────────────────────────
    add_end_card_text(draft_id, audio_duration, server_url=server_url)

    # ── Step 6: Save ──────────────────────────────────────
    draft_url = save_draft(draft_id, server_url)

    print(f"\n✅ CapCut draft saved → {draft_url}")
    print("   Open CapCut or Jianying to review, add effects, and export.")
    return draft_url
