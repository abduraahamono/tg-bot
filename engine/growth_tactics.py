#!/usr/bin/env python3
"""
Arkadaş Consulting - AI Growth Tactics & Telegram Conversion Engine
Autonomous strategies devised by the AI Brain to maximize channel growth and conversions:
1. Twitter-to-Telegram Viral Reply Hook (Anti-spam rotating replies)
2. Social Conversion CTA Generator
3. Lead magnet prompts for Telegram channel
"""

import random
from typing import List

TELEGRAM_CHANNEL_URL = "https://t.me/arkadasuz"
TELEGRAM_CHANNEL_HANDLE = "@arkadasuz"
TELEGRAM_CONSULTANT = "@arkadasuzz"

# Rotating organic reply hooks (Prevents Twitter spam detection, maximizes curiosity & clicks)
TWITTER_REPLY_HOOKS = [
    (
        "📌 Turkiyada o'qish, kontrakt narxlari va grant kvotalari haqidagi barcha rasmiy ma'lumotlar "
        "bosh kanalda e'lon qilinadi:\n"
        "👉 https://t.me/arkadasuz\n\n"
        "Savollaringiz bo'lsa, konsultatsiya mutlaqo bepul! 🇹🇷"
    ),
    (
        "🏛️ Turkiyaning nufuzli davlat universitetlariga imtihonsiz qabul bo'yicha to'liq qo'llanma "
        "Telegram kanalimizda:\n"
        "👉 https://t.me/arkadasuz\n\n"
        "2026-yilgi mavsum uchun kvotalar cheklangan! ✈️"
    ),
    (
        "🎓 O'zbekistonlik talabalar hayoti, arzon yotoqxonalar va stipendiya yutish sirlari haqida "
        "batafsil bu yerda yozamiz:\n"
        "👉 https://t.me/arkadasuz\n\n"
        "Abituriyentlar uchun foydali manba! 🤝"
    ),
    (
        "✈️ Attestat baholari bilan Turkiyada 100% kafolatli talaba bo'ling!\n"
        "Barcha yangiliklar va universitetlar ro'yxati:\n"
        "👉 https://t.me/arkadasuz\n\n"
        "Arkadaş Consulting — Sizning ishonchli do'stingiz. 🇹🇷"
    ),
    (
        "💡 Talabalar uchun haftasiga 20 soat qonuniy ishlash va tejamkor yashash bo'yicha maxsus postlarimiz "
        "kanalda chiqmoqda:\n"
        "👉 https://t.me/arkadasuz"
    )
]

def get_growth_reply() -> str:
    """Returns a randomized, engaging comment with the Telegram channel link."""
    return random.choice(TWITTER_REPLY_HOOKS)

def format_tweet_with_thread(tweet_text: str, auto_reply: bool = True) -> List[str]:
    """
    Splits or formats tweet into a 2-step thread:
    Step 1: The sharp, engaging micro-tweet
    Step 2: The reply comment containing the Telegram channel link
    """
    items = [tweet_text.strip()]
    if auto_reply:
        items.append(get_growth_reply())
    return items
