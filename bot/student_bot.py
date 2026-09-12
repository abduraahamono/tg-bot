#!/usr/bin/env python3
"""
Arkadaş Consulting - 24/7 Student Consultant & Lead Capture Assistant Bot
Features:
1. Answers student questions in Uzbek using the Brand Brain (FAQ + Universities)
2. Automatically detects university mentions (Marmara, Koç, İTÜ, Hacettepe, etc.) and provides facts
3. Captures Student Leads (Name, Phone Number, Target Field)
4. Saves leads to crm/leads.json
5. Instantly alerts Admin on Telegram when a new prospective student leaves contact details!
"""

import os
import sys
import re
import json
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CRM_FILE = BASE_DIR / "crm" / "leads.json"
BRAIN_DIR = BASE_DIR / "brain_data"
from bot.telegram_client import TelegramClient
from bot.admin_bot import load_config
from engine.ai_brain import AIBrain

def load_json(filepath: Path):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

class StudentAssistantBot:
    def __init__(self):
        self.config = load_config()
        self.client = TelegramClient(self.config.get("bot_token"))
        self.brand = load_json(BRAIN_DIR / "brand_profile.json")
        self.faqs = load_json(BRAIN_DIR / "faq_knowledge.json")
        from engine.conversation_memory import ConversationMemory
        self.memory = ConversationMemory()
        from crm.lead_manager import CRMLeadManager
        self.crm_manager = CRMLeadManager()
        self.ai = AIBrain()
        self.pending_leads = {}  # user_id -> state

    def save_lead(self, lead_data: dict):
        # 1. Save locally (JSON + CSV) and Push to Google Sheets (if configured)
        res = self.crm_manager.save_lead(lead_data)
        saved_lead = res.get("lead", lead_data)
        gs_status = "✅ Google Sheets'ga yuborildi" if res.get("google_sheets_synced") else "ℹ️ Google Sheets sozlanmagan"

        # 2. Notify Admin via Telegram
        admin_chat = load_config().get("admin_chat_id")
        if admin_chat and self.client.is_configured():
            alert_text = (
                f"🚨 <b>YANGI TALABA MUROJAATI (LEAD)!</b>\n\n"
                f"👤 <b>Ism:</b> {saved_lead.get('name', 'Noma\'lum')}\n"
                f"📱 <b>Telefon:</b> <code>{saved_lead.get('phone', 'Noma\'lum')}</code>\n"
                f"🎯 <b>Yo'nalish / Maqsad:</b> {saved_lead.get('interest', 'Turkiyada ta\'lim')}\n"
                f"📊 <b>Holat:</b> {saved_lead.get('current_status', 'Yangi ariza')}\n"
                f"💬 <b>Telegram:</b> @{saved_lead.get('username', '')} (ID: <code>{saved_lead.get('user_id')}</code>)\n"
                f"📅 <b>Vaqt:</b> {saved_lead.get('timestamp')}\n"
                f"🌐 <b>Sheets:</b> <i>{gs_status}</i>\n\n"
                f"👉 <i>Darhol bog'lanib, konsultatsiya bering!</i>"
            )
            self.client.send_message(admin_chat, alert_text)

    def generate_reply(self, user_text: str, user_name: str, chat_id: str = "") -> dict:
        text_lower = user_text.lower()

        # 1. Check for Phone Number detection
        phone_match = re.search(r'(\+?[0-9]{1,3}[\s\-]?)?(\(?[0-9]{2,3}\)?[\s\-]?)?([0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}|[0-9]{7,10})', user_text)
        if phone_match and len(re.sub(r'\D', '', phone_match.group(0))) >= 7:
            phone_num = phone_match.group(0).strip()
            reply_txt = (
                f"Rahmat, {user_name}! ✅ Telefon raqamingizni saqlab oldik ({phone_num}).\n\n"
                f"Mutaxassisimiz sizga mos universitetlar va grantlar bo'yicha tez orada to'liq ma'lumot taqdim etadi! 🎓"
            )
            if chat_id:
                self.memory.update_user_profile(chat_id, {"phone": phone_num, "name": user_name})
                self.memory.add_message(chat_id, "user", user_text)
                self.memory.add_message(chat_id, "assistant", reply_txt)
            return {
                "is_lead": True,
                "phone": phone_num,
                "reply": reply_txt
            }

        # 2. Use AI Brain with conversation history & user profile
        hist_context = ""
        user_meta = {"name": user_name, "is_admin": False}
        if chat_id:
            hist_context = self.memory.get_history_summary_for_prompt(chat_id, limit=8)
            self.memory.add_message(chat_id, "user", user_text, user_meta=user_meta)
            user_meta["profile_summary"] = self.memory.get_profile_summary_for_prompt(chat_id)

        try:
            ai_ans = self.ai.answer_student_consultation(user_text, history_context=hist_context, user_info=user_meta)
            if ai_ans:
                if chat_id:
                    self.memory.add_message(chat_id, "assistant", ai_ans)
                return {
                    "is_lead": False,
                    "reply": ai_ans
                }
        except Exception as e:
            print(f"[StudentBot AI Error] {e}", flush=True)

        # Fallback friendly greeting if AI is unavailable
        return {
            "is_lead": False,
            "reply": (
                f"Assalomu alaykum, {user_name}! 👋\n\n"
                f"Arkadaş Consulting bilan Turkiyada oliy ta'lim, 100% gacha grantlar va imtihonsiz qabul bo'yicha qanday savolingiz bor? Savolingizni bemalol yozishingiz mumkin. 😊"
            )
        }

    def process_incoming_message(self, message: dict):
        chat_id = str(message["chat"]["id"])
        user_text = (message.get("text") or message.get("caption") or "").strip()
        from_user = message.get("from", {})
        user_name = from_user.get("first_name", "Do'st")
        username = from_user.get("username", "")

        # Handle photo or document sent without text
        if not user_text and ("photo" in message or "document" in message):
            self.memory.add_message(chat_id, "user", "[Hujjat/Rasm yuborildi]")
            photo_reply = "Rasmni qabul qildik! ✅ Agar bu attestat, diplom yoki pasportingiz bo'lsa, mutaxassisimiz hujjatlaringizni tahlil qilib sizga mos universitetlarni saralab beradi. Qaysi yo'nalishda o'qimoqchisiz?"
            self.memory.add_message(chat_id, "assistant", photo_reply)
            self.client.send_message(chat_id, photo_reply)
            return

        if not user_text:
            return

        result = self.generate_reply(user_text, user_name, chat_id=chat_id)

        if result.get("is_lead"):
            profile = self.memory.get_user_profile(chat_id)
            final_name = profile.get("name") or user_name
            final_interest = profile.get("interest") or "Turkiyada ta'lim"
            lead_entry = {
                "user_id": from_user.get("id"),
                "username": username,
                "name": final_name,
                "phone": result["phone"],
                "interest": final_interest,
                "current_status": "Yangi ariza (Bog'lanish kutilmoqda)",
                "first_message": user_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_lead(lead_entry)

        self.client.send_message(chat_id, result["reply"])

if __name__ == "__main__":
    bot = StudentAssistantBot()
    print("--- Testing Student Assistant Reply Logic ---")
    test_q = "Marmara universitetiga kirish uchun imtihon bormi?"
    rep = bot.generate_reply(test_q, "Jahongir")
    print(f"User: {test_q}\nBot Reply:\n{rep['reply']}\n")

    test_lead = "+998 90 123 45 67 meni ismim Sardor tibbiyotga qiziqaman"
    lead_rep = bot.generate_reply(test_lead, "Sardor")
    print(f"Lead Detected: {lead_rep.get('is_lead')}, Phone: {lead_rep.get('phone')}")
