#!/usr/bin/env python3
"""
Arkadaş Consulting - Expressive Human Voice Studio (ElevenLabs + Copilot Ava)
Solves the "monotone / robotic" issue by providing:
1. ElevenLabs API Integration with youthful, emotive female influencer voices:
   - "Bella" (EXAVITQu4vr4xnSDxMaL) - Enthusiastic, cheerful, friendly TikTok creator
   - "Rachel" (21m00Tcm4TlvDq8ikWAM) - Warm, articulate, calm student
   - "Domi" (AZnzlk1XvdvUeBnXmlld) - Energetic, vibrant, confident
2. Expressive Microsoft Copilot Neural fallback (en-US-AvaMultilingualNeural):
   - Conversational, caring, expressive student tone with custom pitch & rate (+8% speed, +3Hz pitch)
3. Direct key management via bot_config.json
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "bot_config.json"

class VoiceStudio:
    ELEVENLABS_VOICES = {
        "bella": {
            "id": "EXAVITQu4vr4xnSDxMaL",
            "name": "Bella (Quvnoq va Jonli TikToker Qiz)",
            "description": "Eng tabiiy, quvnoq, his-tuyg'uli yosh qiz ovozi."
        },
        "rachel": {
            "id": "21m00Tcm4TlvDq8ikWAM",
            "name": "Rachel (Samimiy va Muloyim)",
            "description": "Iliq, muloyim va tushuntiruvchi talaba qiz."
        },
        "domi": {
            "id": "AZnzlk1XvdvUeBnXmlld",
            "name": "Domi (Energetik va Ishonchli)",
            "description": "Vibrant, kuchli va chaqiruvchi ovoz."
        }
    }

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

    def get_elevenlabs_key(self) -> str:
        return os.environ.get("ELEVENLABS_API_KEY") or self.config.get("elevenlabs_api_key", "")

    def set_elevenlabs_key(self, api_key: str):
        self.config["elevenlabs_api_key"] = api_key.strip()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"[SUCCESS] ElevenLabs API Key saqlandi: {api_key[:6]}...{api_key[-4:]}")

    def generate_elevenlabs_voice(
        self,
        text: str,
        output_path: Path,
        voice_key: str = "bella"
    ) -> bool:
        """Generates hyper-realistic emotive human speech via ElevenLabs API."""
        api_key = self.get_elevenlabs_key()
        if not api_key:
            return False

        voice_id = self.ELEVENLABS_VOICES.get(voice_key, self.ELEVENLABS_VOICES["bella"])["id"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.38,         # Lower = more emotion and variation
                "similarity_boost": 0.85,  # High fidelity
                "style": 0.45,             # Expressive delivery
                "use_speaker_boost": True
            }
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    with open(output_path, "wb") as f:
                        f.write(resp.read())
                    print(f"[ElevenLabs SUCCESS] Generated ultra-realistic voice: {output_path}")
                    return True
        except Exception as e:
            print(f"[ElevenLabs Error] {e}")
            return False

    def generate_expressive_voice(
        self,
        text: str,
        output_path: Path,
        lang: str = "uz"
    ) -> bool:
        """
        Attempts ElevenLabs first if API key exists.
        Otherwise uses Microsoft's most expressive conversational voice (Ava/Svetlana)
        with +8% speed and +3Hz pitch to eliminate flat/robotic delivery.
        """
        # 1. Try ElevenLabs
        if self.get_elevenlabs_key():
            success = self.generate_elevenlabs_voice(text, output_path)
            if success:
                return True

        # 2. Emotive Neural Fallback
        # Clean markdown
        import re
        clean = re.sub(r'[*#_~`@]', '', text).replace('arkadasuz', 'Arkadaş Consulting')

        # Select correct native neural voice for each language:
        if lang == "tr":
            voice = "tr-TR-EmelNeural"
            rate = "+6%"
            pitch = "+2Hz"
        elif lang == "uz":
            voice = "uz-UZ-MadinaNeural"
            rate = "+6%"
            pitch = "+2Hz"
        elif lang == "ru":
            voice = "ru-RU-SvetlanaNeural"
            rate = "+5%"
            pitch = "+2Hz"
        elif lang == "en":
            voice = "en-US-AvaMultilingualNeural"
            rate = "+6%"
            pitch = "+2Hz"
        elif lang == "kk":
            voice = "kk-KZ-AigulNeural"
            rate = "+5%"
            pitch = "+2Hz"
        else:
            voice = "uz-UZ-MadinaNeural"
            rate = "+5%"
            pitch = "+2Hz"

        try:
            cmd = [
                "edge-tts",
                "--voice", voice,
                f"--rate={rate}",     # Energetic youthful delivery
                f"--pitch={pitch}",   # Brighter inflection
                "--text", clean,
                "--write-media", str(output_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.returncode == 0 and output_path.exists()
        except Exception as e:
            print(f"[VoiceStudio Error] {e}")
            return False

if __name__ == "__main__":
    vs = VoiceStudio()
    test_file = BASE_DIR / "output" / "expressive_test.mp3"
    test_text = "Salom do'stlar! Men Milaman. Istanbulda o'qish judayam ajoyib, siz ham keling!"
    vs.generate_expressive_voice(test_text, test_file, lang="uz")
    print("Expressive voice test created:", test_file)
