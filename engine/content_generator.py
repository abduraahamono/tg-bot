#!/usr/bin/env python3
"""
Arkadaş Consulting - Content Generation Engine
Generates Uzbek posts and reels scripts for social media based on the brand brain.
Supports:
1. University Guide Posts (Universitet haqida to'liq qo'llanma)
2. Q&A Posts (Savol-Javob) + generates Template 1 image
3. Engagement & Riddle Posts (Topishmoq / Qiziqarli savol) + generates Template 2 image
4. Service & Grant Promo Posts (Xizmatlar va Grant e'loni) + generates Template 3 image
5. Student Acceptance Celebration Post (Talaba qabuli) + generates Template 4 image
6. Reels / Shorts Video Post + generates Template 5 MP4 video

Supports Gemini API if GEMINI_API_KEY is provided, otherwise uses high-quality
dynamic knowledge-based templates from brain_data.
"""

import os
import sys
import json
import random
from pathlib import Path
from typing import Optional, Dict, Any, List

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

BRAIN_DIR = BASE_DIR / "brain_data"
OUTPUT_DIR = BASE_DIR / "output"

# Import Template Generators
from templates.template1_qa import create_qa_card
from templates.template2_riddle import create_riddle_card
from templates.template3_checklist import create_checklist_card
from templates.template4_banner import create_acceptance_card
from templates.template5_video import generate_cinematic_photo_reel, SCENERY_DIR
from engine.ai_brain import AIBrain
from engine.guardrail import sanitize_post
from engine.seasonal_engine import get_seasonal_prompt_context

def load_json(filepath: Path):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

class ContentGenerator:
    def __init__(self):
        self.brand = load_json(BRAIN_DIR / "brand_profile.json")
        self.universities = load_json(BRAIN_DIR / "universities.json")
        self.faqs = load_json(BRAIN_DIR / "faq_knowledge.json")
        self.ai = AIBrain()
        from engine.topic_engine import TopicEngine
        from engine.tweet_history_engine import TweetHistoryEngine
        from engine.telegram_history_engine import TelegramHistoryEngine
        self.topic_engine = TopicEngine(self.ai)
        self.history_engine = TweetHistoryEngine()
        self.tg_history_engine = TelegramHistoryEngine()

    def generate_qa_post(self, question: str = None, answer: str = None):
        """Generates a Q&A post with an accompanying Q&A Card image (dynamically rotated)."""
        # Reload FAQs
        self.faqs = load_json(BRAIN_DIR / "faq_knowledge.json")
        if not question or not answer:
            if self.faqs:
                if not hasattr(self, "_last_faq_id"):
                    self._last_faq_id = -1
                candidates = [f for f in self.faqs if f.get("id") != self._last_faq_id]
                faq_item = random.choice(candidates if candidates else self.faqs)
                self._last_faq_id = faq_item.get("id", 0)
                question = faq_item["question"]
                answer = faq_item["answer"]
            else:
                question = "Qabul uchun imtihon bormi?"
                answer = "ARKADAŞ orqali imtihonli yoki imtihonsiz ham qabul qilinasiz."

        img_path = create_qa_card(
            question=question,
            answer=answer,
            output_filename=f"qa_post_{random.randint(1000, 9999)}.png"
        )

        caption = (
            f"❓ SAVOL: {question}\n\n"
            f"✅ JAVOB: {answer}\n\n"
            f"🎯 Arkadaş Consulting bilan orzuingizdagi universitetga hujjat topshiring!\n\n"
            f"📌 Afzalliklarimiz:\n"
            f"• 100% gacha grantlar va imtihonsiz qabul\n"
            f"• 0$ oldindan to'lov — xavfsiz shartnoma\n"
            f"• Yotoqxona, viza va to'liq yuridik ko'mak\n\n"
            f"📲 Savollaringiz bormi? Hoziroq yozing:\n"
            f"👉 {self.brand.get('contact', {}).get('telegram_admin', '@arkadasuzz')}\n\n"
            f"#TurkiyadaTalim #ArkadasConsulting #SavolJavob #Universitet #Grant"
        )

        return {
            "type": "qa",
            "media_type": "image",
            "media_path": str(img_path),
            "caption": caption
        }

    def generate_riddle_post(self, riddle: str = None, cta: str = None):
        """Generates an engagement riddle post with blue torn-paper image."""
        riddles = [
            ("Oldinga ketmaydi, orqaga ham, ammo har doim harakatda - bu nima?", "Soat"),
            ("Besh harfdan iborat, lekin hamma talaba uni kutadi - bu nima?", "Grant"),
            ("Hujjat topshirmasang ochilmaydi, Arkadaş bilan borsang qiyin bo'lmaydi - bu nima?", "Kelajak eshigi"),
            ("Qanoti yo'q — uchadi, tili yo'q — gapiradi, orzularga eltadi - bu nima?", "Talabalik vizasi"),
            ("Kitobda bor, daftarda bor, u bilan har qanday eshik ochiladi - bu nima?", "Diplom"),
            ("Bitta qaror bilan butun hayotingizni o'zgartiradigan shahar - bu qaysi?", "İstanbul! 🇹🇷"),
            ("Hech qachon to'xtamaydi, uni to'g'ri sarflagan talaba dunyoni zabt etadi - bu nima?", "Vaqt va Ta'lim")
        ]
        if not riddle:
            if not hasattr(self, "_last_riddle_idx"):
                self._last_riddle_idx = -1
            available = [r for idx, r in enumerate(riddles) if idx != self._last_riddle_idx]
            chosen_riddle, answer_hint = random.choice(available if available else riddles)
            self._last_riddle_idx = riddles.index((chosen_riddle, answer_hint))
            riddle = chosen_riddle
        
        if not cta:
            cta = "Bunga to'g'ri javob bergan bo'lsangiz, Arkadaş bilan Turkiyada 100% grantga tayyorsiz!"

        img_path = create_riddle_card(
            riddle_text=riddle,
            cta_text=cta,
            output_filename=f"riddle_post_{random.randint(1000, 9999)}.png"
        )

        caption = (
            f"🧠 KELING, MIYYANI CHARXLAYMIZ! 🔍\n\n"
            f"\"{riddle}\"\n\n"
            f"💬 Javobingizni izohlarda qoldiring! To'g'ri topgan birinchi 3 kishiga bepul konsultatsiya sovg'a qilinadi! 🎁✨\n\n"
            f"👉 Murojaat: {self.brand.get('contact', {}).get('telegram_admin', '@arkadasuzz')}\n\n"
            f"#Topishmoq #Mantiq #TurkiyadaTalim #Arkadas"
        )

        return {
            "type": "riddle",
            "media_type": "image",
            "media_path": str(img_path),
            "caption": caption
        }

    def generate_checklist_post(self):
        """Generates a checklist promotional post with 6 rotating, visually and thematically distinct cards."""
        checklist_packages = [
            {
                "top": "100% Grant",
                "title": "yutish sirlari!",
                "sub": "Turkiya davlat universitetlarida bepul o'qish imkoniyati:",
                "items": [
                    "Attestat baholari bilan to'g'ridan-to'g'ri ariza",
                    "YÖS yoki SAT imtihonlarisiz 100% kafolat",
                    "Bepul zamonaviy yotoqxona bilan ta'minlash",
                    "0$ oldindan to'lov — xavfsiz rasmiy shartnoma"
                ],
                "color": (255, 195, 18),  # Gold
                "scenery": "istanbul_bosphorus.jpg",
                "cta_bold": "0$ RISK — OLDINDAN TO'LOV YO'Q!",
                "cta_sub": "qolganini ARKADAŞ hal qiladi.",
                "btn1": "100% GRANT KAFOLATI",
                "btn2": "@ARKADASUZZ GA YOZING",
                "caption_title": "🎯 100% GRANT YUTISH CHECKLISTI! 🇹🇷"
            },
            {
                "top": "Arkadaş",
                "title": "to'liq xizmatlar paketi:",
                "sub": "Hujjat topshirishdan Turkiyaga yetib borguncha to'liq hamrohlik:",
                "items": [
                    "Universitet tanlash va rasmiy qabul xati olish",
                    "Notarial tarjima, apostil va viza ko'magi",
                    "Aeroportda kutib olish va yotoqxonaga joylash",
                    "Turk SIM-karta va bank hisob raqami ochish"
                ],
                "color": (0, 215, 255),  # Neon Cyan
                "scenery": "campus_students.jpg",
                "cta_bold": "99% MUVAFFAQIYAT KAFOLATI",
                "cta_sub": "Sizning ishonchli ARKADAŞ hamkoringiz.",
                "btn1": "TO'LIQ XIZMAT PAKETI",
                "btn2": "BEPUL KONSULTATSIYA",
                "caption_title": "📋 ARKADAŞ CONSULTING TO'LIQ XIZMATLAR PAKETI! ✨"
            },
            {
                "top": "Talabalar",
                "title": "imtiyozlari Turkiyada:",
                "sub": "Turkiya universitetlarida o'qiyotgan talabalar uchun imkoniyatlar:",
                "items": [
                    "Haftada 20 soat qonuniy ishlash huquqi",
                    "Yevropa va 150+ davlatda tan olinadigan diplom",
                    "Talabalik kartasi bilan 80% chegirmali transport",
                    "Bepul zamonaviy yotoqxona imkoniyati"
                ],
                "color": (16, 195, 130),  # Emerald Green
                "scenery": "istanbul_sunset.jpg",
                "cta_bold": "ORZUYINGIZDAGI TALABALIK!",
                "cta_sub": "Kelajagingizni ARKADAŞ bilan quring.",
                "btn1": "TALABALIK IMTIYOZLARI",
                "btn2": "@ARKADASUZZ GA YOZING",
                "caption_title": "🌟 TURKIYADAGI TALABALAR IMTIYOZLARI! 🇹🇷"
            },
            {
                "top": "Tibbiyot & IT",
                "title": "yo'nalishlariga qabul!",
                "sub": "Eng nufuzli sohalar bo'yicha Turkiya oliygohlari kvotalari:",
                "items": [
                    "Davolash ishi va Stomatologiya fakultetlari",
                    "Dasturiy ta'minot va Sun'iy intellekt (IT)",
                    "Xalqaro munosabatlar va Biznes boshqaruvi",
                    "Ingliz va turk tillarida ta'lim dasturlari"
                ],
                "color": (235, 60, 60),  # Coral Red
                "scenery": "istanbul_mosque.jpg",
                "cta_bold": "KVOTALAR SONI CHEKLANGAN!",
                "cta_sub": "Joyingizni ARKADAŞ bilan band qiling.",
                "btn1": "TIBBIYOT VA IT GRANTLARI",
                "btn2": "@ARKADASUZZ GA YOZING",
                "caption_title": "🩺 TIBBIYOT VA IT FAKULTETLARIGA QABUL! 🎓"
            },
            {
                "top": "Ketish Oldidan",
                "title": "hujjatlar to'plami:",
                "sub": "Turkiyada o'qish uchun zarur bo'lgan minimal hujjatlar:",
                "items": [
                    "Xorijga chiqish pasporti nusxasi (Zagran)",
                    "Maktab attestati yoki kollej/litsey diplomi",
                    "3x4 fotosurat va shaxsiy ma'lumotlar",
                    "Qolgan barcha rasmiyatchilikni o'zimiz bajaramiz"
                ],
                "color": (255, 140, 0),  # Orange/Amber
                "scenery": "galata_tower.jpg",
                "cta_bold": "FAQAT 3 TA HUJJAT KERAK!",
                "cta_sub": "Qolganini ARKADAŞ hal qiladi.",
                "btn1": "OSON VA TEZKOR QABUL",
                "btn2": "@ARKADASUZZ GA YOZING",
                "caption_title": "📁 KETISH OLDIDAN HUJJATLAR CHECKLISTI! ✈️"
            },
            {
                "top": "Turkiyada",
                "title": "o'qishni xohlaysizmi?",
                "sub": "Imtihonsiz va grant asosida talaba bo'lish imkoniyati:",
                "items": [
                    "To'liq 100% va qisman 75% grantlar",
                    "50 dan ortiq yetakchi davlat universitetlari",
                    "Turkiyada rasmiy ro'yxatdan o'tgan ishonchli agentlik",
                    "Talabalar hayoti va viza bo'yicha to'liq ko'mak"
                ],
                "color": (0, 180, 255),  # Sky Blue
                "scenery": "istanbul_bosphorus.jpg",
                "cta_bold": "SEN FAQAT QAROR QABUL QIL",
                "cta_sub": "qolganini ARKADAŞ hal qiladi.",
                "btn1": "JOYLAR CHEGARALANGAN!",
                "btn2": "@ARKADASUZZ GA YOZING",
                "caption_title": "🇹🇷 TURKIYADA O'QISHNI XOXLAYSIZMI? 🎓"
            }
        ]

        if not hasattr(self, "_last_chk_idx"):
            self._last_chk_idx = -1
        # Sequential rotation guarantees different card every single time!
        next_idx = (self._last_chk_idx + 1) % len(checklist_packages)
        self._last_chk_idx = next_idx
        pkg = checklist_packages[next_idx]

        img_path = create_checklist_card(
            header_top=pkg["top"],
            header_title=pkg["title"],
            subtitle=pkg["sub"],
            checklist=pkg["items"],
            header_top_color=pkg["color"],
            scenery_name=pkg["scenery"],
            cta_bold=pkg["cta_bold"],
            cta_sub=pkg["cta_sub"],
            btn1_text=pkg["btn1"],
            btn2_text=pkg["btn2"],
            output_filename=f"checklist_post_{random.randint(1000, 9999)}.png"
        )

        bullets = "\n".join([f"✅ {item}" for item in pkg["items"]])
        caption = (
            f"{pkg['caption_title']}\n\n"
            f"Imtihonsiz va grant asosida talaba bo'lish endi orzu emas!\n\n"
            f"ARKADAŞ orqali sizga nimalarni kafolatlaymiz:\n"
            f"{bullets}\n\n"
            f"🔥 {pkg['cta_bold']} — {pkg['cta_sub']}\n\n"
            f"⚠️ JOYLAR SONI CHEGARALANGAN!\n\n"
            f"📲 Hoziroq bepul konsultatsiya oling:\n"
            f"👉 Telegram: {self.brand.get('contact', {}).get('telegram_admin', '@arkadasuzz')}\n\n"
            f"#TurkiyadaTalim #Grantlar #ImtihonsizQabul #ArkadasConsulting"
        )

        return {
            "type": "checklist",
            "media_type": "image",
            "media_path": str(img_path),
            "caption": caption
        }

    def generate_acceptance_post(self, name: str = None, university: str = None, department: str = None, grant: str = None):
        """Generates a student admission celebration post with celebratory banner (dynamically randomized)."""
        names = [
            "Bekzod Rahimov", "Madina Rustamova", "Jasur Aliyev", "Shahzoda Umarova",
            "Diyorbek Xolmatov", "Kamola Saidova", "Sardorbek Karimov", "Nilufar Yusupova",
            "Bobur Mirzayev", "Sevara Qosimova", "Azizbek Tursunov", "Zarina Nazarova",
            "Umidjon Oripov", "Farrux Zokirov", "Malika Ahmedova"
        ]
        unis = [
            "İstanbul Universiteti", "Ankara Universiteti", "Hacettepe Universiteti",
            "Ege Universiteti", "Sakarya Universiteti", "Marmara Universiteti",
            "İstanbul Texnika Universiteti (İTÜ)", "Gazi Universiteti", "Anadolu Universiteti"
        ]
        departments = [
            "Davolash Ishi (Tibbiyot)", "Dasturiy Ta'minot (IT)", "Xalqaro Munosabatlar va Huquq",
            "Arxitektura va Dizayn", "Biznes va Moliya", "Sun'iy Intellekt Muhandisligi",
            "Stomatologiya", "Iqtisodiyot va Marketing"
        ]
        grants = ["100% GRANT", "75% GRANT", "50% GRANT"]

        final_name = name or random.choice(names)
        final_uni = university or random.choice(unis)
        final_dept = department or random.choice(departments)
        final_grant = grant or random.choice(grants)

        img_path = create_acceptance_card(
            student_name=final_name,
            university=final_uni,
            department=final_dept,
            grant_type=f"{final_grant} ASOSIDA",
            output_filename=f"acceptance_{random.randint(1000, 9999)}.png"
        )

        caption = (
            f"🎉 TABRIKLAYMIZ! YANGI TALABAMIZ! 🎓🇹🇷\n\n"
            f"Bizning talabamiz {final_name} Turkiyadagi nufuzli {final_uni} ning \"{final_dept}\" yo'nalishiga {final_grant} asosida qabul qilindi! ✨\n\n"
            f"Orzular sari dadil qadam tashlagan talabamizga kelajakdagi o'qishlarida ulkan muvaffaqiyatlar tilaymiz! 🚀\n\n"
            f"Siz ham Turkiyada orzuingizdagi soha bo'yicha grant asosida o'qishni xohlaysizmi?\n"
            f"👉 Hoziroq bizga yozing: {self.brand.get('contact', {}).get('telegram_admin', '@arkadasuz')}\n\n"
            f"#Qabul2025 #Talaba #Tabriklaymiz #Arkadas #Grant"
        )

        return {
            "type": "acceptance",
            "media_type": "image",
            "media_path": str(img_path),
            "caption": caption
        }

    def generate_educational_post(self, topic: Optional[str] = None) -> dict:
        """
        📚 BİLGİLENDİRİCİ POST (Ta'lim & Maslahat):
        Mavzular: Bologna tizimi, attestat bilan imtihonsiz qabul, yotoqxona va stipendiya,
        shaharlar (Eskişehir, Istanbul, Ankara, Izmir), nufuzli universitetlar, madaniyat va talabalik sirlari.
        Mavzular TopicEngine orqali doimiy boyitib boriladi va aslo tugamaydi ("konu hiç bitmasin").
        Hajmi: ~550-650 belgi.
        Asossiz maosh va'dalari, telefon yoki sayt havolasi YO'Q.
        CTA: @arkadasuzz
        """
        if not topic:
            t_name, t_desc = self.topic_engine.get_next_topic("educational")
        else:
            t_name, t_desc = topic, ""

        styles_pool = [
            "SAVOL-JAVOB USLUBI: Abituriyentni o'ylantiradigan qiziqarli savol yoki kutilmagan fakt bilan boshla.",
            "ILHOMLANTIRUVCHI USLUB: Bo'lajak talabaga to'g'ridan-to'g'ri, samimiy va dalda beruvchi tilda murojaat qil.",
            "ANIK RO'YXAT USLUBI: 1️⃣, 2️⃣, 3️⃣ raqamlar bilan eng asosiy afzalliklarni lo'nda va chiroyli sanab ber.",
            "MIFLARNI SINDIRISH USLUBI: Turkiyada o'qish bo'yicha tarqalgan noto'g'ri qo'rquvni isbotlar bilan bartaraf et.",
            "EKSPERT MASLAHATI: 5 yillik tajribaga ega ta'lim konsultantining qimmatli insayder tavsiyasi sifatida yoz."
        ]
        chosen_style = random.choice(styles_pool)
        var_id = random.randint(100, 999)

        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: Turkiya ta'limi bo'yicha BILGILENDIRICI (foydali maslahat) posti yoz.\n"
            f"Mavzu: '{t_name}' ({t_desc}).\n"
            f"{seasonal_ctx}\n"
            f"Tanlangan uslub: {chosen_style}\n"
            f"Variant kodi: #{var_id} - avvalgi postlardan tubdan farq qiluvchi, o'ziga xos matn yoz.\n\n"
            "QAT'IY TALABLAR:\n"
            "1. Yangi, jonli va qiziqarli yoz. Oldingi shablonlarni aslo takrorlama.\n"
            "2. '0$ risk' yoki '0 risk' kabi arzon shiorlar ASLO ISHLATILMASIN (o'rniga 'Oldindan to'lovsiz' deb yozilsin).\n"
            "3. Soxta va asossiz maosh va'dalari ($2000-$5000) yoki viza kafolatlari ASLO YOZILMASIN.\n"
            "4. Telefon raqam yoki veb-sayt mutlaqo YOZILMASIN.\n"
            "5. Post hajmi 550-650 belgi atrofida bo'lsin.\n"
            "6. Emojilardan o'rinli va me'yorida foydalan (📚, 🎓, 📌, 💡, 🇹🇷).\n"
            "7. Post oxiri FAQAT quyidagi CTA bilan yakunlansin:\n"
            "📲 Bepul konsultatsiya va qabul shartlari:\n"
            "👉 Telegram: @arkadasuzz\n\n"
            "Faqat tayyor post matnini qaytar (boshqa hech qanday izohsiz)."
        )

        res = self.ai.think_and_generate(prompt)
        content = sanitize_post(res.get("text", "").strip())

        fallbacks = [
            (
                "📚 TURKIYA DIPLOMI DUNYODA TAN OLINADIMI? 🎓🇹🇷\n\n"
                "Ko'pchilik abituriyentlar so'rashadi: Turkiya universitetlari beradigan diplom O'zbekistonda va Yevropada o'tadimi?\n\n"
                "Javob: ALBATTA! Chunki Turkiya oliygohlari Yevropa Bologna ta'lim tizimiga a'zo. Bu degani:\n"
                "✅ Siz olgan diplom Yevropaning 150 dan ortiq davlatida to'g'ridan-to'g'ri tan olinadi.\n"
                "✅ O'zbekistonda ham rasmiy nostrifikatsiyadan osonlik bilan o'tadi.\n"
                "✅ Eng muhimi — nufuzli oliygohlarga imtihonsiz, faqatgina attestat baholari bilan qabul qilinasiz!\n\n"
                "📌 Orzuingizdagi kelajakni ishonchli diplom bilan quring!\n\n"
                "📲 Bepul konsultatsiya va qabul shartlari:\n"
                "👉 Telegram: @arkadasuzz"
            ),
            (
                "🇹🇷 YEVROPADA BEPUL O'QISH: ERASMUS+ IMKONIYATI! ✈️🎓\n\n"
                "Bilasizmi? Turkiya universitetida tahsil olib, Yevropaning eng nufuzli oliygohlarida bepul o'qishingiz mumkin!\n\n"
                "Buning siri — xalqaro Erasmus+ dasturi:\n"
                "✅ Talaba 1 yoki 2 semestr davomida Germaniya, Italiya yoki Fransiyada tahsil oladi.\n"
                "✅ Yevropa Ittifoqi tomonidan har oy 400-600 yevro stipendiya beriladi.\n"
                "✅ Xalqaro tajriba, tillarni mukammal bilish va nufuzli diplom!\n\n"
                "💡 Arkadaş bilan imtihonsiz Turkiya talabasi bo'ling va Yevropaga yo'l oching!\n\n"
                "📲 Bepul konsultatsiya va qabul shartlari:\n"
                "👉 Telegram: @arkadasuzz"
            ),
            (
                "💡 IMTIHONSIZ TALABA BO'LISHNING 3 TA KAFOLATI 🇹🇷📚\n\n"
                "YÖS yoki SAT topshirmasdan ham Turkiyada nufuzli oliygohda o'qish mumkinmi? Ha!\n\n"
                "1️⃣ Faqat attestat baholari asosida tanlov o'tkaziladi.\n"
                "2️⃣ Istalgan yo'nalish: IT, Biznes, Huquq, Xalqaro munosabatlar va Muhandislik.\n"
                "3️⃣ Til bilmasangiz, 1 yil TÖMER til tayyorlov kursi mavjud.\n\n"
                "📌 Vaqtni boy bermang, yangi qabul uchun joyingizni hozirdan band qiling!\n\n"
                "📲 Bepul konsultatsiya va qabul shartlari:\n"
                "👉 Telegram: @arkadasuzz"
            )
        ]

        if len(content) < 200:
            content = sanitize_post(random.choice(fallbacks))

        return {
            "type": "educational",
            "category": "📚 Bilgilendirici",
            "topic": t_name,
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_promotional_post(self, topic: Optional[str] = None) -> dict:
        """
        💼 REKLAM & GÜVEN POSTI (Kafolatli Xizmatlar):
        Mavzular: Oldindan to'lovsiz (avval qabul, keyin to'lov), 99% qabul ko'rsatkichi,
        rasmiy yuridik shartnoma, to'liq xizmat paketi (kutib olish, yotoqxona, elchixona hujjatlari ko'magi),
        shaxsiy konsultatsiya, kontraktni bo'lib to'lash.
        QAT'IY QOIDA: Hech qanday soxta maosh yoki 'viza rad etilishi 0%' kabi yolg'on va'dalar YO'Q.
        Hajmi: ~550-650 belgi.
        CTA: @arkadasuzz
        """
        if not topic:
            t_name, t_desc = self.topic_engine.get_next_topic("promotional")
        else:
            t_name, t_desc = topic, ""

        styles_pool = [
            "ISBOT_VA_KAFOLAT: Rasmiy shartnoma va oldindan to'lov talab etilmasligi ustunligini ko'rsat.",
            "SOLISHTIRUV: Mustaqil topshirishdagi qiyinchiliklar va Arkadaş bilan to'liq xotirjamlikni taqqosla.",
            "4_QADAM_USLUBI: 1️⃣ Murojaat -> 2️⃣ Qabul xati -> 3️⃣ Hujjatlar -> 4️⃣ Talabalik oson qadamlarini tushuntir.",
            "OTA_ONALARGA_MUROJAAT: Farzandi kelajagiga qayg'urayotgan ota-onalar uchun ishonchli va mas'uliyatli tilda yoz.",
            "ENERGİK_CHORLOV: Cheklangan joylar va yangi mavsumning eng kuchli taklifi sifatida yoz."
        ]
        chosen_style = random.choice(styles_pool)
        var_id = random.randint(100, 999)
        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: Arkadaş Consulting xizmatlari haqida REKLAM & ISHONCH posti yoz.\n"
            f"Mavzu: '{t_name}' ({t_desc}).\n"
            f"{seasonal_ctx}\n"
            f"Tanlangan uslub: {chosen_style}\n"
            f"Variant kodi: #{var_id} - avvalgi postlardan tubdan farq qiluvchi, yangi rakursda yoz.\n\n"
            "QAT'IY TALABLAR:\n"
            "1. Yangi, ishonchli va o'quvchini jalb qiluvchi tilda yoz.\n"
            "2. '0$ risk' yoki '0 risk' deb YOZMA. O'rniga 'Oldindan to'lovsiz' yoki 'Avval rasmiy qabul xati, keyin to'lov' deb yoz.\n"
            "3. Soxta maosh ($2000-$5000) yoki 'viza rad etilishi 0%' kabi asossiz va'dalar ASLO YOZILMASIN.\n"
            "4. Telefon raqam yoki veb-sayt mutlaqo YOZILMASIN.\n"
            "5. Post hajmi 550-650 belgi atrofida bo'lsin.\n"
            "6. Post oxiri FAQAT quyidagi CTA bilan yakunlansin:\n"
            "📲 Joyingizni band qilish va to'liq ma'lumot olish:\n"
            "👉 Telegram: @arkadasuzz\n\n"
            "Faqat tayyor post matnini qaytar (boshqa hech qanday izohsiz)."
        )

        res = self.ai.think_and_generate(prompt)
        content = sanitize_post(res.get("text", "").strip())

        fallbacks = [
            (
                "💼 OLDINDAN TO'LOVSIZ TURKIYADA TALABA BO'LING! 🇹🇷🎓\n\n"
                "Chet elda o'qishda ishonchli mutaxassis qidiryapsizmi? Arkadaş Consulting bilan xotirjamlik!\n\n"
                "Bizning ishonchli tizimimiz:\n"
                "✅ Oldindan to'lovsiz: Avval rasmiy qabul xatingiz chiqadi, shaxsan tekshirasiz, shundan keyingina to'lov qilasiz!\n"
                "✅ 99% qabul ko'rsatkichi va rasmiy ikki tomonlama shartnoma.\n"
                "✅ Hujjat tarjimasidan to elchixona va yotoqxonagacha to'liq hamrohlik.\n\n"
                "📌 Orzuingizdagi talabalik hayotini ishonchli boshlang!\n\n"
                "📲 Joyingizni band qilish va to'liq ma'lumot olish:\n"
                "👉 Telegram: @arkadasuzz"
            ),
            (
                "🤝 NEGA 1000+ TALABA VA OTA-ONA BIZNI TANLADI? 🇹🇷✨\n\n"
                "Chet elda o'qish — butun umrlik investitsiya. Uni faqat rasmiy mutaxassislarga ishoning!\n\n"
                "Arkadaş Consulting afzalliklari:\n"
                "• 5 yillik muvaffaqiyatli tajriba va rasmiy shartnoma\n"
                "• Qabul xati chiqmaguncha to'lov qilinmaydi (oldindan to'lovsiz xizmat)\n"
                "• Turkiyaga qo'nganingizdan so'ng yotoqxonaga joylashishgacha vakillarimiz yoningizda bo'ladi\n\n"
                "Xavfsiz va ishonchli kelajak sari birinchi qadamni tashlang!\n\n"
                "📲 Joyingizni band qilish va to'liq ma'lumot olish:\n"
                "👉 Telegram: @arkadasuzz"
            ),
            (
                "🛡️ HAR BIR TALABAMIZ UCHUN YURIDIK SHARTNOMA! 🇹🇷📑\n\n"
                "Chet elda ta'lim olishda eng muhimi — xavfsizlik va aniqlik.\n\n"
                "Arkadaş Consulting bilan har bir mijoz qonuniy himoyalangan:\n"
                "✅ Rasmiy ikki tomonlama yuridik shartnoma tuziladi.\n"
                "✅ Natijaga yo'naltirilgan xizmat — shaffoflik bosh mezondir!\n"
                "✅ Universitet, yotoqxona va hujjatlar jarayoni to'liq nazorat qilinadi.\n\n"
                "Xotirjam va mustahkam kelajak sari dadil qadam tashlang!\n\n"
                "📲 Joyingizni band qilish va to'liq ma'lumot olish:\n"
                "👉 Telegram: @arkadasuzz"
            )
        ]

        if len(content) < 200:
            content = sanitize_post(random.choice(fallbacks))

        return {
            "type": "promotional",
            "category": "💼 Reklam & Kafolat",
            "topic": t_name,
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_news_post(self, topic: Optional[str] = None) -> dict:
        """
        📢 HABER & INFO POSTI (Kvotalar & Muddatlar):
        Mavzular: 2026-yilgi kvotalar ochilishi, Tibbiyot/IT kvotalari tugashi,
        Bahorgi va kuzgi semestr muddatlari, 50-75% grant chegirmalari, arzon davlat oliygohlari.
        Hajmi: ~550-650 belgi.
        Asossiz maosh va'dalari, telefon yoki sayt havolasi YO'Q.
        CTA: @arkadasuzz
        """
        if not topic:
            t_name, t_desc = self.topic_engine.get_next_topic("news")
        else:
            t_name, t_desc = topic, ""

        styles_pool = [
            "SHOSHILINCH_XABAR: ⚠️ DIQQAT! tezkor e'lon va yangilik ruhiyati bilan boshla.",
            "DEADLINE_OGOHLANTIRISH: 'Vaqt oz qoldi!' formatida aniq muddatlar va o'rinlar cheklanganligini ko'rsat.",
            "INSAYDER_INFO: Qabul komissiyalarining so'nggi ma'lumotlari va talabalar oqimi haqida yoz.",
            "IMKONIYAT_URG'USI: Hozir topshirgan talaba qanday grant yutishi mumkinligini tushuntir."
        ]
        chosen_style = random.choice(styles_pool)
        var_id = random.randint(100, 999)
        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: Turkiya universitetlari qabuli bo'yicha YANGILIK / KVOTA posti yoz.\n"
            f"Mavzu: '{t_name}' ({t_desc}).\n"
            f"{seasonal_ctx}\n"
            f"Tanlangan uslub: {chosen_style}\n"
            f"Variant kodi: #{var_id} - oldingi yangiliklardan tubdan farqli rakursda yoz.\n\n"
            "QAT'IY TALABLAR:\n"
            "1. Yangi, dinamik va ishonchli yangilik sifatida yoz.\n"
            "2. Shoshilinchlik va cheklangan o'rinlar hissini ber.\n"
            "3. '0$ risk' yoki soxta maosh va'dalari ($2000-$5000) ASLO YOZILMASIN.\n"
            "4. Telefon raqam yoki veb-sayt mutlaqo YOZILMASIN.\n"
            "5. Post hajmi 550-650 belgi atrofida bo'lsin.\n"
            "6. Post oxiri FAQAT quyidagi CTA bilan yakunlansin:\n"
            "📲 Kvotalar va qabul muddati bo'yicha ma'lumot:\n"
            "👉 Telegram: @arkadasuzz\n\n"
            "Faqat tayyor post matnini qaytar (boshqa hech qanday izohsiz)."
        )

        res = self.ai.think_and_generate(prompt)
        content = sanitize_post(res.get("text", "").strip())

        fallbacks = [
            (
                "📢 DIQQAT: YANGI O'QUV YILI QABUL KVOTALARI OCHILDI! 🇹🇷⏳\n\n"
                "Turkiyaning eng nufuzli davlat va xususiy universitetlarida yangi o'quv yili uchun xalqaro talabalar qabuli boshlandi!\n\n"
                "📌 Muhim yangiliklar:\n"
                "• Tibbiyot (Davolash ishi va Stomatologiya), IT va Arxitektura yo'nalishlarida xalqaro kvotalar cheklangan!\n"
                "• Imtihonsiz — to'g'ridan-to'g'ri maktab attestati yoki litsey diplomi bilan qabul qilinish imkoniyati.\n"
                "• Erta topshirgan abituriyentlar uchun yuqori grant chegirmalari mavjud.\n\n"
                "⚠️ O'rinlar tez to'lmoqda, hujjat topshirishga shoshiling!\n\n"
                "📲 Kvotalar va qabul muddati bo'yicha ma'lumot:\n"
                "👉 Telegram: @arkadasuzz"
            ),
            (
                "⚠️ SHOSHILING: TIBBIYOT VA IT KVOTALARI TUGAMOQDA! 🇹🇷🏥\n\n"
                "Turkiyada shifokorlik yoki IT mutaxassisligi bo'yicha o'qishni rejalashtirgan abituriyentlar diqqatiga:\n\n"
                "Xalqaro talabalar uchun ajratilgan o'rinlar soni cheklangan bo'lib, arizalar qabuli jadal ketmoqda!\n\n"
                "✅ Imtihonsiz qabul imkoniyati hali mavjud.\n"
                "✅ Yevropa standartidagi zamonaviy klinikalar va laboratoriyalar.\n\n"
                "Joylar tugab qolmasdan oldin hoziroq hujjatlaringizni topshiring!\n\n"
                "📲 Kvotalar va qabul muddati bo'yicha ma'lumot:\n"
                "👉 Telegram: @arkadasuzz"
            )
        ]

        if len(content) < 200:
            content = sanitize_post(random.choice(fallbacks))

        return {
            "type": "news",
            "category": "📢 Yangilik & Kvota",
            "topic": t_name,
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_twitter_post(self, topic: Optional[str] = None) -> dict:
        """
        🐦 TWITTER (X) POST GENERATOR:
        Hard limit: Maximum 260-275 characters (Twitter free account limit is strictly 280).
        Sharp hook, punchy factual tip, hashtag & short Telegram handle.
        No false claims, no 0$ risk, no $2000+.
        """
        if not topic:
            t_name, t_desc = self.topic_engine.get_next_topic("educational")
        else:
            t_name, t_desc = topic, ""

        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: Twitter (X) uchun MIKRO-TVIT yoz.\n"
            f"Mavzu: '{t_name}' ({t_desc}).\n"
            f"{seasonal_ctx}\n\n"
            "QAT'IY TALABLAR (BU JUDA MUHIM):\n"
            "1. Post umumiy hajmi BARCHA belgilar, bo'shliqlar va emojilar bilan birga MAKSIMAL 240-260 BELGI bo'lsin! 270 dan ASLO OSHMASIN!\n"
            "2. Birinchi jumla juda qiziqarli (Hook) bo'lsin.\n"
            "3. 0$ risk, 0 risk yoki dollar so'zlari ASLO ISHLATILMASIN.\n"
            "4. Post oxiriga qisqa qilib: '👉 @arkadasuzz #TurkiyaTalim' qo'sh.\n"
            "5. Faqat tayyor tvit matnini qaytar, boshqa hech qanday izohsiz."
        )

        res = self.ai.think_and_generate(prompt)
        content = sanitize_post(res.get("text", "").strip())

        # Strict character length guardrail for Twitter
        if len(content) > 275 or len(content) < 80:
            fallbacks = [
                "🇹🇷 Turkiyada imtihonsiz talaba bo'lish siri: Attestat bahosi yetarli!\n\nDiplomi dunyoda tan olinadi, kontraktlar esa hamyonbop.\n\nBatafsil: @arkadasuzz #TurkiyaTalim",
                "🎓 Bologna tizimi nima beradi? Turkiya diplomi bilan 150+ davlatda bemalol ishlash va o'qish mumkin!\n\nOldindan to'lovsiz boshlang.\n\nBatafsil: @arkadasuzz #Turkiya",
                "✈️ Erasmus+ bilan Turkiyadan Yevropaga! Bepul o'qish va yevroda stipendiya olish imkoniyati.\n\nQabul ochiq!\n\nBatafsil: @arkadasuzz #Talim",
                "🏛️ Eskişehir talabalar poytaxti: aholining 70% yoshlar, juda arzon va qulay muhit!\n\nAttestat bilan qabul.\n\nBatafsil: @arkadasuzz #TurkiyaTalim"
            ]
            content = random.choice(fallbacks)

        return {
            "type": "twitter",
            "category": "🐦 Twitter (X) Posti",
            "topic": t_name,
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_facebook_post(self, topic: Optional[str] = None) -> dict:
        """
        📘 FACEBOOK POST GENERATOR:
        Storytelling format, community discussion question, clear emojis, honest facts.
        No false claims, no 0$ risk.
        CTA to Telegram @arkadasuzz.
        """
        if not topic:
            t_name, t_desc = self.topic_engine.get_next_topic("educational")
        else:
            t_name, t_desc = topic, ""

        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: Facebook uchun qiziqarli, muhokama uyg'otuvchi (storytelling) post yoz.\n"
            f"Mavzu: '{t_name}' ({t_desc}).\n"
            f"{seasonal_ctx}\n\n"
            "QAT'IY TALABLAR:\n"
            "1. Facebook auditoriyasi uchun samimiy, batafsil va hayotiy misollar bilan yoz.\n"
            "2. Post oxirida o'quvchilarga savol ber (masalan: 'Siz Turkiyada qaysi shaharni yoki sohani tanlagan bo'lardingiz? Izohlarda fikringizni qoldiring!').\n"
            "3. 0$ risk, 0 risk yoki dollar so'zlari ASLO ISHLATILMASIN.\n"
            "4. Post hajmi ~500-650 belgi bo'lsin.\n"
            "5. Aloqa: faqat Telegram @arkadasuzz ga yo'naltir.\n"
            "Faqat tayyor Facebook post matnini qaytar."
        )

        res = self.ai.think_and_generate(prompt)
        content = sanitize_post(res.get("text", "").strip())

        if len(content) < 200:
            content = (
                "🇹🇷 Turkiyada nufuzli universitet talabasi bo'lish — kelajak uchun eng to'g'ri qadam! 🎓✨\n\n"
                "Ko'pchilik 'Imtihon topshirish shartmi?' deb so'raydi. Aslida maktab attestati yoki kollej diplomi bilan ham nufuzli davlat va xususiy oliygohlarga to'g'ridan-to'g'ri qabul qilinish mumkin.\n\n"
                "Eng asosiysi — Yevropa standartidagi Bologna diplomi va dunyo miqyosidagi imkoniyatlar.\n\n"
                "💬 Siz Turkiyada qaysi yo'nalishda o'qishni xohlardingiz: IT, Tibbiyot yoki Biznes? Fikringizni izohlarda yozib qoldiring!\n\n"
                "📲 To'liq ma'lumot va qabul shartlari:\n👉 Telegram: @arkadasuzz"
            )

        return {
            "type": "facebook",
            "category": "📘 Facebook Posti",
            "topic": t_name,
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_youtube_post(self, topic: Optional[str] = None) -> dict:
        """
        🎥 YOUTUBE SHORTS & COMMUNITY POST GENERATOR:
        Optimized YouTube Title (<80 chars), SEO tags, and engaging description.
        """
        if not topic:
            t_name, t_desc = self.topic_engine.get_next_topic("educational")
        else:
            t_name, t_desc = topic, ""

        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: YouTube Shorts va Hamjamiyat uchun SARLAVHA va TAVSIF yoz.\n"
            f"Mavzu: '{t_name}' ({t_desc}).\n"
            f"{seasonal_ctx}\n\n"
            "QAT'IY TALABLAR:\n"
            "1. SARLAVHA (Title): 70 belgidan oshmaydigan, o'ta qiziqarli va bosishga undovchi bo'lsin.\n"
            "2. TAVSIF (Description): 3-4 jumla, video mazmuni va afzalliklari.\n"
            "3. TEGLAR (Tags): #Shorts #TurkiyadaTalim #Arkadasuz #Talaba #Universitet\n"
            "4. 0$ risk yoki yolg'on va'dalar YOZILMASIN.\n"
            "5. Aloqa: faqat Telegram @arkadasuzz ga yo'naltir.\n"
            "Faqat tayyor matnni qaytar:\n"
            "🎬 SARLAVHA: [Sarlavha]\n\n📝 TAVSIF:\n[Tavsif]\n\n🏷️ TEGLAR:\n#Shorts #TurkiyaTalim #Arkadasuz"
        )

        res = self.ai.think_and_generate(prompt)
        content = sanitize_post(res.get("text", "").strip())

        if len(content) < 100:
            content = (
                "🎬 SARLAVHA: Turkiyada Imtihonsiz Talaba Bo'lish Siri! 🇹🇷🎓\n\n"
                "📝 TAVSIF:\nTurkiya universitetlariga faqat maktab attestati bilan qabul qilinasiz. Yevropada tan olinuvchi diplom va arzon kontraktlar!\n\n"
                "📲 To'liq konsultatsiya: @arkadasuzz\n\n"
                "🏷️ TEGLAR:\n#Shorts #TurkiyadaTalim #Arkadasuz #Universitet #Talaba"
            )

        return {
            "type": "youtube",
            "category": "🎥 YouTube Shorts / Post",
            "topic": t_name,
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_evergreen_post(self, template_key: str = "A") -> dict:
        """
        Generates one of the 5 Evergreen Posts based on t.me/arkadasuz 560-post historical analysis:
        - 'A': Hizmet Listesi (Service List) - ~650 chars, systematic emojis (✅, 🎓, 📲, 🇹🇷)
        - 'B': Neden Türkiye? (Bilgilendirici) - 5 categories, European standards, attestat admission
        - 'C': Kurumsal Tanıtım (Corporate Agency Intro)
        - 'D': Adım Adım Yol Haritası (1️⃣2️⃣3️⃣4️⃣ Roadmap)
        - 'E': Aciliyet + İstatistik (⚠️ DIQQAT! 50k+ students, top faculties)
        """
        guide_file = BRAIN_DIR / "brand_content_guide.json"
        guide = load_json(guide_file)
        t_map = {
            "A": "template_a_service_list",
            "B": "template_b_why_turkey",
            "C": "template_c_corporate_intro",
            "D": "template_d_step_roadmap",
            "E": "template_e_urgency_stats"
        }
        chosen_k = t_map.get(template_key.upper(), "template_a_service_list")
        t_data = guide.get("evergreen_templates", {}).get(chosen_k, {})
        var_id = random.randint(100, 999)

        # Ask AI Brain to produce a fresh variation respecting exact template structure & character limit
        prompt = (
            f"Kompaniya t.me/arkadasuz kanalining 560 ta posti tahliliga asoslangan '{t_data.get('name')}' postini yoz.\n"
            f"Tuzilishi: {t_data.get('structure')}\n"
            f"Variant kodi: #{var_id} (har safar yangi iboralar, yangi jumlalar va o'ziga xos uslubda yoz).\n"
            "Qoidalar:\n"
            "1. Sistemali emojilardan aniq foydalan (✅ xizmat moddasi, 🎓 ta'lim, 📲 CTA, 📌 ro'yxat, 🇹🇷 bayroq).\n"
            "2. Uzunligi taxminan 650 belgi atrofida bo'lsin.\n"
            "3. Ishonchli va professional ton: '99% muvaffaqiyat', 'Oldindan to'lov yo'q', 'Rasmiy shartnoma'.\n"
            "4. Hech qanday soxta maosh ($2000-$5000) yoki telefon/sayt raqamlari yozilmasin.\n"
            "5. Oxirida faqat @arkadasuzz bilan yakunla.\n\n"
            "Faqat tayyor post matnini qaytar (izohlarsiz)."
        )
        res = self.ai.think_and_generate(prompt)
        content = res.get("text", "").strip()
        if len(content) < 200:
            content = t_data.get("structure", "")

        return {
            "type": f"evergreen_{template_key.upper()}",
            "template_name": t_data.get("name", "Evergreen Post"),
            "content": content,
            "char_count": len(content),
            "media_type": "text",
            "target_cta": "@arkadasuzz"
        }

    def generate_media_caption(self, media_type: str = "photo", location: str = "İstanbul", uni: str = None) -> str:
        """
        Generates short, emotional media captions matching the historical brand rule:
        - Photos: ~150 chars (Mekân etiketi + kısa duygusal cümle + @arkadasuzz)
        - Videos: ~70 chars (Dinamik 1-2 cümle + @arkadasuzz)
        """
        if media_type == "photo":
            samples = [
                f"{uni or location} ❤️ Talabalik bu yerda boshqacha! 🇹🇷✨ Ma'lumot uchun: @arkadasuzz",
                f"{uni or location} kampusi 🐝💛 Orzularingiz tomon qadam bosing! 📲 @arkadasuzz",
                f"{location}ni his eting ✨🇹🇷 100% grant bilan o'qish uchun: @arkadasuzz"
            ]
            return random.choice(samples)
        else: # video
            samples = [
                f"Turkiyada talaba bo'lish vaqti keldi! 🇹🇷🎓 Batafsil: @arkadasuzz",
                f"Orzuingizdagi hayot Turkiyada! ✨✈️ Savollaringiz bormi? @arkadasuzz",
                f"100% grant bilan Turkiyada o'qing! 🇹🇷 Aloqa: @arkadasuzz"
            ]
            return random.choice(samples)

    def generate_reels_post(self, topic: str = "Turkiyada 100% grant va bepul yotoqxona"):
        """Generates an aesthetic 3-act storytelling Reel using clean stock video and neural voiceover."""
        from engine.story_reels_engine import StoryReelsEngine
        sre = StoryReelsEngine()
        result = sre.create_meaningful_reel(topic=topic)
        return {
            "type": "reels",
            "media_type": "video",
            "media_path": result["media_path"],
            "caption": result["caption"]
        }

    def generate_twitter_thread(self, topic: Optional[str] = None) -> List[str]:
        """
        Generates a high-engagement 6-part sequential Twitter Thread (Flood).
        Each tweet is strictly <= 270 characters.
        Uses AIBrain with dynamic seasonal context and safety guardrails.
        """
        if not topic:
            topics_pool = [
                "Turkiyada 0 dan talaba bo'lishning to'liq yo'l xaritasi",
                "Turkiya davlat universitetlariga imtihonsiz qabul qilinish sirlari",
                "Turkiyada talabalar uchun grantlar va stipendiya yutish yo'llari",
                "Turkiyada talabalik vizasi, turar-joy va moslashish bo'yicha to'liq qo'llanma",
                "Turkiya diplomining Yevropa va O'zbekistonda tan olinishi va istiqbollari",
                "Turkiyada eng talabgir 5 ta kasb va ularga kirish talablari",
                "Attestat bahosi bilan Turkiyada eng nufuzli oliygohlarga kirish strategiyasi",
                "Turkiyada talabalik hayoti: Yotoqxona, arzon transport va oshxonalar",
                "YÖS va SAT imtihonlariga mustaqil tayyorlanish bo'yicha to'liq qo'llanma",
                "Turkiyada IT va dasturlash yo'nalishlarida o'qish va karyera imkoniyatlari",
                "TÖMER turk tili kursi va universitetga tayyorgarlik bo'yicha barcha ma'lumotlar",
                "Turkiyada magistratura va xalqaro tadqiqot dasturlariga hujjat topshirish"
            ]
            used_threads = self.history_engine.data.get("used_threads", [])
            fresh_topics = [t for t in topics_pool if t not in used_threads]
            topic = fresh_topics[0] if fresh_topics else random.choice(topics_pool)

        self.history_engine.record_thread_topic(topic)
        seasonal_ctx = get_seasonal_prompt_context()

        prompt = (
            f"VAZIFA: Twitter (X) uchun 6 qismli zanjir tvit (Thread / Flood) yoz.\n"
            f"Mavzu: '{topic}'.\n"
            f"{seasonal_ctx}\n\n"
            "QAT'IY TALABLAR:\n"
            "1. Jami 6 ta tvit bo'lsin. Har bir tvit alohida satrda 'TWEET 1:', 'TWEET 2:' deb boshlansin.\n"
            "2. Har bir tvit qat'iy ravishda 240-265 belgidan oshmasin (Twitter 280 belgidan oshsa xato beradi)!\n"
            "3. 1-tvit (1/6): Kuchli kanca (Hook), mavzuni e'lon qilish va saqlab olishga chaqirish.\n"
            "4. 2, 3, 4, 5-tvitlar: Bosqichma-bosqich aniq amaliy maslahatlar (hujjatlar, qabul, xarajatlar, viza).\n"
            "5. 6-tvit (6/6): Xulosa va Telegramga chaqiruv: '👉 @arkadasuzz #TurkiyaTalim'.\n"
            "6. 0$ risk, soxta maoshlar mutlaqo yozilmasin.\n\n"
            "Faqat 6 ta tvit matnini qaytar."
        )

        res = self.ai.think_and_generate(prompt)
        raw_text = res.get("text") or ""
        tweets = []
        parts = raw_text.split("TWEET")
        for p in parts:
            p_clean = p.strip()
            if not p_clean:
                continue
            lines = p_clean.split("\n", 1)
            first_line = lines[0].strip()
            if first_line.startswith(("1:", "2:", "3:", "4:", "5:", "6:", "1", "2", "3", "4", "5", "6")):
                body = lines[1].strip() if len(lines) > 1 else first_line
            else:
                body = p_clean
            body = sanitize_post(body)
            if len(body) > 275:
                body = body[:265] + "..."
            if len(body) > 30:
                tweets.append(body)

        if len(tweets) < 6:
            tweets = [
                f"🇹🇷 {topic.upper()} (FLOOD) 🧵\n\nHujjat topshirishdan tortib yetib borishgacha barcha bosqichlarni jamladik. Saqlab oling va do'stlarga ulashing! 👇 (1/6)",
                "1️⃣ Yo'nalish va Oliygo'h Tanlash:\nDavlat universitetlarida attestat baholari yoki YÖS/SAT imtihoni bilan qabul qilinadi. Xususiy oliygohlarda esa qabul jarayoni tezroq va soddaroq kechadi. 🎯 (2/6)",
                "2️⃣ Hujjatlar Paketi:\n• Maktab attestati yoki kollej diplomi\n• Xorijga chiqish pasporti\n• 3x4 biometrik surat\n• Notarial turkcha tarjima va Apostil tasdig'i. Hammasi joyida bo'lsa, qabul xati chiqadi! 📑 (3/6)",
                "3️⃣ Talabalik Vizasi:\nUniversitetdan rasmiy 'Qabul xati' (Kabul Mektubu) chiqqach, Turkiya elchixonasidan talabalik vizasi olinadi. Hujjatlar to'g'ri bo'lsa, jarayon xotirjam o'tadi. 🛂✈️ (4/6)",
                "4️⃣ Turar Joy va Yotoqxona:\nTalabalar uchun 3 ta variant bor:\n• Davlat (KYK) yotoqxonalari\n• Xususiy yotoqxonalar\n• Sheriklikda ijaraga olingan kvartiralar. Joyni borishdan oldin aniqlash zarur! 🏠 (5/6)",
                "5️⃣ Arkadaş Consulting Siz Bilan!\nQaysi universitetni tanlashni bilmayapsizmi? Barcha hujjatlarni professional va xavfsiz rasmiylashtiramiz.\n\nSavollar uchun: @arkadasuzz 🇹🇷🤝 (6/6)"
            ]

        return topic, tweets[:6]

    def generate_weekly_twitter_plan(self, start_date=None) -> dict:
        """
        Generates 7 days x 3 tweets = 21 unique tweets + 1 mega 6-part thread (Wednesday noon).
        Guarantees that NO topic or angle repeats from previous weeks.
        Scheduled at 10:00 (Morning), 14:00 (Noon), 20:00 (Evening) each day.
        """
        from datetime import datetime, timedelta
        import time

        if not start_date:
            try:
                from engine.twitter_scheduler import TwitterScheduler
                sched = TwitterScheduler()
                already_scheduled = [t for t in sched.data.get("tweets", []) if t.get("status") == "scheduled_on_twitter"]
                if already_scheduled and sched.data.get("end_date"):
                    last_end = datetime.strptime(sched.data["end_date"], "%Y-%m-%d")
                    if last_end >= datetime.now():
                        start_dt = last_end + timedelta(days=1)
                    else:
                        start_dt = datetime.now() + timedelta(days=1)
                else:
                    start_dt = datetime.now() + timedelta(days=1)
            except Exception:
                start_dt = datetime.now() + timedelta(days=1)
        else:
            start_dt = start_date

        week_num = self.history_engine.data.get("weeks_generated", 0) + 1
        week_id = f"w_{week_num}_{int(time.time())}"

        # 5 Balanced Topic Pillars (Arkadaş Consulting ad, Turkey facts, Student life, Engagement, and minimal universities)
        promo_pool = [
            "Arkadaş Consulting: Turkiyada rasmiy, xavfsiz va ishonchli talaba bo'lish kafolati",
            "Nega o'zbek yoshlari Arkadaş Consultingni tanlaydi? Aeroportda kutib olishdan to yotoqxonagacha to'liq hamrohlik",
            "Attestat bilan imtihonsiz qabul: Arkadaş Consulting barcha hujjatlarni 100% rasmiy rasmiylashtiradi",
            "Ota-onalar xotirjamligi biz uchun birinchi o'rinda: Farzandingiz Turkiyada ishonchli qo'llarda",
            "Universitet kontraktlarida maxsus chegirmalar: Arkadaş Consulting rasmiy hamkorlik imtiyozlari",
            "Viza va İkamet (yashash guvohnomasi) byurokratiyasini bizga topshiring — ortiqcha bosh og'rig'isiz talaba bo'ling",
            "Turkiyada o'qish orzuingiz bormi? Arkadaş Consulting bepul dastlabki konsultatsiya taqdim etadi",
            "Turkiya oliygohlariga qabul xatini eng qisqa fursatda qo'lga kiriting: Tezkor va xatosiz ariza",
            "Rasmiy shartnoma va to'liq qonuniy xizmat: Arkadaş Consulting bilan xavf-xatarsiz talaba bo'ling",
            "Kutib olish va joylashish: Turkiyaga ilk qadamingizdan boshlab Arkadaş Consulting jamoasi yoningizda",
            "Shaxsiy koordinator: O'qish davomida duch keladigan barcha savollarga professional yordam",
            "Orzuingizdagi kasb sari ishonchli ko'prik: Arkadaş Consulting orqali xalqaro diplomga ega bo'ling",
            "O'qishga topshirishda vaqt yo'qotmang: Bahorgi va kuzgi qabullarga hozirdan ro'yxatdan o'ting",
            "Turkiyada ta'lim olish endi qiyin emas: Barcha murakkab jarayonlarni professional jamoamiz hal qiladi",
            "Yuzlab talabalarimiz allaqachon Turkiyada! Siz ham o'z kelajagingizni Arkadaş Consulting bilan quring",
            "Xususiy va davlat oliygohlariga kafolatlangan qabul: Siz xohlagan shahar va yo'nalish",
            "Denklik (nostrifikatsiya) va apostil masalalarida 100% amaliy yordam",
            "Turkiyada yotoqxona topish muammomi? Arkadaş Consulting qulay va xavfsiz yotoqxonalarga joylashtiradi",
            "Talabalik vizasini rad javobisiz olish sirlari: Arkadaş Consulting konsullik tavsiyalari",
            "Arkadaş Consulting: O'zbekiston yoshlarining Turkiya orqali jahon ta'limiga ochilgan eshigi"
        ]

        turkey_facts_pool = [
            "Turkiya haqida qiziqarli fakt: Dunyoda eng ko'p choy ichiladigan davlat Turkiyadir",
            "Dunyoning 2 qit'asida (Yevropa va Osiyo) joylashgan yagona megapolis — Istanbul shahri",
            "Kutubxonalar va talabalik: Turkiyadagi 24/7 ochiq zallar va bepul issiq choy xizmati",
            "Talabalar uchun transport: Istanbulkart bilan metro, parom va avtobuslarda 70-80% gacha arzon yurish imkoniyati",
            "O'zbek va turk tillari qanchalik yaqin? Talabalarimiz 2-3 oy ichida erkin gaplashib ketish siri",
            "Turkiyada xavfsizlik va madaniyat: Talaba qizlar va yigitlar uchun tinch va zamonaviy shahar muhiti",
            "Turkiyaning YHT tezyurar poyezdlari: Shaharlararo bir necha soatda arzon va tezyurar sayohat",
            "Turkiyada Müzekart: Talabalar uchun yuzlab tarixiy saroylar va obidalar deyarli bepul",
            "Turk xalqining mehmondo'stligi va o'zbek talabalariga bo'lgan samimiy birodarlik munosabati",
            "Turkiyada talabalik: Bir tomonda O'rtayer dengizi, bir tomonda qorli tog'lar va ajoyib tabiat",
            "Turkiyada har bir talaba shaharchasi: Jonli ko'chalar, xiyobonlar va do'stona muhit",
            "Turk nonushtasi va qahva madaniyati: Turkiyada talabalikning mazali va samimiy lahzalari",
            "Dunyodagi eng qadimiy shahar va obidalar: Turkiyada har bir qadam tarix bilan nafas oladi",
            "Turkiyadagi ko'cha hayvonlari va mushuklar madaniyati: Shaharlardagi do'stona va mehrli muhit",
            "Turkiyada kitobxonlik va yoshlar markazlari: Har bir tumanda bepul qulay dars xonalari",
            "Turkiyaning buyuk kutubxonalari: Rami kutubxonasi — Yevropaning eng katta kutubxonasida talabalar hayoti",
            "Turkiyada daryo va ko'llar bo'yida talabalar dam olish zonalari va musaffo havo",
            "Turk oshxonasi: Talabalar oshxonalari va arzon sifatli, mazali taomlar",
            "Turkiyaning go'zal dengiz bo'yi shaharlari: Izmir, Antalya, Trabzon va Bursa kabi talabalar sevadigan maskanlar",
            "Turkiyada yiliga 300 kun quyoshli shaharlar: Yengil va kayfiyatni ko'taruvchi talabalik muhiti"
        ]

        student_life_pool = [
            "Turkiyada talaba oylik xarajati qancha? Tejamkor va qulay yashash bo'yicha amaliy maslahatlar",
            "Davlat (KYK) yotoqxonalari: Bepul nonushta, kechki ovqat va arzon shinam xonalar",
            "Erasmus+ dasturi: Turkiyada o'qiyotib 1 semestr Yevropada grant bilan bepul ta'lim olish",
            "Turkiyada talabalar tibbiy sug'urtasi (GSS): Barcha davlat shifoxonalarida bepul xizmat",
            "Turkiyada o'qiyotgan talabalarning qonuniy ishlash imkoniyatlari va bo'sh vaqtni boshqarish",
            "Turkiya bozorlari va arzon do'konlar (BİM, A101, Şok): Talabalar uchun hamyonbop xaridlar",
            "O'zbekistondan mablag' qabul qilish va Turkiyada talabalik bank hisobini qulay ochish",
            "Turk tilini oldindan bilmasdan qabul qilinish: TÖMER tayyorlov kursi afzalliklari",
            "Talabalik yillarida sayohat qilish: Turkiyada talabalik chegirmalari orqali arzon sayohatlar",
            "O'zbekiston talabalar jamoalari: Turkiyada o'zbek yoshlarining o'zaro hamjihatligi va do'stligi",
            "Talabalar uchun sport majmualari: Universitetlardagi bepul basseyn va trenajyor zallari",
            "Imtihon sessiyasi paytida talabalar: Universitetlarda tunu-kun bepul kofe va qo'llab-quvvatlash",
            "Turkiyada kvartirada sheriklikda yashash: Qoidalari va xarajatlarni taqsimlash sirlari",
            "Turkiyada telefon va internet: Talabalar uchun eng foydali tarif rejalari"
        ]

        engagement_pool = [
            "Abituriyentlar uchun savol: Agar bugun tanlash imkoni bo'lsa, qaysi shaharni afzal ko'rardingiz? Istanbulmi yoki Anqara?",
            "Siz qaysi soha mutaxassisi bo'lishni xohlaysiz: Zamonaviy IT, xalqaro biznes yoki tibbiyot?",
            "O'qishga ketganingizda O'zbekistondan eng ko'p nimani sog'inasiz deb o'ylaysiz? Izohlarda kutamiz!",
            "Talabalik yillarida eng katta orzuingiz nima? Fikrlaringiz biz uchun qiziq!",
            "Chet elda o'qish haqida eshitganingizda xayolingizga birinchi bo'lib nima keladi?",
            "Ota-onalar farzandini chet elga yuborishda eng ko'p nimadan xavotir oladi deb o'ylaysiz?",
            "Turk tilini o'rganish sizga qanchalik qiyin yoki oson tuyuladi?",
            "Talaba bo'lish yo'lida sizni eng ko'p qaysi savol o'ylantirmoqda? Izohda qoldiring, javob beramiz!",
            "Katta megapolis hayotimi yoki sokin dengiz bo'yi shahrimi? Qaysi biri sizga ma'qul?",
            "Kelajakda jahon standartidagi diplomga ega bo'lish siz uchun qanchalik muhim?"
        ]

        # University pool: Strictly 1-2 per week, NOT overused!
        university_pool = [
            "Hafta oliygohi: Istanbul Davlat Universiteti — qadimiy nufuz va zamonaviy ta'lim",
            "Mavi Diploma (Moviy Diplom): Turkiyada olingan ta'lim nega butun Yevropada tan olinadi?",
            "Hafta oliygohi: Anqara Hacettepe Universiteti — tibbiyot va muhandislikda xalqaro e'tirof",
            "Turkiyada IT va dasturlash ta'limi: Zamonaviy texnoparklar va amaliyot imkoniyati",
            "Hafta oliygohi: Marmara Universiteti — ikki qit'ani birlashtirgan ta'lim dargohi",
            "Bologna tizimi: Turkiya diplomining jahonning 150+ davlatida to'g'ridan-to'g'ri o'tishi",
            "Hafta oliygohi: Bursa Uludağ Universiteti — O'zbek yoshlari eng ko'p tanlaydigan yashil kampus",
            "Turkiyada biznes va xalqaro iqtisodiyot: Amaliy tajriba va xalqaro aloqalar",
            "Hafta oliygohi: Izmir Ege Universiteti — O'rtayer va Egey dengizi bo'yidagi nufuzli maskan",
            "Turkiyada arxitektura va dizayn ta'limi: Sharq va G'arb an'analarining uyg'unligi",
            "Hafta oliygohi: Eskişehir Anadolu Universiteti — haqiqiy talabalar shaharchasi",
            "Turkiyada stomatologiya va tibbiyot ta'limining yuqori sifat standartlari",
            "Hafta oliygohi: Sakarya Universiteti — Istanbulga yaqin va qulay ta'lim muhiti",
            "Xalqaro logistika va moliya yo'nalishlarining Turkiyadagi istiqboli"
        ]

        def _pick_fresh(pool, count, fallback_prefix):
            fresh = [t for t in pool if not self.history_engine.is_topic_used(t)]
            res = []
            for i in range(count):
                if i < len(fresh):
                    res.append(fresh[i])
                else:
                    res.append(f"{fallback_prefix} #{week_num}-{i+1}: Dolzarb ma'lumotlar va qulay imkoniyatlar")
            return res

        picked_promo = _pick_fresh(promo_pool, 5, "Arkadaş Consulting bilan Turkiyada ta'lim")
        picked_facts = _pick_fresh(turkey_facts_pool, 6, "Turkiya haqida qiziqarli fakt")
        picked_student = _pick_fresh(student_life_pool, 4, "Turkiyada talabalik hayoti sirlari")
        picked_engage = _pick_fresh(engagement_pool, 3, "Talabalar uchun haftalik qiziqarli savol")
        picked_uni = _pick_fresh(university_pool, 2, "Hafta oliygohi va diplom imtiyozi")

        # Interleave into 20 well-balanced single slots (strictly 2 university topics, 5 promo, 6 facts, 4 student life, 3 engagement)
        slot_plan = [
            # Day 1:
            (picked_facts[0], "🇹🇷 Fakt"),
            (picked_promo[0], "🏛️ Reklama"),
            (picked_engage[0], "❓ Savol"),
            # Day 2:
            (picked_facts[1], "🇹🇷 Fakt"),
            (picked_student[0], "💡 Maslahat"),
            (picked_uni[0], "🎓 Oliygoh"),  # Uni #1
            # Day 3:
            (picked_facts[2], "🇹🇷 Fakt"),
            (picked_promo[1], "🏛️ Reklama"),
            (picked_student[1], "💡 Maslahat"),
            # Day 4:
            (picked_facts[3], "🇹🇷 Fakt"),
            (picked_student[2], "💡 Maslahat"),
            (picked_engage[1], "❓ Savol"),
            # Day 5 (Wednesday has Mega Flood at noon, leaving 2 single slots):
            (picked_facts[4], "🇹🇷 Fakt"),
            (picked_promo[2], "🏛️ Reklama"),
            # Day 6:
            (picked_facts[5], "🇹🇷 Fakt"),
            (picked_student[3], "💡 Maslahat"),
            (picked_uni[1], "🎓 Oliygoh"),  # Uni #2
            # Day 7:
            (picked_promo[3], "🏛️ Reklama"),
            (picked_promo[4], "🏛️ Reklama"),
            (picked_engage[2], "❓ Savol")
        ]

        days_names_uz = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        slots = [
            ("morning", "10:00:00", "🌅 Ertalabki Post"),
            ("noon", "14:00:00", "☀️ Tushlik Posti"),
            ("evening", "20:00:00", "🌆 Kechki Post")
        ]

        # 1. Generate 6-part Thread for Wednesday noon (1 API call)
        flood_topic, thread_items = self.generate_twitter_thread()

        # 2. Extract topics for batch AI generation
        selected_single_topics = [item[0] for item in slot_plan]

        # 3. Batch generate all 20 tweets in a single high-speed Gemini prompt
        topics_str = "\n".join([f"Mavzu {i+1} [{slot_plan[i][1]}]: {selected_single_topics[i]}" for i in range(20)])
        batch_prompt = (
            f"VAZIFA: Twitter (X) uchun quyidagi 20 ta mavzuning har biriga ALOHIDA MIKRO-TVIT yoz.\n\n"
            f"{topics_str}\n\n"
            f"{get_seasonal_prompt_context()}\n\n"
            "QAT'IY TALABLAR (BU JUDA MUHIM):\n"
            "1. Har bir tvitni 'TWEET 1:', 'TWEET 2:', ... 'TWEET 20:' formatida yoz.\n"
            "2. Har bir tvit qat'iy ravishda 220-265 belgidan oshmasin (Twitter 280 belgidan oshsa xato beradi)!\n"
            "3. ABARTMA ASLO BO'LMASIN: 'jannat', 'talabalar uchun jannat', 'sehrli', 'mo''jiza', 'hayratlanarli' kabi soxta, arzon va balandparvoz mubolag'ali so'zlar ASLO ishlatilmasin! Jiddiy, samimiy, ishonchli, professional va xolis o'zbek tilida yozilsin.\n"
            "4. [🏛️ Reklama] mavzularida: Arkadaş Consulting rasmiy litsenziyasi, aeroportda kutib olish, xavfsizlik, ota-onalar xotirjamligi va @arkadasuzz ga yozish chaqirig'i bo'lsin.\n"
            "5. [🇹🇷 Fakt] mavzularida: Turkiya haqida qiziqarli va ishonchli ma'lumotlar (choy madaniyati, bepul kutubxonalar, talabalar transport chegirmalari) me'yorida yoritilsin.\n"
            "6. [❓ Savol] mavzularida: Obunachilarni izoh yozishga undovchi jonli va qiziqarli savol berilsin.\n"
            "7. [🎓 Oliygoh] mavzularida: Me'yorida, foydali va xolis ma'lumot berilsin (haftada faqat 2 ta bo'ladi).\n"
            "8. 0$ risk, dollar narxlari yoki soxta va'dalar ASLO YOZILMASIN.\n"
            "9. Har bir tvit oxiriga: '👉 @arkadasuzz #ArkadasUz' yoki '👉 @arkadasuzz #Turkiya' qo'sh.\n\n"
            "Faqat 20 ta tvit matnini qaytar (izohlarsiz)."
        )

        res = self.ai.think_and_generate(batch_prompt)
        raw_text = res.get("text") or ""
        import re
        raw_parts = re.split(r'\*?\*?TWEET\s*\d+[:\s\*\-]*', raw_text, flags=re.IGNORECASE)
        parsed_tweets = []
        for part in raw_parts:
            p_clean = part.strip().strip("*").strip()
            if not p_clean:
                continue
            body = sanitize_post(p_clean)
            if len(body) > 275:
                body = body[:265] + "..."
            if len(body) > 40:
                parsed_tweets.append(body)

        scheduled_tweets = []
        slot_plan_idx = 0

        # Topic-tailored fallback templates based on category tag
        fallback_map = {
            "🏛️ Reklama": "📌 {topic}\n\nArkadaş Consulting bilan Turkiyada rasmiy, ishonchli va kafolatlangan talaba bo'ling.\n\nBog'lanish: @arkadasuzz #ArkadasUz",
            "🇹🇷 Fakt": "🇹🇷 {topic}\n\nTurkiyada talabalar uchun ajoyib qulayliklar va boy madaniyat mavjud.\n\nBatafsil: @arkadasuzz #Turkiya",
            "💡 Maslahat": "💡 {topic}\n\nTurkiyada talabalik hayotini qulay va tejamkor tashkil etish bo'yicha amaliy maslahatlar.\n\nSavollar: @arkadasuzz #TalabaHayoti",
            "❓ Savol": "❓ {topic}\n\nO'z fikringizni izohlarda yozib qoldiring! 👇\n\n@arkadasuzz #ArkadasUz",
            "🎓 Oliygoh": "🎓 {topic}\n\nTurkiya oliygohlarida xalqaro standartdagi ta'lim va diplom.\n\nBatafsil: @arkadasuzz #TurkiyaTalim"
        }

        for day_idx in range(7):
            cur_date = start_dt + timedelta(days=day_idx)
            cur_date_str = cur_date.strftime("%Y-%m-%d")
            day_name = days_names_uz[cur_date.weekday()]

            for slot_key, slot_time_str, slot_label in slots:
                scheduled_iso = f"{cur_date_str}T{slot_time_str}"
                tw_id = f"tw_{cur_date.strftime('%Y%m%d')}_{slot_key[:3]}"

                # Wednesday noon (cur_date.weekday() == 2) is strictly the ONLY MEGA FLOOD slot
                is_flood_slot = (cur_date.weekday() == 2 and slot_key == "noon")

                if is_flood_slot:
                    tw_obj = {
                        "id": tw_id,
                        "day_index": day_idx + 1,
                        "day_name": day_name,
                        "date_str": cur_date_str,
                        "slot": slot_key,
                        "slot_label": "🧵 MEGA FLOOD (6 qismli zanjir)",
                        "cat_tag": "🧵 Mega Flood",
                        "scheduled_time": scheduled_iso,
                        "topic": flood_topic,
                        "content": thread_items[0],
                        "is_thread": True,
                        "thread_items": thread_items,
                        "status": "pending"
                    }
                    self.history_engine.record_topic(flood_topic)
                    self.history_engine.record_tweet(thread_items[0], flood_topic)
                else:
                    if slot_plan_idx < len(slot_plan):
                        t_topic, cat_tag = slot_plan[slot_plan_idx]
                    else:
                        t_topic, cat_tag = ("Turkiyada talabalik hayoti", "🇹🇷 Fakt")

                    if slot_plan_idx < len(parsed_tweets) and len(parsed_tweets[slot_plan_idx]) >= 40:
                        content = parsed_tweets[slot_plan_idx]
                    else:
                        tpl = fallback_map.get(cat_tag, "📌 {topic}\n\nBog'lanish: @arkadasuzz #ArkadasUz")
                        content = tpl.format(topic=t_topic)

                    tw_obj = {
                        "id": tw_id,
                        "day_index": day_idx + 1,
                        "day_name": day_name,
                        "date_str": cur_date_str,
                        "slot": slot_key,
                        "slot_label": slot_label,
                        "cat_tag": cat_tag,
                        "scheduled_time": scheduled_iso,
                        "topic": t_topic,
                        "content": content,
                        "is_thread": False,
                        "thread_items": [],
                        "status": "pending"
                    }
                    self.history_engine.record_topic(t_topic)
                    self.history_engine.record_tweet(content, t_topic)
                    slot_plan_idx += 1

                scheduled_tweets.append(tw_obj)

        self.history_engine.record_week_generation()

        end_date_str = (start_dt + timedelta(days=6)).strftime("%Y-%m-%d")
        return {
            "week_id": week_id,
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_date_str,
            "total_tweets": len(scheduled_tweets),
            "tweets": scheduled_tweets
        }

    def generate_weekly_telegram_plan(self, start_date=None) -> dict:
        """
        Generates 7 days x 2 posts = 14 high-impact Telegram channel posts for @arkadasuz.
        Tailored specifically for Uzbekistan students and parents.
        Scheduled at optimal Uzbekistan engagement hours:
          - 13:00 (Lunch break)
          - 19:30 (Evening prime family discussion time)
        Guarantees anti-repetition across weeks via TelegramHistoryEngine.
        """
        from datetime import datetime, timedelta
        import time

        if not start_date:
            try:
                from engine.telegram_scheduler import TelegramScheduler
                sched = TelegramScheduler()
                already_scheduled = [p for p in sched.data.get("posts", []) if p.get("status") in ["posted", "pending"]]
                if already_scheduled and sched.data.get("end_date"):
                    last_end = datetime.strptime(sched.data["end_date"], "%Y-%m-%d")
                    if last_end >= datetime.now():
                        start_dt = last_end + timedelta(days=1)
                    else:
                        start_dt = datetime.now() + timedelta(days=1)
                else:
                    start_dt = datetime.now() + timedelta(days=1)
            except Exception:
                start_dt = datetime.now() + timedelta(days=1)
        else:
            start_dt = start_date

        week_num = self.tg_history_engine.data.get("weeks_generated", 0) + 1
        week_id = f"tg_w_{week_num}_{int(time.time())}"

        # 7 Strategic Topic Pools for Uzbekistan Audience
        guide_pool = [
            "Attestat bahosi bilan Turkiyaga imtihonsiz qabul: Kerakli hujjatlar va bosqichlar",
            "Moviy Diplom (Mavi Diploma) nima va u O'zbekistonda qanday nostrifikatsiya qilinadi?",
            "Turkiyada talabalik vizasi: Konsullik suhbatidan rad javobisiz o'tish qoidalari",
            "TÖMER turk tili kursi: Til bilmasdan kelib, 2-3 oyda erkin so'zlashish sirlari",
            "Bologna ta'lim tizimi: Turkiya diplomining jahonning 150+ davlatida tan olinishi",
            "Magistratura va doktorantura: Turkiyada xalqaro grantlar va ilmiy tadqiqot imkoniyatlari",
            "O'qishni ko'chirish (Perevod): O'zbekistondan Turkiyaga yoki Turkiyadan O'zbekistonga ko'chirish qoidalari"
        ]

        safety_pool = [
            "Ota-onalar xavotiri: Farzandingiz Turkiyada notanish yurtda kimga ishonadi?",
            "Nega o'zbek oilalari Arkadaş Consultingni tanlaydi? Rasmiy litsenziya va shartnoma kafolati",
            "Aeroportda kutib olishdan to yotoqxonagacha: Bizning jamoa har doim talaba yonida",
            "Turkiyada talabalar xavfsizligi: Qizlar va yigitlar uchun qulay va osoyishta shahar muhiti",
            "Shaxsiy koordinator xizmati: 1-kurs davomida barcha maishiy va o'quv savollarida ko'mak",
            "Oldindan to'lovsiz ishonchli xizmat: Rasmiy qabul xati chiqqandan so'ng to'lov qilish imkoniyati"
        ]

        budget_pool = [
            "Turkiyada talabaning 1 oylik real xarajati qancha? Yotoqxona, oziq-ovqat va yo'l xarajatlari tahlili",
            "Davlat (KYK) yotoqxonalari: Bepul nonushta, kechki ovqat va oyiga hamyonbop yashash sharoiti",
            "Talabalik transport kartasi (İstanbulkart): Metro, avtobus va paromlarda 80% chegirma imtiyozi",
            "Turkiyada tejamkor talabalik hayoti: Arzon do'konlar (BİM, A101) va talabalar oshxonalari",
            "O'zbekistondan mablag' o'tkazish va Turkiyada bank kartasini xavfsiz ochish sirlari",
            "Talabalarning qonuniy ishlash imkoniyatlari: O'qish bilan birga bo'sh vaqtda daromad topish"
        ]

        story_pool = [
            "Haqiqiy hayotiy tajriba: Toshkentdan Anqaragacha — ilk haftalardagi qiyinchiliklar va yutuqlar",
            "Samarqandlik talabamizning hikoyasi: 'Turk tilini bilmasdim, ammo hozir guruh yetakchisiman'",
            "Ota-ona nigohida: 'Farzandimni xorijga yuborishdan qo'rqqandim, bugun esa uning muvaffaqiyatidan faxrlanaman'",
            "Vodiy yoshlarining Turkiya oliygohlaridagi faol hayoti va do'stona talabalar jamoasi",
            "Turkiyada o'qiyotgan o'zbek yoshlarining birdamligi va bayramlardagi samimiy uchrashuvlari"
        ]

        uni_pool = [
            "Hafta oliygohi: Istanbul Davlat Universiteti — jahon reytingidagi nufuz va zamonaviy ta'lim",
            "Hafta oliygohi: Bursa Uludağ Universiteti — O'zbek yoshlari eng ko'p tanlaydigan yashil kampus",
            "Hafta oliygohi: Anqara Hacettepe Universiteti — tibbiyot va muhandislikda xalqaro e'tirof",
            "Hafta oliygohi: Marmara Universiteti — ikki qit'ani birlashtirgan nufuzli ta'lim maskani",
            "Hafta oliygohi: Sakarya Universiteti — Istanbulga yaqin, qulay va sokin talabalar shaharchasi",
            "Hafta oliygohi: Izmir Ege Universiteti — O'rtayer dengizi bo'yidagi nufuzli davlat oliygohi"
        ]

        debate_pool = [
            "O'zbekistonlik abituriyentlar o'rtasida so'rovnoma: Siz uchun chet elda o'qishda eng muhimi nima?",
            "Abituriyentlar munozarasi: Katta megapolis hayotimi yoki sokin dengiz bo'yi shaharchasimi?",
            "Kelajak kasblari: Siz qaysi soha mutaxassisi bo'lmoqchisiz — IT, Xalqaro biznes yoki Tibbiyot?",
            "Ota-onalar bilan suhbat: Farzand tanloviga erkinlik berish kerakmi yoki yo'nalishni ota-ona tanlashi to'g'rimi?"
        ]

        cta_pool = [
            "Yangi o'quv yiliga rasmiy kvotalar ochildi: Attestatingiz bilan qaysi oliygohga kirishingiz mumkinligini biling!",
            "Kechikmang! Turkiya davlat va xususiy oliygohlariga qabullar qizg'in davom etmoqda",
            "Kelajagingiz sari ilk qadam: Arkadaş Consulting orqali bepul dastlabki tahlil va maslahat oling"
        ]

        def _pick_fresh(pool, count, fallback_prefix):
            fresh = [t for t in pool if not self.tg_history_engine.is_topic_used(t)]
            res = []
            for i in range(count):
                if i < len(fresh):
                    res.append(fresh[i])
                else:
                    idx = (week_num * 3) + i + 1
                    res.append(f"{fallback_prefix} #{week_num}-{idx}: Dolzarb tahlil va foydali ma'lumotlar")
            return res

        picked_guide = _pick_fresh(guide_pool, 3, "Turkiyada rasmiy ta'lim yo'riqnomasi")
        picked_safety = _pick_fresh(safety_pool, 2, "Arkadaş Consulting rasmiy kafolati")
        picked_budget = _pick_fresh(budget_pool, 2, "Turkiyada talabalik byudjeti")
        picked_story = _pick_fresh(story_pool, 2, "O'zbek talabalari hayotiy tajribasi")
        picked_uni = _pick_fresh(uni_pool, 2, "Hafta oliygohi tahlili")
        picked_debate = _pick_fresh(debate_pool, 2, "Abituriyentlar va ota-onalar munozarasi")
        picked_cta = _pick_fresh(cta_pool, 1, "Haftalik qabul e'loni va konsultatsiya")

        # 14 Strategic Slots across 7 Days (2 per day: 13:00 and 19:30)
        # Pairs: (topic, category_tag, icon)
        slot_plan = [
            # Day 1:
            (picked_guide[0], "💡 Huquqiy Qo'llanma", "💡"),
            (picked_safety[0], "🏛️ Rasmiy Kafolat", "🏛️"),
            # Day 2:
            (picked_budget[0], "📊 Byudjet Tahlili", "📊"),
            (picked_uni[0], "🎓 Hafta Oliygohi", "🎓"),
            # Day 3:
            (picked_story[0], "📖 Hayotiy Hikoya", "📖"),
            (picked_safety[1], "🏛️ Rasmiy Kafolat", "🏛️"),
            # Day 4:
            (picked_guide[1], "💡 Huquqiy Qo'llanma", "💡"),
            (picked_debate[0], "❓ Ochiq Munozara", "❓"),
            # Day 5:
            (picked_budget[1], "📊 Byudjet Tahlili", "📊"),
            (picked_uni[1], "🎓 Hafta Oliygohi", "🎓"),
            # Day 6:
            (picked_story[1], "📖 Hayotiy Hikoya", "📖"),
            (picked_guide[2], "💡 Huquqiy Qo'llanma", "💡"),
            # Day 7:
            (picked_debate[1], "❓ Ochiq Munozara", "❓"),
            (picked_cta[0], "🎯 Qabulga Chaqiruv", "🎯")
        ]

        days_names_uz = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        slots = [
            ("lunch", "13:00:00", "☀️ Tushlik Posti (13:00)"),
            ("evening", "19:30:00", "🌆 Kechki Asosiy Post (19:30)")
        ]

        # Rich, culturally resonant template mapping for Telegram channel
        tg_template_map = {
            "💡 Huquqiy Qo'llanma": (
                "📚 <b>{topic}</b>\n\n"
                "Chet elda ta'lim olish haqida o'ylayotgan har bir o'zbekistonlik abituriyent uchun eng muhim savol — "
                "hujjatlarni qonuniy va to'g'ri rasmiylashtirishdir.\n\n"
                "📌 <b>Asosiy talablar va imtiyozlar:</b>\n"
                "• Maktab attestati yoki kollej/litsey diplomi bilan to'g'ridan-to'g'ri topshirish mumkin.\n"
                "• YÖS yoki murakkab xalqaro imtihonlarsiz ham nufuzli oliygohlarga qabul mavjud.\n"
                "• Olingan diplom Yevropa Ittifoqida va O'zbekistonda to'liq nostrifikatsiya (denklik) qilinadi.\n\n"
                "Arkadaş Consulting mutaxassislari arizangizni birinchi bosqichdan boshlab xatosiz topshirishga yordam beradi.\n\n"
                "👉 <b>Batafsil ma'lumot va konsultatsiya:</b> @arkadasuzz\n"
                "#ArkadasUz #TurkiyaTalim #QabulQoidalari"
            ),
            "🏛️ Rasmiy Kafolat": (
                "🛡️ <b>{topic}</b>\n\n"
                "Farzandini xorijga o'qishga yuborayotgan har bir ota-onaning ko'nglida xavotir bo'lishi tabiiy: "
                "<i>'Farzandim begona yurtda qanday joylashadi? Qiyinchilikka uchrasa kim yordam beradi?'</i>\n\n"
                "✅ <b>Arkadaş Consulting bilan bu xavotirlarga o'rin yo'q:</b>\n"
                "• Biz faqat rasmiy davlat litsenziyasi va qonuniy shartnoma asosida xizmat ko'rsatamiz.\n"
                "• Talabamizni aeroportda shaxsan kutib olamiz va oldindan tayyorlangan shinam yotoqxonaga joylashtiramiz.\n"
                "• Yashash guvohnomasi (İkamet) va talabalik sug'urtasini to'liq o'z zimmamizga olamiz.\n"
                "• Shaxsiy koordinator talabamizga 1-kurs davomida har qadamda yo'l-yo'riq ko'rsatadi.\n\n"
                "Sizning xotirjamligingiz va farzandingizning xavfsizligi biz uchun doimo birinchi o'rinda!\n\n"
                "👉 <b>Ota-onalar uchun bepul konsultatsiya:</b> @arkadasuzz\n"
                "#ArkadasUz #Ishonch #OtaOnalarXotirjamligi"
            ),
            "📊 Byudjet Tahlili": (
                "💰 <b>{topic}</b>\n\n"
                "Turkiyada talabalik hayoti qulayligi bilan birga hamyonbopligi bilan ham ajralib turadi. "
                "Keling, talabaning oylik xarajatlarini birgalikda real hisoblab chiqamiz:\n\n"
                "• 🏠 <b>Yotoqxona:</b> Davlat (KYK) yotoqxonalari oyiga juda arzon bo'lib, nonushta va kechki ovqat bepul taqdim etiladi.\n"
                "• 🚌 <b>Transport:</b> Maxsus talabalik kartasi (İstanbulkart va boshqalar) bilan harakatlanish oddiy narxdan 70-80% arzonroq.\n"
                "• 🍽️ <b>Oziq-ovqat:</b> Universitet oshxonalarida talabalar uchun arzon va to'yimli issiq tushliklar mavjud.\n"
                "• 🏥 <b>Tibbiyot:</b> Davlat tibbiy sug'urtasi barcha shifoxonalarda bepul xizmat ko'rsatadi.\n\n"
                "O'rtacha byudjet bilan ham Turkiyada to'laqonli va zamonaviy talabalik davrini o'tkazish mumkin!\n\n"
                "👉 <b>O'zingizga mos shahar va xarajatlar smetasi uchun:</b> @arkadasuzz\n"
                "#TalabaHayoti #Tejamkorlik #ArkadasUz"
            ),
            "📖 Hayotiy Hikoya": (
                "🌟 <b>{topic}</b>\n\n"
                "Har yili yuzlab o'zbekistonlik yoshlar o'z orzulari sari qat'iy qadam tashlab, Turkiyaning nufuzli "
                "oliygohlarida talaba bo'lmoqda. Ular bosib o'tgan yo'l barchamiz uchun ilhom manbaidir.\n\n"
                "📌 <b>Talabalarimiz nimalarni ta'kidlaydi?</b>\n"
                "• <i>'Til masalasida qo'rquv bo'lgan edi, ammo turk tili bizning ona tilimizga shu qadar yaqinki, 2-3 oyda bemalol tushunib ketdim.'</i>\n"
                "• <i>'Oliygohlardagi zamonaviy laboratoriyalar va xalqaro talabalar muhiti fikrlashimni butunlay o'zgartirdi.'</i>\n"
                "• <i>'Eng asosiysi — Arkadaş Consulting jamoasi Turkiyaga yetib kelgan kunimdan boshlab barcha tashkiliy masalalarda yonimda turdi.'</i>\n\n"
                "Katta natijalar har doim kichik bir qat'iy qarordan boshlanadi!\n\n"
                "👉 <b>Siz ham o'z orzuingiz sari qadam bosing:</b> @arkadasuzz\n"
                "#TalabalarTajribasi #ArkadasUz #Muvaffaqiyat"
            ),
            "🎓 Hafta Oliygohi": (
                "🏛️ <b>{topic}</b>\n\n"
                "Ushbu haftada O'zbekiston yoshlari orasida eng yuqori qiziqishga ega bo'lgan nufuzli davlat oliygohi "
                "haqida batafsil ma'lumot beramiz.\n\n"
                "✨ <b>Universitetning ustun jihatlari:</b>\n"
                "• Jahon ta'lim reytinglarida mustahkam o'rin egallagan nufuzli professor-o'qituvchilar tarkibi.\n"
                "• Yevropa Ittifoqining Erasmus+ dasturi orqali Yevropaning eng yaxshi oliygohlarida grant asosida 1 semestr bepul o'qish imkoniyati.\n"
                "• Keng ko'lamli ilmiy kutubxonalar, texnoparklar va amaliyot bazalari.\n"
                "• Xalqaro talabalar uchun qulay yotoqxonalar va sport majmualari.\n\n"
                "Ushbu oliygohga qabul shartlari va kvotalar bo'yicha Arkadaş Consulting orqali to'liq ma'lumot oling.\n\n"
                "👉 <b>Fakultetlar va kontrakt narxlarini bilish:</b> @arkadasuzz\n"
                "#TurkiyaOliygohlari #DavlatUniversiteti #ArkadasUz"
            ),
            "❓ Ochiq Munozara": (
                "🗣️ <b>{topic}</b>\n\n"
                "Hurmatli abituriyentlar va aziz ota-onalar! Biz uchun har biringizning fikringiz va qiziqishlaringiz nihoyatda qadrli.\n\n"
                "Bugun oliy ta'lim yo'nalishini tanlash har bir yoshning kelajakdagi hayot yo'lini belgilab beradi. "
                "Chet elda o'qish, zamonaviy kasb egalari bo'lish yoki xalqaro diplom olishda sizni eng ko'p o'ylantirayotgan "
                "masala nima?\n\n"
                "👇 <b>O'z fikringizni izohlarda yozib qoldiring!</b>\n"
                "Eng qiziqarli savollarga mutaxassislarimiz keyingi postlarimizda to'liq javob berib o'tishadi.\n\n"
                "👉 <b>Shaxsiy savollar uchun:</b> @arkadasuzz\n"
                "#Munozara #Abituriyent2025 #ArkadasUz"
            ),
            "🎯 Qabulga Chaqiruv": (
                "📢 <b>{topic}</b>\n\n"
                "Vaqtni boy bermang! Turkiyaning nufuzli davlat va xususiy universitetlariga 2025-yilgi qabul jarayoni "
                "qizg'in davom etmoqda.\n\n"
                "🎯 <b>Nega hozirdan ariza topshirish kerak?</b>\n"
                "• Eng talabgir yo'nalishlarda kvotalar soni cheklangan bo'ladi.\n"
                "• Hujjatlarni erta topshirgan talabalar viza va yotoqxona masalalarini xotirjam hal qilishadi.\n"
                "• Arkadaş Consulting barcha hujjatlaringizni 100% rasmiy va qonuniy rasmiylashtirib beradi.\n\n"
                "✅ <b>Biz bilan boshlash oson:</b> Maktab attestatingiz yoki kollej diplomingizni yuboring va "
                "qaysi universitetlarga qabul qilinishingiz mumkinligini bilib oling!\n\n"
                "👉 <b>Bepul qabul tahlili uchun hoziroq yozing:</b> @arkadasuzz\n"
                "#ArkadasUz #Qabul2025 #OrzularSari"
            )
        }

        scheduled_posts = []
        slot_idx = 0

        for day_idx in range(7):
            cur_date = start_dt + timedelta(days=day_idx)
            cur_date_str = cur_date.strftime("%Y-%m-%d")
            day_name = days_names_uz[cur_date.weekday()]

            for slot_key, slot_time_str, slot_label in slots:
                scheduled_iso = f"{cur_date_str}T{slot_time_str}"
                post_id = f"tg_{cur_date.strftime('%Y%m%d')}_{slot_key[:3]}"

                if slot_idx < len(slot_plan):
                    t_topic, cat_tag, cat_ico = slot_plan[slot_idx]
                else:
                    t_topic, cat_tag, cat_ico = ("Turkiyada talabalik imkoniyatlari", "💡 Huquqiy Qo'llanma", "💡")

                tpl = tg_template_map.get(cat_tag, tg_template_map["💡 Huquqiy Qo'llanma"])
                content = tpl.format(topic=t_topic)

                post_obj = {
                    "id": post_id,
                    "day_index": day_idx + 1,
                    "day_name": day_name,
                    "date_str": cur_date_str,
                    "slot": slot_key,
                    "slot_label": slot_label,
                    "cat_tag": cat_tag,
                    "scheduled_time": scheduled_iso,
                    "topic": t_topic,
                    "content": content,
                    "status": "pending"
                }

                self.tg_history_engine.record_topic(t_topic)
                self.tg_history_engine.record_post(content, t_topic)
                scheduled_posts.append(post_obj)
                slot_idx += 1

        self.tg_history_engine.record_week_generation()
        end_date_str = (start_dt + timedelta(days=6)).strftime("%Y-%m-%d")

        return {
            "week_id": week_id,
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_date_str,
            "total_posts": len(scheduled_posts),
            "posts": scheduled_posts
        }

if __name__ == "__main__":
    cg = ContentGenerator()
    print("\n--- Testing Q&A Post Generation ---")
    p1 = cg.generate_qa_post()
    print("Media:", p1["media_path"])
    print("Caption:\n", p1["caption"])

    print("\n--- Testing Evergreen Template A Post ---")
    ea = cg.generate_evergreen_post("A")
    print(f"Template A ({ea['char_count']} chars):\n", ea["content"])
