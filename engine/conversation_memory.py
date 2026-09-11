"""
Conversation Memory Engine
Tracks persistent multi-turn chat history and user profiles (phone numbers, names, target fields)
Extracts key entities automatically from text so the AI maintains genuine conversational memory.
"""

import re
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

    def extract_entities_from_text(self, chat_id: str, text: str, user_name: str = ""):
        """Auto-detects phone numbers, names, and field interests from user input."""
        cid = str(chat_id)
        updates = {}
        if user_name and not self.data["users"].get(cid, {}).get("name"):
            updates["name"] = user_name

        # 1. Phone number detection (e.g., 93-566-66-66, +998901234567, 90 123 45 67)
        phone_match = re.search(r'(\+?[0-9]{1,3}[\s\-]?)?(\(?[0-9]{2,3}\)?[\s\-]?)?([0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}|[0-9]{7,10})', text)
        if phone_match:
            raw_phone = phone_match.group(0).strip()
            digits = re.sub(r'\D', '', raw_phone)
            if len(digits) >= 7:
                updates["phone"] = raw_phone

        # 2. Field of study detection
        t_low = text.lower()
        if any(k in t_low for k in ["tip", "tibbiyot", "doktor", "shifokor", "meditsina", "stomatolog"]):
            updates["interest"] = "Tibbiyot / Stomatologiya"
        elif any(k in t_low for k in ["ilahiyot", "islom", "dinshunos", "29 mayis"]):
            updates["interest"] = "İlahiyat (Dinshunoslik)"
        elif any(k in t_low for k in ["it", "dasturlash", "programmer", "kiber", "sun'iy intellekt"]):
            updates["interest"] = "IT va Dasturlash"
        elif any(k in t_low for k in ["biznes", "menejment", "iqtisod", "marketing"]):
            updates["interest"] = "Biznes va Menejment"
        elif any(k in t_low for k in ["burs", "turkiya burslari", "grant"]):
            updates["interest"] = "Türkiye Bursları (Davlat granti)"

        # 3. Explicit name intro
        name_match = re.search(r'(?:ismim|mening ismim|otim)\s+([A-ZА-Яa-zа-яA-Za-z\']+)', text, re.IGNORECASE)
        if name_match:
            updates["name"] = name_match.group(1).capitalize()

        if updates:
            self.update_user_profile(cid, updates)

    def add_message(self, chat_id: str, role: str, text: str, user_meta: Optional[dict] = None):
        cid = str(chat_id)
        if cid not in self.data["history"]:
            self.data["history"][cid] = []
            
        if user_meta:
            self.update_user_profile(cid, user_meta)

        if role == "user":
            self.extract_entities_from_text(cid, text, user_name=user_meta.get("name", "") if user_meta else "")

        self.data["history"][cid].append({
            "role": role,
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Keep last 15 messages per user for context window
        if len(self.data["history"][cid]) > 15:
            self.data["history"][cid] = self.data["history"][cid][-15:]
        self._save()

    def get_recent_history(self, chat_id: str, limit: int = 8) -> List[dict]:
        cid = str(chat_id)
        return self.data["history"].get(cid, [])[-limit:]

    def get_history_summary_for_prompt(self, chat_id: str, limit: int = 8) -> str:
        cid = str(chat_id)
        hist = self.get_recent_history(cid, limit=limit)
        if not hist:
            return ""

        lines = []
        for h in hist:
            speaker = "Mijoz" if h["role"] == "user" else "Konsultant"
            lines.append(f"{speaker}: {h['text']}")
        return "\n".join(lines)

    def get_profile_summary_for_prompt(self, chat_id: str) -> str:
        """Returns structured memory of known facts about this user."""
        p = self.get_user_profile(chat_id)
        if not p:
            return ""

        items = []
        if p.get("name"):
            items.append(f"- Ismi: {p['name']}")
        if p.get("phone"):
            items.append(f"- Qoldirgan telefon raqami: {p['phone']}")
        if p.get("interest"):
            items.append(f"- Qiziqqan sohasi: {p['interest']}")
        if p.get("is_admin"):
            items.append("- Maqomi: Kompaniya rahbari / Admin (@prodbyapo)")

        if not items:
            return ""
        return "FOYDALANUVCHI PROFILI (Xotirangizdagi faktlar):\n" + "\n".join(items)

    def _save(self):
        atomic_save_json(self.storage_file, self.data)
