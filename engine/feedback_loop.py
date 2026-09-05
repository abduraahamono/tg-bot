#!/usr/bin/env python3
"""
Arkadaş Consulting - Otonom Geri Besleme Döngüsü (CRM -> Marketing Feedback Loop)
Analyzes incoming student inquiries and CRM leads to identify trending questions,
student pain points (yotoqxona, viza, grant, narx), and automatically generates
targeted Q&A or Madina AI Influencer Reels to answer them on social media.
"""

import os
import sys
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CRM_FILE = BASE_DIR / "crm" / "leads.json"
from engine.ai_brain import AIBrain
from engine.content_generator import ContentGenerator
from engine.influencer_engine import InfluencerEngine

class MarketingFeedbackLoop:
    def __init__(self):
        self.ai = AIBrain()
        self.cg = ContentGenerator()
        self.ie = InfluencerEngine()

    def analyze_leads_and_trends(self) -> dict:
        """Extracts key themes from captured student leads."""
        if not CRM_FILE.exists():
            return {"total_leads": 0, "top_topics": ["Imtihonsiz qabul", "Grantlar", "Yotoqxona"]}

        try:
            with open(CRM_FILE, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except Exception:
            leads = []

        if not leads:
            return {"total_leads": 0, "top_topics": ["Imtihonsiz qabul", "Grantlar", "Yotoqxona"]}

        # Count keyword occurrences
        text_corpus = " ".join([l.get("first_message", "") + " " + l.get("interest", "") for l in leads]).lower()
        
        topics = []
        if any(k in text_corpus for k in ["grant", "burs", "tekin"]):
            topics.append("Turkiyada 100% grant yutish shartlari")
        if any(k in text_corpus for k in ["imtihon", "yos", "attestat"]):
            topics.append("Attestat baholari bilan imtihonsiz qabul")
        if any(k in text_corpus for k in ["yotoqxona", "yashash", "viza"]):
            topics.append("Turkiyada talabalar yotoqxonasi va xavfsizlik")
        if any(k in text_corpus for k in ["tibbiyot", "doktor", "stomatologiya"]):
            topics.append("Tibbiyot va stomatologiya fakultetlariga qabul")
        if any(k in text_corpus for k in ["marmara", "itu", "hacettepe"]):
            topics.append("Istanbul va Anqara davlat universitetlari")

        if not topics:
            topics = ["Turkiyada ta'lim olish kafolati", "Oldindan to'lovsiz o'qishga kirish"]

        return {
            "total_leads": len(leads),
            "top_topics": topics
        }

    def generate_reactive_post(self) -> dict:
        """
        Creates a new marketing post (Q&A or Madina Reel)
        directly tailored to the most requested student topic.
        """
        analysis = self.analyze_leads_and_trends()
        trending_topic = analysis["top_topics"][0]

        print(f"[FEEDBACK LOOP] Top student demand detected: '{trending_topic}'")
        print("[FEEDBACK LOOP] Asking AI Brain to formulate a viral solution...")

        # Ask AI Brain to formulate high-impact Q&A or Reel
        prompt = (
            f"Talabalarimiz eng ko'p so'rayotgan muammo/mavzu: '{trending_topic}'.\n"
            "Arkadaş Consulting nomidan ushbu muammoni to'liq hal qiluvchi, yoshlarni "
            "tinchlantiruvchi va @arkadasuz ga murojaat qilishga undovchi 1 ta Savol va 1 ta Javob yoz.\n"
            "Format:\n"
            "SAVOL: ...\n"
            "JAVOB: ..."
        )
        ai_res = self.ai.think_and_generate(prompt)
        text = ai_res.get("text", "")

        q = "Turkiyada o'qish uchun qanday kafolatlar bor?"
        a = "Arkadaş Consulting bilan oldindan to'lov yo'q. Dastlab rasmiy qabul olasiz, keyin to'laysiz!"

        if "SAVOL:" in text and "JAVOB:" in text:
            try:
                parts = text.split("JAVOB:")
                q = parts[0].replace("SAVOL:", "").strip()
                a = parts[1].strip()
            except Exception:
                pass

        print("[FEEDBACK LOOP] Rendering reactive Q&A post...")
        post = self.cg.generate_qa_post(question=q[:120], answer=a[:200])
        return {
            "trending_topic": trending_topic,
            "post": post
        }

if __name__ == "__main__":
    fb = MarketingFeedbackLoop()
    res = fb.generate_reactive_post()
    print("Reactive Post Generated:", res["post"]["media_path"])
