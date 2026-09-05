#!/usr/bin/env python3
"""
Arkadaş Consulting - Autonomous Topic Engine
Manages rich, diverse topic pools across 3 post categories:
1. educational (30+ topics: cities, specific universities, history, culture, student hacks, Bologna)
2. promotional (25+ honest topics: 0$ advance payment, 99% admission rate, official contract, full support)
   - STRICT RULE: NEVER make false visa claims (NO "0% viza rad" or guaranteed visa issuance).
3. news (25+ topics: 2026 quotas, deadlines, medical/IT seats, discounts, university calendars)

Autonomous Replenishment:
When unused topics in any category drop below a threshold, the engine automatically
calls AI Brain to synthesize 10 brand-new, unique, unrepeated topics based on real
Turkish universities, student cities, and historical/cultural connections.
Topics NEVER end ("konu hiç bitmesin").
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

BASE_DIR = Path(__file__).parent.parent
BRAIN_DIR = BASE_DIR / "brain_data"
TOPICS_FILE = BRAIN_DIR / "dynamic_topics.json"

BASELINE_TOPICS: Dict[str, List[Dict[str, str]]] = {
    "educational": [
        {"title": "Bologna konvensiyasi va Yevropa diplomi", "desc": "Turkiya oliygohlarining Bologna tizimiga a'zoligi, diplomi 150+ davlatda va O'zbekistonda hech qanday to'siqsiz tan olinishi va oson nostrifikatsiyasi"},
        {"title": "Attestat baholari bilan imtihonsiz qabul", "desc": "YÖS yoki SAT imtihonisiz faqatgina maktab attestati yoki kollej/litsey diplomi baholari asosida to'g'ridan-to'g'ri qabul qilinish sirlari"},
        {"title": "KYK davlat va xususiy yotoqxonalari", "desc": "Turkiyada talabalar turar joyi: zamonaviy KYK va qulay xususiy yotoqxonalar, 3 mahal to'yimli ovqat, bepul Wi-Fi va 24/7 xavfsizlik"},
        {"title": "Erasmus+ bilan Yevropada bepul o'qish", "desc": "Turkiya universitetlari talabalari Erasmus+ dasturi orqali Germaniya, Italiya, Polsha yoki Fransiyada 1-2 semestr bepul tahsil olib, yevroda stipendiya olishi"},
        {"title": "Til o'rganish: TÖMER va Ingliz tili", "desc": "Turk tilini bilmasangiz ham xavotir yo'q: TÖMER til tayyorlov kursi 0 dan o'rgatadi yoki to'liq ingliz tilidagi xalqaro fakultetlarda o'qish imkoniyati"},
        {"title": "Talabalik kartasi (Öğrenci Kartı) imtiyozlari", "desc": "Turkiya talabalik kartasi beradigan qulayliklar: shahar transportiga 70% chegirma, bepul davlat muzeylari, teatrlar va arzon oshxonalar"},
        {"title": "Tibbiyot va Stomatologiya amaliyoti", "desc": "Turkiya tibbiyot fakultetlarining jahon andozasidagi laboratoriyalari, zamonaviy klinikalardagi jonli amaliyot va Yevropa darajasidagi diplom"},
        {"title": "IT va Dasturiy ta'minot istiqbollari", "desc": "Turkiyaning eng yirik texnoparklarida amaliyot o'tash, startaplar va xalqaro kompaniyalar bilan ishlash imkoniyati"},
        {"title": "Talabalik vizasi (İkamet) va qonuniy huquqlar", "desc": "Turkiyada talabaning qonuniy yashash ruxsatnomasi (ikamet), davlat tibbiy sug'urtasi va to'liq himoyalangan xavfsiz hayoti"},
        {"title": "O'zbekistonlik talabalar muhiti", "desc": "Turkiyada tahsil olayotgan minglab o'zbek yoshlari, talabalar uyushmalari, samimiy do'stlik va begonalik his qilmaslik"},
        {"title": "Eskişehir — Haqiqiy talabalar poytaxti", "desc": "Aholisining 70% talabalar bo'lgan, velosipedlar shahri Eskişehir, Anadolu universiteti kampusi va arzon hayot tarzi"},
        {"title": "Istanbul: Madaniyat va ilm-fan megapolisi", "desc": "Tarix va zamonaviylik uyg'unlashgan shahar: 50 dan ortiq universitetlar, Bosfor manzarasi va jahon miqyosidagi imkoniyatlar"},
        {"title": "Anqara: Talabalar va intellektual poytaxt", "desc": "Turkiya poytaxtida ta'lim: ODTÜ, Gazi, Hacettepe va Anqara universitetlari, sokin akademik muhit va kutubxonalar"},
        {"title": "Izmir: Egey dengizi bo'yidagi erkin talabalik", "desc": "Ege va Dokuz Eylül universitetlari, yoqimli dengiz iqlimi, mehmondo'st odamlar va talabalar uchun qulay sharoitlar"},
        {"title": "Bursa: Tarixiy Usmonli poytaxti va Uludağ kampusi", "desc": "Samarqandga o'xshash qadimiy obidalar, yashil tabiat, kuchli sanoat va Uludağ universiteti imkoniyatlari"},
        {"title": "Sakarya: O'zbek talabalari eng ko'p tanlagan shahar", "desc": "Istanbulga atigi 1.5 soatlik masofa, sokin Serdivan kampusi, ko'l bo'yidagi hordiq va hamyonbop ijara narxlari"},
        {"title": "Antalya: O'rta yer dengizida xalqaro ta'lim", "desc": "Akdeniz universiteti, xalqaro turizm, iliq iqlim va butun dunyodan kelgan talabalar muhiti"},
        {"title": "Konya: Seljuqiylar tarixi va qadimiy ilm maskani", "desc": "Mavlono Rumiy yurti, Selçuk universiteti, juda arzon yashash xarajatlari va samimiy an'anaviy muhit"},
        {"title": "Istanbul Universiteti (1453-yil)", "desc": "Turkiyaning eng qadimiy OTMi: Beyazıt maydonidagi tarixiy darvoza, mashhur huquq, adabiyot va tibbiyot maktabi"},
        {"title": "Marmara Universiteti: 5 tildagi ta'lim", "desc": "Istanbulning Yevropa va Osiyo tomonlaridagi kampuslari, nemischa, inglizcha va fransuzcha ta'lim dasturlari"},
        {"title": "Yıldız Teknik Universiteti: Muhandislik afsonasi", "desc": "1911-yildan buyon texnik elitalarni yetishtirib kelayotgan ulkan muhandislik va arxitektura markazi"},
        {"title": "O'zbek va Turk xalqlarining mushtarak qadriyatlari", "desc": "Umumiy turkiy ildizlar, Alisher Navoiy va Yunus Emre merosi, mehmondo'stlik va 100% halol muhit"},
        {"title": "Universitet oshxonalari (Yemekhane) siri", "desc": "Turkiyada davlat subsidiyasi bilan 1 dollar atrofida beriladigan 4 xil issiq va to'yimli talabalar tushligi"},
        {"title": "Turkiya kutubxonalari: 24/7 ochiq ilm zallari", "desc": "Tunda bepul choy, qahva va sho'rva ulashiladigan ulkan zamonaviy talabalar kutubxonalari"},
        {"title": "Qonuniy talabalik ishlash huquqi", "desc": "Turkiyada magistratura va doktorantura talabalari uchun qonuniy haftalik ishlash tartiblari va amaliyotlar"},
        {"title": "ECTS kredit tizimi va fanlarni tanlash erkinligi", "desc": "Talaba o'z dars jadvalini o'zi tuzishi, qiziqqan fanlarini erkin tanlashi va o'z vaqtini boshqarishi"},
        {"title": "Vize va Final imtihonlari tizimi", "desc": "Turkiya oliygohlarida baholash tizimi: oraliq (vize) va yakuniy (final) imtihonlari va stipendiya olish imkoniyati"},
        {"title": "Turk tilini o'rganish qanchalik oson?", "desc": "O'zbek tili bilan 70% grammatik va leksik yaqinlik tufayli o'zbek yoshlari turk tilini 3-4 oyda ravon gapirib ketishi"},
        {"title": "Talabalar uchun sport va to'garaklar (Kulüpler)", "desc": "Har bir universitetda 100 dan ortiq qiziqish klublari: robototexnika, kino, alpinizm, ot sporti va teatr"},
        {"title": "O'zbekistonga qaytganda diplomni nostrifikatsiyalash", "desc": "Bologna tizimidagi Turkiya diplomlarining Ta'lim sifatini nazorat qilish inspeksiyasidan oson o'tish tartibi"}
    ],
    "promotional": [
        {"title": "0$ Oldindan to'lov — 0$ Xavf tizimi", "desc": "Talaba avval o'z nomiga chiqqan rasmiy universitet qabul xatini (Acceptance Letter) qo'liga oladi, tekshiradi, keyin to'lov qiladi"},
        {"title": "99% Universitet qabuli muvaffaqiyati", "desc": "Arkadaş Consulting ning 5 yillik tajribasi, 1000 dan ortiq talabalari va to'g'ri tanlangan strategiya natijasi"},
        {"title": "Ikki tomonlama rasmiy yuridik shartnoma", "desc": "Har bir talaba va ota-ona bilan qonuniy shartnoma imzolanadi, barcha majburiyatlar va to'lovlar shaffof ko'rsatiladi"},
        {"title": "Shaxsiy ta'lim mentori biriktirilishi", "desc": "Abituriyentning qobiliyati, byudjeti va maqsadiga qarab eng to'g'ri yo'nalish va universitetni tanlashda yordam beramiz"},
        {"title": "Hujjatlarni professional tarjima va apostil qilish", "desc": "Hujjatlarni xalqaro andozalarga moslab turk tiliga notarial tarjima va apostil qilishda ko'maklashamiz"},
        {"title": "Elchixona suhbatiga to'g'ri tayyorgarlik ko'rish", "desc": "Viza arizasini xatosiz to'ldirish, talab qilinadigan barcha hujjatlar to'plamini tartibli tayyorlash va suhbat tavsiyalari"},
        {"title": "Aeroportda maxsus transport bilan kutib olish", "desc": "Istanbul yoki Anqaraga ilk bor qo'nganingizda xodimlarimiz sizni kutib oladi va xavfsiz manzilga eltadi"},
        {"title": "Yotoqxonaga joylashishda shaxsiy hamrohlik", "desc": "Oldindan band qilingan qulay yotoqxonaga joylashish, shartnoma tuzish va ro'yxatdan o'tishda yoningizda bo'lamiz"},
        {"title": "Mahalliy SIM-karta va bank hisob ochish", "desc": "Turkiyadagi ilk kunlardayoq aloqa va to'lov vositalariga ega bo'lishingiz uchun amaliy yordam"},
        {"title": "Kontrakt to'lovlarini to'g'ridan-to'g'ri universitetga to'lash", "desc": "Hech qanday vositachilarsiz, o'qish pulini bevosita universitetning rasmiy hisob raqamiga to'lash kafolati"},
        {"title": "Kontraktni semestrma-semestr bo'lib to'lash", "desc": "Yillik to'lovni birdaniga emas, 2 ga bo'lib to'lash imkoniyatini taqdim etuvchi universitetlar"},
        {"title": "Toshkentdagi ofisimizda yuzma-yuz bepul konsultatsiya", "desc": "Ota-onalar va talabalar ofisimizga kelib, barcha savollariga to'liq va ochiq javob olishlari mumkin"},
        {"title": "Universitet ichki grant chegirmalarini qo'lga kiritish", "desc": "Abituriyentning attestat baholari yuqori bo'lsa, xususiy universitetlarda 50% dan 75% gacha grant chegirmalariga topshirish"},
        {"title": "Hujjat topshirishdan talaba bo'lishgacha to'liq monitoring", "desc": "Qabul komissiyasi bilan to'g'ridan-to'g'ri aloqa orqali har bir arizaning holatini doimiy nazorat qilib boramiz"},
        {"title": "Ota-onalar uchun to'liq xotirjamlik va ochiqlik", "desc": "Farzandingizning xavfsizligi, qonuniy maqomi va o'qish joyi haqida muntazam ma'lumot beramiz"},
        {"title": "To'g'ri mutaxassislik tanlash bo'yicha yo'riqnoma", "desc": "Kelajakda talab yuqori bo'lgan sohalarni zamonaviy mehnat bozori tahliliga asoslanib tanlash"},
        {"title": "Turkiya davlat universitetlari bo'yicha kuchli tajriba", "desc": "Arzon kontraktli va nufuzli davlat oliygohlarining xalqaro kvotalariga to'g'ri hujjat topshirish"},
        {"title": "Talabalik vizasi (İkamet) hujjatlarini to'g'ri yig'ish", "desc": "Turkiyaga yetib borgach, politsiya va migratsiya idorasiga topshiriladigan hujjatlarni rasmiylashtirishda ko'mak"},
        {"title": "Shoshilinch holatlarda tezkor yordam", "desc": "O'qish boshlangandan keyin ham savollar va murojaatlarga doimiy ochiq bo'lgan Arkadaş jamoasi"},
        {"title": "Shaffof narxlar — yashirin to'lovlarsiz", "desc": "Bizning xizmat narxlarimiz boshidanoq ochiq aytiladi, keyinchalik kutilmagan to'lovlar chiqmaydi"},
        {"title": "5 yillik obro' va ishonchli hamkorlik", "desc": "Turkiyaning yetakchi oliygohlari bilan to'g'ridan-to'g'ri rasmiy aloqalar"},
        {"title": "Mustaqil topshirishdagi xatolarning oldini olish", "desc": "Noto'g'ri hujjat topshirib, 1 yil vaqtni boy bermaslik uchun professional ekspert ko'magi"},
        {"title": "Diplom va attestat baholarini to'g'ri ekvivalentlash", "desc": "Turkiya ta'lim vazirligi (MEB) talablariga mos holda baholarni hisoblash"},
        {"title": "Arzon va sifatli turar joy topishda maslahatlar", "desc": "Byudjetingizga mos bo'lgan eng qulay va xavfsiz rayonlarni tavsiya qilish"},
        {"title": "Kelajakdagi karyera va amaliyotga zamin", "desc": "Bologna diplomi orqali xalqaro kompaniyalarga yo'l ochishda ilk to'g'ri qadam"}
    ],
    "news": [
        {"title": "2026-yilgi Turkiya qabul kvotalari ochildi", "desc": "Davlat va xususiy universitetlarda yangi o'quv yili uchun xalqaro talabalar arizalari qabuli boshlandi"},
        {"title": "Tibbiyot va Stomatologiya kvotalari kam qoldi", "desc": "Davolash ishi va tish shifokorligi fakultetlarida xalqaro talabalar uchun o'rinlar juda cheklangan"},
        {"title": "IT va Sun'iy intellekt yo'nalishlarida muddatlar", "desc": "Dasturiy ta'minot, kiberxavfsizlik va kompyuter muhandisligi bo'yicha 1-bosqich qabuli yakunlanmoqda"},
        {"title": "Xususiy universitetlarda 50%-75% grant davri", "desc": "Erta ro'yxatdan o'tgan abituriyentlar uchun yuqori grant chegirmalari belgilangan muddatgacha amal qiladi"},
        {"title": "Istanbul va Anqara davlat universitetlari taqvimi", "desc": "Turkiyaning eng nufuzli top-universitetlarida hujjat topshirish sanalari va bosqichlari"},
        {"title": "Maktab attestati bilan 1-bosqich ro'yxatga olish", "desc": "Attestat yoki litsey diplomi baholari asosida imtihonsiz qabul qilinishning dastlabki bosqichi"},
        {"title": "Bahorgi va kuzgi semestr qabul taqvimi", "desc": "Turkiya universitetlarining yangi o'quv yili uchun rasmiy qabul muddatlari e'lon qilindi"},
        {"title": "Arzon kontraktli davlat oliygohlari kvotalari", "desc": "Yillik to'lovi hamyonbop bo'lgan nufuzli davlat universitetlariga hujjat topshirish boshlandi"},
        {"title": "Arxitektura va Qurilish fakultetlarida yangi o'rinlar", "desc": "Turkiyaning eng kuchli texnik universitetlarida xalqaro talabalar uchun yangi kvotalar ajratildi"},
        {"title": "Biznes, Moliya va Marketing yo'nalishlarida qabul", "desc": "Xalqaro akkreditatsiyalarga ega nufuzli biznes maktablariga erta ariza topshirish davri"},
        {"title": "Magistratura va Bakalavriat uchun yangi qoidalar", "desc": "2026-yildan xalqaro talabalar uchun hujjat topshirishdagi qulayliklar va soddalashtirilgan tartib"},
        {"title": "TÖMER tayyorlov guruhlarida joylar band qilinmoqda", "desc": "Turk tilini o'rganishni istaganlar uchun yangi semestr til kurslariga ro'yxatdan o'tish"},
        {"title": "Yotoqxona (KYK) arizalari topshirish vaqtlari", "desc": "Kelgusi o'quv yilida arzon va shinam yotoqxonaga ega bo'lish uchun erta harakat qilish zarurligi"},
        {"title": "Huquq va Xalqaro munosabatlar fakultetlari qabuli", "desc": "Diplomatiya va huquqshunoslik bo'yicha Turkiyaning yetakchi OTMlarida joylar ajratildi"},
        {"title": "Ingliz tilidagi dasturlar uchun kvotalar taqvimi", "desc": "IELTS yoki TOEFL orqali to'liq ingliz tilida o'qitiladigan fakultetlarga qabul boshlanishi"},
        {"title": "Erta qabulning eng katta ustunliklari", "desc": "Hujjatlarni erta topshirgan talabalar universitet tanlashda eng birinchi o'rinlarga ega bo'lishi"},
        {"title": "Psixologiya va Ijtimoiy fanlar qabuli", "desc": "Ommabop gumanitar fakultetlarda xalqaro talabalar uchun yangi o'quv yili kvotalari"},
        {"title": "Turkiya xususiy OTMlarida erta stipendiya dasturlari", "desc": "Universitetlar tomonidan beriladigan ichki rag'batlantiruvchi stipendiyalar haqida rasmiy e'lon"},
        {"title": "Hujjatlarni apostil qilish bo'yicha eslatma", "desc": "Abituriyentlar uchun qabul mavsumida kerak bo'ladigan asosiy hujjatlar ro'yxati va tayyorgarlik"},
        {"title": "Davlat universitetlarining qo'shimcha kvotalari (Ek Kontenjan)", "desc": "Asosiy qabuldan so'ng bo'sh qolgan o'rinlar bo'yicha yangiliklar va imkoniyatlar"},
        {"title": "Muhandislik fakultetlarida sanoat amaliyoti dasturlari", "desc": "Talabalar uchun yangi ochilgan amaliy texnologik stajirovka dasturlari"},
        {"title": "Dizayn, Animatsiya va Rivojlanayotgan sohalar", "desc": "Zamonaviy raqamli kasblar bo'yicha Turkiya oliygohlarida yangi ta'lim yo'nalishlari"},
        {"title": "Xalqaro talabalar uchun sug'urta va qonuniy tartib yangiliklari", "desc": "Yangi o'quv yilida talabalar vizasi va yashash guvohnomasi bo'yicha rasmiy yangilanishlar"},
        {"title": "Sohilbo'yi shaharlaridagi universitetlar qabuli", "desc": "Izmir, Antalya va Samsun oliygohlarida xalqaro talabalar uchun hujjat qabul qilish muddatlari"},
        {"title": "Qabul muddatining yakuniy bosqichi eslatmasi", "desc": "Joylar to'lib borayotganligi va kech qolmaslik uchun so'nggi muddatlar"}
    ]
}

class TopicEngine:
    def __init__(self, ai_brain=None):
        self.ai = ai_brain
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if TOPICS_FILE.exists():
            try:
                with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if all(k in data for k in ("educational", "promotional", "news")):
                        # Verify baseline count
                        for cat, items in BASELINE_TOPICS.items():
                            existing_titles = {p.get("title") for p in data[cat]["pool"]}
                            for b_it in items:
                                if b_it["title"] not in existing_titles:
                                    data[cat]["pool"].append(b_it)
                        return data
            except Exception:
                pass

        # Initialize from baseline
        initial_data = {
            "educational": {"pool": list(BASELINE_TOPICS["educational"]), "used_indices": []},
            "promotional": {"pool": list(BASELINE_TOPICS["promotional"]), "used_indices": []},
            "news": {"pool": list(BASELINE_TOPICS["news"]), "used_indices": []}
        }
        self._save_data(initial_data)
        return initial_data

    def _save_data(self, data: Dict[str, Any]):
        try:
            with open(TOPICS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TopicEngine] Error saving dynamic topics: {e}")

    def get_next_topic(self, category: str) -> Tuple[str, str]:
        """
        Picks the next unrepeated topic for the specified category.
        If available topics are running low (fewer than 5 unused),
        autonomously triggers AI replenishment to synthesize 10 new topics.
        """
        if category not in self.data:
            category = "educational"

        cat_data = self.data[category]
        pool = cat_data.get("pool", [])
        used = set(cat_data.get("used_indices", []))

        unused_indices = [i for i in range(len(pool)) if i not in used]

        # If running low, autonomously replenish new topics via AI
        if len(unused_indices) <= 5:
            self.replenish_topics(category)
            pool = self.data[category]["pool"]
            used = set(self.data[category]["used_indices"])
            unused_indices = [i for i in range(len(pool)) if i not in used]

        if not unused_indices:
            cat_data["used_indices"] = []
            unused_indices = list(range(len(pool)))

        chosen_idx = random.choice(unused_indices)
        cat_data["used_indices"].append(chosen_idx)
        self._save_data(self.data)

        item = pool[chosen_idx]
        return item.get("title", "Turkiya ta'limi"), item.get("desc", "")

    def replenish_topics(self, category: str):
        """
        Autonomously synthesizes 10 brand-new, unique topics using AI Brain.
        Focuses on real student cities, historical facts, specific university details, and tips.
        """
        if not self.ai:
            from engine.ai_brain import AIBrain
            self.ai = AIBrain()

        cat_names = {
            "educational": "Bilgilendirici (talabalik hayoti, shaharlar, tarix, universitetlar, maslahatlar)",
            "promotional": "Reklam & Ishonch (0$ oldindan to'lov, 99% qabul, yuridik kafolat, to'liq xizmat)",
            "news": "Yangilik & Kvota (2026-yilgi qabul, muddatlar, stipendiyalar, chegirmalar)"
        }

        prompt = (
            f"Sen Arkadaş Consulting uchun yangi mavzular yaratuvchi ekspertisan.\n"
            f"Bizga '{cat_names.get(category, category)}' toifasi uchun MUTLAQO YANGI va takrorlanmagan 10 ta mavzu kerak.\n\n"
            "Talablar:\n"
            "- Mavzular real Turkiya shaharlari (Istanbul, Ankara, Izmir, Eskişehir, Bursa, Sakarya, Antalya, Konya),\n"
            "  aniq universitetlar (Koç, Sabancı, ITU, Sakarya, Marmara, Hacettepe, Gazi, Anadolu),\n"
            "  tarixiy va madaniy mushtaraklik (O'zbekiston-Turkiya qardoshligi, mehmondo'stlik, halol taomlar),\n"
            "  talabalik sirlari (arzon yemekhane, kutubxonalar, transport chegirmalari) haqida bo'lsin.\n"
            "- QAT'IY QOIDA: Hech qanday soxta maosh ($2000-$5000) yoki 'viza rad etilishi 0%' kabi yolg'on va'dalar YOZILMASIN!\n\n"
            "Javobni FAQAT quyidagi JSON formatida qaytar (boshqa hech qanday so'z yoki matnsiz):\n"
            "[\n"
            '  {"title": "Mavzu nomi", "desc": "Mavzuning qisqa mazmuni va ochib beriladigan tomoni"},\n'
            "  ...\n"
            "]"
        )

        try:
            res = self.ai.think_and_generate(prompt)
            raw_text = res.get("text", "").strip()
            if "```" in raw_text:
                parts = raw_text.split("```")
                raw_text = parts[1] if len(parts) > 1 else raw_text
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            new_items = json.loads(raw_text)
            if isinstance(new_items, list) and len(new_items) > 0:
                valid_count = 0
                for it in new_items:
                    if isinstance(it, dict) and "title" in it and "desc" in it:
                        existing_titles = {p.get("title") for p in self.data[category]["pool"]}
                        if it["title"] not in existing_titles:
                            self.data[category]["pool"].append(it)
                            valid_count += 1
                if valid_count > 0:
                    self._save_data(self.data)
                    print(f"[TopicEngine] Autonomously replenished {valid_count} new topics for '{category}'!")
                    return
        except Exception as e:
            print(f"[TopicEngine] Autonomous replenishment error: {e}")

        # Static replenishment fallback
        extra_fallbacks = [
            {"title": "Turkiya texnoparklarida talabalik startaplari", "desc": "Universitetlar qoshidagi texnoparklarda talabalar o'z loyihalarini grantlar yordamida yo'lga qo'yishi"},
            {"title": "Talabalar uchun arzon sayohat: Doğu Ekspresi", "desc": "Turkiya bo'ylab poezdda arzon va go'zal sayohat qilish, talabalik xotiralari"},
            {"title": "Akademik taqvim: Bahorgi va kuzgi semestrlar", "desc": "Turkiya universitetlarida darslar boshlanish vaqtlari va ta'til muddatlari"},
            {"title": "Talabalik vizasi uchun talab qilinadigan hujjatlar", "desc": "Elchixonaga topshiriladigan hujjatlarni to'g'ri va tartibli tayyorlash qoidalari"},
            {"title": "Kutubxonalardagi elektron ma'lumotlar bazalari", "desc": "Jahon ilmiy jurnallari va Scopus maqolalaridan bepul foydalanish imkoniyati"}
        ]
        for it in extra_fallbacks:
            self.data[category]["pool"].append(it)
        self._save_data(self.data)

if __name__ == "__main__":
    te = TopicEngine()
    print("Baseline topic counts:")
    for k, v in te.data.items():
        print(f"  {k}: {len(v['pool'])} topics")
    t1, d1 = te.get_next_topic("educational")
    print(f"\nNext educational topic:\nTitle: {t1}\nDesc: {d1}")
