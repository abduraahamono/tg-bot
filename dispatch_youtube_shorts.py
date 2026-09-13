#!/usr/bin/env python3
"""
dispatch_youtube_shorts.py
Checks brain_data/scheduled_youtube_shorts.json, finds due Shorts,
and uploads them to YouTube channel with automated Pinned Telegram Comment!
Can be called from cron, daemon, or with --force to publish next pending short.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from engine.youtube_publisher import YouTubePublisher

BASE_DIR = Path(__file__).resolve().parent
SCHEDULE_FILE = BASE_DIR / "brain_data" / "scheduled_youtube_shorts.json"

def dispatch(force: bool = False, dry_run: bool = False):
    if not SCHEDULE_FILE.exists():
        print("[INFO] No YouTube schedule file found.")
        return

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data.get("active"):
        print("[INFO] YouTube schedule is inactive.")
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    due_short = None

    for item in data.get("shorts", []):
        if item.get("status") == "pending":
            if force or item.get("scheduled_time") <= now_str:
                due_short = item
                break

    if not due_short:
        print("[INFO] No YouTube Shorts due for publishing right now.")
        return

    print(f"\n[YOUTUBE SHORTS DUE]")
    print(f"ID: {due_short['id']} | Time: {due_short['scheduled_time']}")
    print(f"Title: {due_short['title']}")
    print(f"Video: {due_short['video_path']}")

    if dry_run:
        print("[DRY-RUN] Test mode. Video not uploaded.")
        return

    publisher = YouTubePublisher()
    if not publisher.is_configured():
        print("[ERROR] YouTube API service not configured or unauthorized.")
        return

    full_video_path = BASE_DIR / due_short["video_path"]
    res = publisher.upload_short(
        video_path=str(full_video_path),
        title=due_short["title"],
        description=due_short["description"],
        pin_telegram_comment=True
    )

    if res.get("success"):
        due_short["status"] = "posted"
        due_short["posted_at"] = now_str
        due_short["video_id"] = res.get("video_id")
        due_short["video_url"] = res.get("video_url")
        due_short["comment_pinned"] = res.get("comment_pinned")

        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"🎉 [YOUTUBE POSTED SUCCESS] URL: {res.get('video_url')}")
    else:
        due_short["status"] = "failed"
        due_short["error"] = res.get("error")
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"❌ [YOUTUBE UPLOAD FAILED] {res.get('error')}")

if __name__ == "__main__":
    force = "--force" in sys.argv
    dry = "--dry-run" in sys.argv
    dispatch(force=force, dry_run=dry)
