#!/usr/bin/env python3
"""
Arkadaş Consulting - Omnichannel Content Formatter
Har bir tayyorlangan postni barcha platformalar formatiga moslab beradi:
1. Instagram (Kengaytirilgan matn + 12 ta maqsadli hashtag)
2. Twitter / X (280 belgilik ixcham tvit + link)
3. TikTok / Reels (Kanca + Qisqa tavsif + Trend musiqa tavsiyasi)
4. Facebook (Rasmiy korporativ matn + To'liq aloqa)
"""

import re
from typing import Dict, Any

INSTA_HASHTAGS = (
    "#TurkiyadaTalim #ArkadasConsulting #Talaba2026 #Grantlar #Istanbul #Ankara "
    "#OzbekistonTalabalari #Universitet #Talabalik #ImtihonsizQabul #Viza #Turkiya"
)

def format_multichannel_pack(post_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Bitta postdan barcha platformalar uchun maxsus nusxalarni yaratadi.
    """
    is_card = post_data.get("media_type") == "image"
    raw_text = post_data.get("caption") if is_card else post_data.get("content", "")
    
    # Strip HTML tags for platforms that do not support them
    clean_text = re.sub(r"<[^>]+>", "", raw_text).strip()
    
    # 1. INSTAGRAM FORMAT
    insta_caption = clean_text
    if "@arkadas.uz" not in insta_caption:
        insta_caption += "\n\n📲 Instagram: @arkadasuz\n👉 Telegram: @arkadasuzz"
    if "#TurkiyadaTalim" not in insta_caption:
        insta_caption += f"\n\n.\n.\n{INSTA_HASHTAGS}"

    # 2. TWITTER / X FORMAT (Max 275 chars)
    lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
    first_line = lines[0] if lines else "Turkiyada 100% grant asosida o'qish imkoniyati! 🇹🇷"
    second_line = lines[1] if len(lines) > 1 else "Arkadaş Consulting bilan imtihonsiz qabul."
    
    tw_base = f"{first_line}\n\n{second_line}\n\n📲 Murojaat: @arkadasuzz\n#TurkiyadaTalim #Grant"
    if len(tw_base) > 275:
        tw_base = tw_base[:240] + "...\n📲 @arkadasuzz\n#TurkiyadaTalim"

    # 3. TIKTOK / REELS FORMAT
    tt_hook = lines[0] if lines else "Turkiyada o'qishni xohlaysizmi? 🇹🇷"
    tt_caption = (
        f"🔥 {tt_hook}\n\n"
        f"✅ Imtihonsiz to'g'ridan-to'g'ri qabul\n"
        f"✅ 100% gacha grantlar va yotoqxona ko'magi\n"
        f"📲 Batafsil ma'lumot: Telegram @arkadasuzz\n\n"
        f"#turkiya #talaba #uzbekistan #arkadas #grant #tashkent"
    )
    tt_music = "🎵 Tavsiya etilgan fon musiqasi: Blok3 — 'Ne Yapıyorsun' yoki Inspiring Travel Beat"

    # 4. FACEBOOK & YOUTUBE COMMUNITY FORMAT
    fb_caption = (
        f"{clean_text}\n\n"
        f"📍 Rasmiy konsalting agentligi: ARKADAŞ Consulting 🇹🇷\n"
        f"📸 Instagram: @arkadasuz\n"
        f"🎥 YouTube: @arkadasuz\n"
        f"📩 Telegram: @arkadasuzz\n"
        f"🌐 Web: arkadas.uz"
    )

    return {
        "instagram": insta_caption,
        "twitter": tw_base,
        "tiktok": tt_caption,
        "tiktok_music": tt_music,
        "facebook": fb_caption
    }

if __name__ == "__main__":
    sample = {
        "media_type": "text",
        "content": "Assalomu alaykum! 🇹🇷 Turkiyada 100% grant yutishni xohlaysizmi? Arkadaş orqali imtihonsiz qabul! 📲 @arkadasuz"
    }
    pack = format_multichannel_pack(sample)
    print("=== INSTAGRAM ===")
    print(pack["instagram"][:150])
    print("\n=== TWITTER ===")
    print(pack["twitter"])
    print("\n=== TIKTOK ===")
    print(pack["tiktok"][:150])
