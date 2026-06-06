# ============================================================
#  upload_only.py — Upload an already-exported video to YouTube
#
#  Use this after exporting from CapCut:
#    python upload_only.py path/to/exported_video.mp4
# ============================================================

import os
import json
import argparse
from config import OUTPUT_DIR


def upload_exported_video(video_path: str, privacy: str = "private"):
    """Uploads a manually-exported video using saved metadata from main.py."""

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Load metadata saved by main.py
    package_path = os.path.join(OUTPUT_DIR, "video_package.json")
    if not os.path.exists(package_path):
        raise FileNotFoundError(
            f"No metadata found at {package_path}.\n"
            "Run main.py first to generate the script and metadata."
        )

    with open(package_path) as f:
        data = json.load(f)

    print(f"\n📤 Uploading: {video_path}")
    print(f"   Title      : {data['title']}")
    print(f"   Privacy    : {privacy}")

    from youtube_uploader import upload_video
    video_url = upload_video(
        video_path=video_path,
        title=data["title"],
        description=data["description"],
        tags=data["tags"],
        privacy=privacy,
    )

    print(f"\n🎉 Upload complete! → {video_url}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload an exported CapCut video to YouTube"
    )
    parser.add_argument("video_path", help="Path to the exported MP4 file")
    parser.add_argument(
        "--privacy",
        choices=["private", "unlisted", "public"],
        default="private",
        help="YouTube privacy setting (default: private)",
    )
    args = parser.parse_args()
    upload_exported_video(args.video_path, privacy=args.privacy)
