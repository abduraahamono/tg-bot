#!/usr/bin/env python3
"""
Arkadaş Consulting - Free AI Video & Avatar Engines Hub (Dunyo Bepul Limitlari)
Connects all free-tier and free-credit AI video, voice, and avatar generators:

1. Kling AI (klingai.com) -> Har kuni 66 ta BEPUL kredit! Dunyoning #1 real inson harakatlantiruvchisi.
2. Hailuo AI / Minimax (hailuoai.video) -> Bepul kunlik limitlar. Eng tabiiy yuz va tana harakatlari.
3. Luma Dream Machine (lumalabs.ai) -> Oyiga 30 ta bepul video generatsiya.
4. Hedra (hedra.com) -> Bepul gapiradigan 3D xarakter va ifodali bosh harakatlari.
5. Pika Art (pika.art) -> Har kuni bepul kreditlar va Lip-Sync.
6. Fal.ai (fal.ai) -> Ro'yxatdan o'tganda $10 bepul balans (Wan2.1, Kling, Minimax API).
7. HuggingFace ZeroGPU -> Bepul Nvidia H100 quvvati (Wav2Lip, LivePortrait, SadTalker).
8. ElevenLabs (elevenlabs.io) -> Har oy 10,000 bepul belgi (Eng hissiyotli qiz ovozlari).
9. Google AI Studio (aistudio.google.com) -> Kuniga 1500 ta bepul so'rov (Gemini 2.0 Flash).
10. Microsoft Edge-TTS -> 100% bepul va cheksiz jonli ovozlar.
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "bot_config.json"

FREE_PLATFORMS = {
    "kling": {
        "name": "Kling AI",
        "url": "https://klingai.com",
        "free_tier": "Har kuni 66 ta BEPUL kredit (Kunlik yangilanadi)",
        "capabilities": "Fotodan 100% haqiqiy yuradigan, gapiradigan va harakatlanadigan inson videosi",
        "best_for": "Mila Istanbul ko'chalarida yurib selfi olib gapirishi"
    },
    "hailuo": {
        "name": "Hailuo AI (Minimax)",
        "url": "https://hailuoai.video",
        "free_tier": "Kunlik bepul generatsiyalar",
        "capabilities": "Gollivud darajasidagi tana va qo'l harakatlari, jonli nigohlar",
        "best_for": "Universitet kafesida kofe ichib gapirayotgan talaba vlogger"
    },
    "luma": {
        "name": "Luma Dream Machine",
        "url": "https://lumalabs.ai/dream-machine",
        "free_tier": "Har oy 30 ta BEPUL yuqori sifatli video",
        "capabilities": "Kamera harakati (zoom in, pan, orbit), fotorealistik 4K dinamika",
        "best_for": "Kampus va daryo bo'yida dinamik kamera o'tishlari"
    },
    "hedra": {
        "name": "Hedra AI (Character-2)",
        "url": "https://www.hedra.com",
        "free_tier": "Har kuni bepul audio va video sinxronlash",
        "capabilities": "Audio berilsa, qahramonning boshini, ko'zlarini va yuzini tabiiy harakatlantiradi",
        "best_for": "Mila portretini ovoz bilan jonlantirish"
    },
    "pika": {
        "name": "Pika Art",
        "url": "https://pika.art",
        "free_tier": "Kunlik bepul kreditlar",
        "capabilities": "Lip-sync, sound effects va matndan video yaratish",
        "best_for": "Qisqa 4 soniyalik dinamik TikTok hooklari"
    },
    "fal": {
        "name": "Fal.ai Developer Studio",
        "url": "https://fal.ai",
        "free_tier": "Yangi hisob ochilganda bepul balans / sinov",
        "capabilities": "Wan 2.1, Kling va Minimax uchun to'g'ridan-to'g'ri Python API",
        "best_for": "Avtomatlashtirilgan backend video ishlab chiqarish"
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "url": "https://elevenlabs.io",
        "free_tier": "Har oy 10,000 bepul belgi (Karta shart emas)",
        "capabilities": "Dunyoning eng yaxshi kulgi, nafas va hissiyotli qiz ovozlari (Bella, Rachel)",
        "best_for": "Duyguli va tabiiy inson ovozi"
    }
}

class FreeAIHub:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_prompts_for_mila_walking_vlog(self, topic: str = "Turkiyada 100% grant yutish") -> dict:
        """
        Kling, Hailuo yoki Luma ga tashlab 10 soniyada 100% real inson videosi
        olish uchun tayyor professional promptlar to'plami.
        """
        return {
            "kling_prompt": (
                "Hyper-realistic 9:16 vertical smartphone selfie vlog of Mila, a gorgeous 19-year-old female student with light blonde wavy hair. "
                "She is walking outdoors in Istanbul near Galata and university campus, holding the phone in her hand, smiling warmly, talking energetically directly into the camera lens. "
                "Natural handheld camera motion, organic walking bounce, soft breeze gently moving her hair, daylight golden hour, cinematic 4k, lifelike facial expressions, nodding and lively hand gestures."
            ),
            "hailuo_prompt": (
                "A candid 9:16 vertical TikTok vlog video of a friendly 19-year-old student girl sitting in a vibrant Istanbul university cafe holding an iced coffee. "
                "She looks into the camera and speaks passionately with natural smiles, blinking, and expressive hand gestures. Realistic skin texture, modern aesthetic, natural ambient lighting, 4K resolution."
            ),
            "luma_prompt": (
                "Camera slowly orbits around a stylish 19yo European-Uzbek girl standing in Istanbul Bosphorus coastline, she enthusiastically speaks to the viewer, laughing naturally and gesturing towards the university in the background, ultra high definition."
            )
        }

    def prepare_free_generation_package(self, output_dir: Path, topic: str = "Turkiyada 100% grant") -> dict:
        """
        Kling / Hailuo / Hedra ga yuklash uchun Mila'ning 4K fotosi, ovoz fayli va promptini bitta papkaga tayyorlaydi.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        from engine.voice_studio import VoiceStudio
        vs = VoiceStudio()

        script = f"Salom! Turkiyada 100% grant yutish haqiqat! Arkadaş Consulting bilan hoziroq boshlang!"
        voice_path = output_dir / "mila_speech.mp3"
        vs.generate_expressive_voice(script, voice_path, lang="uz")

        prompts = self.get_prompts_for_mila_walking_vlog(topic)
        prompt_txt = output_dir / "free_ai_prompts.txt"
        with open(prompt_txt, "w", encoding="utf-8") as f:
            f.write("=== BEPUL AI SAYTLARI UCHUN PROMPTLAR VA QO'LLANMA ===\n\n")
            f.write(f"1. KLING AI (https://klingai.com - Har kuni 66 kredit bepul):\n")
            f.write(prompts["kling_prompt"] + "\n\n")
            f.write(f"2. HAILUO AI (https://hailuoai.video - Bepul generatsiya):\n")
            f.write(prompts["hailuo_prompt"] + "\n\n")
            f.write(f"3. HEDRA AI (https://www.hedra.com - Bepul):\n")
            f.write("Portretni yuklang + mila_speech.mp3 ni yuklang -> Bosh harakatlari bilan gapirib beradi!\n")

        # Copy front portrait
        front_img = BASE_DIR / "assets" / "influencer_mila" / "mila_00_reference_front.jpg"
        target_img = output_dir / "mila_reference_face.jpg"
        if front_img.exists():
            import shutil
            shutil.copy(front_img, target_img)

        return {
            "package_dir": str(output_dir),
            "face_image": str(target_img),
            "voice_audio": str(voice_path),
            "prompts_file": str(prompt_txt),
            "prompts": prompts
        }

if __name__ == "__main__":
    hub = FreeAIHub()
    pkg = hub.prepare_free_generation_package(BASE_DIR / "output" / "free_ai_package")
    print("Free AI Package ready at:", pkg["package_dir"])
