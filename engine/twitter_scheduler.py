"""
Twitter Scheduler Engine:
Manages scheduling, persistent storage in brain_data/scheduled_tweets.json,
and automatic background publishing of single tweets and multi-part Threads.
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEDULE_FILE = BASE_DIR / "brain_data" / "scheduled_tweets.json"


class TwitterScheduler:
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
            "tweets": []
        }

    def _save(self):
        try:
            with open(self.schedule_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TwitterScheduler] Error saving schedule: {e}")

    def save_weekly_plan(self, week_plan: dict):
        self.data = {
            "active": True,
            "created_at": datetime.now().isoformat(),
            "week_id": week_plan.get("week_id", f"w_{int(time.time())}"),
            "start_date": week_plan.get("start_date"),
            "end_date": week_plan.get("end_date"),
            "tweets": week_plan.get("tweets", [])
        }
        self._save()

    def cancel_plan(self):
        self.data["active"] = False
        for tw in self.data.get("tweets", []):
            if tw.get("status") == "pending":
                tw["status"] = "cancelled"
        self._save()

    def is_active(self) -> bool:
        return bool(self.data.get("active", False))

    def get_all_tweets(self) -> List[dict]:
        return self.data.get("tweets", [])

    def get_pending_tweets(self) -> List[dict]:
        return [tw for tw in self.data.get("tweets", []) if tw.get("status") == "pending"]

    def get_summary(self) -> dict:
        tweets = self.data.get("tweets", [])
        total = len(tweets)
        posted = len([t for t in tweets if t.get("status") == "posted"])
        pending = len([t for t in tweets if t.get("status") == "pending"])
        threads = len([t for t in tweets if t.get("is_thread")])
        return {
            "active": self.data.get("active", False),
            "total": total,
            "posted": posted,
            "pending": pending,
            "threads": threads,
            "start_date": self.data.get("start_date", "—"),
            "end_date": self.data.get("end_date", "—")
        }

    def check_and_publish_due(self, browser_pub, notify_cb: Optional[Callable[[str], Any]] = None):
        """
        Scans pending tweets. If datetime.now() >= scheduled_time, publishes to Twitter!
        """
        if not self.data.get("active", False):
            return

        now = datetime.now()
        updated = False

        for tw in self.data.get("tweets", []):
            if tw.get("status") != "pending":
                continue

            sched_str = tw.get("scheduled_time")
            if not sched_str:
                continue

            try:
                sched_dt = datetime.fromisoformat(sched_str)
            except Exception:
                continue

            # Check if time has arrived (within current minute or earlier)
            if now >= sched_dt:
                is_thread = tw.get("is_thread", False)
                content = tw.get("content", "")
                thread_items = tw.get("thread_items", [])
                image_path = tw.get("image_path")

                print(f"[TwitterScheduler] Publishing due tweet {tw.get('id')} ({tw.get('slot')})...")

                if is_thread and thread_items:
                    res = browser_pub.publish_twitter_thread(thread_items)
                else:
                    res = browser_pub.publish_twitter_web(content, image_path)

                if res.get("success"):
                    tw["status"] = "posted"
                    tw["posted_at"] = now.isoformat()
                    updated = True

                    msg = (
                        f"✅ <b>[TWITTER REJASI: E'LON QILINDI]</b>\n"
                        f"⏰ <b>Vaqti:</b> {tw.get('scheduled_time', '')}\n"
                        f"📌 <b>Mavzu:</b> {tw.get('topic', '')}\n\n"
                        f"<i>{content[:200]}...</i>\n\n"
                        f"🌐 <i>Twitter (@arkadasuz) ga muvaffaqiyatli chiqdi!</i>"
                    )
                    if notify_cb:
                        try:
                            notify_cb(msg)
                        except Exception as e:
                            print(f"[TwitterScheduler] Notify error: {e}")
                else:
                    tw["status"] = "failed"
                    tw["error"] = res.get("error", "Noma'lum xatolik")
                    tw["attempted_at"] = now.isoformat()
                    updated = True

                    msg = (
                        f"⚠️ <b>[TWITTER REJASI: XATOLIK]</b>\n"
                        f"⏰ <b>Vaqti:</b> {tw.get('scheduled_time', '')}\n"
                        f"❌ <b>Sabab:</b> {tw.get('error')}"
                    )
                    if notify_cb:
                        try:
                            notify_cb(msg)
                        except Exception:
                            pass

        if updated:
            # If no more pending tweets, deactivate schedule
            if len(self.get_pending_tweets()) == 0:
                self.data["active"] = False
            self._save()
