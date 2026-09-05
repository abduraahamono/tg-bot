#!/usr/bin/env python3
"""
Arkadaş Consulting - Omnichannel Social Media Publisher
Quyidagi 6 ta platformaga yagona nuqtadan kontent tarqatish:
1. Telegram (Kanal & Guruh)
2. Instagram (Feed / Carousel / Post)
3. Facebook (Sahifa posti)
4. Twitter / X (Rasm va tvit)
5. YouTube (Community posti)
6. TikTok (Post e'loni)
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CREDENTIALS_FILE = BASE_DIR / "social_credentials.json"
from bot.telegram_client import TelegramClient

def load_credentials() -> Dict[str, Any]:
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_credentials(creds: Dict[str, Any]):
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f, ensure_ascii=False, indent=2)

class SocialPublisher:
    def __init__(self):
        self.creds = load_credentials()
        tg_conf = self.creds.get("telegram", {})
        self.tg_client = TelegramClient(tg_conf.get("bot_token", ""))

    def get_platforms_status(self) -> Dict[str, Dict[str, Any]]:
        """Qaysi platformalar ulangan va qaysilari kutilayotganini ko'rsatadi."""
        self.creds = load_credentials()
        res = {}
        for plat in ["telegram", "instagram", "facebook", "twitter", "youtube", "tiktok"]:
            cfg = self.creds.get(plat, {})
            is_enabled = cfg.get("enabled", False)
            configured = False

            if plat == "telegram":
                configured = bool(cfg.get("bot_token") and cfg.get("channel_id"))
            elif plat in ["instagram", "facebook"]:
                configured = bool(cfg.get("access_token") and (cfg.get("account_id") or cfg.get("page_id")))
            elif plat == "twitter":
                configured = bool(cfg.get("api_key") and cfg.get("access_token"))
            elif plat == "youtube":
                configured = bool(cfg.get("client_id") and cfg.get("refresh_token"))
            elif plat == "tiktok":
                configured = bool(cfg.get("access_token"))

            res[plat] = {
                "enabled": is_enabled,
                "configured": configured,
                "status_text": "✅ Bog'langan" if (is_enabled and configured) else ("⏳ Kalit kerak" if not configured else "⏸️ O'chirilgan")
            }
        return res

    # 1. TELEGRAM
    def publish_telegram(self, post_data: dict) -> dict:
        tg_conf = self.creds.get("telegram", {})
        channel = tg_conf.get("channel_id", "@arkadasuz")
        is_card = post_data.get("media_type") == "image"
        media_path = post_data.get("media_path")
        text = post_data.get("caption") if is_card else post_data.get("content", "")

        try:
            if is_card and media_path and os.path.exists(media_path):
                r = self.tg_client.send_photo(channel, media_path, caption=text)
            else:
                r = self.tg_client.send_message(channel, text)
            return {"platform": "telegram", "success": r.get("ok", False), "details": r}
        except Exception as e:
            return {"platform": "telegram", "success": False, "error": str(e)}

    # 2. INSTAGRAM (Meta Graph API)
    def publish_instagram(self, post_data: dict) -> dict:
        ig_conf = self.creds.get("instagram", {})
        if not ig_conf.get("enabled") or not ig_conf.get("access_token") or not ig_conf.get("account_id"):
            return {"platform": "instagram", "success": False, "error": "Instagram API kalitlari kiritilmagan"}

        account_id = ig_conf["account_id"]
        token = ig_conf["access_token"]
        is_card = post_data.get("media_type") == "image"
        caption = post_data.get("caption") if is_card else post_data.get("content", "")

        # Instagram API requires a publicly accessible image URL or container upload
        # Meta Graph API: POST /{ig-user-id}/media -> POST /{ig-user-id}/media_publish
        try:
            # Container creation endpoint
            url = f"https://graph.facebook.com/v19.0/{account_id}/media"
            payload = {
                "access_token": token,
                "caption": caption
            }
            if is_card and post_data.get("image_url"):
                payload["image_url"] = post_data["image_url"]

            r = requests.post(url, data=payload, timeout=30)
            res = r.json()
            if "id" in res:
                creation_id = res["id"]
                # Publish container
                pub_url = f"https://graph.facebook.com/v19.0/{account_id}/media_publish"
                pub_r = requests.post(pub_url, data={"creation_id": creation_id, "access_token": token}, timeout=30)
                pub_res = pub_r.json()
                return {"platform": "instagram", "success": "id" in pub_res, "post_id": pub_res.get("id")}
            return {"platform": "instagram", "success": False, "error": res.get("error", {}).get("message", "Noma'lum xato")}
        except Exception as e:
            return {"platform": "instagram", "success": False, "error": str(e)}

    # 3. FACEBOOK (Meta Graph API)
    def publish_facebook(self, post_data: dict) -> dict:
        fb_conf = self.creds.get("facebook", {})
        if not fb_conf.get("enabled") or not fb_conf.get("access_token") or not fb_conf.get("page_id"):
            return {"platform": "facebook", "success": False, "error": "Facebook API kalitlari kiritilmagan"}

        page_id = fb_conf["page_id"]
        token = fb_conf["access_token"]
        is_card = post_data.get("media_type") == "image"
        media_path = post_data.get("media_path")
        text = post_data.get("caption") if is_card else post_data.get("content", "")

        try:
            if is_card and media_path and os.path.exists(media_path):
                url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                with open(media_path, "rb") as f:
                    r = requests.post(url, data={"caption": text, "access_token": token}, files={"source": f}, timeout=45)
            else:
                url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
                r = requests.post(url, data={"message": text, "access_token": token}, timeout=30)

            res = r.json()
            return {"platform": "facebook", "success": "id" in res or "post_id" in res, "details": res}
        except Exception as e:
            return {"platform": "facebook", "success": False, "error": str(e)}

    # 4. TWITTER / X (X API v2)
    def publish_twitter(self, post_data: dict) -> dict:
        tw_conf = self.creds.get("twitter", {})
        if not tw_conf.get("enabled") or not tw_conf.get("api_key") or not tw_conf.get("access_token"):
            return {"platform": "twitter", "success": False, "error": "Twitter (X) API kalitlari kiritilmagan"}

        # Twitter 280-char limit formatting
        is_card = post_data.get("media_type") == "image"
        text = post_data.get("caption") if is_card else post_data.get("content", "")
        if len(text) > 275:
            text = text[:265] + "...\n👉 @arkadasuz"

        try:
            from requests_oauthlib import OAuth1
            auth = OAuth1(
                tw_conf["api_key"],
                tw_conf.get("api_secret", ""),
                tw_conf["access_token"],
                tw_conf.get("access_token_secret", "")
            )
            # Post tweet v2
            r = requests.post("https://api.twitter.com/2/tweets", json={"text": text}, auth=auth, timeout=30)
            res = r.json()
            return {"platform": "twitter", "success": "data" in res, "details": res}
        except Exception as e:
            return {"platform": "twitter", "success": False, "error": str(e)}

    # 5. YOUTUBE (YouTube Community / Data API)
    def publish_youtube(self, post_data: dict) -> dict:
        yt_conf = self.creds.get("youtube", {})
        if not yt_conf.get("enabled") or not yt_conf.get("refresh_token"):
            return {"platform": "youtube", "success": False, "error": "YouTube API kalitlari kiritilmagan"}
        return {"platform": "youtube", "success": False, "error": "YouTube Community API sozlanmoqda"}

    # 6. TIKTOK (Content Posting API)
    def publish_tiktok(self, post_data: dict) -> dict:
        tk_conf = self.creds.get("tiktok", {})
        if not tk_conf.get("enabled") or not tk_conf.get("access_token"):
            return {"platform": "tiktok", "success": False, "error": "TikTok API kalitlari kiritilmagan"}
        return {"platform": "tiktok", "success": False, "error": "TikTok Content Posting API sozlanmoqda"}

    # OMNICHANNEL BROADCAST (Barchasiga Bir Vaqtda Tarqatish)
    def broadcast_all(self, post_data: dict, selected_platforms: List[str] = None) -> Dict[str, Any]:
        """Belgilangan yoki barcha faol platformalarga bir vaqtda postni chiqaradi."""
        targets = selected_platforms or ["telegram", "instagram", "facebook", "twitter", "youtube", "tiktok"]
        results = {}

        for plat in targets:
            if plat == "telegram":
                results["telegram"] = self.publish_telegram(post_data)
            elif plat == "instagram":
                results["instagram"] = self.publish_instagram(post_data)
            elif plat == "facebook":
                results["facebook"] = self.publish_facebook(post_data)
            elif plat == "twitter":
                results["twitter"] = self.publish_twitter(post_data)
            elif plat == "youtube":
                results["youtube"] = self.publish_youtube(post_data)
            elif plat == "tiktok":
                results["tiktok"] = self.publish_tiktok(post_data)

        return results

if __name__ == "__main__":
    pub = SocialPublisher()
    st = pub.get_platforms_status()
    print("=== IJTIMOIY TARMOQLAR HOLATI ===")
    for k, v in st.items():
        print(f"• {k.upper():10}: {v['status_text']}")
