#!/usr/bin/env python3
"""
Arkadaş Consulting - Buffer / Publer Bridge (Adım 2)
Resmi Meta va TikTok API lari bilan ovora bo'lmasdan,
Buffer orqali Instagram, Facebook va TikTok ga rasmiy avtomat post chiqarish.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / "social_credentials.json"

def get_buffer_config() -> Dict[str, Any]:
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("buffer", {})
        except Exception:
            pass
    return {}

def save_buffer_config(cfg: Dict[str, Any]):
    data = {}
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["buffer"] = cfg
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class BufferBridge:
    def __init__(self):
        self.config = get_buffer_config()
        self.access_token = self.config.get("access_token", "")
        self.profile_ids = self.config.get("profile_ids", [])

    def is_configured(self) -> bool:
        return bool(self.access_token and len(self.access_token) > 10 and self.profile_ids)

    def get_user_profiles(self) -> List[Dict[str, Any]]:
        """Buffer hisobiga ulangan barcha profillarni (Instagram, FB, TikTok) oladi."""
        if not self.access_token:
            return []
        url = "https://api.bufferapp.com/1/profiles.json"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"}, timeout=15)
            if r.status_code == 200:
                profiles = r.json()
                # Profile ID larni avtomatik saqlab qo'yish
                p_ids = [p["id"] for p in profiles if "id" in p]
                self.profile_ids = p_ids
                self.config["profile_ids"] = p_ids
                save_buffer_config(self.config)
                return profiles
        except Exception as e:
            print(f"[BUFFER ERROR] Profiles fetch failed: {e}")
        return []

    def publish_post(self, text: str, image_url: str = None, post_now: bool = True) -> Dict[str, Any]:
        """Buffer orqali ulangan barcha kanallarga post yuboradi."""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Buffer sozlanmagan. Token va profil ID lari kerak."
            }

        url = "https://api.bufferapp.com/1/updates/create.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        payload = {
            "text": text,
            "now": "true" if post_now else "false"
        }
        for idx, pid in enumerate(self.profile_ids):
            payload[f"profile_ids[{idx}]"] = pid

        if image_url:
            payload["media[photo]"] = image_url

        try:
            r = requests.post(url, headers=headers, data=payload, timeout=25)
            res = r.json()
            return {
                "success": res.get("success", False),
                "details": res
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_setup_guide(self) -> str:
        return (
            "📋 <b>BUFFER ORQALI BEPUL ULASH BO'YICHA YO'RIQNOMA (ADIM 2):</b>\n\n"
            "1. <b>buffer.com</b> saytiga kiring va bepul ro'yxatdan o'ting.\n"
            "2. 'Connect Channels' tugmasini bosib, Instagram, Facebook va TikTok hisoblaringizni bog'lang (3 ta hisobgacha mutlaqo bepul).\n"
            "3. <b>buffer.com/developers/apps</b> sahifasiga kirib, 'Create an App' orqali bepul <b>Access Token</b> oling.\n"
            "4. Ushbu tokenni Telegram botga yuboring yoki <code>social_credentials.json</code> faylidagi 'buffer' bo'limiga qo'ying.\n\n"
            "✅ Shundan so'ng barcha postlar avtomatik tarzda Instagram, Facebook va TikTok ga chiqadi!"
        )

if __name__ == "__main__":
    b = BufferBridge()
    print("Buffer Configured:", b.is_configured())
    print("Setup Guide:\n", b.get_setup_guide())
