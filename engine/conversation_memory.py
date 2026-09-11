"""
Conversation Memory Engine
Tracks persistent multi-turn chat history and user profiles (e.g., admin status, target field, name)
so the AI consultant acts with genuine contextual memory instead of greeting as a stranger on every turn.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from engine.storage_utils import atomic_save_json, safe_load_json

BASE_DIR = Path(__file__).parent.parent
MEMORY_FILE = BASE_DIR / "brain_data" / "chat_memory.json"

class ConversationMemory:
    def __init__(self, storage_file: Path = MEMORY_FILE):
        self.storage_file = storage_file
        self.data: Dict[str, Any] = safe_load_json(self.storage_file, default={"users": {}, "history": {}})
        if "users" not in self.data:
            self.data["users"] = {}
        if "history" not in self.data:
            self.data["history"] = {}

    def get_user_profile(self, chat_id: str) -> dict:
        cid = str(chat_id)
        return self.data["users"].get(cid, {})

    def update_user_profile(self, chat_id: str, updates: dict):
        cid = str(chat_id)
        if cid not in self.data["users"]:
            self.data["users"][cid] = {
                "chat_id": cid,
                "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        self.data["users"][cid].update(updates)
        self.data["users"][cid]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()

    def add_message(self, chat_id: str, role: str, text: str, user_meta: Optional[dict] = None):
        cid = str(chat_id)
        if cid not in self.data["history"]:
            self.data["history"][cid] = []
            
        if user_meta:
            self.update_user_profile(cid, user_meta)

        self.data["history"][cid].append({
            "role": role,
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Keep last 20 messages per user
        if len(self.data["history"][cid]) > 20:
            self.data["history"][cid] = self.data["history"][cid][-20:]
        self._save()

    def get_recent_history(self, chat_id: str, limit: int = 6) -> List[dict]:
        cid = str(chat_id)
        return self.data["history"].get(cid, [])[-limit:]

    def get_history_summary_for_prompt(self, chat_id: str, limit: int = 6) -> str:
        cid = str(chat_id)
        hist = self.get_recent_history(cid, limit=limit)
        if not hist:
            return ""

        lines = []
        for h in hist:
            speaker = "Mijoz" if h["role"] == "user" else "Konsultant"
            lines.append(f"{speaker}: {h['text']}")
        return "\n".join(lines)

    def _save(self):
        atomic_save_json(self.storage_file, self.data)
