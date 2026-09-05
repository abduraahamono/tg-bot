#!/usr/bin/env python3
"""
Arkadaş Consulting - Telegram Marketing & Post Agent Bot
Admin telefondan yoki kompyuterdan to'liq boshqarishi uchun:
1. 📝 Salt Metin Postlari (5 Evergreen Şablon + Maxsus Mavzu)
2. 🖼️ Görsel Post Kartalari (Q&A, Checklist, Mantiq, Qabul Tabriknomasi)
3. 🚀 Kanalga bitta tugma bilan chiqarish (@arkadasuz)
4. 📊 Lead CRM va 7 Kunlik Marketing Rejasi
"""

import os
import sys
import json
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CONFIG_FILE = BASE_DIR / "bot_config.json"
from bot.telegram_client import TelegramClient
from engine.content_generator import ContentGenerator
from engine.social_publisher import SocialPublisher
from engine.omnichannel_formatter import format_multichannel_pack
from engine.buffer_bridge import BufferBridge
from engine.browser_publisher import BrowserPublisher
from engine.twitter_scheduler import TwitterScheduler
from engine.telegram_scheduler import TelegramScheduler

def load_config():
    default_config = {
        "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", "7850828340:AAENUCBd_PG2U7Nzl2lx0RsE45h8t5i0vqg"),
        "admin_chat_id": os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "8021468690"),
        "channel_id": os.environ.get("TELEGRAM_CHANNEL_ID", "@arkadasuz")
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_config.update(saved)
        except Exception:
            pass
    return default_config

MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "🗓️ 1 Haftalik Reja & Takvim"}],
        [{"text": "🌐 Ilovalar Hubi (5 Ta Tarmoq)"}],
        [{"text": "📱 Telegram Posti"}, {"text": "🖼️ Görsel Post Kartı"}],
        [{"text": "💡 Maxsus Post Yozish"}, {"text": "🎓 Talabalar Yordamchisi"}],
        [{"text": "📊 Leadlar & CRM"}, {"text": "📋 Matnlarni Olish"}]
    ],
    "resize_keyboard": True
}

POSTS_CACHE_FILE = BASE_DIR / "brain_data" / "pending_posts.json"

class AdminApprovalBot:
    def __init__(self):
        self.config = load_config()
        self.client = TelegramClient(self.config.get("bot_token"))
        self.generator = ContentGenerator()
        self.publisher = SocialPublisher()
        self.buffer_bridge = BufferBridge()
        self.browser_pub = BrowserPublisher()
        self.scheduler = TwitterScheduler()
        self.tg_scheduler = TelegramScheduler()
        self.pending_posts = self._load_pending_posts()
        self.admin_states = {}   # chat_id -> state string

        from bot.student_bot import StudentAssistantBot
        self.student_bot = StudentAssistantBot()
        self._start_scheduler_daemon()

    def _start_scheduler_daemon(self):
        def _loop():
            while True:
                try:
                    admin_id = self.config.get("admin_chat_id")
                    self.scheduler.check_and_publish_due(
                        browser_pub=self.browser_pub,
                        notify_cb=lambda msg: self.client.send_message(admin_id, msg) if admin_id else None
                    )
                    self.tg_scheduler.check_and_publish_due(
                        tg_client=self.client,
                        channel_id=self.config.get("channel_id", "@arkadasuz"),
                        notify_cb=lambda msg: self.client.send_message(admin_id, msg) if admin_id else None
                    )
                except Exception as e:
                    print(f"[Scheduler Loop Exception] {e}")
                time.sleep(30)

        threading.Thread(target=_loop, daemon=True).start()

    def _load_pending_posts(self) -> dict:
        if POSTS_CACHE_FILE.exists():
            try:
                with open(POSTS_CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_pending_posts(self):
        try:
            with open(POSTS_CACHE_FILE, "w", encoding="utf-8") as f:
                keys = list(self.pending_posts.keys())[-500:]
                trimmed = {k: self.pending_posts[k] for k in keys}
                json.dump(trimmed, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AdminBot] Error saving pending posts: {e}")

    def get_or_recover_post(self, pid: str, cb: dict) -> dict:
        """
        Retrieves post from memory/disk cache, or auto-recovers directly
        from the Telegram message body so 'Taslaq eskirgan' never occurs.
        """
        p = self.pending_posts.get(pid)
        if p:
            return p

        # Recover from Telegram Message object
        msg = cb.get("message", {})
        txt = msg.get("caption") or msg.get("text") or ""
        has_photo = bool(msg.get("photo"))
        has_video = bool(msg.get("video"))

        media_path = None
        if has_photo:
            output_dir = BASE_DIR / "output"
            recent_imgs = sorted(output_dir.glob("*.png"), key=os.path.getmtime, reverse=True)
            if recent_imgs:
                media_path = str(recent_imgs[0])

        recovered = {
            "content": txt,
            "caption": txt,
            "media_type": "image" if has_photo else ("video" if has_video else "text"),
            "media_path": media_path,
            "type": "twitter" if len(txt) <= 280 else "recovered",
            "target_platform": "twitter" if len(txt) <= 280 else "telegram"
        }
        self.pending_posts[pid] = recovered
        self._save_pending_posts()
        return recovered

    def send_main_menu(self, chat_id: str, welcome: bool = False):
        msg = (
            "👑 <b>ARKADAŞ CONSULTING — POST & MARKETING AGENT</b> 🇹🇷\n\n"
            "Quyidagi tugmalar orqali barcha ijtimoiy tarmoqlar uchun <b>post, tvit, rasm va video</b> tayyorlashingiz mumkin:\n\n"
            "• <b>🌐 Ilovalar Hubi:</b> Telegram, Twitter, Instagram, Facebook, YouTube\n"
            "• <b>📱 Telegram Posti:</b> @arkadasuz uchun tayyor matn va shablonlar\n"
            "• <b>🖼️ Görsel Post Kartı:</b> Ultra sifatli Q&A, Checklist va Tabriknoma kartalari\n"
            "• <b>💡 Maxsus Post:</b> Istalgan mavzuni yozasiz, AI beyni yozib beradi\n"
            "• <b>🚀 To'g'ridan-to'g'ri E'lon:</b> Telegram (@arkadasuz), Twitter va Facebook ga bitta tugma bilan chiqarish!"
        ) if welcome else "Kerakli bo'limni tanlang:"
        self.client.send_message(chat_id, msg, reply_markup=MAIN_KEYBOARD)

    def prompt_apps_hub(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "📱 Telegram (@arkadasuz)", "callback_data": "app_menu_tg"}],
                [{"text": "🐦 Twitter (X)", "callback_data": "app_menu_tw"}, {"text": "📸 Instagram", "callback_data": "app_menu_ig"}],
                [{"text": "📘 Facebook", "callback_data": "app_menu_fb"}, {"text": "🎥 YouTube (Shorts)", "callback_data": "app_menu_yt"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "🌐 <b>Qaysi platforma uchun kontent tayyorlaymiz?</b>\n\n"
            "• 📱 <b>Telegram:</b> @arkadasuz kanali uchun to'liq post, rasm va video\n"
            "• 🐦 <b>Twitter (X):</b> 280 belgili aniq mikro-tvit, rasm yoki video\n"
            "• 📸 <b>Instagram:</b> Rasm, karusel yoki Reels video\n"
            "• 📘 <b>Facebook:</b> Storytelling va savol-javob posti\n"
            "• 🎥 <b>YouTube:</b> 9:16 Shorts video va Hamjamiyat (Community) posti",
            reply_markup=kb
        )

    def prompt_twitter_menu(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "🗓️ 1 Haftalik Rejani Tuzish (21 Tvit + Flood)", "callback_data": "app_tw_plan_week"}],
                [{"text": "📋 Rejadagi Tvitlar & Holat", "callback_data": "app_tw_view_plan"}, {"text": "🛑 Rejani Bekor Qilish", "callback_data": "app_tw_cancel_plan"}],
                [{"text": "📝 Oddiy Tvit Matni (280 belgi)", "callback_data": "app_tw_text"}],
                [{"text": "🖼️ Rasm + Tvit Matni", "callback_data": "app_tw_photo"}, {"text": "🎬 Video + Tvit Matni", "callback_data": "app_tw_video"}],
                [{"text": "⬅️ Orqaga", "callback_data": "app_menu_main"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "🐦 <b>Twitter (X) Boshqaruv Markazi:</b>\n\n"
            "• <b>🗓️ 1 Haftalik Avtomatik Reja:</b> 7 kunlik (kuniga 3 ta) takrorlanmas 21 ta tvit + Chorshanba kungi 6 qismli Mega Flood zanjiri.\n"
            "• <b>🛡️ Anti-Repetition:</b> Har hafta mutlaqo yangi mavzular va turlicha yondashuvlar ishlatiladi.\n"
            "• <b>⏰ Avtomatik Vaqt:</b> Soat 10:00, 14:00 va 20:00 da bot o'zi fonda joylaydi.\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=kb
        )

    def show_telegram_calendar(self, chat_id: str):
        plan = self.tg_scheduler.data
        posts = plan.get("posts", [])
        if not posts:
            self.client.send_message(
                chat_id,
                "⚠️ <b>Hozircha faol 1 haftalik reja topilmadi.</b>\n"
                "Quyidagi tugmani bosib 14 ta ekspert postdan iborat yangi haftalik rejani tuzishingiz mumkin:",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "🗓️ 1 Haftalik Rejani Tuzish (14 Post)", "callback_data": "app_tg_plan_week"}]
                    ]
                }
            )
            return

        days_seen = []
        day_btns = []
        current_row = []
        for idx, p in enumerate(posts):
            d_name = p.get("day_name", "")
            d_idx = p.get("day_index", 1) - 1
            if d_name not in days_seen:
                days_seen.append(d_name)
                d_date = p.get("date_str", "")[5:]
                st_icon = "✅" if p.get("status") == "posted" else "⏳"
                btn_text = f"🗓️ {d_name} ({d_date}) {st_icon}"
                current_row.append({"text": btn_text, "callback_data": f"app_tg_day_{d_idx}"})
                if len(current_row) == 2:
                    day_btns.append(current_row)
                    current_row = []
        if current_row:
            day_btns.append(current_row)

        summ = self.tg_scheduler.get_summary()
        st_str = "🟢 FAOL (Bulut avtomatik yoqilgan)" if summ["active"] else "⚪️ KUTILMOQDA"

        cal_msg = (
            f"🗓️ <b>1 HAFTALIK TELEGRAM POSTLAR TAKVIMI</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>Holat:</b> {st_str}\n"
            f"• <b>Davr:</b> {summ['start_date']} — {summ['end_date']}\n"
            f"• <b>Kanalga joylangan:</b> {summ['posted']} ta ✅\n"
            f"• <b>Navbatda kutilayotgan:</b> {summ['pending']} ta ⏳\n\n"
            f"👇 <b>Batafsil ko'rish va boshqarish uchun kunni tanlang:</b>"
        )
        kb = {
            "inline_keyboard": day_btns + [
                [{"text": "🔄 Yangi 1 Haftalik Reja Tuzish", "callback_data": "app_tg_plan_week"}],
                [{"text": "🛑 Rejani Bekor Qilish", "callback_data": "app_tg_cancel_plan"}],
                [{"text": "⬅️ Telegram Menyusiga", "callback_data": "app_menu_tg"}]
            ]
        }
        self.client.send_message(chat_id, cal_msg, reply_markup=kb)

    def prompt_telegram_menu(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "🗓️ 1 Haftalik Rejani Tuzish (14 Ekspert Post)", "callback_data": "app_tg_plan_week"}],
                [{"text": "📋 Rejadagi Telegram Postlar & Holat", "callback_data": "app_tg_view_plan"},
                 {"text": "🛑 Rejani Bekor Qilish", "callback_data": "app_tg_cancel_plan"}],
                [{"text": "📝 Faqat Matn Posti (~600 belgi)", "callback_data": "app_tg_text"}],
                [{"text": "🖼️ Sarlavhali Dizayn Kartasi (Rasm + Matn)", "callback_data": "app_tg_photo_text"}],
                [{"text": "🖼️ Faqat Rasm (Matnsiz)", "callback_data": "app_tg_photo_only"}],
                [{"text": "🎬 Video + Matn", "callback_data": "app_tg_video"}],
                [{"text": "⬅️ Orqaga", "callback_data": "app_menu_main"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "📱 <b>Telegram (@arkadasuz) Boshqaruv Markazi:</b>\n\n"
            "• 🗓️ <b>1 Haftalik Ekspert Reja:</b> O'zbekistonlik abituriyentlar va ota-onalar uchun maxsus 14 ta chuqur tahliliy, huquqiy va ishonchli post.\n"
            "• ⏰ <b>Optimal Vaqtlar:</b> O'zbekistonda eng faol vaqtlar bo'lgan <b>13:00 (Tushlik)</b> va <b>19:30 (Kechki oilaviy vaqt)</b> da kanalda e'lon qilinadi.\n"
            "• 🛡️ <b>Anti-Repetition:</b> Har haftada mutlaqo yangi mavzular, hikoyalar va maslahatlar.\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=kb
        )

    def prompt_instagram_menu(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "🖼️ Rasm + Caption", "callback_data": "app_ig_photo"}],
                [{"text": "🎬 Reels Video", "callback_data": "app_ig_video"}],
                [{"text": "⬅️ Orqaga", "callback_data": "app_menu_main"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "📸 <b>Instagram uchun formatni tanlang:</b>",
            reply_markup=kb
        )

    def prompt_facebook_menu(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "📝 Faqat Facebook Posti (Hikoya & Savol)", "callback_data": "app_fb_text"}],
                [{"text": "🖼️ Rasm + Facebook Matni", "callback_data": "app_fb_photo"}],
                [{"text": "🎬 Video + Facebook Matni", "callback_data": "app_fb_video"}],
                [{"text": "⬅️ Orqaga", "callback_data": "app_menu_main"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "📘 <b>Facebook uchun formatni tanlang:</b>\n"
            "<i>(Facebook algoritmi uchun storytelling va o'quvchini izoh yozishga chorlovchi savol bilan tayyorlanadi)</i>",
            reply_markup=kb
        )

    def prompt_youtube_menu(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "🎬 YouTube Shorts (Video + Sarlavha/Teglar)", "callback_data": "app_yt_shorts"}],
                [{"text": "📝 Hamjamiyat (Community) Posti", "callback_data": "app_yt_community"}],
                [{"text": "⬅️ Orqaga", "callback_data": "app_menu_main"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "🎥 <b>YouTube uchun formatni tanlang:</b>\n"
            "<i>(YouTube algoritmi va SEO uchun optimallashtirilgan sarlavha va teglar bilan tayyorlanadi)</i>",
            reply_markup=kb
        )

    def prompt_text_templates(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "📚 1. Bilgilendirici Post (Bologna, Nostrifikatsiya)", "callback_data": "text_edu"}],
                [{"text": "💼 2. Reklam Posti (Oldindan To'lovsiz, 99% Qabul)", "callback_data": "text_promo"}],
                [{"text": "📢 3. Yangilik Posti (Kvota & Muddatlar)", "callback_data": "text_news"}],
                [{"text": "📋 4. Xizmatlar Ro'yxati (Evergreen A)", "callback_data": "tpl_A"}],
                [{"text": "🗺️ 5. 4 Qadamli Yo'l Xaritasi (Evergreen D)", "callback_data": "tpl_D"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "📝 <b>Qaysi turdagi matn postini tayyorlaymiz?</b>\n"
            "<i>(Mavzular aniq va ishonchli, yolg'on va'dalarsiz, ~600 belgi):</i>\n\n"
            "• 📚 <b>Bilgilendirici:</b> Bologna tizimi, nostrifikatsiya, attestat bilan imtihonsiz qabul\n"
            "• 💼 <b>Reklam:</b> Oldindan to'lovsiz xizmat, 99% muvaffaqiyat, rasmiy shartnoma\n"
            "• 📢 <b>Yangilik:</b> Rasmiy qabul kvotalari, Tibbiyot va IT bo'yicha muddatlar",
            reply_markup=kb
        )

    def prompt_card_templates(self, chat_id: str):
        kb = {
            "inline_keyboard": [
                [{"text": "❓ 1. Q&A Savol-Javob Kartasi", "callback_data": "card_qa"}],
                [{"text": "📋 2. Xizmatlar Checklist Kartasi", "callback_data": "card_chk"}],
                [{"text": "🧩 3. Qiziqarli Topishmoq Kartasi", "callback_data": "card_riddle"}],
                [{"text": "🎓 4. Talaba Qabul Tabriknomasi", "callback_data": "card_acc"}],
                [{"text": "🖼️ Faqat Rasm (Matnsiz)", "callback_data": "app_tg_photo_only"}]
            ]
        }
        self.client.send_message(
            chat_id,
            "🖼️ <b>Qaysi turdagi dizayn kartasini tayyorlaymiz?</b>\n"
            "<i>(Post ostidagi tugmalar orqali matnni alohida, rasmni alohida yoki ikkalasini birga o'zgartirishingiz mumkin):</i>",
            reply_markup=kb
        )

    def send_post_preview(self, chat_id: str, post_data: dict):
        post_id = f"p_{int(time.time()*1000)%1000000}"
        self.pending_posts[post_id] = post_data
        self._save_pending_posts()

        is_image = post_data.get("media_type") == "image"
        is_video = post_data.get("media_type") == "video"
        target_plat = post_data.get("target_platform", "")
        p_type = post_data.get("type", "")
        is_twitter = p_type == "twitter" or target_plat == "twitter"
        is_fb = p_type == "facebook" or target_plat == "facebook"
        is_yt = p_type == "youtube" or target_plat == "youtube"
        has_caption = bool(post_data.get("caption", "").strip()) if (is_image or is_video) else False

        kb_rows = []

        if is_image:
            if has_caption:
                kb_rows.append([
                    {"text": "✏️ Matnni almashtir", "callback_data": f"modtext_{post_id}"},
                    {"text": "🎨 Rasmni almashtir", "callback_data": f"modimg_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "🔄 Ikkalasini almashtir", "callback_data": f"modboth_{post_id}"}
                ])
            else:
                kb_rows.append([
                    {"text": "🎨 Rasmni almashtir", "callback_data": f"modimg_{post_id}"},
                    {"text": "✏️ Matn qo'shish", "callback_data": f"modtext_{post_id}"}
                ])

            # Platform Action Buttons
            if is_twitter:
                kb_rows.append([
                    {"text": "🐦 Twitter'ga joylash", "callback_data": f"twpost_{post_id}"},
                    {"text": "🚀 Telegram Kanalga", "callback_data": f"pub_{post_id}"}
                ])
            elif is_fb:
                kb_rows.append([
                    {"text": "📘 Facebook'ga joylash", "callback_data": f"fbpost_{post_id}"},
                    {"text": "🚀 Telegram Kanalga", "callback_data": f"pub_{post_id}"}
                ])
            elif is_yt:
                kb_rows.append([
                    {"text": "🎥 YouTube'ga chiqarish", "callback_data": f"ytpost_{post_id}"},
                    {"text": "🚀 Telegram Kanalga", "callback_data": f"pub_{post_id}"}
                ])
            else:
                kb_rows.append([
                    {"text": "🚀 Telegram (@arkadasuz)", "callback_data": f"pub_{post_id}"},
                    {"text": "🐦 Twitter'ga joylash", "callback_data": f"twpost_{post_id}"}
                ])

            kb_rows.append([
                {"text": "📋 Matnlarni Olish", "callback_data": f"copy_{post_id}"},
                {"text": "🤖 Brauzer Bilan", "callback_data": f"web_{post_id}"}
            ])

        elif is_video:
            kb_rows.append([
                {"text": "✏️ Matnni almashtir", "callback_data": f"modtext_{post_id}"},
                {"text": "🎬 Videoni almashtir", "callback_data": f"modvideo_{post_id}"}
            ])
            if is_yt:
                kb_rows.append([
                    {"text": "🎥 YouTube Shorts ga yuklash", "callback_data": f"ytpost_{post_id}"},
                    {"text": "🚀 Telegram Kanalga", "callback_data": f"pub_{post_id}"}
                ])
            elif is_fb:
                kb_rows.append([
                    {"text": "📘 Facebook'ga joylash", "callback_data": f"fbpost_{post_id}"},
                    {"text": "🚀 Telegram Kanalga", "callback_data": f"pub_{post_id}"}
                ])
            elif is_twitter:
                kb_rows.append([
                    {"text": "🐦 Twitter'ga tvitlash", "callback_data": f"twpost_{post_id}"},
                    {"text": "🚀 Telegram Kanalga", "callback_data": f"pub_{post_id}"}
                ])
            else:
                kb_rows.append([
                    {"text": "🚀 Telegram (@arkadasuz)", "callback_data": f"pub_{post_id}"},
                    {"text": "🐦 Twitter'ga tvitlash", "callback_data": f"twpost_{post_id}"}
                ])
            kb_rows.append([
                {"text": "📋 Matnlarni Olish", "callback_data": f"copy_{post_id}"}
            ])

        else: # Text post
            if is_twitter:
                kb_rows.append([
                    {"text": "🔄 Tvit Matnini yangilash", "callback_data": f"modtext_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "🐦 Twitter'ga tvitlash", "callback_data": f"twpost_{post_id}"},
                    {"text": "🚀 Telegram (@arkadasuz)", "callback_data": f"pub_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "📋 Nusxa olish", "callback_data": f"copy_{post_id}"}
                ])
            elif is_fb:
                kb_rows.append([
                    {"text": "🔄 Facebook Matnini yangilash", "callback_data": f"modtext_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "📘 Facebook'ga joylash", "callback_data": f"fbpost_{post_id}"},
                    {"text": "🚀 Telegram (@arkadasuz)", "callback_data": f"pub_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "📋 Nusxa olish", "callback_data": f"copy_{post_id}"}
                ])
            elif is_yt:
                kb_rows.append([
                    {"text": "🔄 YouTube Tavsifini yangilash", "callback_data": f"modtext_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "🎥 YouTube Community (API)", "callback_data": f"ytpost_{post_id}"},
                    {"text": "🚀 Telegram (@arkadasuz)", "callback_data": f"pub_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "📋 Nusxa olish", "callback_data": f"copy_{post_id}"}
                ])
            else:
                p_type = post_data.get("type", "")
                if p_type in ["educational", "promotional", "news"]:
                    regen_cb = f"regen_text_{p_type}"
                else:
                    regen_cb = f"regen_tpl_{post_data.get('tpl_key', 'A')}"

                kb_rows.append([
                    {"text": "🔄 Yangi Matn (Boshqa Mavzu)", "callback_data": regen_cb}
                ])
                kb_rows.append([
                    {"text": "🚀 Telegram (@arkadasuz)", "callback_data": f"pub_{post_id}"},
                    {"text": "🐦 Twitter'ga tvitlash", "callback_data": f"twpost_{post_id}"}
                ])
                kb_rows.append([
                    {"text": "📚 Bilgilendirici", "callback_data": "text_edu"},
                    {"text": "💼 Reklam", "callback_data": "text_promo"},
                    {"text": "📢 Yangilik", "callback_data": "text_news"}
                ])
                kb_rows.append([
                    {"text": "📋 Matnlarni Olish", "callback_data": f"copy_{post_id}"},
                    {"text": "🤖 Brauzer Bilan", "callback_data": f"web_{post_id}"}
                ])

        kb = {"inline_keyboard": kb_rows}

        if is_image:
            self.client.send_photo(
                chat_id,
                post_data["media_path"],
                caption=post_data.get("caption", ""),
                reply_markup=kb
            )
        elif is_video:
            self.client.send_video(
                chat_id,
                post_data["media_path"],
                caption=post_data.get("caption", ""),
                reply_markup=kb
            )
        else:
            self.client.send_message(
                chat_id,
                post_data["content"],
                reply_markup=kb
            )

    def publish_to_channel(self, post_data: dict) -> bool:
        channel = self.config.get("channel_id", "@arkadasuz")
        if post_data.get("media_type") == "video":
            res = self.client.send_video(channel, post_data["media_path"], caption=post_data.get("caption", ""))
        elif post_data.get("media_type") == "image":
            res = self.client.send_photo(channel, post_data["media_path"], caption=post_data.get("caption", ""))
        else:
            res = self.client.send_message(channel, post_data["content"])
        return res.get("ok", False)

    def run(self):
        if not self.client.is_configured():
            print("[ERROR] Telegram Bot Token kiritilmagan!")
            return

        print(f"[OK] Arkadaş Post & Marketing Bot ishga tushdi! (@uzbekfootybot)")
        print(f"[INFO] Admin ID: {self.config.get('admin_chat_id')} | Kanal: {self.config.get('channel_id')}")
        offset = 0

        # Send greeting to admin on startup
        admin_id = self.config.get("admin_chat_id")
        if admin_id:
            try:
                self.send_main_menu(admin_id, welcome=True)
            except Exception:
                pass

        while True:
            try:
                updates = self.client.get_updates(offset=offset, timeout=20)
                for u in updates:
                    offset = u["update_id"] + 1

                    # 1. Inline Button Callback Queries
                    if "callback_query" in u:
                        cb = u["callback_query"]
                        cb_id = cb["id"]
                        data = cb.get("data", "")
                        from_user = str(cb["from"]["id"])

                        # 1. Publish to Telegram channel
                        if data.startswith("pub_"):
                            pid = data.replace("pub_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                success = self.publish_to_channel(p)
                                if success:
                                    self.client.answer_callback_query(cb_id, "🎉 Post kanalda e'lon qilindi!")
                                    self.client.send_message(from_user, "✅ <b>Muvaffaqiyatli!</b> Post @arkadasuz kanaliga joylashtirildi.")
                                else:
                                    self.client.answer_callback_query(cb_id, "❌ Xatolik yuz berdi. Bot kanalda admin ekanligini tekshiring.")
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # 2. Copy formatted text for Instagram, Twitter, TikTok, FB (Adım 1)
                        elif data.startswith("copy_"):
                            pid = data.replace("copy_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "📋 Matnlar tayyorlandi!")
                                pack = format_multichannel_pack(p)
                                copy_msg = (
                                    "📱 <b>BARCHA PLATFORMALAR UCHUN TAYYOR MATNLAR:</b>\n"
                                    "<i>(Matn ustiga bitta bosish bilan avtomatik nusxalanadi)</i>\n\n"
                                    f"📸 <b>INSTAGRAM & FACEBOOK (Bosib nusxalang):</b>\n"
                                    f"<code>{pack['instagram']}</code>\n\n"
                                    f"🐦 <b>TWITTER / X (280 belgi):</b>\n"
                                    f"<code>{pack['twitter']}</code>\n\n"
                                    f"🎵 <b>TIKTOK / REELS:</b>\n"
                                    f"<code>{pack['tiktok']}</code>\n"
                                    f"<i>{pack['tiktok_music']}</i>"
                                )
                                self.client.send_message(from_user, copy_msg)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # 3. Publish via Buffer API Bridge (Adım 2)
                        elif data.startswith("buf_"):
                            pid = data.replace("buf_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                if not self.buffer_bridge.is_configured():
                                    self.client.answer_callback_query(cb_id, "ℹ️ Buffer sozlanmagan. Yo'riqnoma yuborildi.")
                                    self.client.send_message(from_user, self.buffer_bridge.get_setup_guide())
                                else:
                                    self.client.answer_callback_query(cb_id, "⏳ Buffer orqali yuborilmoqda...")
                                    is_card = p.get("media_type") == "image"
                                    txt = p.get("caption") if is_card else p.get("content", "")
                                    res = self.buffer_bridge.publish_post(txt)
                                    if res.get("success"):
                                        self.client.send_message(from_user, "✅ <b>Muvaffaqiyatli!</b> Post Buffer orqali Instagram, Facebook va TikTok ga chiqarildi!")
                                    else:
                                        self.client.send_message(from_user, f"❌ Buffer xatoligi: {res.get('error')}")
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # 4. Publish via Headless Browser Automation (Adım 3)
                        elif data.startswith("web_"):
                            pid = data.replace("web_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "🤖 Brauzer orqali yuklanmoqda...")
                                is_card = p.get("media_type") == "image"
                                media_path = p.get("media_path")
                                txt = p.get("caption") if is_card else p.get("content", "")

                                res_tw = self.browser_pub.publish_twitter_web(txt[:270], media_path)
                                res_ig = self.browser_pub.publish_instagram_web(media_path, txt) if is_card else {"success": False, "error": "Faqat rasm postlar"}

                                rep = "🤖 <b>BRAUZER BILAN YUKLASH NATIJALARI (ADIM 3):</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
                                rep += f"• 🐦 Twitter: {'✅ E\'lon qilindi' if res_tw.get('success') else '⚠️ ' + str(res_tw.get('error'))}\n"
                                rep += f"• 📸 Instagram: {'✅ E\'lon qilindi' if res_ig.get('success') else '⚠️ ' + str(res_ig.get('error'))}\n\n"
                                rep += "💡 <i>Eslatma: Agar 'login qilinmagan' xatosi chiqsa, terminalda bir marta tizimga kirib olish kerak.</i>"
                                self.client.send_message(from_user, rep)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # Publish to all 6 Omnichannel platforms
                        elif data.startswith("omni_"):
                            pid = data.replace("omni_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "⏳ Barcha 6 ta tarmoqqa yuborilmoqda...")
                                res = self.publisher.broadcast_all(p)
                                report = "🌐 <b>TARMOQLARGA CHIQARISH HISOBOTI:</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
                                icons = {"telegram": "📱", "instagram": "📸", "facebook": "👥", "twitter": "🐦", "youtube": "🎥", "tiktok": "🎵"}
                                for plat, r in res.items():
                                    ico = icons.get(plat, "🌐")
                                    status_str = "✅ E'lon qilindi!" if r.get("success") else f"⏳ {r.get('error', 'Kutilmoqda')}"
                                    report += f"• {ico} <b>{plat.upper()}:</b> {status_str}\n"
                                report += "━━━━━━━━━━━━━━━━━━━━━━\n💡 <i>Platformalarni faollashtirish uchun 'social_credentials.json' fayliga API kalitlarini kiritish kifoya.</i>"
                                self.client.send_message(from_user, report)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # Generate Categorized Text Post (Bilgilendirici, Reklam, Haber)
                        elif data.startswith("text_") or data.startswith("regen_text_"):
                            t_sub = data.replace("regen_text_", "").replace("text_", "")
                            self.client.answer_callback_query(cb_id, "⏳ Professional post yozilmoqda...")
                            if t_sub in ["edu", "educational"]:
                                post = self.generator.generate_educational_post()
                            elif t_sub in ["promo", "promotional"]:
                                post = self.generator.generate_promotional_post()
                            else:
                                post = self.generator.generate_news_post()
                            self.send_post_preview(from_user, post)

                        # Generate Evergreen Text Template
                        elif data.startswith("tpl_") or data.startswith("regen_tpl_"):
                            t_key = data.split("_")[-1]
                            self.client.answer_callback_query(cb_id, f"⏳ Şablon {t_key} yozilmoqda...")
                            post = self.generator.generate_evergreen_post(t_key)
                            post["tpl_key"] = t_key
                            post["media_type"] = "text"
                            self.send_post_preview(from_user, post)

                        # Generate Visual Card
                        elif data.startswith("card_") or data.startswith("regen_card_"):
                            ctype = data.split("_")[-1]
                            self.client.answer_callback_query(cb_id, "⏳ Karta dizayni tayyorlanmoqda...")
                            if ctype == "qa":
                                p = self.generator.generate_qa_post()
                            elif ctype == "chk":
                                p = self.generator.generate_checklist_post()
                            elif ctype == "riddle":
                                p = self.generator.generate_riddle_post()
                            else: # acc
                                p = self.generator.generate_acceptance_post()
                            p["card_type"] = ctype
                            self.send_post_preview(from_user, p)

                        # Apps Hub & Platform Menus
                        elif data == "app_menu_main":
                            self.client.answer_callback_query(cb_id, "")
                            self.prompt_apps_hub(from_user)

                        elif data == "app_menu_tw":
                            self.client.answer_callback_query(cb_id, "")
                            self.prompt_twitter_menu(from_user)

                        elif data == "app_menu_tg":
                            self.client.answer_callback_query(cb_id, "")
                            self.prompt_telegram_menu(from_user)

                        elif data == "app_menu_ig":
                            self.client.answer_callback_query(cb_id, "")
                            self.prompt_instagram_menu(from_user)

                        elif data == "app_menu_fb":
                            self.client.answer_callback_query(cb_id, "")
                            self.prompt_facebook_menu(from_user)

                        elif data == "app_menu_yt":
                            self.client.answer_callback_query(cb_id, "")
                            self.prompt_youtube_menu(from_user)

                        # 1 Haftalik Ekspert Telegram Rejasi (@arkadasuz)
                        elif data == "app_tg_plan_week":
                            self.client.answer_callback_query(cb_id, "⏳ 1 haftalik Telegram rejasi tuzilmoqda...")
                            self.client.send_message(
                                from_user,
                                "⏳ <b>AI 1 haftalik ekspert Telegram rejasini tayyorlamoqda...</b>\n"
                                "<i>O'zbekiston yoshlari va ota-onalari uchun 14 ta chuqur tahliliy post tayyorlanmoqda, kuting...</i>"
                            )
                            plan = self.generator.generate_weekly_telegram_plan()
                            self.tg_scheduler.save_weekly_plan(plan)

                            posts = plan.get("posts", [])
                            # Build interactive calendar grid
                            days_seen = []
                            day_btns = []
                            current_row = []
                            for idx, p in enumerate(posts):
                                d_name = p.get("day_name", "")
                                d_idx = p.get("day_index", 1) - 1
                                if d_name not in days_seen:
                                    days_seen.append(d_name)
                                    d_date = p.get("date_str", "")[5:]  # MM-DD
                                    btn_text = f"🗓️ {d_name} ({d_date})"
                                    current_row.append({"text": btn_text, "callback_data": f"app_tg_day_{d_idx}"})
                                    if len(current_row) == 2:
                                        day_btns.append(current_row)
                                        current_row = []
                            if current_row:
                                day_btns.append(current_row)

                            cal_msg = (
                                f"🗓️ <b>1 HAFTALIK TELEGRAM POSTLAR TAKVIMI</b>\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"📅 <b>Davr:</b> {plan.get('start_date')} — {plan.get('end_date')}\n"
                                f"📊 <b>Jami:</b> 14 ta ekspert post (Kuniga 2 ta: 13:00 va 19:30)\n"
                                f"📍 <b>Kanal:</b> @arkadasuz\n"
                                f"🛡️ <b>Mavzular:</b> 100% yangi va takrorlanmas!\n\n"
                                f"👇 <b>Batafsil ko'rish uchun quyidagi kunlardan birini bosing:</b>"
                            )

                            kb = {
                                "inline_keyboard": day_btns + [
                                    [{"text": "📢 Telegram Kanaliga Avtomatik Joylash (Taymerni Yoqish)", "callback_data": "app_tg_confirm_plan"}],
                                    [{"text": "🔄 Yangi Reja Tuzish", "callback_data": "app_tg_plan_week"},
                                     {"text": "⬅️ Telegram Menyusiga", "callback_data": "app_menu_tg"}]
                                ]
                            }
                            self.client.send_message(from_user, cal_msg, reply_markup=kb)

                        elif data == "app_tg_confirm_plan":
                            self.tg_scheduler.data["active"] = True
                            self.tg_scheduler._save()
                            self.client.answer_callback_query(cb_id, "🎉 Reja faollashtirildi!")
                            self.client.send_message(
                                from_user,
                                "🚀 <b>1 HAFTALIK TELEGRAM KANAL REJASI ISHGA TUSHDI!</b>\n\n"
                                "• Bot har kuni <b>13:00 va 19:30</b> da @arkadasuz kanaliga yangi postlarni avtomatik chiqaradi.\n"
                                "• Har bir post chiqqanda sizga Telegramda hisobot keladi.\n\n"
                                "<i>Sizdan hech qanday qo'shimcha harakat talab qilinmaydi!</i>",
                                reply_markup={"inline_keyboard": [[{"text": "🗓️ Takvimni Ko'rish", "callback_data": "app_tg_view_plan"}]]}
                            )

                        elif data == "app_tg_view_plan":
                            self.client.answer_callback_query(cb_id, "🗓️ Takvim ochilmoqda...")
                            self.show_telegram_calendar(from_user)

                        elif data.startswith("app_tg_day_"):
                            d_idx = int(data.replace("app_tg_day_", ""))
                            posts = self.tg_scheduler.get_all_posts()
                            day_posts = [p for p in posts if p.get("day_index") == d_idx + 1]
                            if not day_posts:
                                self.client.answer_callback_query(cb_id, "⚠️ Bu kun uchun post topilmadi")
                            else:
                                self.client.answer_callback_query(cb_id, "")
                                d_name = day_posts[0].get("day_name", "")
                                d_date = day_posts[0].get("date_str", "")
                                p1 = day_posts[0]
                                p2 = day_posts[1] if len(day_posts) > 1 else None

                                p1_st = "✅ Chiqarilgan" if p1.get("status") == "posted" else "⏳ Kutilmoqda"
                                msg = (
                                    f"📅 <b>{d_name.upper()} ({d_date}) REJASI</b>\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    f"☀️ <b>13:00 [Tushlik Posti]</b> ({p1.get('cat_tag')})\n"
                                    f"📌 <i>{p1.get('topic')}</i>\n"
                                    f"Holat: {p1_st}\n\n"
                                )
                                if p2:
                                    p2_st = "✅ Chiqarilgan" if p2.get("status") == "posted" else "⏳ Kutilmoqda"
                                    msg += (
                                        f"🌆 <b>19:30 [Kechki Post]</b> ({p2.get('cat_tag')})\n"
                                        f"📌 <i>{p2.get('topic')}</i>\n"
                                        f"Holat: {p2_st}\n\n"
                                    )
                                msg += "👇 <b>Post matnini to'liq ko'rish va boshqarish uchun bosing:</b>"

                                p1_idx = posts.index(p1)
                                p2_idx = posts.index(p2) if p2 else p1_idx

                                day_kb = [
                                    [{"text": "☀️ 13:00 Postini Ko'rish (Tushlik)", "callback_data": f"app_tg_view_post_{p1_idx}"}]
                                ]
                                if p2:
                                    day_kb.append([{"text": "🌆 19:30 Postini Ko'rish (Kechki)", "callback_data": f"app_tg_view_post_{p2_idx}"}])
                                day_kb.append([{"text": "🗓️ Barcha Kunlar Takvimiga Qaytish", "callback_data": "app_tg_view_plan"}])
                                day_kb.append([{"text": "⬅️ Telegram Menyusiga", "callback_data": "app_menu_tg"}])

                                self.client.send_message(from_user, msg, reply_markup={"inline_keyboard": day_kb})

                        elif data == "app_tg_cancel_plan":
                            self.tg_scheduler.cancel_plan()
                            self.client.answer_callback_query(cb_id, "🛑 Reja to'xtatildi")
                            self.client.send_message(
                                from_user,
                                "🛑 <b>1 Haftalik Telegram rejasi to'xtatildi.</b>\n"
                                "Avtomatik e'lon qilish pauza qilindi. Xohlagan vaqt yangi reja tuzishingiz mumkin."
                            )

                        elif data.startswith("app_tg_view_post_"):
                            idx = int(data.replace("app_tg_view_post_", ""))
                            posts = self.tg_scheduler.get_all_posts()
                            if not posts:
                                self.client.answer_callback_query(cb_id, "⚠️ Reja topilmadi")
                            else:
                                idx = max(0, min(idx, len(posts) - 1))
                                p = posts[idx]
                                t_str = p['scheduled_time'].replace('T', ' ')
                                st_ico = "✅ Chiqarilgan" if p.get("status") == "posted" else "⏳ Kutilmoqda"
                                header = f"📌 <b>Post {idx+1}/{len(posts)}</b> [{p.get('cat_tag')}]\n⏰ <b>Vaqt:</b> {p.get('day_name')} {t_str} ({st_ico})\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                full_msg = header + p.get("content", "")

                                nav_btns = []
                                if idx > 0:
                                    nav_btns.append({"text": f"⬅️ Oldingi ({idx})", "callback_data": f"app_tg_view_post_{idx-1}"})
                                if idx < len(posts) - 1:
                                    nav_btns.append({"text": f"Keyingi ({idx+2}) ➡️", "callback_data": f"app_tg_view_post_{idx+1}"})

                                post_kb = {
                                    "inline_keyboard": [
                                        [{"text": "📢 Hozir Kanalga Joylash", "callback_data": f"app_tg_pub_now_{idx}"}],
                                        nav_btns if nav_btns else [],
                                        [{"text": "📋 Reja Holatiga Qaytish", "callback_data": "app_tg_view_plan"},
                                         {"text": "⬅️ Telegram Menyusiga", "callback_data": "app_menu_tg"}]
                                    ]
                                }
                                # filter out empty button rows
                                post_kb["inline_keyboard"] = [r for r in post_kb["inline_keyboard"] if r]
                                self.client.send_message(from_user, full_msg, reply_markup=post_kb)

                        elif data.startswith("app_tg_pub_now_"):
                            idx = int(data.replace("app_tg_pub_now_", ""))
                            posts = self.tg_scheduler.get_all_posts()
                            if 0 <= idx < len(posts):
                                p = posts[idx]
                                ch = self.config.get("channel_id", "@arkadasuz")
                                self.client.answer_callback_query(cb_id, "🚀 Kanalga yuborilmoqda...")
                                from datetime import datetime
                                res = self.client.send_message(ch, p.get("content", ""))
                                if res.get("ok"):
                                    p["status"] = "posted"
                                    p["posted_at"] = datetime.now().isoformat()
                                    self.tg_scheduler._save()
                                    self.client.send_message(from_user, f"✅ <b>Muvaffaqiyatli!</b> '{p.get('topic')}' posti @arkadasuz kanaliga joylashtirildi.")
                                else:
                                    self.client.send_message(from_user, f"❌ Xatolik: {res.get('description')}")
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Post topilmadi")

                        # 1 Haftalik Avtomatik Twitter Rejasi
                        elif data == "app_tw_plan_week":
                            self.client.answer_callback_query(cb_id, "⏳ 1 haftalik takrorlanmas reja tuzilmoqda...")
                            self.client.send_message(
                                from_user,
                                "⏳ <b>AI 1 haftalik takrorlanmas 21 ta tvit va 6 qismli Mega Flood tayyorlamoqda...</b>\n"
                                "<i>Mavzular tanlanmoqda, iltimos kuting...</i>"
                            )
                            plan = self.generator.generate_weekly_twitter_plan()
                            self.scheduler.save_weekly_plan(plan)

                            summary = (
                                f"🗓️ <b>1 HAFTALIK TWITTER (X) YAYIN REJASI TAYYOR!</b>\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"📅 <b>Muddat:</b> {plan['start_date']} — {plan['end_date']}\n"
                                f"📊 <b>Jami tvitlar:</b> 21 ta (Kuniga 3 ta: 10:00, 14:00, 20:00)\n"
                                f"🧵 <b>Mega Flood:</b> Chorshanba 14:00 da (6 qismli zanjir)\n"
                                f"🛡️ <b>Mavzular balansi:</b>\n"
                                f"  • 🏛️ 5 ta Arkadaş Consulting reklami & kafolat\n"
                                f"  • 🇹🇷 6 ta Turkiya haqida hayratlanarli faktlar\n"
                                f"  • 💡 4 ta Talabalik hayoti & tejamkorlik sirlari\n"
                                f"  • ❓ 3 ta Interaktiv savol-javob\n"
                                f"  • 🎓 2 ta Nufuzli oliygoh (haftasiga faqat 2 marta!)\n"
                                f"  • 🧵 1 ta Mega Flood (Chorshanba 14:00)\n\n"
                                f"<b>KUN TARTIBI:</b>\n"
                            )
                            days_dict = {}
                            for tw in plan.get("tweets", []):
                                d = tw["day_name"]
                                days_dict.setdefault(d, []).append(tw)

                            for d_name, tws in days_dict.items():
                                summary += f"\n📌 <b>{d_name}:</b>\n"
                                for tw in tws:
                                    ico = "🧵" if tw.get("is_thread") else "🐦"
                                    cat = tw.get("cat_tag", "")
                                    t_str = tw['scheduled_time'].split('T')[1][:5]
                                    cat_label = f"[{cat}]" if cat else ""
                                    summary += f"  • {ico} <b>{t_str}</b> {cat_label}: {tw['topic'][:33]}...\n"

                            summary += (
                                "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                                "👇 <b>Rejani tasdiqlaysizmi?</b>\n"
                                "Tasdiqlasangiz, bot har kuni belgilangan soatda tvitlarni Twitterga o'zi avtomatik chiqaradi!"
                            )
                            kb = {
                                "inline_keyboard": [
                                    [{"text": "☁️ Twitter Serveriga Rejalashtirish (Native Schedule)", "callback_data": "app_tw_native_schedule"}],
                                    [{"text": "🤖 Bot Taymerini Yoqish (Avtomatik Daemon)", "callback_data": "app_tw_confirm_plan"}],
                                    [{"text": "🔄 Yangi Reja Tuzish", "callback_data": "app_tw_plan_week"}],
                                    [{"text": "⬅️ Twitter Menyusiga", "callback_data": "app_menu_tw"}]
                                ]
                            }
                            self.client.send_message(from_user, summary, reply_markup=kb)

                        elif data == "app_tw_native_schedule":
                            self.client.answer_callback_query(cb_id, "🚀 Twitter serveriga yuklash boshlandi...")
                            plan = self.scheduler.data
                            tweets = plan.get("tweets", [])
                            if not tweets:
                                self.client.send_message(from_user, "⚠️ Hozirda faol reja topilmadi. Avval '1 Haftalik Rejani Tuzish' tugmasini bosing.")
                            else:
                                self.client.send_message(
                                    from_user,
                                    "⏳ <b>Tvitlar Twitter (X) rasmiy serveriga rejalashtirilmoqda (Schedule)...</b>\n\n"
                                    "• Har bir tvit to'g'ridan-to'g'ri Twitter takvimiga joylanadi.\n"
                                    "• Bu jarayon tugagach, <b>kompyuteringizni o'chirib qo'ysangiz ham</b> Twitter o'zi belgilangan vaqtda (10:00, 14:00, 20:00) avtomatik chiqaradi!\n"
                                    "<i>Iltimos, kuting (orqa fonda yuklanmoqda)...</i>"
                                )

                                def _run_native_schedule():
                                    items_to_schedule = []
                                    from datetime import datetime
                                    for tw in tweets:
                                        if tw.get("is_thread"):
                                            continue  # Twitter web multi-tweet threads can't be scheduled natively
                                        if tw.get("status") in ["posted", "scheduled_on_twitter"]:
                                            continue
                                        try:
                                            s_time = tw.get("scheduled_time")
                                            dt = datetime.fromisoformat(s_time)
                                            if dt < datetime.now():
                                                continue
                                            items_to_schedule.append({
                                                "id": tw["id"],
                                                "content": tw["content"],
                                                "dt": dt,
                                                "tw_ref": tw
                                            })
                                        except Exception:
                                            pass

                                    if not items_to_schedule:
                                        all_done = len([t for t in tweets if t.get("status") == "scheduled_on_twitter"])
                                        self.client.send_message(
                                            from_user,
                                            f"ℹ️ <b>Barcha tvitlar allaqachon Twitter rasmiy serveriga rejalashtirilgan ({all_done} ta tvit).</b>"
                                        )
                                        return

                                    def on_item_scheduled(item, ok):
                                        if ok:
                                            item["tw_ref"]["status"] = "scheduled_on_twitter"
                                            self.scheduler._save()

                                    res = self.browser_pub.schedule_twitter_posts_batch(items_to_schedule, on_each_callback=on_item_scheduled)
                                    s_cnt = res.get("scheduled_count", 0)
                                    all_scheduled = len([t for t in tweets if t.get("status") == "scheduled_on_twitter"])

                                    self.client.send_message(
                                        from_user,
                                        f"🎉 <b>TWITTER RASMIY SERVERIGA JOYLANDI!</b>\n\n"
                                        f"✅ <b>Jami {all_scheduled} ta tvit</b> (shu jumladan yangi {s_cnt} ta) Twitter (X) rasmiy serveriga rejalashtirildi (Scheduled).\n\n"
                                        f"🛡️ <b>Endi bot yoki kompyuterni ochiq qoldirish shart emas!</b>\n"
                                        f"Twitter o'z bulut serverlaridan har kuni <b>10:00, 14:00 va 20:00</b> da tvitlarni avtomatik chiqaradi.\n\n"
                                        f"📌 <i>Eslatma: Chorshanba kungi 6 qismli Mega Flood esa Twitter qoidasiga ko'ra zanjir bo'lgani uchun vaqti kelganda bot orqali yoki qo'lda bir tugma bilan chiqariladi.</i>"
                                    )

                                threading.Thread(target=_run_native_schedule, daemon=True).start()

                        elif data == "app_tw_confirm_plan":
                            self.scheduler.data["active"] = True
                            self.scheduler._save()
                            self.client.answer_callback_query(cb_id, "🎉 Reja faollashtirildi!")
                            self.client.send_message(
                                from_user,
                                "🚀 <b>1 HAFTALIK TWITTER REJASI ISHGA TUSHDI!</b>\n\n"
                                "• Bot har kuni <b>10:00, 14:00 va 20:00</b> da Twitter (@arkadasuz) hisobingizga avtomatik tvit joylaydi.\n"
                                "• Chorshanba 14:00 da 6 qismli Mega Flood zanjiri chiqadi.\n"
                                "• Har bir tvit chiqqanda sizga Telegramda hisobot keladi.\n\n"
                                "<i>Sizdan hech qanday qo'shimcha harakat talab qilinmaydi!</i>"
                            )

                        elif data == "app_tw_view_plan":
                            self.client.answer_callback_query(cb_id, "📋 Reja holati...")
                            summ = self.scheduler.get_summary()
                            status_str = "🟢 FAOL (Taymer yoqilgan)" if summ["active"] else "⚪️ NOFAOL (Kutilmoqda)"
                            msg = (
                                f"📋 <b>REJALASHTIRILGAN TVITLAR HOLATI:</b>\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"• <b>Holat:</b> {status_str}\n"
                                f"• <b>Davr:</b> {summ['start_date']} — {summ['end_date']}\n"
                                f"• <b>Jami tvitlar:</b> {summ['total']} ta\n"
                                f"• <b>Chiqarilgan:</b> {summ['posted']} ta ✅\n"
                                f"• <b>Kutilmoqda:</b> {summ['pending']} ta ⏳\n"
                                f"• <b>Mega Flood:</b> {summ['threads']} ta 🧵\n\n"
                            )
                            pending = self.scheduler.get_pending_tweets()
                            if pending:
                                msg += "<b>NAVOBATDAGI TVITLAR:</b>\n"
                                for tw in pending[:5]:
                                    ico = "🧵" if tw.get("is_thread") else "🐦"
                                    msg += f"• {ico} <b>{tw['day_name']} {tw['scheduled_time'].replace('T', ' ')}:</b>\n  <i>{tw['topic']}</i>\n"
                            else:
                                msg += "<i>Hozircha navbatda kutilayotgan tvitlar yo'q. '1 Haftalik Rejani Tuzish' orqali yangi hafta boshlashingiz mumkin.</i>"

                            kb = {
                                "inline_keyboard": [
                                    [{"text": "🗓️ Yangi 1 Haftalik Reja Tuzish", "callback_data": "app_tw_plan_week"}],
                                    [{"text": "🛑 Rejani Bekor Qilish", "callback_data": "app_tw_cancel_plan"}],
                                    [{"text": "⬅️ Orqaga", "callback_data": "app_menu_tw"}]
                                ]
                            }
                            self.client.send_message(from_user, msg, reply_markup=kb)

                        elif data == "app_tw_cancel_plan":
                            self.scheduler.cancel_plan()
                            self.client.answer_callback_query(cb_id, "🛑 Reja to'xtatildi")
                            self.client.send_message(
                                from_user,
                                "🛑 <b>1 Haftalik Twitter rejasi to'xtatildi.</b>\n"
                                "Avtomatik e'lon qilish pauza qilindi. Xohlagan vaqt yangi reja tuzishingiz mumkin."
                            )

                        # Twitter Post Generation
                        elif data == "app_tw_text":
                            self.client.answer_callback_query(cb_id, "⏳ 280 belgili mikro-tvit yozilmoqda...")
                            p = self.generator.generate_twitter_post()
                            p["target_platform"] = "twitter"
                            self.send_post_preview(from_user, p)

                        elif data == "app_tw_photo":
                            self.client.answer_callback_query(cb_id, "⏳ Twitter uchun rasm + mikro-tvit tayyorlanmoqda...")
                            p = self.generator.generate_qa_post()
                            tw = self.generator.generate_twitter_post()
                            p["caption"] = tw["content"]
                            p["target_platform"] = "twitter"
                            self.send_post_preview(from_user, p)

                        elif data == "app_tw_video":
                            self.client.answer_callback_query(cb_id, "⏳ Twitter uchun video tayyorlanmoqda...")
                            p = self.generator.generate_reels_post()
                            tw = self.generator.generate_twitter_post()
                            p["caption"] = tw["content"]
                            p["target_platform"] = "twitter"
                            self.send_post_preview(from_user, p)

                        # Facebook Post Generation
                        elif data == "app_fb_text":
                            self.client.answer_callback_query(cb_id, "⏳ Facebook uchun storytelling post yozilmoqda...")
                            p = self.generator.generate_facebook_post()
                            p["target_platform"] = "facebook"
                            self.send_post_preview(from_user, p)

                        elif data == "app_fb_photo":
                            self.client.answer_callback_query(cb_id, "⏳ Facebook uchun rasm + post tayyorlanmoqda...")
                            p = self.generator.generate_qa_post()
                            fb = self.generator.generate_facebook_post()
                            p["caption"] = fb["content"]
                            p["target_platform"] = "facebook"
                            self.send_post_preview(from_user, p)

                        elif data == "app_fb_video":
                            self.client.answer_callback_query(cb_id, "⏳ Facebook uchun video post tayyorlanmoqda...")
                            p = self.generator.generate_reels_post()
                            fb = self.generator.generate_facebook_post()
                            p["caption"] = fb["content"]
                            p["target_platform"] = "facebook"
                            self.send_post_preview(from_user, p)

                        # YouTube Shorts & Community Generation
                        elif data == "app_yt_shorts":
                            self.client.answer_callback_query(cb_id, "⏳ YouTube Shorts video va sarlavha tayyorlanmoqda...")
                            p = self.generator.generate_reels_post()
                            yt = self.generator.generate_youtube_post()
                            p["caption"] = yt["content"]
                            p["target_platform"] = "youtube"
                            self.send_post_preview(from_user, p)

                        elif data == "app_yt_community":
                            self.client.answer_callback_query(cb_id, "⏳ YouTube Community posti yozilmoqda...")
                            p = self.generator.generate_youtube_post()
                            p["target_platform"] = "youtube"
                            self.send_post_preview(from_user, p)

                        # Telegram Specific Formats
                        elif data == "app_tg_text":
                            self.prompt_text_templates(from_user)

                        elif data == "app_tg_photo_text":
                            self.client.answer_callback_query(cb_id, "⏳ Sarlavhali dizayn kartasi tayyorlanmoqda...")
                            p = self.generator.generate_qa_post()
                            p["target_platform"] = "telegram"
                            self.send_post_preview(from_user, p)

                        elif data == "app_tg_photo_only":
                            self.client.answer_callback_query(cb_id, "⏳ Faqat rasm (matnsiz) tayyorlanmoqda...")
                            p = self.generator.generate_qa_post()
                            p["caption"] = ""
                            p["no_caption"] = True
                            p["target_platform"] = "telegram"
                            self.send_post_preview(from_user, p)

                        elif data == "app_tg_video":
                            self.client.answer_callback_query(cb_id, "⏳ Video tayyorlanmoqda...")
                            p = self.generator.generate_reels_post()
                            p["target_platform"] = "telegram"
                            self.send_post_preview(from_user, p)

                        # Instagram Formats
                        elif data == "app_ig_photo":
                            self.client.answer_callback_query(cb_id, "⏳ Instagram rasm + caption tayyorlanmoqda...")
                            p = self.generator.generate_checklist_post()
                            p["target_platform"] = "instagram"
                            self.send_post_preview(from_user, p)

                        elif data == "app_ig_video":
                            self.client.answer_callback_query(cb_id, "⏳ Reels video tayyorlanmoqda...")
                            p = self.generator.generate_reels_post()
                            p["target_platform"] = "instagram"
                            self.send_post_preview(from_user, p)

                        # Facebook Web Direct Posting
                        elif data.startswith("fbpost_"):
                            pid = data.replace("fbpost_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "👥 Facebook ga yuklanmoqda...")
                                is_card = p.get("media_type") == "image"
                                media_path = p.get("media_path") if is_card else None
                                txt = p.get("caption") if is_card else p.get("content", "")
                                res_fb = self.browser_pub.publish_facebook_web(txt, media_path)
                                if res_fb.get("success"):
                                    self.client.send_message(from_user, "✅ <b>Muvaffaqiyatli!</b> Post Facebook hisobingizga joylandi!")
                                else:
                                    self.client.send_message(from_user, f"⚠️ Facebook xatosi: {res_fb.get('error')}\n\n💡 <i>Eslatma: Facebook hisobingizga bir marta kirish uchun terminalda 'python3 login_browser.py' buyrug'ini ishga tushiring.</i>")
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # YouTube API Posting Guide
                        elif data.startswith("ytpost_"):
                            pid = data.replace("ytpost_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "🎥 YouTube ma'lumoti...")
                                guide_msg = (
                                    "🎥 <b>YOUTUBE GA YUKLASH (Shorts / Community):</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
                                    "Bugun kechqurun YouTube API olasiz. Ajoyib!\n\n"
                                    "🔑 <b>API kalitingiz tayyor bo'lgach:</b>\n"
                                    "Google Cloud Console dan yuklab olingan <code>client_secrets.json</code> faylini loyiha papkasiga tashlashingiz kifoya — bot to'liq avtomatik yuklaydi!\n\n"
                                    "Hozircha esa tayyorlangan video fayl va sarlavha/tavsifni bevosita qo'lda yuklash uchun nusxalab olishingiz mumkin."
                                )
                                self.client.send_message(from_user, guide_msg)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        # Granular Edit Controls (Matnni, Rasmni yoki Ikkalasini o'zgartirish)
                        elif data.startswith("modtext_"):
                            pid = data.replace("modtext_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "⏳ Yangi matn yozilmoqda...")
                                p_type = p.get("type", "")
                                if p_type == "twitter" or p.get("target_platform") == "twitter":
                                    new_tp = self.generator.generate_twitter_post()
                                    new_txt = new_tp["content"]
                                elif p_type == "facebook" or p.get("target_platform") == "facebook":
                                    new_tp = self.generator.generate_facebook_post()
                                    new_txt = new_tp["content"]
                                elif p_type == "youtube" or p.get("target_platform") == "youtube":
                                    new_tp = self.generator.generate_youtube_post()
                                    new_txt = new_tp["content"]
                                elif p_type in ["promo", "promotional"]:
                                    new_tp = self.generator.generate_promotional_post()
                                    new_txt = new_tp["content"]
                                elif p_type in ["news"]:
                                    new_tp = self.generator.generate_news_post()
                                    new_txt = new_tp["content"]
                                else:
                                    new_tp = self.generator.generate_educational_post()
                                    new_txt = new_tp["content"]

                                if p.get("media_type") in ["image", "video"]:
                                    p["caption"] = new_txt
                                else:
                                    p["content"] = new_txt
                                self.send_post_preview(from_user, p)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        elif data.startswith("modimg_"):
                            pid = data.replace("modimg_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "⏳ Yangi dizayn yaratilmoqda...")
                                ctype = p.get("card_type", "qa")
                                if ctype == "chk":
                                    new_p = self.generator.generate_checklist_post()
                                elif ctype == "riddle":
                                    new_p = self.generator.generate_riddle_post()
                                elif ctype == "acc":
                                    new_p = self.generator.generate_acceptance_post()
                                else:
                                    new_p = self.generator.generate_qa_post()
                                p["media_path"] = new_p["media_path"]
                                self.send_post_preview(from_user, p)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        elif data.startswith("modboth_"):
                            pid = data.replace("modboth_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "⏳ Rasm va matn yangilanmoqda...")
                                ctype = p.get("card_type", "qa")
                                if ctype == "chk":
                                    new_p = self.generator.generate_checklist_post()
                                elif ctype == "riddle":
                                    new_p = self.generator.generate_riddle_post()
                                elif ctype == "acc":
                                    new_p = self.generator.generate_acceptance_post()
                                else:
                                    new_p = self.generator.generate_qa_post()
                                p["media_path"] = new_p["media_path"]
                                if p.get("target_platform") == "twitter":
                                    tw = self.generator.generate_twitter_post()
                                    p["caption"] = tw["content"]
                                elif not p.get("no_caption"):
                                    p["caption"] = new_p["caption"]
                                self.send_post_preview(from_user, p)
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                        elif data.startswith("twpost_"):
                            pid = data.replace("twpost_", "")
                            p = self.get_or_recover_post(pid, cb)
                            if p:
                                self.client.answer_callback_query(cb_id, "🐦 Twitter (X) ga yuklanmoqda...")
                                is_card = p.get("media_type") == "image"
                                media_path = p.get("media_path") if is_card else None
                                txt = p.get("caption") if is_card else p.get("content", "")
                                if len(txt) > 275:
                                    tw_obj = self.generator.generate_twitter_post(topic=p.get("topic"))
                                    tw_txt = tw_obj["content"]
                                else:
                                    tw_txt = txt

                                res_tw = self.browser_pub.publish_twitter_web(tw_txt, media_path)
                                if res_tw.get("success"):
                                    self.client.send_message(from_user, "✅ <b>Muvaffaqiyatli!</b> Tvit Twitter (X) ga joylandi!\n\n<code>" + tw_txt + "</code>")
                                else:
                                    self.client.send_message(from_user, f"⚠️ Twitter xatosi: {res_tw.get('error')}")
                            else:
                                self.client.answer_callback_query(cb_id, "⚠️ Taslaq eskirgan.")

                    # 2. Text Messages & Menu Buttons
                    elif "message" in u and "text" in u["message"]:
                        msg = u["message"]
                        chat_id = str(msg["chat"]["id"])
                        text = msg["text"].strip()

                        # Auto-assign Admin ID if not set
                        if not self.config.get("admin_chat_id"):
                            self.config["admin_chat_id"] = chat_id
                            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                                json.dump(self.config, f, indent=2)

                        # If user is Admin:
                        if chat_id == self.config.get("admin_chat_id"):
                            menu_buttons = [
                                "🌐 Ilovalar Hubi (5 Ta Tarmoq)",
                                "🌐 Ilovalar Hubi (Twitter / Insta / TG)",
                                "📱 Telegram Posti",
                                "📝 Salt Metin Posti", "🖼️ Görsel Post Kartı",
                                "💡 Maxsus Post Yozish", "📅 7 Kunlik Reja",
                                "📊 Lead CRM Ro'yxati", "❓ Yordam / Menyu",
                                "/start", "/menu", "/help"
                            ]

                            # If a menu button was clicked, always reset waiting state
                            if text in menu_buttons:
                                self.admin_states[chat_id] = None

                            state = self.admin_states.get(chat_id)

                            # Handle custom topic input
                            if state == "waiting_topic" and text not in menu_buttons and not text.startswith("/"):
                                self.admin_states[chat_id] = None
                                self.client.send_message(chat_id, f"⏳ '{text}' mavzusida 650 belgili marketing posti yozilmoqda...")
                                prompt = (
                                    f"Sen Arkadaş Consulting marketing mutaxassisisan.\n"
                                    f"Mavzu: '{text}'.\n\n"
                                    "QOIDALAR (t.me/arkadasuz kanalining 560 ta posti asosida):\n"
                                    "1. Sarlavhada 🇹🇷 Turkiya bayrog'i bo'lsin.\n"
                                    "2. Emojilar: ✅ xizmat va afzallik, 🎓 ta'lim, 📲 CTA.\n"
                                    "3. Matn hajmi taxminan 600 - 650 belgi orasida bo'lsin (keng va to'liq).\n"
                                    "4. '99% muvaffaqiyat darajasi' va 'Oldindan to'lov yo'q' deb ishonch ber.\n"
                                    "5. Oxirida faqat @arkadasuz ga yo'naltir.\n\n"
                                    "MUHIM: Faqat va faqat tayyor post matnini qaytar! Hech qanday tushuntirish, reja, 'Verify Constraints', markdown tegi yozma!"
                                )
                                res = self.generator.ai.think_and_generate(prompt)
                                raw_txt = res.get("text", "").strip()
                                
                                # Deep clean output
                                import re
                                clean_txt = re.sub(r"<think>.*?</think>", "", raw_txt, flags=re.DOTALL).strip()
                                if clean_txt.startswith("```"):
                                    clean_txt = re.sub(r"^```[a-zA-Z]*\n?", "", clean_txt)
                                    clean_txt = re.sub(r"\n?```$", "", clean_txt).strip()
                                for stop_phrase in ["Verify Constraints", "**Verify", "Verification", "Note:", "Izoh:"]:
                                    if stop_phrase in clean_txt:
                                        clean_txt = clean_txt.split(stop_phrase)[0].strip()

                                custom_post = {
                                    "type": "custom_text",
                                    "media_type": "text",
                                    "content": clean_txt,
                                    "tpl_key": "custom"
                                }
                                self.send_post_preview(chat_id, custom_post)
                                continue

                            # Menu selections
                            if text in ["/start", "/menu", "❓ Yordam / Menyu"]:
                                self.send_main_menu(chat_id, welcome=True)

                            elif text in ["🗓️ 1 Haftalik Reja & Takvim", "takvim", "reja", "haftalik reja"]:
                                self.show_telegram_calendar(chat_id)

                            elif text in ["🌐 Ilovalar Hubi (5 Ta Tarmoq)", "🌐 Ilovalar Hubi (Twitter / Insta / TG)"]:
                                self.prompt_apps_hub(chat_id)

                            elif text in ["📱 Telegram Posti", "📝 Salt Metin Posti"]:
                                self.prompt_text_templates(chat_id)

                            elif text == "🖼️ Görsel Post Kartı":
                                self.prompt_card_templates(chat_id)

                            elif "matnlarni olish" in text.lower():
                                p = None
                                if self.pending_posts:
                                    last_pid = list(self.pending_posts.keys())[-1]
                                    p = self.pending_posts[last_pid]
                                if not p:
                                    p = self.generator.generate_evergreen_post("A")
                                    p["tpl_key"] = "A"
                                    p["media_type"] = "text"
                                pack = format_multichannel_pack(p)
                                copy_msg = (
                                    "📱 <b>BARCHA PLATFORMALAR UCHUN TAYYOR MATNLAR:</b>\n"
                                    "<i>(Matn ustiga bitta bosish bilan avtomatik nusxalanadi)</i>\n\n"
                                    f"📸 <b>INSTAGRAM & FACEBOOK (Bosib nusxalang):</b>\n"
                                    f"<code>{pack['instagram']}</code>\n\n"
                                    f"🐦 <b>TWITTER / X (280 belgi):</b>\n"
                                    f"<code>{pack['twitter']}</code>\n\n"
                                    f"🎵 <b>TIKTOK / REELS:</b>\n"
                                    f"<code>{pack['tiktok']}</code>\n"
                                    f"<i>{pack['tiktok_music']}</i>"
                                )
                                self.client.send_message(chat_id, copy_msg)

                            elif text == "💡 Maxsus Post Yozish":
                                self.admin_states[chat_id] = "waiting_topic"
                                self.client.send_message(
                                    chat_id,
                                    "✍️ <b>Istalgan mavzuni yozib yuboring:</b>\n\n"
                                    "Masalan:\n"
                                    "• <i>Tibbiyot fakultetiga 100% grantlar</i>\n"
                                    "• <i>Yotoqxona narxlari va sharoitlari</i>\n"
                                    "• <i>Attestat bilan imtihonsiz qabul</i>"
                                )

                            elif text == "📅 7 Kunlik Reja":
                                cal_text = (
                                    "📅 <b>7 KUNLIK SOATLIK MARKETING TAQVIMI (@arkadasuz)</b> 🇹🇷\n"
                                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                                    "🎯 <b>KUNLIK STRATEGIYA:</b> Kuniga 3 ta post (2 ta Salt Metin + 1 ta Görsel Karta)\n"
                                    "⏰ <b>ENG FAOL SOATLAR:</b>\n"
                                    "• 🌅 <b>10:00</b> — Ertalabki Hook / Metin Posti (~650 belgi)\n"
                                    "• ☀️ <b>14:30</b> — Tushlikdagi Infografika / Dizayn Kartasi (PNG)\n"
                                    "• 🌙 <b>19:30</b> — Kechki Prime-Time: Aciliyet yoki Qabul Tabriknomasi\n"
                                    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    "📌 <b>DUSHANBA (Hafta Boshlanishi):</b>\n"
                                    "• 10:00 📝 <i>Şablon A: To'liq xizmatlar ro'yxati (99% kafolat)</i>\n"
                                    "• 14:30 🖼️ <i>Q&A Kartasi: 'Qabul uchun imtihon bormi?'</i>\n"
                                    "• 19:30 📝 <i>Şablon E: 2026-yilgi qabul boshlandi, joylar oz!</i>\n\n"
                                    "📌 <b>SESHANBA (Imkoniyatlar):</b>\n"
                                    "• 10:00 📝 <i>Şablon B: Nega Turkiya? ($2000-$5000 maosh + 20 soat ish)</i>\n"
                                    "• 14:30 🖼️ <i>Checklist Kartasi: '100% Grant yutish sirlari'</i>\n"
                                    "• 19:30 🖼️ <i>Talaba Qabul Tabriknomasi (Muvaffaqiyat isboti)</i>\n\n"
                                    "📌 <b>CHORSHANBA (Yo'l Xaritasi):</b>\n"
                                    "• 10:00 📝 <i>Şablon D: 4 oddiy qadamda talaba bo'ling</i>\n"
                                    "• 14:30 🖼️ <i>Q&A Kartasi: 'Turkiya diplomlari O'zbekistonda tan olinadimi?'</i>\n"
                                    "• 19:30 📝 <i>Şablon C: Rasmiy korporativ kafolat (0$ risk)</i>\n\n"
                                    "📌 <b>PAYSHANBA (Xizmatlar & Yotoqxona):</b>\n"
                                    "• 10:00 📝 <i>Şablon A: Aeroportda kutib olish va bepul sim-karta</i>\n"
                                    "• 14:30 🖼️ <i>Checklist Kartasi: 'Turkiyadagi talabalar imtiyozlari'</i>\n"
                                    "• 19:30 🖼️ <i>Talaba Qabul Tabriknomasi (Tibbiyot / IT yo'nalishi)</i>\n\n"
                                    "📌 <b>JUMA (Rasmiy & Islomiy Hurmat):</b>\n"
                                    "• 10:00 📝 <i>Şablon C: Juma Muborak + Arkadaş rasmiy agentligi</i>\n"
                                    "• 14:30 🖼️ <i>Q&A Kartasi: 'Turk tilini bilish shartmi? (Ingliz tili)'</i>\n"
                                    "• 19:30 📝 <i>Şablon E: Grant kvotalari tugamoqda!</i>\n\n"
                                    "📌 <b>SHANBA (Dam Olish & Interaktiv):</b>\n"
                                    "• 10:00 📝 <i>Şablon B: Talabalar uchun haftada 20 soat qonuniy ish</i>\n"
                                    "• 14:30 🖼️ <i>Topishmoq / Mantiqiy savol kartasi (Izohlarni portlatish)</i>\n"
                                    "• 19:30 🖼️ <i>Talaba Qabul Tabriknomasi (Grant sertifikati)</i>\n\n"
                                    "📌 <b>YAKSHANBA (Haftalik Xulosa & Tayyorgarlik):</b>\n"
                                    "• 10:00 📝 <i>Şablon D: Yangi hafta oldidan hujjat topshirish</i>\n"
                                    "• 14:30 🖼️ <i>Checklist Kartasi: 'Turkiyaga ketish oldidan hujjatlar'</i>\n"
                                    "• 19:30 📝 <i>Şablon E: Ertaga qabulning yangi bosqichi boshlanadi</i>\n\n"
                                    "📊 <b>HAFTALIK JAMI:</b> 21 ta Post (14 ta Metin + 7 ta Dizayn Kartasi)"
                                )
                                self.client.send_message(chat_id, cal_text)

                            elif text == "📊 Lead CRM Ro'yxati":
                                crm_file = BASE_DIR / "brain_data" / "leads_crm.json"
                                leads = []
                                if crm_file.exists():
                                    try:
                                        with open(crm_file, "r", encoding="utf-8") as f:
                                            leads = json.load(f)
                                    except Exception: pass
                                if leads:
                                    ltxt = f"📊 <b>Jami Yangi Talabalar: {len(leads)} ta</b>\n\n"
                                    for idx, l in enumerate(leads[-5:], 1):
                                        ltxt += f"{idx}. <b>{l.get('name')}</b> | 📞 {l.get('phone')} | {l.get('interest')}\n"
                                    self.client.send_message(chat_id, ltxt)
                                else:
                                    self.client.send_message(chat_id, "ℹ️ Hozircha CRM bazasida yangi arizalar mavjud emas.")
                            elif text == "🌐 6 Ta Tarmoq Holati":
                                st = self.publisher.get_platforms_status()
                                txt = "🌐 <b>IJTIMOIY TARMOQLAR INTEGRATSIYASI (6 TA PLATFORMA):</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
                                icons = {"telegram": "📱", "instagram": "📸", "facebook": "👥", "twitter": "🐦", "youtube": "🎥", "tiktok": "🎵"}
                                for plat, info in st.items():
                                    txt += f"• {icons.get(plat, '🌐')} <b>{plat.upper()}:</b> {info['status_text']}\n"
                                txt += (
                                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                                    "💡 <b>Qanday kalitlar kerak?</b>\n"
                                    "• <b>Telegram:</b> ✅ Bog'langan (@arkadasuz)\n"
                                    "• <b>Instagram & Facebook:</b> Meta Graph API Token & Page/Account ID\n"
                                    "• <b>Twitter (X):</b> API Key + Secret + Access Tokens\n"
                                    "• <b>YouTube:</b> Google Cloud Client ID & Refresh Token\n"
                                    "• <b>TikTok:</b> TikTok Developers Client Key & Access Token\n\n"
                                    "Kalitlarni to'g'ridan-to'g'ri <code>social_credentials.json</code> fayliga kiritishingiz mumkin!"
                                )
                                self.client.send_message(chat_id, txt)

                            else:
                                self.client.send_message(chat_id, "ℹ️ Quyidagi tugmalardan birini bosing:", reply_markup=MAIN_KEYBOARD)

                        else:
                            # Message from regular student / user
                            self.student_bot.process_incoming_message(msg)

            except Exception as e:
                print(f"[POLL ERROR] {e}")
                time.sleep(3)

if __name__ == "__main__":
    bot = AdminApprovalBot()
    bot.run()
