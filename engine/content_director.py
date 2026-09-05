#!/usr/bin/env python3
"""
Arkadaş Consulting - Unified Content Director (Fastlane Architecture)
Central router for all marketing assets:
1. Video Engine:
   - Faced (Yüzlü):
     * UGC Vlogger: Full-motion real creator with hand gestures & podcast mic
     * Mila (@mila.travels): 19yo European/Uzbek student
     * Madina (@madina_in_istanbul): 20yo Uzbek student
   - Faceless (Yüzsüz / Manzaralı):
     * 4K Drone/Istanbul B-roll + Progressive Satır-Satır Kinetik Subtitr + Blok3 Trend Şarkı
2. Post Engine:
   - Faced: Mila or Madina acceptance / story banners
   - Faceless: Scenic Q&A, Services Checklist, Grant Quiz
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from engine.fastlane_faceless_engine import FastlaneFacelessEngine
from engine.fastlane_ugc_engine import FastlaneUGCEngine
from engine.fastlane_vlogger_pro import FastlaneVloggerPro
from engine.mila_tiktoker_engine import MilaTikTokerEngine
from engine.content_generator import ContentGenerator

class ContentDirector:
    def __init__(self):
        self.faceless_eng = FastlaneFacelessEngine()
        self.ugc_eng = FastlaneUGCEngine()
        self.vlogger_pro = FastlaneVloggerPro()
        self.mila_eng = MilaTikTokerEngine()
        self.gen = ContentGenerator()

    def create_video(
        self,
        mode: str = "faceless",         # "faceless" or "faced"
        creator_type: str = "vlogger_pro", # "vlogger_pro", "ugc", "mila", "madina"
        music_type: str = "blok3",       # "blok3" or "chill"
        topic: str = "Turkiyada 100% grant yutish va yotoqxona",
        lang: str = "uz"
    ) -> dict:
        """Generates video according to user selection."""
        if mode == "faceless":
            return self.faceless_eng.create_faceless_video(
                topic=topic,
                music_type=music_type
            )
        else:
            if creator_type in ("vlogger_pro", "ugc"):
                return self.vlogger_pro.create_vlogger_pro_video(
                    topic=topic,
                    lang=lang,
                    music_type=music_type
                )
            elif creator_type == "mila":
                return self.mila_eng.create_tiktok_video(
                    lang=lang,
                    category="grants"
                )
            else:
                from engine.influencer_engine import InfluencerEngine
                ie = InfluencerEngine()
                return ie.create_influencer_reel(persona_key="madina", with_voice=True)

    def create_post(
        self,
        mode: str = "faceless",         # "faceless" or "faced"
        post_type: str = "checklist",   # "qa", "checklist", "acceptance", "riddle"
        name: str = "Bekzod Rahimov",
        uni: str = "İstanbul Universiteti",
        dept: str = "Xalqaro Huquq",
        grant: str = "100% GRANT"
    ) -> dict:
        """Generates post according to user selection."""
        if mode == "faced":
            return self.gen.generate_acceptance_post(name, uni, dept, grant)
        else:
            if post_type == "qa":
                return self.gen.generate_qa_post()
            elif post_type == "riddle":
                return self.gen.generate_riddle_post()
            else:
                return self.gen.generate_checklist_post()

if __name__ == "__main__":
    cd = ContentDirector()
    v1 = cd.create_video(mode="faceless", music_type="blok3")
    print("Faceless Video:", v1["media_path"])
