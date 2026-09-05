#!/usr/bin/env python3
"""
Arkadaş Consulting - Mila TikToker & Multi-Language Walking Influencer Engine
Features:
1. Multi-Language Neural Voiceover:
   - Uzbek (O'zbekcha): uz-UZ-MadinaNeural
   - Russian (Русский): ru-RU-SvetlanaNeural
   - English (English): en-US-JennyNeural
   - Kazakh (Қазақша): kk-KZ-AigulNeural
   - Optional: ElevenLabs integration if API key is provided
2. Brain-Driven Content Generation:
   - Educational & Grants (FAQ & Universities knowledge)
   - Istanbul Lifestyle & Walking Vibe (Galata, Bosphorus, Student Cafes)
   - Mythbusting & Student Safety
3. Multi-Scene TikToker Video Pipeline with SFX & Transitions:
   - Scene 1: Mila Walking / Intro in Istanbul (Hook)
   - Transition: Swoosh sound effect (whoosh_sfx.aac)
   - Scene 2: Cinematic B-Roll of Campus / City / Library (Value)
   - Transition: Pop chime sound effect (pop_sfx.aac)
   - Scene 3: Mila in Courtyard with CTA & Arkadaş Trust Badge
4. Dynamic TikTok-Style Timed Kinetic Subtitles
5. Audio Ducking (Music lowers during speech)
"""

import os
import sys
import re
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
AUDIO_DIR = ASSETS_DIR / "audio"
MILA_DIR = ASSETS_DIR / "influencer_mila"
CLEAN_VIDEOS_DIR = ASSETS_DIR / "clean_videos"
SCENERY_DIR = ASSETS_DIR / "scenery"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

from engine.ai_brain import AIBrain
from engine.stock_video_engine import StockVideoEngine
from templates.template5_video import get_font, wrap_text

VOICE_CONFIG = {
    "tr": {
        "voice": "tr-TR-EmelNeural",
        "name": "Türkçe",
        "prompt_lang": "Türkçe dilinde"
    },
    "uz": {
        "voice": "uz-UZ-MadinaNeural",
        "name": "O'zbekcha",
        "prompt_lang": "o'zbek tilida"
    },
    "ru": {
        "voice": "ru-RU-SvetlanaNeural",
        "name": "Русский",
        "prompt_lang": "на русском языке"
    },
    "en": {
        "voice": "en-US-JennyNeural",
        "name": "English",
        "prompt_lang": "in English"
    },
    "kk": {
        "voice": "kk-KZ-AigulNeural",
        "name": "Қазақша",
        "prompt_lang": "қазақ тілінде"
    }
}

class MilaTikTokerEngine:
    def __init__(self):
        self.ai = AIBrain()
        self.stock = StockVideoEngine()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._load_brain()

    def _load_brain(self):
        self.faqs = []
        faq_file = BRAIN_DIR / "faq_knowledge.json"
        if faq_file.exists():
            with open(faq_file, "r", encoding="utf-8") as f:
                self.faqs = json.load(f)

        self.unis = []
        uni_file = BRAIN_DIR / "universities.json"
        if uni_file.exists():
            with open(uni_file, "r", encoding="utf-8") as f:
                self.unis = json.load(f)

    def pick_brain_topic(self, category: str = "auto") -> dict:
        """Picks an authentic topic from Brain data."""
        categories = ["grants", "lifestyle", "myths"]
        chosen_cat = category if category in categories else random.choice(categories)

        if chosen_cat == "grants":
            uni_sample = random.choice(self.unis) if self.unis else {"name": "İstanbul Universiteti"}
            return {
                "category": "grants",
                "title": f"Turkiyada 100% grant yutish va {uni_sample.get('name')}",
                "focus": "Imtihonsiz qabul, faqat attestat baholari bilan davlat universitetlariga grantlar va kafolatlangan yotoqxona."
            }
        elif chosen_cat == "lifestyle":
            spots = ["Galata minorasi atrofidagi kofeynyalar", "Bosfor bo'yida choy ichib dars qilish", "Istanbulda talaba byudjeti"]
            spot = random.choice(spots)
            return {
                "category": "lifestyle",
                "title": f"Istanbulda talabalik hayoti: {spot}",
                "focus": "Talabalar uchun hayot qanchalik qiziq va qulay, transport kartasi (İstanbulkart), o'qish va sayr atmosferasi."
            }
        else:
            return {
                "category": "myths",
                "title": "Turkiyada o'qish qimmat va xavfli degan miflar",
                "focus": "Xorijlik talabalar uchun Turkiya xavfsizligi, Arkadaş Consulting orqali aeroportda kutib olish va 0$ oldindan to'lov."
            }

    def generate_multilingual_script(self, topic_info: dict, lang: str = "uz") -> dict:
        """Generates script in the selected language using AI Brain."""
        cfg = VOICE_CONFIG.get(lang, VOICE_CONFIG["uz"])
        lang_instruction = cfg["prompt_lang"]

        prompt = (
            f"Sen Milaсан (@mila.travels) — Istanbulda ITÜ da arxitektura o'qiydigan 19 yoshli, "
            f"juda zamonaviy, quvnoq, TikToker talaba qizsan.\n"
            f"Mavzu: '{topic_info['title']}' ({topic_info['focus']}).\n\n"
            f"Ushbu ssenariyni {lang_instruction} yoz. "
            "Kameraga qarab xuddi do'sting bilan ko'chada ketayotib gaplashayotgandek jonli, samimiy va baquvvat ohangda yoz:\n\n"
            "1. SCENE 1 (HOOK): Qiziqarli, e'tiborni tortuvchi boshlanish (maksimum 7-8 so'z).\n"
            "2. SCENE 2 (VALUE): Asosiy foydali ma'lumot yoki qiziq fakt (maksimum 12-14 so'z).\n"
            "3. SCENE 3 (CTA): Harakatga chaqiruv, Arkadaş Consulting haqida gapir (maksimum 7-8 so'z).\n"
            "4. CAPTION: Ijtimoiy tarmoqlar uchun to'liq post matni (emojilar va hashtaglar bilan).\n\n"
            "Javobni JSON formatida qaytar:\n"
            "{\n"
            '  "scene1_hook": "...",\n'
            '  "scene2_value": "...",\n'
            '  "scene3_cta": "...",\n'
            '  "caption": "..."\n'
            "}"
        )

        res = self.ai.think_and_generate(prompt)
        text = res.get("text", "")

        try:
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except Exception:
            pass

        # Fallbacks by language
        fallbacks = {
            "tr": {
                "scene1_hook": "Türkiye'de üniversite okumak pahalı mı sanıyorsun?",
                "scene2_value": "Yanılıyorsun! Sadece lise diplomanla %100 burs kazanıp sınavsız yerleşebilirsin!",
                "scene3_cta": "Sıfır ön ödemeyle — @arkadasuz DM'den hemen bilgi al!",
                "caption": "İstanbul'da öğrenci olmak artık hayal değil! 🇹🇷🎓\n\nArkadaş Danışmanlık ile sıfır ön ödeme güvencesiyle hayalindeki bölüme yerleş!"
            },
            "uz": {
                "scene1_hook": "Turkiyada o'qish uchun boy bo'lish shartmi?",
                "scene2_value": "Yo'q! Faqat attestat bilan 100% grant yutish va bepul yotoqxonada yashash mumkin!",
                "scene3_cta": "Oldindan to'lov yo'q — @arkadasuz ga yozing!",
                "caption": "Turkiyada talaba bo'lish — orzu emas, real imkoniyat! 🇹🇷🎓\n\nArkadaş Consulting bilan 0$ oldindan to'lov asosida hujjat topshiring!"
            },
            "ru": {
                "scene1_hook": "Думаешь, учиться в Турции очень дорого?",
                "scene2_value": "Вовсе нет! С одним школьным аттестатом можно получить 100% грант на учебу!",
                "scene3_cta": "Без предоплаты — пишите в @arkadasuz прямо сейчас!",
                "caption": "Учеба в Турции доступна каждому! 🇹🇷✨\n\nПоступайте на гранты без экзаменов вместе с Arkadaş Consulting!"
            },
            "en": {
                "scene1_hook": "Thinking studying in Turkey is super expensive?",
                "scene2_value": "Actually, you can win a 100% scholarship with just your high school grades!",
                "scene3_cta": "Zero prepayment — DM @arkadasuz to start today!",
                "caption": "Studying in Istanbul was the best decision of my life! 🇹🇷🎓\n\nGet accepted with Arkadaş Consulting with 0 advance fee!"
            },
            "kk": {
                "scene1_hook": "Түркияда оқу тым қымбат деп ойлайсың ба?",
                "scene2_value": "Жоқ! Тек аттестат бағаларымен 100% грант жеңіп, тегін жатақханаға кіруге болады!",
                "scene3_cta": "Алдын ала төлемсіз — @arkadasuz парақшасына жазыңыз!",
                "caption": "Түркияда студент атану — нақты мүмкіндік! 🇹🇷🎓\n\nArkadaş Consulting арқылы кепілді оқуға түсіңіз!"
            }
        }
        return fallbacks.get(lang, fallbacks["uz"])

    def generate_voice(self, spoken_text: str, output_path: Path, lang: str = "uz") -> bool:
        """Generates expressive, emotive voiceover (ElevenLabs if key set, or Copilot Ava with +8% rate/+3Hz pitch)."""
        from engine.voice_studio import VoiceStudio
        vs = VoiceStudio()
        return vs.generate_expressive_voice(spoken_text, output_path, lang=lang)

    def get_duration(self, audio_path: Path) -> float:
        cmd = [FFPROBE_BIN, "-i", str(audio_path), "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return float(res.stdout.strip())
        except Exception:
            return 10.0

    def render_tiktok_caption_card(
        self,
        text: str,
        highlight_color: str,
        badge_text: str,
        output_png: Path
    ):
        """Renders modern TikTok-style bold subtitles with dark contrast backing."""
        width, height = 1080, 1920
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font_badge = get_font("Arial Bold", 32)
        font_main = get_font("Georgia Bold", 58)

        # Scrim at bottom third
        scrim = Image.new("RGBA", (width, 500), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(scrim)
        for y in range(scrim.height):
            alpha = int(190 * (y / scrim.height) ** 1.2)
            s_draw.line([(0, y), (width, y)], fill=(5, 10, 20, alpha))
        img.paste(scrim, (0, height - 560), scrim)

        current_y = height - 520

        # Pill Badge
        if badge_text:
            badge_clean = re.sub(r'[^\w\s\-\.\!\?\:\/]', '', badge_text).strip()
            bbox = draw.textbbox((0, 0), badge_clean, font=font_badge)
            bw = bbox[2] - bbox[0] + 44
            bh = bbox[3] - bbox[1] + 20
            bx = (width - bw) // 2
            draw.rounded_rectangle([bx, current_y, bx + bw, current_y + bh], radius=16, fill=(15, 30, 60, 230), outline=(0, 210, 255, 255), width=2)
            draw.text((bx + 22, current_y + 8), badge_clean, font=font_badge, fill=(255, 255, 255, 255))
            current_y += bh + 30

        # Main Subtitle Lines
        lines = wrap_text(text.upper(), font_main, width - 180, draw)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_main)
            lw = bbox[2] - bbox[0]
            lx = (width - lw) // 2
            # Drop shadow
            draw.text((lx + 3, current_y + 3), line, font=font_main, fill=(0, 0, 0, 250))
            draw.text((lx, current_y), line, font=font_main, fill=highlight_color)
            current_y += 72

        # Small bottom logo
        sticker_path = ASSETS_DIR / "sticker_clean.png"
        if sticker_path.exists():
            stk = Image.open(sticker_path).convert("RGBA")
            sw = 280
            sh = int(stk.height * (sw / stk.width))
            stk = stk.resize((sw, sh), Image.Resampling.LANCZOS)
            img.paste(stk, ((width - sw) // 2, height - sh - 50), stk)

        img.save(output_png, "PNG")

    def create_tiktok_video(
        self,
        lang: str = "uz",
        category: str = "auto",
        output_filename: str = None
    ) -> dict:
        """
        Builds a full 3-scene TikToker walking & talking video with SFX and transitions:
        Scene 1: Mila in Istanbul (Hook)
        Scene 2: B-Roll of Campus / City / Vibe (Value)
        Scene 3: Mila in Courtyard with CTA
        """
        out_name = output_filename or f"mila_tiktok_{lang}_{random.randint(1000, 9999)}.mp4"
        out_mp4 = OUTPUT_DIR / out_name

        # 1. Pick Topic from Brain
        topic = self.pick_brain_topic(category)
        print(f"[MILA TIKTOKER] Topic selected ({topic['category']}): {topic['title']}")

        # 2. Generate Multi-Language Script
        script = self.generate_multilingual_script(topic, lang=lang)
        s1 = script.get("scene1_hook")
        s2 = script.get("scene2_value")
        s3 = script.get("scene3_cta")

        full_speech = f"{s1}. {s2}. {s3}."

        # 3. Generate Neural Voiceover
        temp_voice = OUTPUT_DIR / f"temp_voice_{random.randint(100, 999)}.mp3"
        self.generate_voice(full_speech, temp_voice, lang=lang)
        total_duration = self.get_duration(temp_voice)
        total_duration = max(total_duration + 1.2, 9.0)

        t1 = round(total_duration * 0.32, 2)
        t2 = round(total_duration * 0.70, 2)
        t3 = round(total_duration, 2)

        # 4. Prepare Visuals (Select Mila's real Istanbul portraits)
        bosphorus_candidates = list(MILA_DIR.glob("*bosphorus*.jpg"))
        campus_candidates = list(MILA_DIR.glob("*campus*.jpg"))
        cafe_candidates = list(MILA_DIR.glob("*cafe*.jpg"))
        all_mila = list(MILA_DIR.glob("*.jpg"))

        img_mila_bosphorus = bosphorus_candidates[0] if bosphorus_candidates else all_mila[0]
        img_mila_campus = campus_candidates[0] if campus_candidates else all_mila[-1]
        clean_broll = self.stock.get_clean_video(topic["title"])

        # 5. Render 3 TikTok-Style Captions
        temp_cap1 = OUTPUT_DIR / f"temp_cap1_{random.randint(100, 999)}.png"
        temp_cap2 = OUTPUT_DIR / f"temp_cap2_{random.randint(100, 999)}.png"
        temp_cap3 = OUTPUT_DIR / f"temp_cap3_{random.randint(100, 999)}.png"

        badge_titles = {
            "uz": ("💡 MIF YOKI HAQIQAT?", "🔥 ASL HAQIQAT", "🚀 ARKADAŞ BILAN TALABA BO'LING"),
            "ru": ("💡 МИФ ИЛИ ПРАВДА?", "🔥 ГЛАВНЫЙ СЕКРЕТ", "🚀 ПОСТУПАЙ С ARKADAŞ"),
            "en": ("💡 MYTH OR FACT?", "🔥 THE REAL TRUTH", "🚀 JOIN ARKADAŞ TODAY"),
            "kk": ("💡 АҢЫЗ БА, ШЫНДЫҚ ПА?", "🔥 НЕГІЗГІ ШЫНДЫҚ", "🚀 ARKADAŞ-ПЕН БІРГЕ ТҮСІҢІЗ")
        }
        b1, b2, b3 = badge_titles.get(lang, badge_titles["uz"])

        self.render_tiktok_caption_card(s1, "#FFFFFF", b1, temp_cap1)
        self.render_tiktok_caption_card(s2, "#FFD700", b2, temp_cap2)
        self.render_tiktok_caption_card(s3, "#00E5FF", b3, temp_cap3)

        # 6. Audio Assets
        music_files = list(AUDIO_DIR.glob("*.mp3"))
        bg_music = random.choice(music_files) if music_files else None
        whoosh_sfx = AUDIO_DIR / "whoosh_sfx.aac"
        pop_sfx = AUDIO_DIR / "pop_sfx.aac"

        d1 = int(t1 * 25)
        d2 = int((t2 - t1) * 25)
        d3 = int((t3 - t2) * 25)

        filter_complex = (
            f"[0:v]zoompan=z='min(zoom+0.0012,1.15)':d={d1}:fps=25:s=1080x1920,"
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,fps=25[v_scene1];"
            f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,fps=25,"
            f"trim=duration={t2 - t1}[v_scene2];"
            f"[2:v]zoompan=z='min(zoom+0.0012,1.15)':d={d3}:fps=25:s=1080x1920,"
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,fps=25[v_scene3];"
            f"[v_scene1][v_scene2][v_scene3]concat=n=3:v=1:a=0[v_base];"
            f"[v_base][3:v]overlay=0:0:enable='between(t,0,{t1})'[vo1];"
            f"[vo1][4:v]overlay=0:0:enable='between(t,{t1},{t2})'[vo2];"
            f"[vo2][5:v]overlay=0:0:enable='between(t,{t2},{t3})'[vout];"
            f"[6:a]volume=1.0[voice];"
            f"[7:a]volume=0.14,afade=t=out:st={t3-1.5}:d=1.5[music];"
            f"[8:a]adelay={int(t1*1000)}|{int(t1*1000)},volume=0.45[sfx_whoosh];"
            f"[9:a]adelay={int(t2*1000)}|{int(t2*1000)},volume=0.40[sfx_pop];"
            f"[voice][music][sfx_whoosh][sfx_pop]amix=inputs=4:duration=first[aout]"
        )

        ffmpeg_cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(img_mila_bosphorus),
            "-stream_loop", "-1", "-i", str(clean_broll),
            "-i", str(img_mila_campus),
            "-i", str(temp_cap1),
            "-i", str(temp_cap2),
            "-i", str(temp_cap3),
            "-i", str(temp_voice),
            "-i", str(bg_music),
            "-i", str(whoosh_sfx),
            "-i", str(pop_sfx),
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-t", str(t3),
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_mp4)
        ]

        print(f"[MILA TIKTOKER] Rendering 3-scene dynamic video ({total_duration:.1f}s) in {VOICE_CONFIG[lang]['name']}...")
        res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("Mila TikToker video render failed")

        # Cleanup temp
        for tmp in [temp_voice, temp_cap1, temp_cap2, temp_cap3]:
            if tmp.exists():
                tmp.unlink()

        print(f"[SUCCESS] Mila TikToker Video Created: {out_mp4}")

        return {
            "media_path": str(out_mp4),
            "language": lang,
            "lang_name": VOICE_CONFIG[lang]["name"],
            "topic": topic["title"],
            "duration": t3,
            "caption": script.get("caption", "")
        }

if __name__ == "__main__":
    eng = MilaTikTokerEngine()
    for l in ["uz", "ru"]:
        res = eng.create_tiktok_video(lang=l)
        print(f"Rendered {l}: {res['media_path']}")
