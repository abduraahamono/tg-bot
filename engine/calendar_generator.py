#!/usr/bin/env python3
"""
Arkadaş Consulting - 7-Day Autonomous Content Calendar Generator
Produces a complete, ready-to-publish weekly marketing plan:
- Day 1 (Dushanba): Q&A Post (Visa & Exam-free Admission)
- Day 2 (Seshanba): AI Influencer Madina Reel (Student life & 100% grant)
- Day 3 (Chorshanba): Interactive Riddle (Engagement booster)
- Day 4 (Payshanba): University Checklist (Top Turkish universities)
- Day 5 (Juma): Social Proof & Acceptance Celebration
- Day 6 (Shanba): Cinematic Istanbul Sunset Reel + Music
- Day 7 (Yakshanba): Weekly Q&A Recap & Direct Consultation Funnel
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

OUTPUT_DIR = BASE_DIR / "output" / "haftalik_reja"
from engine.content_generator import ContentGenerator
from engine.influencer_engine import InfluencerEngine

class CalendarGenerator:
    def __init__(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.cg = ContentGenerator()
        self.ie = InfluencerEngine()

    def generate_weekly_pack(self) -> list:
        print("\n" + "="*60)
        print("🚀 7 KUNLIK TO'LIQ MARKETING REJASI YARATILMOQDA...")
        print("="*60)

        week_plan = []
        today = datetime.now()

        # Day 1: Dushanba - Q&A
        print("\n[1/7] Dushanba: Savol-Javob Posti tayyorlanmoqda...")
        p1 = self.cg.generate_qa_post()
        week_plan.append({
            "day": "Dushanba (1-kun)",
            "theme": "Savol-Javob & Imtihonsiz Qabul",
            "type": "image",
            "file": p1["media_path"],
            "caption": p1["caption"]
        })

        # Day 2: Seshanba - Madina AI Influencer Reel
        print("\n[2/7] Seshanba: AI Influencer Madina Reels Videosi render qilinmoqda...")
        p2 = self.ie.create_influencer_reel(topic="Marmara universitetida grant asosida o'qish sirlari")
        week_plan.append({
            "day": "Seshanba (2-kun)",
            "theme": "AI Influencer Madina - Talabalik hayoti",
            "type": "video",
            "file": p2["media_path"],
            "caption": p2["caption"]
        })

        # Day 3: Chorshanba - Riddle Card
        print("\n[3/7] Chorshanba: Qiziqarli Topishmoq posti tayyorlanmoqda...")
        p3 = self.cg.generate_riddle_post()
        week_plan.append({
            "day": "Chorshanba (3-kun)",
            "theme": "Topishmoq & Mantiqiy Savol (Auditoriya jalb qilish)",
            "type": "image",
            "file": p3["media_path"],
            "caption": p3["caption"]
        })

        # Day 4: Payshanba - University Checklist
        print("\n[4/7] Payshanba: Universitetlar Checklist posti tayyorlanmoqda...")
        p4 = self.cg.generate_checklist_post()
        week_plan.append({
            "day": "Payshanba (4-kun)",
            "theme": "Top Universitetlar & Grant Shartlari",
            "type": "image",
            "file": p4["media_path"],
            "caption": p4["caption"]
        })

        # Day 5: Juma - Acceptance Celebration
        print("\n[5/7] Juma: Yangi Talaba Qabul Tabriknomasi tayyorlanmoqda...")
        p5 = self.cg.generate_acceptance_post("Azizbek Norboyev", "Istanbul Texnika Universiteti (İTÜ)", "Dasturiy Ta'minot Muhandisligi", "100% GRANT")
        week_plan.append({
            "day": "Juma (5-kun)",
            "theme": "Muvaffaqiyat Tarixi & Ijtimoiy Isbot (Social Proof)",
            "type": "image",
            "file": p5["media_path"],
            "caption": p5["caption"]
        })

        # Day 6: Shanba - Cinematic Istanbul Sunset Reel
        print("\n[6/7] Shanba: Sinematik Istanbul Reels videosi musiqasi bilan tayyorlanmoqda...")
        p6 = self.cg.generate_reels_post(
            italic_hook="Istanbulda talabalik gashtini suring...",
            bold_headline="ARKADAŞ BILAN BEPUL TA'LIM VA KAFOLATLI YOTOQXONA!",
            sub_tagline="Hujjatlarni bugunoq topshiring!"
        )
        week_plan.append({
            "day": "Shanba (6-kun)",
            "theme": "Sinematik Istanbul Reels (Musiqali)",
            "type": "video",
            "file": p6["media_path"],
            "caption": p6["caption"]
        })

        # Day 7: Yakshanba - Madina Sunday Advice Reel
        print("\n[7/7] Yakshanba: Madina Karimova Maslahati Reels tayyorlanmoqda...")
        p7 = self.ie.create_influencer_reel(topic="Qizlar uchun Turkiyada xavfsiz yashash va yotoqxona")
        week_plan.append({
            "day": "Yakshanba (7-kun)",
            "theme": "Yakshanba Konsultatsiyasi & Madina Maslahati",
            "type": "video",
            "file": p7["media_path"],
            "caption": p7["caption"]
        })

        # Save summary JSON
        plan_file = OUTPUT_DIR / "haftalik_reja_summary.json"
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(week_plan, f, ensure_ascii=False, indent=2)

        print("\n" + "="*60)
        print("🎉 7 KUNLIK TO'LIQ KONTENT REJASI TAYYOR BO'LDI!")
        print(f"📁 Barcha materiallar: {OUTPUT_DIR}")
        print("="*60)
        return week_plan

if __name__ == "__main__":
    cal = CalendarGenerator()
    cal.generate_weekly_pack()
