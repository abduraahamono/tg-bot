#!/usr/bin/env python3
"""
Arkadaş Consulting - Universal AI Brain Engine
Multi-Provider Fault-Tolerant LLM Architecture:
Supports:
1. Google Gemini (with multi-key rotation across up to 3 keys)
2. Groq (Llama 3.3 70B / 8B - ultra-fast)
3. GLM (Zhipu AI GLM-4 / GLM-4-Flash)
4. Ollama (Local offline models: llama3, mistral, etc.)
5. Automatic Fallback: Gemini -> Groq -> GLM -> Ollama -> Brand Knowledge Engine

Every call automatically injects the Arkadaş Consulting Brand Identity,
services, promises ("Oldindan to'lov yo'q"), and native Uzbek marketing tone.
"""

import os
import sys
import json
import random
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List

BASE_DIR = Path(__file__).parent.parent
BRAIN_DIR = BASE_DIR / "brain_data"
CONFIG_FILE = BASE_DIR / "ai_config.json"
ENV_FILE = BASE_DIR / ".env"

def load_ai_config() -> Dict[str, Any]:
    config = {
        "active_provider": "auto",  # 'gemini', 'groq', 'glm', 'ollama', or 'auto'
        "gemini_keys": [],          # Supports 1, 2, or 3 keys for rotation
        "groq_key": "",
        "glm_key": "",
        "ollama_host": "http://127.0.0.1:11434",
        "ollama_model": "llama3",
        "gemini_model": "gemini-2.5-flash",
        "groq_model": "llama-3.3-70b-versatile",
        "glm_model": "glm-4-flash"
    }

    # Load from .env if present
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip().upper()
                v = v.strip().strip("'\"")
                if k in ("GEMINI_API_KEY", "GEMINI_KEY", "GEMINI_API_KEY_1"):
                    if v and v not in config["gemini_keys"]:
                        config["gemini_keys"].append(v)
                elif k in ("GEMINI_API_KEY_2", "GEMINI_API_KEY_3"):
                    if v and v not in config["gemini_keys"]:
                        config["gemini_keys"].append(v)
                elif k in ("GROQ_API_KEY", "GROQ_KEY"):
                    config["groq_key"] = v
                elif k in ("GLM_API_KEY", "ZHIPU_API_KEY", "GLM_KEY"):
                    config["glm_key"] = v

    # Override from ai_config.json
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config.update(saved)
        except Exception:
            pass

    # Check environment variables directly
    for env_k, env_v in os.environ.items():
        if "GEMINI" in env_k and "KEY" in env_k and env_v:
            if env_v not in config["gemini_keys"]:
                config["gemini_keys"].append(env_v)
        elif "GROQ" in env_k and "KEY" in env_k and env_v:
            config["groq_key"] = env_v
        elif "GLM" in env_k and "KEY" in env_k and env_v:
            config["glm_key"] = env_v

    return config

class AIBrain:
    def __init__(self):
        self.config = load_ai_config()
        self.current_gemini_idx = 0
        self._load_brand_context()

    def _load_brand_context(self):
        brand_path = BRAIN_DIR / "brand_profile.json"
        guide_path = BRAIN_DIR / "brand_content_guide.json"
        uni_path = BRAIN_DIR / "universities.json"
        faq_path = BRAIN_DIR / "faq_knowledge.json"

        brand = {}
        if brand_path.exists():
            with open(brand_path, "r", encoding="utf-8") as f:
                brand = json.load(f)

        unis = []
        if uni_path.exists():
            with open(uni_path, "r", encoding="utf-8") as f:
                unis = json.load(f)

        self.system_prompt = (
            "Sen 'Arkadaş Consulting' kompaniyasining bosh marketing bo'yicha sun'iy intellekt ekspertisan.\n"
            "Ushbu ko'rsatmalar t.me/arkadasuz kanalining 560 ta real posti tahlilidan va rasmiy brend qoidalaridan olingan:\n\n"
            "1. MARKA OVOZI VA PRINSIPLARI:\n"
            "   - Dürüst, ishonchli, samimiy va professional.\n"
            "   - ASLO yolg'on yoki asossiz maosh va'dalari (masalan '$2000-$5000 maosh') YOZILMAYDI!\n"
            "   - Asosiy kuchli tomonlarimiz: '99% muvaffaqiyat darajasi', 'Oldindan to'lov yo'q — 0$ risk (avval rasmiy qabul xati chiqadi, keyin to'lov)', 'Bologna tizimi — 150+ davlatda tan olinadigan diplom', 'Attestat bilan imtihonsiz qabul'.\n\n"
            "2. POSTLARNING 3 ASOSIY TURI:\n"
            "   - 📚 1. BİLGİLENDİRİCİ (Ta'lim & Maslahat): Bologna konvensiyasi, nostrifikatsiya, YÖS/SAT imtihonisiz attestat bilan qabul, talabalar hayoti va yotoqxona sharoitlari.\n"
            "   - 💼 2. REKLAM & GÜVEN (Xizmatlar): 0$ risk tizimi, rasmiy shartnoma, universitet tanlashdan viza, aeroportda kutib olish va yotoqxonaga joylashtirishgacha to'liq hamrohlik.\n"
            "   - 📢 3. HABER & INFO (Kvotalar & Deadlines): 2026-yilgi qabul kvotalari, Tibbiyot, IT, Muhandislik bo'yicha cheklangan o'rinlar, hujjat topshirish muddatlari.\n\n"
            "3. SISTEMALI EMOJI QOIDALARI:\n"
            "   - ✅ = Xizmat va afzallik\n"
            "   - 🎓 = Ta'lim va universitet\n"
            "   - 📌 = Muhim fakt / ro'yxat\n"
            "   - 🇹🇷 = Turkiya bayrog'i sarlavhada albatta ishlatiladi\n"
            "   - 📲 = Faqat CTA qismida\n\n"
            "4. POST UZUNLIGI:\n"
            "   - 550 - 650 belgi (chiroyli bo'shliqlar va qatorlar bilan o'qishga oson).\n\n"
            "5. QAT'IY ALOQA STANDARTI (Telefon va veb-sayt yo'q):\n"
            "   Har bir post oxirida FAQAT va FAQAT ushbu formatda CTA qo'yiladi:\n"
            "   📲 Bepul konsultatsiya va qabul uchun:\n"
            "   👉 Telegram: @arkadasuzz\n"
            f"Universitetlar ma'lumotlaridan to'g'ri foydalan (jami {len(unis)} ta nufuzli universitet)."
        )

    # 1. Google Gemini Provider
    def _call_gemini(self, prompt: str, custom_system_prompt: Optional[str] = None, max_tokens: int = 4096) -> Optional[str]:
        keys = self.config.get("gemini_keys", [])
        if not keys:
            return None

        sys_p = custom_system_prompt if custom_system_prompt else self.system_prompt
        parts_text = f"{sys_p}\n\nMijoz savoli: {prompt}" if custom_system_prompt else f"{sys_p}\n\n---\nVAZIFA:\n{prompt}"

        # Priority working models
        models = ["gemini-flash-lite-latest", "gemini-pro-latest", "gemini-flash-latest"]
        for model in models:
            for _ in range(len(keys)):
                key = keys[self.current_gemini_idx % len(keys)]
                self.current_gemini_idx += 1
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": parts_text}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.6 if custom_system_prompt else 0.7,
                        "maxOutputTokens": max_tokens
                    }
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )

                try:
                    with urllib.request.urlopen(req, timeout=12) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        candidate = data.get("candidates", [{}])[0]
                        parts = candidate.get("content", {}).get("parts", [])
                        text = "".join([p.get("text", "") for p in parts if "text" in p]).strip()
                        if len(text) > 10:
                            return text
                except Exception:
                    pass

        return None

    # 2. Groq Provider (Ultra-Fast)
    def _call_groq(self, prompt: str) -> Optional[str]:
        key = self.config.get("groq_key", "")
        if not key:
            return None

        url = "https://api.groq.com/openai/v1/chat/completions"
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    return None  # Key invalid, stop immediately
            except Exception:
                pass

        return None

    # 3. GLM (Zhipu AI GLM-4) Provider
    def _call_glm(self, prompt: str) -> Optional[str]:
        key = self.config.get("glm_key", "")
        if not key:
            return None

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        model = self.config.get("glm_model", "glm-4-flash")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[GLM Error] {e}")
            return None

    # 4. Ollama (Local Offline Model)
    def _call_ollama(self, prompt: str) -> Optional[str]:
        host = self.config.get("ollama_host", "http://127.0.0.1:11434")
        model = self.config.get("ollama_model", "llama3")
        url = f"{host}/api/generate"

        payload = {
            "model": model,
            "prompt": f"{self.system_prompt}\n\n{prompt}",
            "stream": False
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip()
        except Exception as e:
            return None

    # Master Generate with Auto-Fallback
    def think_and_generate(self, task_prompt: str, custom_system_prompt: Optional[str] = None, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Executes prompt through active provider or auto-fallback chain:
        Gemini -> Groq -> GLM -> Ollama
        """
        provider = self.config.get("active_provider", "auto")

        # 1. Direct provider selection if specified
        if provider == "gemini":
            res = self._call_gemini(task_prompt, custom_system_prompt=custom_system_prompt, max_tokens=max_tokens)
            if res: return {"provider": "gemini", "text": res}
        elif provider == "groq":
            res = self._call_groq(task_prompt)
            if res: return {"provider": "groq", "text": res}
        elif provider == "glm":
            res = self._call_glm(task_prompt)
            if res: return {"provider": "glm", "text": res}
        elif provider == "ollama":
            res = self._call_ollama(task_prompt)
            if res: return {"provider": "ollama", "text": res}

        # 2. Auto-Fallback Chain
        # Try Gemini first (Best Uzbek accuracy)
        res = self._call_gemini(task_prompt, custom_system_prompt=custom_system_prompt, max_tokens=max_tokens)
        if res:
            return {"provider": "gemini", "text": res}

        # Fallback to Groq (Blazing fast)
        res = self._call_groq(task_prompt)
        if res:
            return {"provider": "groq", "text": res}

        # Fallback to GLM
        res = self._call_glm(task_prompt)
        if res:
            return {"provider": "glm", "text": res}

        # Fallback to Ollama
        res = self._call_ollama(task_prompt)
        if res:
            return {"provider": "ollama", "text": res}

        return {"provider": "deterministic_fallback", "text": None}

    # Specialized Marketing Generators
    def generate_viral_reels_script(self, topic: str = "Turkiyada o'qish va grantlar") -> str:
        prompt = (
            f"Mavzu: '{topic}'.\n"
            "Instagram Reels va TikTok uchun 15 soniyalik juda qiziqarli, yoshlarni o'ziga tortadigan "
            "video senariy yoz. 3 qismdan iborat bo'lsin:\n"
            "1. KANCA (Hook) - birinchi 3 soniyada qiziqtiradigan savol yoki fakt\n"
            "2. ASOSIY MAZMUN - Arkadaş Consulting orqali beriladigan imkoniyat\n"
            "3. HARAKATGA CHAQIRUV (Call to action) - Kommentariyada yozing yoki profilga kiring\n"
            "O'zbek tilida, yoshlarbop emojilar bilan."
        )
        res = self.think_and_generate(prompt)
        return res["text"] or "2025 o'quv mavsumi boshlandi! Turkiyadagi eng yaxshi universitetlarga grant asosida qabul bo'ling!"

    def answer_student_consultation(self, student_question: str, history_context: str = "", user_info: dict = None) -> str:
        user_desc = ""
        if user_info:
            if user_info.get("is_admin"):
                user_desc = "DIQQAT: Bu suhbatdosh kompaniya admini/rahbari. Unga alohida hurmat bilan javob ber.\n"
            if user_info.get("name"):
                user_desc += f"Mijoz ismi: {user_info.get('name')}\n"

        consultant_system = (
            "Sen Arkadaş Consulting kompaniyasining Telegramdagi jonli va samimiy konsultanisan (Turkiyada ta'lim bo'yicha).\n"
            f"{user_desc}"
            "KOMPANIYA VA XIZMATLARIMIZ (ARKADAŞ CONSULTING ANIQ MA'LUMOTLARI):\n"
            "- Biz O'zbekistonda rasmiy ro'yxatdan o'tgan MChJ konsalting kompaniyasimiz. Shartnoma asosida, 100% qonuniy va ishonchli ishlaymiz (o'tgan yili 40 nafar, bu yil 20 dan ortiq talabani yubordik).\n"
            "- BURS XIZMATI ('Türkiye Bursları' davlat stipendiyasi):\n"
            "  Qishda arizalar ochiladi. Yutgan talabaga: bepul o'qish, bepul yotoqxona, oylik stipendiya va samolyot bileti beriladi. Biz ariza topshirish, motivatsion xat yozish va tavsiyanoma olishda to'liq yordam beramiz. ENG MUHIM KAFOLAT: Agar grant chiqmasa, to'lovingizning 50% qaytariladi YOKI $500 qiymatidagi 'Asosiy Paket'imiz sizga BEPUL taqdim etiladi! (20 dan ortiq talabamiz yutgan).\n"
            "- RASMIY XIZMAT PAKETLARI VA NARXLAR:\n"
            "  1) Asosiy Paket ($500) - 99% kafolatli: Ariza topshirish, elchixonadan denklik olish, hujjatlar rasmiy tarjimasi, qabul xati.\n"
            "  2) O'rta Paket ($800): Asosiy paket + Aeroportda kutib olish, 1 kunlik Istanbul sayohati, sog'liq sug'urtasi, yashash ruxsatnomasi (kimlik/ikamet), SIM-karta va bank hisobi ochish.\n"
            "  3) Katta Paket ($1100): O'rta paket + 1 yillik TÖMER tili tayyorlov kursi + 4 yillik to'liq grant kelishuvi (75% gacha grant yoki bepul o'qish).\n"
            "- QABUL VA IMTIHONLAR:\n"
            "  * DTM yoki YÖS siz, faqat maktab/kollej attestat baholari bilan davlat va xususiy universitetlarga to'g'ridan-to'g'ri qabul qilamiz.\n"
            "  * YÖS ballari: Davlatga YÖS topshirsa 90-95 ball kerak, xususiyga SAT, lekin YÖSsiz attestat bilan ham kirsa bo'ladi.\n"
            "- YO'NALISHLAR VA UNIVERSITETLAR:\n"
            "  * Tibbiyot ('tıp') va stomatologiya: Davlatda $800 - $2,000/yil (Istanbul va Ankara universitetlari juda kuchli va hamyonbop). Medipol esa xususiy va juda qimmat.\n"
            "  * Ilahiyot (İlahiyat): 29 Mayıs Universiteti va Istanbul Universiteti juda kuchli. Arab tilini bilmasa, universitetda 1 yil arabcha tayyorlov kursi (hazırlık) o'qiladi.\n"
            "  * Boshqa davlat universitetlari yillik to'lovi: $300 - $800 atrofida. Yotoqxona va oylik yashash: $150 - $250.\n\n"
            "QAT'IY USLUB VA ETIKET QOIDALARI:\n"
            "1. HURMAT VA 'SIZ' USLUBI (ENG MUHIM): Biz professional kompaniyasimiz. ASLO 'sen', 'o'zing', 'borasan' deb senlama! Har doim xushmuomala 'Siz' deb gapir: 'borganingiz ma'qul', 'o'zingiz', 'bormoqchisiz', 'topshirishingiz mumkin', 'qiziqyapsizmi'.\n"
            "2. BURS VA REKLAMAMIZ MAZMUNI: Agar mijoz 'burs', 'Türkiye Bursları' yoki 'grant' desa, quruq rasmiy gap aytma! Kompaniyamizning haqiqiy Burs xizmatini samimiy ayt: grant chiqsa bepul o'qish, stipendiya va yotoqxona borligini, biz hujjat va motivatsion xat yozib berishimizni, chiqmasa 50% pul qaytarilishi yoki $500 lik Asosiy Paket bepul berilishini lo'nda tushuntir!\n"
            "3. XOTIRA VA SUHBAT DAVOMIYLIGI: Avvalgi suhbat tarixini diqqat bilan esla. Agar mijoz qisqa so'z aytsa (masalan: 'tip', 'narx', 'ha', 'burs'), bu avvalgi savolingizga javob! Suhbat davomida qayta-qayta 'Assalomu alaykum' deb yangidan boshlama!\n"
            "4. JAVOBING JUDA QISQA VA TABIIY BO'LSIN: Maksimal 2-3 ta lo'nda jumla! Hech qanday keraksiz uzun ro'yxatlar tashlama.\n"
            "5. Oxirida 'Siz' shaklida bitta qisqa, xushmuomala savol bilan suhbatni davom ettir."
        )

        full_prompt = student_question
        if history_context:
            full_prompt = (
                f"OLDINGI SUHBAT TARIXI:\n{history_context}\n\n"
                f"MIJOZNING YANGI XABARI: {student_question}\n"
                "Ushbu yangi xabarga oldingi suhbat mantiqidan kelib chiqib qisqa, tabiiy va 'Siz' deb javob qaytar:"
            )

        res = self.think_and_generate(full_prompt, custom_system_prompt=consultant_system, max_tokens=250)
        return res.get("text") or "Turkiyada ta'lim bo'yicha savolingiz bormi? O'zingiz qaysi yo'nalishga qiziqyapsiz?"

if __name__ == "__main__":
    brain = AIBrain()
    print("AI Brain initialized.")
    print("Configured Providers:")
    print(" - Gemini Keys:", len(brain.config.get("gemini_keys", [])))
    print(" - Groq Key:", "Present" if brain.config.get("groq_key") else "Missing")
    print(" - GLM Key:", "Present" if brain.config.get("glm_key") else "Missing")
    print(" - Ollama Host:", brain.config.get("ollama_host"))
