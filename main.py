# ============================================================
#  main.py — Orchestrator: run everything end-to-end
# ============================================================

import os
import json
import argparse
import subprocess
import sys
from config import OUTPUT_DIR, IMAGES_DIR

os.makedirs(OUTPUT_DIR,  exist_ok=True)
os.makedirs(IMAGES_DIR,  exist_ok=True)


def run_pipeline(topic: str, skip_upload: bool = False):
    print(f"\n🚀 Starting pipeline for topic: '{topic}'\n")

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
    print("  1. Use Google Flow to generate images from the prompts")
    print("  2. Use Meta AI to animate images → download via VerseVidSaver")
    print("  3. Use the Media Uploader window to add files to the pipeline")
    print()
    print("  Opening Media Uploader...")
    print("="*60)
    subprocess.run([sys.executable, "media_uploader.py"])
    print("✅ Media uploader closed. Continuing pipeline...")

    # ── STEP 3: Assemble video ──────────────────────────────
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
        privacy="private",   # ← change to "public" when ready to go live
    )

    print(f"\n🎉 Pipeline complete!")
    print(f"   🎬 Local file : {final_video_path}")
    print(f"   ▶️  YouTube    : {video_url}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated YouTube Channel Pipeline")
    parser.add_argument("topic", help='Video topic e.g. "5 Facts About Black Holes"')
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    args = parser.parse_args()

    run_pipeline(args.topic, skip_upload=args.no_upload)
