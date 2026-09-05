#!/usr/bin/env python3
"""
Arkadaş Consulting - AI Influencer Engine ("Madina Karimova")
Persona: 20-year-old Uzbek female student at Marmara University in Istanbul.
Came to Turkey via Arkadaş Consulting on a 100% grant.
Features:
1. Generates authentic first-person Uzbek video scripts & captions (using Gemini AI)
2. Produces cinematic 9:16 vertical Reels with Madina's portrait + Ken Burns motion + chill acoustic background music + modern typography
3. Solves student questions with relatable, sisterly advice (opadek maslahat)
"""

import os
import sys
import json
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

BRAIN_DIR = BASE_DIR / "brain_data"
ASSETS_DIR = BASE_DIR / "assets"
INFLUENCER_DIR = ASSETS_DIR / "influencer"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"

from engine.ai_brain import AIBrain
from templates.template5_video import create_aesthetic_overlay

class InfluencerEngine:
    def __init__(self):
        self.ai = AIBrain()
        self._load_persona()

    def _load_persona(self):
        p_file = BRAIN_DIR / "influencer_persona.json"
        if p_file.exists():
            with open(p_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "personas" in data:
                    self.personas = data["personas"]
                    self.active_key = data.get("active_persona", "mila")
                else:
                    self.personas = {"madina": data}
                    self.active_key = "madina"
        else:
            self.personas = {
                "mila": {
                    "name": "Mila",
                    "handle": "@mila.travels",
                    "university": "İstanbul Texnika Universiteti (İTÜ)",
                    "image_folder": "assets/influencer_mila"
                }
            }
            self.active_key = "mila"

    def generate_influencer_script(self, topic: str = "Turkiyada talabalik hayoti va grantlar", persona_key: str = None) -> dict:
        """
        Uses AI Brain to generate a natural, first-person Reels script
        from Mila or Madina's voice with Hook, Headline, and Call to action.
        """
        key = persona_key or self.active_key
        p_info = self.personas.get(key, self.personas.get("mila", {}))
        name = p_info.get("name", "Mila")
        handle = p_info.get("handle", "@mila.travels")
        uni = p_info.get("university", "İstanbul Texnika Universiteti")

        prompt = (
            f"Sen {name}san ({handle}) — Istanbulda {uni}da "
            f"Arkadaş Consulting orqali 100% grant bilan o'qiyotgan zamonaviy, quvnoq, samimiy talaba qizsan.\n"
            f"Mavzu: '{topic}'.\n\n"
            "Instagram Reels uchun 3 ta qismdan iborat qisqa, zamonaviy matn yoz:\n"
            "1. ITALIC_HOOK: 1 ta qisqa qiziqtiruvchi savol (maksimum 6-7 so'z)\n"
            "2. BOLD_HEADLINE: 1 ta katta, esda qolarli sarlavha (maksimum 8 so'z)\n"
            "3. SUB_TAGLINE: 1 ta dalda beruvchi shior (maksimum 6 so'z)\n"
            "4. POST_CAPTION: Instagram/Telegram uchun samimiy post matni (o'z tajribangdan gapir, 'Arkadaş bilan bog'laning' deb tugat, emojilar va hashtaglar bilan).\n\n"
            "Javobni JSON formatida ber:\n"
            "{\n"
            '  "italic_hook": "...",\n'
            '  "bold_headline": "...",\n'
            '  "sub_tagline": "...",\n'
            '  "post_caption": "..."\n'
            "}"
        )

        res = self.ai.think_and_generate(prompt)
        text = res.get("text", "")

        try:
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                data = json.loads(m.group(0))
                return data
        except Exception:
            pass

        return {
            "italic_hook": "Istanbulda o'qish orzuingizmi?",
            "bold_headline": "ARKADAŞ BILAN 100% GRANT ASOSIDA TALABA BO'LING!",
            "sub_tagline": "Oldindan to'lov yo'q — Kafolatlangan!",
            "post_caption": (
                f"Hey do'stlar! Men {name}man ✨\n\n"
                f"Turkiyada talaba bo'lish hayotimdagi eng to'g'ri qaror bo'ldi. "
                "Arkadaş Consulting bilan imtihonsiz va oldindan to'lovsiz grant yutdim!\n\n"
                "Siz ham orzuingizni kechiktirmang! @arkadasuz ga yozing 🇹🇷❤️"
            )
        }

    def generate_spoken_audio(self, text: str, output_path: Path) -> bool:
        """Generates authentic Uzbek spoken voice for Madina using edge-tts."""
        try:
            # Clean text of markdown and emojies for clean pronunciation
            import re
            clean_text = re.sub(r'[*#_~`]', '', text)
            clean_text = clean_text.replace('@arkadasuz', 'Arkadaş Consulting').replace('@', '')
            cmd = [
                "edge-tts",
                "--voice", "uz-UZ-MadinaNeural",
                "--text", clean_text,
                "--write-media", str(output_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.returncode == 0 and output_path.exists()
        except Exception as e:
            print(f"[TTS Error] {e}")
            return False

    def create_influencer_reel(
        self,
        topic: str = "Turkiyada grant va xavfsiz yotoqxona",
        output_filename: str = None,
        duration_seconds: int = 8,
        with_voice: bool = True,
        persona_key: str = "mila"
    ) -> dict:
        """
        Creates a high-end 9:16 vertical Reel:
        - Photo: Mila or Madina's portrait in Istanbul
        - Motion: Smooth Ken Burns cinematic zoom
        - Voice: Real Uzbek AI Neural Voice (speaking!)
        - Audio: Chill acoustic Istanbul background music (ducked behind voice)
        - Typography: Aesthetic Italic Hook + Bold Headline + Subtitle
        - Brand: Arkadaş logo at bottom
        """
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        p_info = self.personas.get(persona_key, self.personas.get("mila", {}))
        influencer_name = p_info.get("name", "Mila")
        img_folder = BASE_DIR / p_info.get("image_folder", "assets/influencer_mila")

        out_name = output_filename or f"{persona_key}_reel_{random.randint(1000, 9999)}.mp4"
        out_path = OUTPUT_DIR / out_name
        temp_overlay = OUTPUT_DIR / f"temp_{persona_key}_overlay_{random.randint(100, 999)}.png"
        temp_voice = OUTPUT_DIR / f"temp_voice_{random.randint(100, 999)}.mp3"

        # 1. Select Influencer's image
        images = list(img_folder.glob("*.jpg")) + list(img_folder.glob("*.png"))
        if not images:
            images = list(INFLUENCER_DIR.glob("*.jpg"))
        
        # Prioritize 9:16 vertical student/campus/cafe photos
        preferred = [im for im in images if any(k in im.name.lower() for k in ["bosphorus", "campus", "cafe"])]
        chosen_img = random.choice(preferred) if preferred else (random.choice(images) if images else (ASSETS_DIR / "scenery" / "galata_tower.jpg"))

        # 2. Generate Script via AI
        script = self.generate_influencer_script(topic, persona_key=persona_key)
        hook = script.get("italic_hook", "Istanbulda o'qish orzuingizmi?")
        headline = script.get("bold_headline", "ARKADAŞ BILAN 100% GRANT ASOSIDA TALABA BO'LING!")
        sub = script.get("sub_tagline", "Oldindan to'lov yo'q — Kafolatlangan!")

        # 3. Create Typography Overlay
        width, height = 1080, 1920
        create_aesthetic_overlay(
            width=width,
            height=height,
            italic_hook=hook,
            bold_headline=headline,
            sub_tagline=sub,
            output_png=temp_overlay
        )

        # 4. Generate Neural Voice (Madina Speaking!)
        voice_success = False
        voice_duration = duration_seconds
        if with_voice:
            spoken_text = f"{hook}. {headline}. {sub}. Qolganini Arkadaş Consulting hal qiladi!"
            voice_success = self.generate_spoken_audio(spoken_text, temp_voice)
            if voice_success:
                # Measure voice duration with ffprobe
                probe_cmd = [
                    "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe",
                    "-i", str(temp_voice),
                    "-show_entries", "format=duration",
                    "-v", "quiet", "-of", "csv=p=0"
                ]
                try:
                    dur_out = subprocess.run(probe_cmd, capture_output=True, text=True).stdout.strip()
                    voice_duration = max(int(float(dur_out)) + 1, 6)
                except Exception:
                    voice_duration = duration_seconds
        
        final_duration = voice_duration if voice_success else duration_seconds

        # 5. Select background audio
        audio_files = list(AUDIO_DIR.glob("*.mp3"))
        chosen_audio = random.choice(audio_files) if audio_files else None

        # 6. Render with FFmpeg (Video + Ken Burns + Music + Voice)
        total_frames = final_duration * 30
        zoom_step = 0.15 / total_frames

        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+{zoom_step:.6f},1.20)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30[bg];"
            f"[bg][1:v]overlay=0:0[v]"
        )

        ffmpeg_cmd = [
            FFMPEG_BIN,
            "-y",
            "-loop", "1",
            "-i", str(chosen_img),
            "-i", str(temp_overlay)
        ]

        if voice_success and chosen_audio:
            # Both voice and background music: duck music under voice
            ffmpeg_cmd.extend([
                "-i", str(temp_voice),
                "-i", str(chosen_audio),
                "-filter_complex", (
                    f"{filter_complex};"
                    f"[3:a]volume=0.18,afade=t=out:st={final_duration-1.5}:d=1.5[music];"
                    f"[2:a]volume=1.0[voice];"
                    f"[voice][music]amix=inputs=2:duration=first[aout]"
                ),
                "-map", "[v]",
                "-map", "[aout]"
            ])
        elif voice_success:
            # Only voice
            ffmpeg_cmd.extend([
                "-i", str(temp_voice),
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "2:a"
            ])
        elif chosen_audio:
            # Only music
            ffmpeg_cmd.extend([
                "-i", str(chosen_audio),
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "2:a",
                "-af", f"volume=0.35,afade=t=in:ss=0:d=1,afade=t=out:st={final_duration-1.5}:d=1.5"
            ])
        else:
            ffmpeg_cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "[v]"
            ])

        ffmpeg_cmd.extend([
            "-t", str(final_duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "21",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_path)
        ])

        print(f"[INFO] Rendering {influencer_name} Reel ({chosen_img.name} | Voice: {voice_success} | Duration: {final_duration}s)...")
        res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("FFmpeg rendering failed")

        # Cleanup temp
        if temp_overlay.exists():
            temp_overlay.unlink()
        if temp_voice.exists():
            temp_voice.unlink()

        print(f"[SUCCESS] AI Influencer {influencer_name} Reel Created: {out_path}")

        return {
            "type": "influencer_reels",
            "influencer": influencer_name,
            "persona_key": persona_key,
            "media_path": str(out_path),
            "image_used": str(chosen_img),
            "audio_used": chosen_audio.name if chosen_audio else "None",
            "voice_enabled": voice_success,
            "duration": final_duration,
            "caption": script.get("post_caption", "")
        }

if __name__ == "__main__":
    engine = InfluencerEngine()
    print("Testing AI Influencer Reel Generation...")
    result = engine.create_influencer_reel()
    print("\n--- INFLUENCER REEL GENERATED ---")
    print("Video:", result["media_path"])
    print("Caption:\n", result["caption"])
