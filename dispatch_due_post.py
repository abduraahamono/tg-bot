#!/usr/bin/env python3
"""
dispatch_due_post.py
Runs locally or in GitHub Actions (Cloud Cron).
Checks brain_data/scheduled_telegram_posts.json, finds posts due now,
and posts them to Telegram channel @arkadasuz using Telegram Bot API.
Supports both text-only (sendMessage) and visual card + caption (sendPhoto) with automatic fallback.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

UZ_TZ = timezone(timedelta(hours=5))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_FILE = os.path.join(BASE_DIR, "brain_data", "scheduled_telegram_posts.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

def get_env_var(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return default

BOT_TOKEN = get_env_var("TELEGRAM_BOT_TOKEN", "8855584904:AAGlBVSXCDIfUy8WvMOdmzpQjLb0YIONOyU")
CHANNEL_ID = get_env_var("TELEGRAM_CHANNEL_ID", "@arkadasuz")

def parse_telegram_error(err_str: str) -> str:
    """Human-friendly error description for Telegram API failures."""
    if "bot is not a member of the channel" in err_str or "member list is inaccessible" in err_str or "need administrator rights" in err_str:
        return "Bot (@ArkadasAdminBot) @arkadasuz kanaliga Administrator (yoki a'zo) qilib qo'shilmagan! Kanal sozlamalaridan botni Administrator qilib, 'Post Messages' (Xabarlarni joylashtirish) ruxsatini bering."
    if "chat not found" in err_str:
        return "Kanal (@arkadasuz) topilmadi yoki noto'g'ri ko'rsatilgan."
    if "Unauthorized" in err_str:
        return "Telegram Bot tokeni noto'g'ri yoki yaroqsiz."
    return err_str

def send_telegram_photo(text: str, photo_path: str) -> bool:
    """Uploads a local card image via multipart/form-data to sendPhoto."""
    ok, _ = send_telegram_photo_detailed(text, photo_path)
    return ok

def send_telegram_photo_detailed(text: str, photo_path: str) -> tuple[bool, str]:
    if not os.path.exists(photo_path):
        return False, f"Görsel dosyası bulunamadı: {photo_path}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    boundary = "----WebKitFormBoundaryArkadasPost"
    data = []

    # chat_id
    data.extend([
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'.encode("utf-8"),
        f"{CHANNEL_ID}\r\n".encode("utf-8")
    ])

    # caption
    if text:
        data.extend([
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="caption"\r\n\r\n'.encode("utf-8"),
            f"{text}\r\n".encode("utf-8"),
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="parse_mode"\r\n\r\n'.encode("utf-8"),
            b"HTML\r\n"
        ])

    # photo file
    fname = os.path.basename(photo_path)
    with open(photo_path, "rb") as f:
        file_bytes = f.read()

    data.extend([
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="photo"; filename="{fname}"\r\n'.encode("utf-8"),
        b"Content-Type: image/jpeg\r\n\r\n",
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8")
    ])

    body = b"".join(data)
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                print(f"[OK] Rasm va matn kanalga muvaffaqiyatli yuborildi: {CHANNEL_ID} (sendPhoto)")
                return True, "OK"
            else:
                desc = res_data.get('description', '')
                print(f"[WARN] sendPhoto rad etildi: {desc}")
                return False, parse_telegram_error(desc)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            desc = json.loads(err_body).get("description", err_body)
        except Exception:
            desc = err_body
        friendly = parse_telegram_error(desc)
        print(f"[ERROR] sendPhoto HTTP {e.code}: {friendly}")
        return False, friendly
    except Exception as e:
        print(f"[WARN] sendPhoto tarmoq xatosi: {e}")
        return False, str(e)

def send_telegram_text(text: str) -> bool:
    """Sends text-only message via sendMessage."""
    ok, _ = send_telegram_text_detailed(text)
    return ok

def send_telegram_text_detailed(text: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                print(f"[OK] Matnli post kanalga muvaffaqiyatli yuborildi: {CHANNEL_ID} (sendMessage)")
                return True, "OK"
            else:
                desc = res_data.get('description', '')
                print(f"[ERROR] Telegram API xatosi: {desc}")
                return False, parse_telegram_error(desc)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            desc = json.loads(err_body).get("description", err_body)
        except Exception:
            desc = err_body
        friendly = parse_telegram_error(desc)
        print(f"[ERROR] sendMessage HTTP {e.code}: {friendly}")
        return False, friendly
    except Exception as e:
        print(f"[ERROR] Tarmoq xatosi: {e}")
        return False, str(e)

def send_telegram_video_detailed(text: str, video_path: str) -> tuple[bool, str]:
    """Uploads a local video via multipart/form-data to sendVideo."""
    if not os.path.exists(video_path):
        return False, f"Video dosyası bulunamadı: {video_path}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    boundary = "----WebKitFormBoundaryArkadasPostVid"
    data = []

    # chat_id
    data.extend([
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'.encode("utf-8"),
        f"{CHANNEL_ID}\r\n".encode("utf-8")
    ])

    # caption
    if text:
        data.extend([
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="caption"\r\n\r\n'.encode("utf-8"),
            f"{text}\r\n".encode("utf-8"),
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="parse_mode"\r\n\r\n'.encode("utf-8"),
            b"HTML\r\n"
        ])

    fname = os.path.basename(video_path)
    with open(video_path, "rb") as f:
        file_bytes = f.read()

    data.extend([
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="video"; filename="{fname}"\r\n'.encode("utf-8"),
        b"Content-Type: video/mp4\r\n\r\n",
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8")
    ])

    body = b"".join(data)
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("ok"):
                print(f"[OK] Video kanalga muvaffaqiyatli yuborildi: {CHANNEL_ID} (sendVideo)")
                return True, "OK"
            else:
                desc = res_data.get('description', '')
                return False, parse_telegram_error(desc)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            desc = json.loads(err_body).get("description", err_body)
        except Exception:
            desc = err_body
        friendly = parse_telegram_error(desc)
        return False, friendly
    except Exception as e:
        return False, str(e)

def send_telegram_media_or_text(text: str, photo_path: str = "", video_path: str = "") -> tuple[bool, str]:
    """Unified dispatcher supporting photo, video, and text."""
    if not BOT_TOKEN:
        return False, "TELEGRAM_BOT_TOKEN topilmadi!"

    if video_path and os.path.exists(video_path):
        return send_telegram_video_detailed(text, video_path)

    if photo_path and os.path.exists(photo_path):
        return send_telegram_photo_detailed(text, photo_path)

    return send_telegram_text_detailed(text)

def send_telegram_post(text: str, photo_path: str = "") -> bool:
    ok, _ = send_telegram_media_or_text(text, photo_path=photo_path)
    return ok

def dispatch(dry_run: bool = False, force_first_pending: bool = False):
    now_uz = datetime.now(UZ_TZ)
    now_str = now_uz.strftime("%Y-%m-%dT%H:%M:%S")
    today_str = now_uz.strftime("%Y-%m-%d")
    print(f"[INFO] Hozirgi O'zbekiston vaqti: {now_str}")

    if not os.path.exists(POSTS_FILE):
        print(f"[WARN] Fayl topilmadi: {POSTS_FILE}")
        return

    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data.get("active"):
        print("[INFO] Reja aktiv emas.")
        return

    posts = data.get("posts", [])
    due_post = None

    for post in posts:
        if post.get("status") == "pending":
            sched_time = post.get("scheduled_time", "")
            if force_first_pending:
                due_post = post
                break
            elif sched_time <= now_str:
                due_post = post
                break

    if not due_post:
        print("[INFO] Hozir yuborilishi kerak bo'lgan navbatdagi post yo'q.")
        return

    photo_p = due_post.get("photo_path", "")
    if photo_p and not os.path.isabs(photo_p):
        photo_p = os.path.join(BASE_DIR, photo_p)

    has_photo = "Mavjud (sendPhoto)" if photo_p and os.path.exists(photo_p) else "Yo'q (sendMessage)"

    print(f"[POSTING] ID: {due_post.get('id')} | Sana: {due_post.get('date_str')} | Slot: {due_post.get('slot_label')}")
    print(f"Mavzu: {due_post.get('topic')}")
    print(f"Dizayn Kartasi (Rasm): {has_photo}")

    if dry_run:
        print("[DRY-RUN] Sinov rejimi. Xabar yuborilmadi.")
        return

    success = send_telegram_post(due_post["content"], photo_path=photo_p)
    if success:
        due_post["status"] = "posted"
        due_post["posted_at"] = now_str
        from engine.storage_utils import atomic_save_json
        atomic_save_json(POSTS_FILE, data)
        print("[OK] Rejadagi holat 'posted' ga yangilandi va saqlandi.")

if __name__ == "__main__":
    force = "--force" in sys.argv
    dry = "--dry-run" in sys.argv
    dispatch(dry_run=dry, force_first_pending=force)
