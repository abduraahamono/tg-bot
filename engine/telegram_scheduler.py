"""
Telegram Scheduler Engine:
Manages weekly scheduled posts for Telegram Channel (@arkadasuz),
persistent storage in brain_data/scheduled_telegram_posts.json,
and automatic background publishing at scheduled hours (e.g. 13:00 and 19:30).
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_FILE = BASE_DIR / "brain_data" / "scheduled_telegram_posts.json"


class TelegramScheduler:
    def __init__(self):
        self.schedule_file = SCHEDULE_FILE
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "active": False,
            "created_at": None,
            "week_id": None,
            "posts": []
        }

    def _save(self):
        try:
            with open(self.schedule_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TelegramScheduler] Error saving schedule: {e}")

    def save_weekly_plan(self, week_plan: dict):
        self.data = {
            "active": True,
            "created_at": datetime.now().isoformat(),
            "week_id": week_plan.get("week_id", f"tg_w_{int(time.time())}"),
            "start_date": week_plan.get("start_date"),
            "end_date": week_plan.get("end_date"),
            "posts": week_plan.get("posts", [])
        }
        self._save()

    def cancel_plan(self):
        self.data["active"] = False
        for p in self.data.get("posts", []):
            if p.get("status") == "pending":
                p["status"] = "cancelled"
        self._save()

    def is_active(self) -> bool:
        return bool(self.data.get("active", False))

    def get_all_posts(self) -> List[dict]:
        return self.data.get("posts", [])

    def get_pending_posts(self) -> List[dict]:
        return [p for p in self.data.get("posts", []) if p.get("status") == "pending"]

    def get_summary(self) -> dict:
        posts = self.data.get("posts", [])
        total = len(posts)
        posted = len([p for p in posts if p.get("status") == "posted"])
        pending = len([p for p in posts if p.get("status") == "pending"])
        return {
            "active": self.data.get("active", False),
            "total": total,
            "posted": posted,
            "pending": pending,
            "start_date": self.data.get("start_date", "—"),
            "end_date": self.data.get("end_date", "—")
        }

    def check_and_publish_due(self, tg_client, channel_id: str, notify_cb: Optional[Callable[[str], Any]] = None):
        """
        Scans pending posts. If datetime.now() >= scheduled_time, publishes directly to Telegram channel!
        """
        if not self.data.get("active", False):
            return

        now = datetime.now()
        updated = False

        for post in self.data.get("posts", []):
            if post.get("status") != "pending":
                continue

            scheduled_iso = post.get("scheduled_time")
            if not scheduled_iso:
                continue

            try:
                dt = datetime.fromisoformat(scheduled_iso)
            except Exception:
                continue

            if now >= dt:
                content = post.get("content", "")
                if not content:
                    continue

                print(f"[TelegramScheduler] Publishing due post {post.get('id')} to {channel_id}...")
                try:
                    res = tg_client.send_message(channel_id, content)
                    if res.get("ok"):
                        post["status"] = "posted"
                        post["posted_at"] = now.isoformat()
                        updated = True
                        if notify_cb:
                            time_str = dt.strftime("%Y-%m-%d %H:%M")
                            notify_cb(
                                f"📢 <b>Telegram Kanaliga Post Joylandi!</b>\n\n"
                                f"📌 <b>Mavzu:</b> {post.get('topic')}\n"
                                f"⏰ <b>Vaqt:</b> {time_str}\n"
                                f"📍 <b>Kanal:</b> {channel_id}\n\n"
                                f"✅ Post muvaffaqiyatli e'lon qilindi!"
                            )
                    else:
                        print(f"[TelegramScheduler] Failed to publish post: {res}")
                except Exception as e:
                    print(f"[TelegramScheduler] Error sending message: {e}")

        if updated:
            self._save()
