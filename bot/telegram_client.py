#!/usr/bin/env python3
"""
Arkadaş Consulting - Lightweight Telegram API Client
Pure Python standard library implementation (urllib.request).
Zero external dependencies required.
Supports:
- Sending text with formatting (HTML / Markdown)
- Sending photos with captions
- Sending videos with captions
- Inline Keyboard buttons (callback queries)
- Polling for updates (long polling)
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List

class TelegramClient:
    def __init__(self, bot_token: Optional[str] = None):
        self.token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def is_configured(self) -> bool:
        return bool(self.token and len(self.token) > 15)

    def _post_json(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            return {"ok": False, "error": "Bot token not configured"}
        url = f"{self.api_url}/{endpoint}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._post_json("sendMessage", payload)

    def send_photo(
        self,
        chat_id: str,
        photo_path: str,
        caption: str = "",
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Uploads a local photo file via multipart/form-data."""
        if not self.is_configured():
            return {"ok": False, "error": "Bot token not configured"}
        
        url = f"{self.api_url}/sendPhoto"
        boundary = "----WebKitFormBoundaryArkadasBot"
        body = []

        # chat_id field
        body.extend([
            f"--{boundary}".encode("utf-8"),
            f'Content-Disposition: form-data; name="chat_id"'.encode("utf-8"),
            b"",
            str(chat_id).encode("utf-8")
        ])

        # caption field
        if caption:
            body.extend([
                f"--{boundary}".encode("utf-8"),
                f'Content-Disposition: form-data; name="caption"'.encode("utf-8"),
                b"",
                caption.encode("utf-8")
            ])

        # parse_mode field
        if parse_mode:
            body.extend([
                f"--{boundary}".encode("utf-8"),
                f'Content-Disposition: form-data; name="parse_mode"'.encode("utf-8"),
                b"",
                parse_mode.encode("utf-8")
            ])

        # reply_markup field
        if reply_markup:
            body.extend([
                f"--{boundary}".encode("utf-8"),
                f'Content-Disposition: form-data; name="reply_markup"'.encode("utf-8"),
                b"",
                json.dumps(reply_markup).encode("utf-8")
            ])

        # photo file field
        p = Path(photo_path)
        with open(p, "rb") as f:
            file_data = f.read()

        body.extend([
            f"--{boundary}".encode("utf-8"),
            f'Content-Disposition: form-data; name="photo"; filename="{p.name}"'.encode("utf-8"),
            b"Content-Type: image/png",
            b"",
            file_data,
            f"--{boundary}--".encode("utf-8"),
            b""
        ])

        payload_bytes = b"\r\n".join(body)
        req = urllib.request.Request(
            url,
            data=payload_bytes,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_video(
        self,
        chat_id: str,
        video_path: str,
        caption: str = "",
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Uploads a local video file via multipart/form-data."""
        if not self.is_configured():
            return {"ok": False, "error": "Bot token not configured"}
        
        url = f"{self.api_url}/sendVideo"
        boundary = "----WebKitFormBoundaryArkadasVideo"
        body = []

        body.extend([
            f"--{boundary}".encode("utf-8"),
            f'Content-Disposition: form-data; name="chat_id"'.encode("utf-8"),
            b"",
            str(chat_id).encode("utf-8")
        ])

        if caption:
            body.extend([
                f"--{boundary}".encode("utf-8"),
                f'Content-Disposition: form-data; name="caption"'.encode("utf-8"),
                b"",
                caption.encode("utf-8")
            ])

        if parse_mode:
            body.extend([
                f"--{boundary}".encode("utf-8"),
                f'Content-Disposition: form-data; name="parse_mode"'.encode("utf-8"),
                b"",
                parse_mode.encode("utf-8")
            ])

        if reply_markup:
            body.extend([
                f"--{boundary}".encode("utf-8"),
                f'Content-Disposition: form-data; name="reply_markup"'.encode("utf-8"),
                b"",
                json.dumps(reply_markup).encode("utf-8")
            ])

        p = Path(video_path)
        with open(p, "rb") as f:
            file_data = f.read()

        body.extend([
            f"--{boundary}".encode("utf-8"),
            f'Content-Disposition: form-data; name="video"; filename="{p.name}"'.encode("utf-8"),
            b"Content-Type: video/mp4",
            b"",
            file_data,
            f"--{boundary}--".encode("utf-8"),
            b""
        ])

        payload_bytes = b"\r\n".join(body)
        req = urllib.request.Request(
            url,
            data=payload_bytes,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_updates(self, offset: int = 0, timeout: int = 25) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []
        url = f"{self.api_url}/getUpdates?offset={offset}&timeout={timeout}"
        try:
            with urllib.request.urlopen(url, timeout=timeout + 5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result", [])
        except Exception:
            return []

    def answer_callback_query(self, callback_query_id: str, text: str = ""):
        return self._post_json("answerCallbackQuery", {
            "callback_query_id": callback_query_id,
            "text": text
        })
