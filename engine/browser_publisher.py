#!/usr/bin/env python3
"""
Arkadaş Consulting - Headless Browser Automation (Adım 3)
Playwright orqali rasmiy API siz, to'g'ridan-to'g'ri Web interfeysidan:
1. Instagram Web (Post chiqarish)
2. Twitter / X Web (Tvit chiqarish)
3. Doimiy sessiya (Cookies) saqlash
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

BASE_DIR = Path(__file__).parent.parent
PROFILE_DIR = BASE_DIR / "data" / "browser_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

class BrowserPublisher:
    def __init__(self):
        self.profile_path = str(PROFILE_DIR)

    def launch_manual_login(self, platform: str = "instagram"):
        """
        Foydalanuvchi bir marta tizimga kirib olishi uchun
        ko'rinadigan brauzer oynasini ochadi va sessiyani saqlaydi.
        """
        from playwright.sync_api import sync_playwright
        url = "https://www.instagram.com" if platform == "instagram" else "https://x.com/i/flow/login"
        print(f"\n[INFO] {platform.upper()} uchun brauzer ochilmoqda...")
        print("[INFO] Iltimos, ochilgan oynada hisobingizga kiring. Sessiya avtomatik saqlanadi.")
        print("[INFO] Kirib bo'lgach, brauzer oynasini yopishingiz mumkin.")

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(60000)  # 60 soniya kutadi
            browser.close()
        print(f"[OK] {platform.upper()} sessiyasi saqlandi!")

    def clean_locks(self):
        """Clean any dangling Chromium Singleton locks."""
        for f in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
            lock_file = PROFILE_DIR / f
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass

    def publish_twitter_web(self, text: str, image_path: str = None) -> Dict[str, Any]:
        """Twitter (X) ga bepul tvit chiqarish."""
        self.clean_locks()
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = browser.new_page()
                page.goto("https://x.com/home", timeout=25000)
                page.wait_for_timeout(3000)

                # Dismiss any open menus/modals with Escape
                page.keyboard.press("Escape")
                page.wait_for_timeout(400)
                page.keyboard.press("Escape")
                page.wait_for_timeout(400)

                # Find compose box
                box = page.locator('div[data-testid="tweetTextarea_0"], div[role="textbox"]').first
                if box.count() == 0:
                    page.goto("https://x.com/compose/post", timeout=20000)
                    page.wait_for_timeout(3000)
                    box = page.locator('div[data-testid="tweetTextarea_0"], div[role="textbox"]').first

                if box.count() == 0:
                    browser.close()
                    return {
                        "success": False,
                        "error": "Twitter hisobiga kirmagansiz yoki yuklanmadi. Terminalda 'python3 login_browser.py' deb qayta kiring."
                    }

                box.click()
                page.wait_for_timeout(400)
                box.fill(text)
                page.wait_for_timeout(1000)

                # Upload image if provided
                if image_path and os.path.exists(image_path):
                    file_input = page.locator('input[data-testid="fileInput"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(image_path)
                        page.wait_for_timeout(3500)

                # Submit tweet via native shortcut (Meta+Enter on Mac, Control+Enter on Win/Linux)
                page.keyboard.press("Meta+Enter")
                page.wait_for_timeout(2000)

                # Fallback: Control+Enter
                box_check = page.locator('div[data-testid="tweetTextarea_0"]').first
                if box_check.count() > 0 and box_check.inner_text().strip():
                    page.keyboard.press("Control+Enter")
                    page.wait_for_timeout(2000)

                # Fallback: Button click
                if box_check.count() > 0 and box_check.inner_text().strip():
                    post_btn = page.locator('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]').first
                    if post_btn.count() > 0:
                        post_btn.scroll_into_view_if_needed()
                        post_btn.click(force=True)
                        page.wait_for_timeout(3000)

                page.wait_for_timeout(2000)
                browser.close()
                return {"success": True, "platform": "twitter_web"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def publish_twitter_thread(self, thread_items: List[str]) -> Dict[str, Any]:
        """Twitter (X) ga ko'p qismli (Flood / Thread) zanjir tvit chiqarish."""
        if not thread_items:
            return {"success": False, "error": "Tvitlar ro'yxati bo'sh"}
        self.clean_locks()
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = browser.new_page()
                page.goto("https://x.com/compose/post", timeout=25000)
                page.wait_for_timeout(3000)

                page.keyboard.press("Escape")
                page.wait_for_timeout(300)

                for idx, tweet_text in enumerate(thread_items):
                    boxes = page.locator('div[data-testid^="tweetTextarea_"], div[role="textbox"]').all()
                    target_box = boxes[-1] if boxes else page.locator('div[data-testid="tweetTextarea_0"]').first
                    target_box.click()
                    page.wait_for_timeout(200)
                    target_box.fill(tweet_text)
                    page.wait_for_timeout(500)

                    if idx < len(thread_items) - 1:
                        add_btn = page.locator('button[data-testid="addButton"]').first
                        if add_btn.count() > 0:
                            add_btn.click(force=True)
                            page.wait_for_timeout(800)

                page.wait_for_timeout(1000)
                post_btn = page.locator('button[data-testid="tweetButton"]').first
                if post_btn.count() > 0:
                    post_btn.click(force=True)
                    page.wait_for_timeout(4000)
                else:
                    page.keyboard.press("Meta+Enter")
                    page.wait_for_timeout(3000)

                browser.close()
                return {"success": True, "platform": "twitter_thread", "count": len(thread_items)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def schedule_twitter_post(self, tweet_text: str, dt: datetime) -> Dict[str, Any]:
        """
        Twitter (X) rasmiy Web interfeysining 'Schedule' (Zamanlama) funksiyasi orqali
        tvitni to'g'ridan-to'g'ri Twitter serverlariga rejalashtiradi.
        Bu rejalashtirilgach, bot/kompyuter o'chiq bo'lsa ham Twitter o'zi chiqaradi!
        """
        self.clean_locks()
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = browser.new_page()
                page.goto("https://x.com/compose/post", timeout=25000)
                page.wait_for_timeout(2500)

                box = page.locator('div[data-testid="tweetTextarea_0"]').first
                if box.count() == 0:
                    box = page.locator('div[role="textbox"]').first
                box.click()
                box.fill(tweet_text)
                page.wait_for_timeout(500)

                sch_btn = page.locator('button[data-testid="scheduleOption"]').first
                if sch_btn.count() == 0:
                    browser.close()
                    return {"success": False, "error": "Schedule tugmasi topilmadi"}
                sch_btn.dispatch_event("click")

                page.locator('select').first.wait_for(state="visible", timeout=10000)
                selects = page.locator('select').all()
                if len(selects) < 6:
                    browser.close()
                    return {"success": False, "error": f"Schedule selectlari yetarli emas: {len(selects)}"}

                # Month (1-12)
                selects[0].select_option(value=str(dt.month))
                page.wait_for_timeout(80)

                # Day (1-31)
                selects[1].select_option(value=str(dt.day))
                page.wait_for_timeout(80)

                # Year
                selects[2].select_option(value=str(dt.year))
                page.wait_for_timeout(80)

                # Hour (1-12)
                hour_12 = dt.hour % 12
                if hour_12 == 0:
                    hour_12 = 12
                selects[3].select_option(value=str(hour_12))
                page.wait_for_timeout(80)

                # Minute (0-59)
                selects[4].select_option(value=str(dt.minute))
                page.wait_for_timeout(80)

                # AM/PM
                ampm = "pm" if dt.hour >= 12 else "am"
                selects[5].select_option(value=ampm)
                page.wait_for_timeout(200)

                # Confirm button
                confirm_btn = page.locator('button[data-testid="scheduledConfirmationPrimaryAction"]').first
                if confirm_btn.count() > 0:
                    confirm_btn.dispatch_event("click")
                    page.wait_for_timeout(1000)

                # Click Schedule button
                sched_btn = page.locator('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]').first
                if sched_btn.count() > 0:
                    sched_btn.dispatch_event("click")
                    page.wait_for_timeout(3000)
                else:
                    page.keyboard.press("Meta+Enter")
                    page.wait_for_timeout(3000)

                browser.close()
                return {"success": True, "platform": "twitter_native_schedule", "scheduled_time": dt.isoformat()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def schedule_twitter_posts_batch(self, items: List[Dict[str, Any]], on_each_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Schedules multiple tweets in a SINGLE persistent browser session.
        Faster, 100% reliable, eliminates multiple browser launch overhead.
        """
        if not items:
            return {"success": False, "error": "Bo'sh ro'yxat"}

        self.clean_locks()
        from playwright.sync_api import sync_playwright
        success_count = 0
        errors = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = browser.new_page()

                for idx, item in enumerate(items):
                    tw_id = item.get("id", f"tw_{idx}")
                    tweet_text = item.get("content", "")
                    dt = item.get("dt")
                    if not tweet_text or not dt:
                        continue

                    try:
                        page.goto("https://x.com/compose/post", timeout=25000)
                        page.wait_for_timeout(2500)

                        box = page.locator('div[data-testid="tweetTextarea_0"]').first
                        if box.count() == 0:
                            box = page.locator('div[role="textbox"]').first
                        box.click()
                        box.fill(tweet_text)
                        page.wait_for_timeout(400)

                        sch_btn = page.locator('button[data-testid="scheduleOption"]').first
                        if sch_btn.count() == 0:
                            errors.append(f"{tw_id}: Schedule tugmasi topilmadi")
                            continue

                        sch_btn.dispatch_event("click")
                        page.locator('select').first.wait_for(state="visible", timeout=10000)

                        selects = page.locator('select').all()
                        if len(selects) < 6:
                            errors.append(f"{tw_id}: Selectlar yetarli emas ({len(selects)})")
                            continue

                        # Month (1-12)
                        selects[0].select_option(value=str(dt.month))
                        page.wait_for_timeout(80)

                        # Day (1-31)
                        selects[1].select_option(value=str(dt.day))
                        page.wait_for_timeout(80)

                        # Year
                        selects[2].select_option(value=str(dt.year))
                        page.wait_for_timeout(80)

                        # Hour (1-12)
                        hour_12 = dt.hour % 12
                        if hour_12 == 0:
                            hour_12 = 12
                        selects[3].select_option(value=str(hour_12))
                        page.wait_for_timeout(80)

                        # Minute (0-59)
                        selects[4].select_option(value=str(dt.minute))
                        page.wait_for_timeout(80)

                        # AM/PM
                        ampm = "pm" if dt.hour >= 12 else "am"
                        selects[5].select_option(value=ampm)
                        page.wait_for_timeout(200)

                        # Confirm button
                        confirm_btn = page.locator('button[data-testid="scheduledConfirmationPrimaryAction"]').first
                        if confirm_btn.count() > 0:
                            confirm_btn.dispatch_event("click")
                            page.wait_for_timeout(1000)

                        # Click Schedule button
                        sched_btn = page.locator('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]').first
                        if sched_btn.count() > 0:
                            sched_btn.dispatch_event("click")
                            page.wait_for_timeout(2500)
                        else:
                            page.keyboard.press("Meta+Enter")
                            page.wait_for_timeout(2500)

                        success_count += 1
                        if on_each_callback:
                            try:
                                on_each_callback(item, True)
                            except Exception:
                                pass

                    except Exception as item_err:
                        errors.append(f"{tw_id}: {str(item_err)}")
                        if on_each_callback:
                            try:
                                on_each_callback(item, False)
                            except Exception:
                                pass

                browser.close()
                return {
                    "success": success_count > 0,
                    "scheduled_count": success_count,
                    "total": len(items),
                    "errors": errors
                }
        except Exception as e:
            return {"success": False, "error": str(e), "scheduled_count": success_count}

    def publish_instagram_web(self, image_path: str, caption: str) -> Dict[str, Any]:
        """Instagram Web orqali post chiqarish."""
        self.clean_locks()
        from playwright.sync_api import sync_playwright
        if not image_path or not os.path.exists(image_path):
            return {"success": False, "error": "Instagram faqat rasm qabul qiladi. 'Görsel Post Kartı' orqali chiqaring."}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = browser.new_page()
                page.goto("https://www.instagram.com/", timeout=30000)
                page.wait_for_timeout(4000)

                # 1. Click Create (+) button
                create_btn = page.locator('svg[aria-label="New post"], svg[aria-label="Yangi post"], svg[aria-label="Create"]').first
                if create_btn.count() == 0:
                    browser.close()
                    return {
                        "success": False,
                        "error": "Instagram hisobiga kirmagansiz. Terminalda 'python3 login_browser.py' deb login qiling."
                    }

                create_btn.click()
                page.wait_for_timeout(1500)

                # 2. Click 'Post' in the dropdown menu
                post_choice = page.get_by_text("Post", exact=True).first
                if post_choice.count() > 0:
                    post_choice.click()
                    page.wait_for_timeout(2000)

                # 3. Set file in upload input
                file_input = page.locator('input[type="file"]').first
                try:
                    file_input.wait_for(timeout=8000)
                except Exception:
                    pass

                if file_input.count() > 0:
                    file_input.set_input_files(image_path)
                    page.wait_for_timeout(3000)

                    # 4. Next button (Crop screen)
                    next_btn = page.get_by_role("button", name="Next")
                    if next_btn.count() == 0:
                        next_btn = page.get_by_text("Next")
                    if next_btn.count() == 0:
                        next_btn = page.get_by_text("Keyingisi")
                    if next_btn.count() > 0:
                        next_btn.first.click()
                        page.wait_for_timeout(2000)

                        # 5. Next button (Filter screen)
                        next_btn.first.click()
                        page.wait_for_timeout(2000)

                    # 6. Caption input
                    caption_box = page.locator('div[aria-label="Write a caption..."], div[aria-label="Izoh yozing..."], div[role="textbox"]').first
                    if caption_box.count() > 0:
                        caption_box.fill(caption)
                        page.wait_for_timeout(1000)

                    # 7. Share button
                    share_btn = page.get_by_role("button", name="Share")
                    if share_btn.count() == 0:
                        share_btn = page.get_by_text("Share")
                    if share_btn.count() == 0:
                        share_btn = page.get_by_text("Ulashish")
                    if share_btn.count() > 0:
                        share_btn.first.click()
                        page.wait_for_timeout(7000)

                    browser.close()
                    return {"success": True, "platform": "instagram_web"}

                browser.close()
                return {"success": False, "error": "Instagram yuklash oynasi ochilmadi."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def publish_facebook_web(self, text: str, image_path: str = None) -> Dict[str, Any]:
        """Facebook Web orqali post chiqarish."""
        self.clean_locks()
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_path,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = browser.new_page()
                page.goto("https://www.facebook.com/", timeout=30000)
                page.wait_for_timeout(4000)

                # Check if logged in
                post_trigger = page.locator('div[role="button"][aria-label*="mind"], div[role="button"][aria-label*="hayolingizda"], div[role="button"][aria-label*="fikr"]').first
                if post_trigger.count() == 0:
                    browser.close()
                    return {
                        "success": False,
                        "error": "Facebook hisobiga kirmagansiz. Terminalda 'python3 login_browser.py' deb login qiling."
                    }

                post_trigger.click()
                page.wait_for_timeout(2000)

                # Find post textbox in popup modal
                box = page.locator('div[role="textbox"][aria-label*="mind"], div[role="textbox"][aria-label*="hayolingizda"], div[role="textbox"]').first
                if box.count() > 0:
                    box.fill(text)
                    page.wait_for_timeout(1000)

                # Upload image if provided
                if image_path and os.path.exists(image_path):
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(image_path)
                        page.wait_for_timeout(3000)

                # Click post submit button
                post_btn = page.locator('div[aria-label="Post"], div[aria-label="Chiqarish"], div[aria-label="Ulashish"]').first
                if post_btn.count() > 0:
                    post_btn.click()
                    page.wait_for_timeout(6000)
                    browser.close()
                    return {"success": True, "platform": "facebook_web"}

                browser.close()
                return {"success": False, "error": "Facebook 'Post' tugmasi topilmadi."}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    bp = BrowserPublisher()
    print("Browser Publisher Initialized. Profile path:", bp.profile_path)
