"""
Tweet History Engine:
Tracks all previously generated and posted Twitter content to guarantee
that Week 2, Week 3, and subsequent weeks are 100% unique and NEVER repeated.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "brain_data" / "tweet_history.json"


class TweetHistoryEngine:
    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = Path(history_file) if history_file else HISTORY_FILE
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "used_topics": [],
            "used_threads": [],
            "tweet_hashes": [],
            "total_tweets_posted": 0,
            "weeks_generated": 0
        }

    def _save(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TweetHistory] Error saving history: {e}")

    def get_used_topics(self) -> List[str]:
        return self.data.get("used_topics", [])

    def is_topic_used(self, topic: str) -> bool:
        t_clean = topic.strip().lower()
        return any(t_clean in past.lower() or past.lower() in t_clean for past in self.data.get("used_topics", []))

    def record_topic(self, topic: str):
        if topic and topic not in self.data.get("used_topics", []):
            self.data.setdefault("used_topics", []).append(topic)
            self._save()

    def record_tweet(self, text: str, topic: Optional[str] = None):
        h = hashlib.md5(text.strip().encode("utf-8")).hexdigest()
        if h not in self.data.get("tweet_hashes", []):
            self.data.setdefault("tweet_hashes", []).append(h)
        if topic and topic not in self.data.get("used_topics", []):
            self.data.setdefault("used_topics", []).append(topic)
        self.data["total_tweets_posted"] = self.data.get("total_tweets_posted", 0) + 1
        self._save()

    def record_thread_topic(self, topic: str):
        if topic and topic not in self.data.get("used_threads", []):
            self.data.setdefault("used_threads", []).append(topic)
            self._save()

    def record_week_generation(self):
        self.data["weeks_generated"] = self.data.get("weeks_generated", 0) + 1
        self._save()

    def get_history_summary(self) -> dict:
        return {
            "used_topics_count": len(self.data.get("used_topics", [])),
            "used_threads_count": len(self.data.get("used_threads", [])),
            "total_tweets_posted": self.data.get("total_tweets_posted", 0),
            "weeks_generated": self.data.get("weeks_generated", 0)
        }
