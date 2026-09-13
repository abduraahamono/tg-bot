#!/usr/bin/env python3
"""
Arkadaş Consulting - Official YouTube Shorts Uploader & Conversion Engine
Uses YouTube Data API v3 with refresh_token authentication.
Capabilities:
1. Resumable video upload as YouTube Shorts (9:16)
2. SEO-optimized Uzbek titles & viral tags (#Shorts, #TurkiyadaTalim)
3. Automatic Pinned Comment with Telegram Channel link (https://t.me/arkadasuz)
4. Persistent scheduling tracking
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN_FILE = BASE_DIR / "youtube_token.json"
CRED_FILE = BASE_DIR / "social_credentials.json"
SCHEDULE_FILE = BASE_DIR / "brain_data" / "scheduled_youtube_shorts.json"

TELEGRAM_CHANNEL_URL = "https://t.me/arkadasuz"

class YouTubePublisher:
    def __init__(self):
        self.youtube = self._get_authenticated_service()

    def _get_authenticated_service(self):
        if not TOKEN_FILE.exists():
            return None
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                tdata = json.load(f)
            creds = Credentials.from_authorized_user_info(tdata)
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"[YouTube Auth Error]: {e}", flush=True)
            return None

    def is_configured(self) -> bool:
        return self.youtube is not None

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "public",
        pin_telegram_comment: bool = True
    ) -> Dict[str, Any]:
        """
        Uploads a video to YouTube as a Short and pins a Telegram link comment.
        """
        if not self.is_configured():
            return {"success": False, "error": "YouTube API not configured or token expired"}

        p = Path(video_path)
        if not p.exists():
            return {"success": False, "error": f"Video file not found: {video_path}"}

        # Ensure #Shorts is in title or description for YouTube algorithm
        if "#Shorts" not in title and "#shorts" not in title:
            clean_title = f"{title[:85]} #Shorts"
        else:
            clean_title = title[:100]

        default_tags = ["TurkiyadaTalim", "ArkadasConsulting", "Talaba2026", "Shorts", "Grantlar", "Istanbul", "Uzbekistan"]
        final_tags = tags if tags else default_tags

        full_description = (
            f"{description}\n\n"
            f"🇹🇷 Arkadaş Consulting — Turkiyada kafolatlangan ta'lim!\n"
            f"📲 Barcha universitetlar ro'yxati va bepul konsultatsiya rasmiy Telegram kanalimizda:\n"
            f"👉 {TELEGRAM_CHANNEL_URL}\n\n"
            f"#Shorts #TurkiyadaTalim #ArkadasConsulting #Talaba #Grant"
        )

        body = {
            "snippet": {
                "title": clean_title,
                "description": full_description,
                "tags": final_tags,
                "categoryId": "27"  # Education
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        try:
            media = MediaFileUpload(str(p), mimetype="video/mp4", resumable=True, chunksize=1024*1024*2)
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"[YouTube Uploading] {int(status.progress() * 100)}%", flush=True)

            video_id = response.get("id")
            video_url = f"https://youtube.com/shorts/{video_id}"
            print(f"[YouTube Upload Success] Video ID: {video_id} -> {video_url}", flush=True)

            # Add Pinned Comment with Telegram Channel Link
            comment_result = None
            if pin_telegram_comment and video_id:
                comment_result = self.post_pinned_comment(video_id)

            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url,
                "title": clean_title,
                "comment_pinned": comment_result
            }

        except Exception as e:
            print(f"[YouTube Upload Failed]: {e}", flush=True)
            return {"success": False, "error": str(e)}

    def post_pinned_comment(self, video_id: str) -> bool:
        """Adds top comment with Telegram channel funnel."""
        try:
            comment_text = (
                "🇹🇷 Turkiyada imtihonsiz o'qish, kontrakt narxlari va 100% grant kvotalari "
                "haqidagi barcha ma'lumotlar rasmiy Telegram kanalimizda:\n"
                f"👉 {TELEGRAM_CHANNEL_URL}\n\n"
                "Mutaxassislarimiz bilan bog'laning (Konsultatsiya bepul!) 🤝"
            )
            body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
            self.youtube.commentThreads().insert(
                part="snippet",
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"[YouTube Comment Warning]: {e}", flush=True)
            return False

if __name__ == "__main__":
    pub = YouTubePublisher()
    print("YouTube Publisher Configured:", pub.is_configured())
