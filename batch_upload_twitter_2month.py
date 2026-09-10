#!/usr/bin/env python3
"""
batch_upload_twitter_2month.py
Automates uploading and scheduling tweets directly into Twitter (X) Web scheduler.
Iterates through pending tweets in brain_data/scheduled_tweets.json and sets them up in Twitter's native queue.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
TWEETS_FILE = BASE_DIR / "brain_data" / "scheduled_tweets.json"
PROFILE_DIR = BASE_DIR / "data" / "browser_profile"

def clean_locks():
    for f in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        lf = PROFILE_DIR / f
        if lf.exists():
            try:
                lf.unlink()
            except Exception:
                pass

def batch_schedule(max_count: int = 50):
    clean_locks()

    if not TWEETS_FILE.exists():
        print("[ERROR] scheduled_tweets.json topilmadi!")
        return

    with open(TWEETS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    tweets = data.get("tweets", [])
    pending = [t for t in tweets if t.get("status") == "pending" and t.get("scheduled_time") >= "2026-09-11T00:00:00"]

    if not pending:
        print("[INFO] Kutilayotgan yangi tvitlar yo'q.")
        return

    to_schedule = pending[:max_count]
    print(f"[INFO] Twitterga yuklash uchun tanlandi: {len(to_schedule)} ta tvit (Limit: {max_count})")

    success_count = 0
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()

        for idx, tw in enumerate(to_schedule, 1):
            tw_id = tw.get("id")
            content = tw.get("content", "").strip()
            sched_str = tw.get("scheduled_time")

            try:
                dt = datetime.fromisoformat(sched_str)
            except Exception as e:
                print(f"[{idx}/{len(to_schedule)}] {tw_id} sana xatosi: {e}")
                continue

            print(f"[{idx}/{len(to_schedule)}] Yuklanmoqda: {tw_id} ({dt.strftime('%d.%m.%Y %H:%M')})...")

            try:
                page.goto("https://x.com/compose/post", timeout=25000)
                page.wait_for_timeout(2000)

                # Find textbox
                box = page.locator('div[data-testid="tweetTextarea_0"]').first
                if box.count() == 0:
                    box = page.locator('div[role="textbox"]').first
                
                box.click()
                box.fill(content)
                page.wait_for_timeout(400)

                # Click Schedule button
                sch_btn = page.locator('button[data-testid="scheduleOption"]').first
                if sch_btn.count() == 0:
                    print(f"  ❌ Schedule tugmasi topilmadi")
                    errors.append((tw_id, "Schedule button missing"))
                    continue

                sch_btn.dispatch_event("click")
                page.locator('select').first.wait_for(state="visible", timeout=10000)

                selects = page.locator('select').all()
                if len(selects) < 6:
                    print(f"  ❌ Selectlar yetarli emas")
                    errors.append((tw_id, "Insufficient selects"))
                    continue

                # 0: Month (1-12)
                selects[0].select_option(value=str(dt.month))
                page.wait_for_timeout(60)

                # 1: Day (1-31)
                selects[1].select_option(value=str(dt.day))
                page.wait_for_timeout(60)

                # 2: Year (2026, 2027)
                selects[2].select_option(value=str(dt.year))
                page.wait_for_timeout(60)

                # 3: Hour (1-12)
                hour_12 = dt.hour % 12
                if hour_12 == 0:
                    hour_12 = 12
                selects[3].select_option(value=str(hour_12))
                page.wait_for_timeout(60)

                # 4: Minute (0-59)
                selects[4].select_option(value=str(dt.minute))
                page.wait_for_timeout(60)

                # 5: AM / PM
                ampm = "pm" if dt.hour >= 12 else "am"
                selects[5].select_option(value=ampm)
                page.wait_for_timeout(150)

                # Confirm in modal
                confirm_btn = page.locator('button[data-testid="scheduledConfirmationPrimaryAction"]').first
                if confirm_btn.count() > 0:
                    confirm_btn.dispatch_event("click")
                    page.wait_for_timeout(800)

                # Click Schedule Post button
                post_sched_btn = page.locator('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]').first
                if post_sched_btn.count() > 0:
                    post_sched_btn.dispatch_event("click")
                    page.wait_for_timeout(2000)
                else:
                    page.keyboard.press("Meta+Enter")
                    page.wait_for_timeout(2000)

                # Check if error/limit alert appeared
                toast = page.locator('div[data-testid="toast"]').first
                if toast.count() > 0 and "limit" in toast.inner_text().lower():
                    print(f"  ⚠️ Twitter rejalashtirish limitiga yetildi: {toast.inner_text()}")
                    break

                tw["status"] = "scheduled_on_twitter"
                tw["twitter_queued_at"] = datetime.now().isoformat()
                success_count += 1
                print(f"  ✅ Muvaffaqiyatli rejalashtirildi!")

                # Save after each tweet
                with open(TWEETS_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                page.wait_for_timeout(1200)

            except Exception as e:
                print(f"  ❌ Xatolik: {e}")
                errors.append((tw_id, str(e)))

        browser.close()

    print(f"\n[XULOSA] Jami muvaffaqiyatli rejalashtirildi: {success_count}/{len(to_schedule)}")
    if errors:
        print(f"[OGOHLANTIRISH] Xatolar soni: {len(errors)}")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    batch_schedule(max_count=count)
