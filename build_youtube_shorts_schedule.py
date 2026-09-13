#!/usr/bin/env python3
"""
Builds a 24-day automated YouTube Shorts Schedule (2 Shorts per day: 13:00 and 19:30).
Maps 48 real Telegram channel video files with high-converting Uzbek titles, descriptions, and hashtags.
"""

import os
import glob
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "brain_data" / "scheduled_youtube_shorts.json"

# Topic metadata mapped to video types
TOPIC_POOLS = [
    ("Turkiyada imtihonsiz qabul: Attestat bahosi yetarli! 🇹🇷", "Turkiya davlat universitetlariga imtihonsiz kirish tartibi."),
    ("Talabalarning 1 oylik xarajati qancha? 💰", "Yotoqxona, oziq-ovqat va talabalik chegirmalari."),
    ("TÖMER turk tili kursi nima va qanday o'qitiladi? 📚", "Til bilmasdan turib qanday qilib erkin so'zlashish mumkin?"),
    ("Bologna tizimi: Diplom 150+ davlatda tan olinadi! 🌍", "Turkiya oliy ta'limining xalqaro nufuzi va imtiyozlari."),
    ("Istanbul Davlat Universiteti: Qadimiy va zamonaviy kampus 🏛️", "O'zbek yoshlari uchun eng mashhur universitetlar."),
    ("Turkiyada qonuniy ishlash imkoniyati (haftada 20 soat) 💼", "Talabalar o'qishdan bo'sh vaqtlarida qanday daromad topishi mumkin?"),
    ("Davlat (KYK) yotoqxonalari: Bepul ovqat va arzon turar joy 🏨", "Xavfsiz va qulay talabalar yotoqxonalari sharoitlari."),
    ("Samarqandlik va Toshkentlik talabalar tajribasi ✈️", "Turkiyaga ilk bor borgan talabalarimiz nimalarga duch keldi?"),
    ("100% Grant yutish sirlari: Türkiye Bursları 🎓", "Davlat stipendiyasi orqali bepul o'qish va yashash."),
    ("Turkiyada talabalar xavfsizligi: Qizlar uchun sharoitlar 🌸", "Ota-onalar xotirjamligi va doimiy hamrohlik."),
    ("Erasmus+ dasturi: Turkiyadan Yevropaga tekinga sayohat 🇪🇺", "Yevropa universitetlarida 1 semestr bepul tahsil olish."),
    ("Marmara Universiteti: Ikki qit'ani bog'lagan nufuzli dargoh 🌊", "Istanbulning eng go'zal kampusi haqida.")
]

def get_video_duration(fpath):
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', fpath]
        return float(subprocess.check_output(cmd).decode().strip())
    except Exception:
        return 20.0

def main():
    video_dir = BASE_DIR / "ChatExport_Turkiyada ta'lim🇹🇷" / "video_files"
    all_files = sorted(glob.glob(str(video_dir / "*")))
    
    # Filter valid video files <= 65s
    shorts = []
    for f in all_files:
        if not f.lower().endswith(('.mp4', '.mov')):
            continue
        dur = get_video_duration(f)
        if dur <= 65 and dur >= 4:
            shorts.append((f, dur))

    print(f"Total eligible Shorts videos: {len(shorts)}")

    # We take up to 48 videos for a 24-day schedule (2 per day)
    shorts = shorts[:48]
    start_date = datetime(2026, 9, 14)  # Starting from tomorrow

    schedule_items = []
    video_idx = 0

    for day_idx in range(len(shorts) // 2):
        cur_date = start_date + timedelta(days=day_idx)
        date_str = cur_date.strftime("%Y-%m-%d")

        # 1. Lunch Slot (13:00)
        v1, dur1 = shorts[video_idx]
        topic1, desc1 = TOPIC_POOLS[video_idx % len(TOPIC_POOLS)]
        schedule_items.append({
            "id": f"yt_short_{date_str}_lun",
            "date": date_str,
            "slot": "lunch",
            "scheduled_time": f"{date_str} 13:00:00",
            "video_path": os.path.relpath(v1, BASE_DIR),
            "duration": round(dur1, 1),
            "title": topic1,
            "description": desc1,
            "status": "pending"
        })
        video_idx += 1

        # 2. Evening Prime-Time Slot (19:30)
        v2, dur2 = shorts[video_idx]
        topic2, desc2 = TOPIC_POOLS[video_idx % len(TOPIC_POOLS)]
        schedule_items.append({
            "id": f"yt_short_{date_str}_eve",
            "date": date_str,
            "slot": "evening",
            "scheduled_time": f"{date_str} 19:30:00",
            "video_path": os.path.relpath(v2, BASE_DIR),
            "duration": round(dur2, 1),
            "title": topic2,
            "description": desc2,
            "status": "pending"
        })
        video_idx += 1

    payload = {
        "active": True,
        "created_at": datetime.now().isoformat(),
        "total_shorts": len(schedule_items),
        "days_covered": len(schedule_items) // 2,
        "start_date": schedule_items[0]["date"] if schedule_items else "",
        "end_date": schedule_items[-1]["date"] if schedule_items else "",
        "shorts": schedule_items
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"🎉 24-Day YouTube Shorts Schedule built successfully!")
    print(f"Total Shorts: {len(schedule_items)} | Range: {payload['start_date']} to {payload['end_date']}")

if __name__ == "__main__":
    main()
