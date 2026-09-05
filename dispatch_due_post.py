#!/usr/bin/env python3
"""
dispatch_due_post.py
Runs locally or in GitHub Actions (Cloud Cron).
Checks brain_data/scheduled_telegram_posts.json, finds posts due now,
and posts them to Telegram channel @arkadasuz using Telegram Bot API.
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

BOT_TOKEN = get_env_var("TELEGRAM_BOT_TOKEN", "7850828340:AAENUCBd_PG2U7Nzl2lx0RsE45h8t5i0vqg")
CHANNEL_ID = get_env_var("TELEGRAM_CHANNEL_ID", "@arkadasuz")

def send_telegram_post(text: str) -> bool:
    if not BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN topilmadi!")
        return False
    
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
                print(f"[OK] Post kanalga muvaffaqiyatli yuborildi: {CHANNEL_ID}")
                return True
            else:
                print(f"[ERROR] Telegram API xatosi: {res_data}")
                return False
    except Exception as e:
        print(f"[ERROR] Tarmoq xatosi: {e}")
        return False

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

    print(f"[POSTING] ID: {due_post.get('id')} | Sana: {due_post.get('date_str')} | Slot: {due_post.get('slot_label')}")
    print(f"Mavzu: {due_post.get('topic')}")

    if dry_run:
        print("[DRY-RUN] Sinov rejimi. Xabar yuborilmadi.")
        return

    success = send_telegram_post(due_post["content"])
    if success:
        due_post["status"] = "posted"
        due_post["posted_at"] = now_str
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[OK] Rejadagi holat 'posted' ga yangilandi va saqlandi.")

if __name__ == "__main__":
    force = "--force" in sys.argv
    dry = "--dry-run" in sys.argv
    dispatch(dry_run=dry, force_first_pending=force)
