# ============================================================
#  video_assembler.py — FFmpeg image+audio → final MP4
# ============================================================

import os
import subprocess
import glob
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    IMAGES_DIR, VIDEO_CLIPS_DIR, FINAL_VIDEO_DIR,
    CLIP_DURATION, FADE_DURATION,
)

os.makedirs(VIDEO_CLIPS_DIR, exist_ok=True)
os.makedirs(FINAL_VIDEO_DIR, exist_ok=True)


SUPPORTED_FORMATS = (".mp4", ".mov", ".avi", ".webm")
IMAGE_FORMATS     = (".jpg", ".jpeg", ".png", ".webp")


def get_media_files() -> list[str]:
    """
    Returns sorted list of video clips AND images from IMAGES_DIR.
    Videos are used as-is; images are converted to clips.
    """
    files = []
    for ext in SUPPORTED_FORMATS + IMAGE_FORMATS:
        files += glob.glob(os.path.join(IMAGES_DIR, f"*{ext}"))
    return sorted(files)


def image_to_clip(image_path: str, index: int, duration: float = CLIP_DURATION) -> str:
    """
    Converts a single image to a video clip with a slow Ken Burns zoom effect.
    """
    out_path = os.path.join(VIDEO_CLIPS_DIR, f"clip_{index:03d}.mp4")
    zoom_filter = (
        f"scale=8000:-1,zoompan=z='min(zoom+0.0015,1.5)':d={int(duration * VIDEO_FPS)}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={VIDEO_WIDTH}x{VIDEO_HEIGHT}"
        f",fps={VIDEO_FPS}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", zoom_filter,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


def prepare_clips(audio_duration: float) -> list[str]:
    """
    Converts all images/clips to equal-duration clips that together
    match (or slightly exceed) the audio duration.
    """
    media_files = get_media_files()
    if not media_files:
        raise FileNotFoundError(
            f"No media found in {IMAGES_DIR}. "
            "Drop your Meta AI videos or images there first."
        )

    clip_duration = audio_duration / len(media_files)
    clip_paths = []

    for i, path in enumerate(media_files):
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_FORMATS:
            print(f"  🖼️  Converting image {i+1}/{len(media_files)}: {os.path.basename(path)}")
            clip_paths.append(image_to_clip(path, i, clip_duration))
        else:
            # Already a video clip — re-encode to standard size/fps
            out_path = os.path.join(VIDEO_CLIPS_DIR, f"clip_{i:03d}.mp4")
            cmd = [
                "ffmpeg", "-y", "-i", path,
                "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
                       f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                "-t", str(clip_duration),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                out_path,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            clip_paths.append(out_path)
            print(f"  🎬 Processed clip  {i+1}/{len(media_files)}: {os.path.basename(path)}")

    return clip_paths


def build_concat_list(clip_paths: list[str]) -> str:
    """Writes an FFmpeg concat list file and returns its path."""
    list_path = os.path.join(VIDEO_CLIPS_DIR, "concat_list.txt")
    with open(list_path, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    return list_path


def assemble_video(audio_path: str, title: str = "final_video") -> str:
    """
    Main function: takes all media from IMAGES_DIR + voiceover audio
    and produces a finished MP4 with captions-ready audio.
    Returns path to the final video.
    """
    from audio_generator import get_audio_duration

    print("\n🎬 Assembling video...")
    audio_duration = get_audio_duration(audio_path)
    print(f"   Audio duration: {audio_duration:.1f}s")

    clip_paths = prepare_clips(audio_duration)
    concat_list = build_concat_list(clip_paths)

    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:50]
    final_path = os.path.join(FINAL_VIDEO_DIR, f"{safe_title}.mp4")

    # Step 1 — Concatenate all clips
    raw_video = os.path.join(VIDEO_CLIPS_DIR, "raw_concat.mp4")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        raw_video,
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 2 — Merge audio + video, trim to audio length
    cmd_merge = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_path,
    ]
    subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"✅ Final video saved → {final_path}")
    return final_path
