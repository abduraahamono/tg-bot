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
        self.universities = load_json(BRAIN_DIR / "universities.json")
        self.ai = AIBrain()
        self.pending_leads = {}  # user_id -> state

    def save_lead(self, lead_data: dict):
        CRM_FILE.parent.mkdir(parents=True, exist_ok=True)
        leads = []
        if CRM_FILE.exists():
            try:
                with open(CRM_FILE, "r", encoding="utf-8") as f:
                    leads = json.load(f)
            except Exception:
                leads = []
        
        leads.append(lead_data)
        with open(CRM_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

        # Notify Admin
        admin_chat = load_config().get("admin_chat_id")
        if admin_chat and self.client.is_configured():
            alert_text = (
                f"🚨 <b>YANGI TALABA MUROJAATI (LEAD)!</b>\n\n"
                f"👤 <b>Ism:</b> {lead_data.get('name', 'Noma\'lum')}\n"
                f"📱 <b>Telefon:</b> <code>{lead_data.get('phone', 'Noma\'lum')}</code>\n"
                f"🎓 <b>Qiziqqan soha:</b> {lead_data.get('interest', 'Turkiyada ta\'lim')}\n"
                f"📅 <b>Vaqt:</b> {lead_data.get('timestamp')}\n"
                f"💬 <b>Telegram:</b> @{lead_data.get('username', '')} (ID: {lead_data.get('user_id')})\n\n"
                f"👉 <i>Darhol bog'lanib, konsultatsiya bering!</i>"
            )
            self.client.send_message(admin_chat, alert_text)

    def generate_reply(self, user_text: str, user_name: str) -> str:
        text_lower = user_text.lower()

        # 1. Check for Phone Number detection
        phone_match = re.search(r'(\+?[0-9\s\-]{9,16})', user_text)
        if phone_match and len(re.sub(r'\D', '', phone_match.group(1))) >= 9:
            phone_num = phone_match.group(1).strip()
            return {
                "is_lead": True,
                "phone": phone_num,
                "reply": (
                    f"Rahmat, {user_name}! ✅ Telefon raqamingiz qabul qilindi ({phone_num}).\n\n"
                    f"Tez orada Arkadaş Consulting bosh mutaxassisi siz bilan bog'lanadi va "
                    f"sizga mos universitetlar hamda grant dasturlari bo'yicha bepul to'liq yo'l xaritasini taqdim etadi! 🎓✨"
                )
            }

        # 2. Check for University queries
        for uni in self.universities:
            u_name = uni["name"].lower()
            short_name = u_name.replace("universiteti", "").replace("üniversitesi", "").strip()
            if short_name in text_lower:
                return {
                    "is_lead": False,
                    "reply": (
                        f"🏛 <b>{uni['name']}</b> haqida ma'lumot:\n\n"
                        f"📍 Joylashuvi: {uni.get('location', 'Turkiya')}\n"
                        f"🏢 Turi: {uni.get('type', 'Davlat')}\n"
                        f"🗓 Tashkil etilgan: {uni.get('established', 'Noma\'lum')}\n\n"
                        f"Ushbu universitetga qabul shartlari va grant imkoniyatlarini bilish uchun "
                        f"<b>telefon raqamingizni</b> qoldiring, mutaxassisimiz sizga to'liq tushuntirib beradi! 😊"
                    )
                }

        # 3. Check for specific FAQ topics
        if any(k in text_lower for k in ["imtihon", "yos", "yös", "attestat", "qabul"]):
            return {
                "is_lead": False,
                "reply": (
                    "🎓 <b>Qabul tartibi:</b>\n"
                    "Arkadaş Consulting orqali imtihonli yoki <b>imtihonsiz (faqat attestat baholari asosida)</b> "
                    "Turkiya universitetlariga qabul qilinasiz!\n\n"
                    "Siz qaysi yo'nalishga qiziqyapsiz? Ismingiz va telefon raqamingizni yozsangiz, mos variantlarni tashlab beramiz."
                )
            }

        if any(k in text_lower for k in ["grant", "burs", "tekin", "bepul"]):
            return {
                "is_lead": False,
                "reply": (
                    "💸 <b>Grant va Stipendiyalar:</b>\n"
                    "Biz orqali 25%, 50%, 75% va hatto <b>100% gacha bo'lgan to'liq grant</b> asosida "
                    "Turkiyada ta'lim olish imkoniyati mavjud!\n\n"
                    "Batafsil grant shartlari uchun telefon raqamingizni qoldiring, danishmandimiz aloqaga chiqadi."
                )
            }

        if any(k in text_lower for k in ["tolov", "to'lov", "narx", "kontrakt", "oldindan"]):
            return {
                "is_lead": False,
                "reply": (
                    "🚫 <b>Oldindan to'lov yo'q!</b>\n"
                    "Dastlab o'qishga qabul qilinib, rasmiy taklifnoma olganingizdan keyin xizmat haqi to'lanadi. "
                    "Hech qanday moliyaviy xavf yo'q!\n\n"
                    "Raqamingizni qoldiring, barcha shartlarni shaffof tushuntirib beramiz."
                )
            }

        if any(k in text_lower for k in ["yotoqxona", "yashash", "viza", "kutib olish", "aeroport"]):
            return {
                "is_lead": False,
                "reply": (
                    "🏠 <b>Yotoqxona va Hamrohlik:</b>\n"
                    "Turkiyaga kelishingiz bilan sizni aeroportda kutib olamiz, hamyonbop yotoqxonaga joylashtiramiz, "
                    "yashash ruxsatnomasi (ikamet), sim-karta va bank hisobi ochishda to'liq yordam beramiz!"
                )
            }

        # 4. If AI Brain has active provider (Gemini, Groq, GLM, Ollama), ask AI Brain!
        try:
            ai_ans = self.ai.answer_student_consultation(user_text)
            if ai_ans:
                return {
                    "is_lead": False,
                    "reply": ai_ans
                }
        except Exception:
            pass

        # Default friendly greeting & Lead funnel
        return {
            "is_lead": False,
            "reply": (
                f"Assalomu alaykum, {user_name}! 👋\n\n"
                f"Men <b>Arkadaş Consulting</b> virtual assistentiman.\n\n"
                f"Biz sizga Turkiyada:\n"
                f"✅ 100% gacha grantlar\n"
                f"✅ Imtihonsiz to'g'ridan-to'g'ri qabul\n"
                f"✅ Yotoqxona va barcha hujjatlar bo'yicha yordam beramiz.\n\n"
                f"Sizga eng mos universitet va grantni aniqlab berishimiz uchun:\n"
                f"👉 <b>Ismingiz, qiziqqan sohangiz va telefon raqamingizni</b> yozib qoldiring! 😊"
            )
        }

    def process_incoming_message(self, message: dict):
        chat_id = str(message["chat"]["id"])
        user_text = message.get("text", "").strip()
        from_user = message.get("from", {})
        user_name = from_user.get("first_name", "Do'st")
        username = from_user.get("username", "")

        result = self.generate_reply(user_text, user_name)

        if result.get("is_lead"):
            lead_entry = {
                "user_id": from_user.get("id"),
                "username": username,
                "name": user_name,
                "phone": result["phone"],
                "interest": "Turkiyada ta'lim",
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
