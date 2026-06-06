# ============================================================
#  main.py — Orchestrator: run everything end-to-end
#
#  Usage:
#    python main.py "Topic"                   # FFmpeg assembly (default)
#    python main.py "Topic" --editor capcut   # CapCut draft via VectCutAPI
#    python main.py "Topic" --no-upload       # Skip YouTube upload
# ============================================================

import os
import json
import argparse
import subprocess
import sys
from config import OUTPUT_DIR, IMAGES_DIR

os.makedirs(OUTPUT_DIR,  exist_ok=True)
os.makedirs(IMAGES_DIR,  exist_ok=True)


def run_pipeline(topic: str, skip_upload: bool = False, editor: str = "ffmpeg"):
    print(f"\n🚀 Starting pipeline for topic: '{topic}'")
    print(f"   Editor: {editor.upper()}\n")

    # ── STEP 1: Generate script + prompts ──────────────────
    from script_generator import generate_script_and_prompts, print_package
    print("📝 Step 1/4 — Generating script with ChatGPT...")
    data = generate_script_and_prompts(topic)
    print_package(data)

    # Save package to disk for reference
    package_path = os.path.join(OUTPUT_DIR, "video_package.json")
    with open(package_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Package saved → {package_path}")

    # ── STEP 2: Generate audio ──────────────────────────────
    from audio_generator import generate_audio
    print("\n🎙️  Step 2/4 — Generating voiceover with ElevenLabs...")
    audio_path = generate_audio(data["script"])

    # ── PAUSE: Open Media Uploader GUI ─────────────────────
    print("\n" + "="*60)
    print("⏸️  MANUAL STEPS REQUIRED (see image_prompts above):")
    print()
    print("  1. Use Google Flow  →  generate images from the prompts above")
    print("  2. Use Meta AI      →  animate images into short video clips")
    print("  3. Use VerseVidSaver→  download HD versions without watermark")
    print("  4. Use the Media Uploader window to load files into the pipeline")
    print()
    print("  Opening Media Uploader...")
    print("="*60)
    subprocess.run([sys.executable, "media_uploader.py"])
    print("✅ Media uploader closed. Continuing pipeline...")

    # ── STEP 3: Assemble video ──────────────────────────────
    if editor == "capcut":
        # ── CapCut mode: create a draft in CapCut via VectCutAPI ──
        from capcut_api import build_capcut_video
        print("\n🎬 Step 3/4 — Building CapCut draft via VectCutAPI...")
        print("   (Make sure VectCutAPI server is running: python capcut_server.py)")
        draft_url = build_capcut_video(audio_path, title=data["title"])
        print(f"\n🎉 CapCut draft ready!")
        print(f"   Draft : {draft_url}")
        print("   → Open CapCut/Jianying, review the draft, export as MP4.")
        print("   → Then run:  python upload_only.py  to upload to YouTube.")
        _save_metadata_for_upload(data)
        return
    else:
        # ── FFmpeg mode: fully automated assembly ──────────────
        from video_assembler import assemble_video
        print("\n🎬 Step 3/4 — Assembling video with FFmpeg...")
        final_video_path = assemble_video(audio_path, title=data["title"])

    if skip_upload:
        print(f"\n🎉 Done! Video ready at: {final_video_path}")
        print("   (Upload skipped — run without --no-upload to enable)")
        return

    # ── STEP 4: Upload to YouTube ───────────────────────────
    from youtube_uploader import upload_video
    print("\n📤 Step 4/4 — Uploading to YouTube...")
    video_url = upload_video(
        video_path=final_video_path,
        title=data["title"],
        description=data["description"],
        tags=data["tags"],
        privacy="private",   # ← change to "public" when ready
    )

    print(f"\n🎉 Pipeline complete!")
    print(f"   🎬 Local file : {final_video_path}")
    print(f"   ▶️  YouTube    : {video_url}\n")


def _save_metadata_for_upload(data: dict):
    """Saves title/description/tags so upload_only.py can use them later."""
    path = os.path.join(OUTPUT_DIR, "video_package.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"   Metadata saved → {path}  (used by upload_only.py)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automated YouTube Channel Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "5 Facts About Black Holes"
  python main.py "5 Facts About Black Holes" --editor capcut
  python main.py "Top 10 AI Tools" --no-upload
"""
    )
    parser.add_argument("topic",       help='Video topic e.g. "5 Facts About Black Holes"')
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument(
        "--editor",
        choices=["ffmpeg", "capcut"],
        default="ffmpeg",
        help="Video editor: 'ffmpeg' (default, fully automated) or 'capcut' (CapCut draft via VectCutAPI)",
    )
    args = parser.parse_args()

    run_pipeline(args.topic, skip_upload=args.no_upload, editor=args.editor)
