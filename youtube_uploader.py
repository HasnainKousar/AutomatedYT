# ============================================================
#  youtube_uploader.py — Upload to YouTube via Data API v3
# ============================================================

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_SCOPES

TOKEN_PICKLE = "youtube_token.pickle"


def get_youtube_client():
    """Handles OAuth2 — opens browser on first run, uses cached token after."""
    creds = None

    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PICKLE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "22",        # 22 = People & Blogs | 27 = Education
    privacy: str = "private",       # "private" | "unlisted" | "public"
    thumbnail_path: str = None,
) -> str:
    """
    Uploads video to YouTube and returns the video URL.
    Video is uploaded as 'private' by default — change to 'public' when ready.
    """
    youtube = get_youtube_client()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:15],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")

    print(f"\n📤 Uploading to YouTube: '{title}'")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"   Upload progress: {pct}%", end="\r")

    video_id  = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\n✅ Uploaded! → {video_url}")

    # Optional: set custom thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path),
        ).execute()
        print("🖼️  Thumbnail set.")

    return video_url
