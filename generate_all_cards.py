#!/usr/bin/env python3
"""
generate_all_cards.py
Generates 14 high-definition branded visual cards for the weekly Telegram plan.
Saves images to output/cards/ and updates scheduled_telegram_posts.json with photo_path.
"""

import os
import json
from pathlib import Path
from engine.visual_card_generator import create_branded_card

BASE_DIR = Path(__file__).parent
POSTS_FILE = BASE_DIR / "brain_data" / "scheduled_telegram_posts.json"
OUTPUT_DIR = BASE_DIR / "output" / "cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 14 Custom-crafted bullet sets tailored for each post
card_specs = [
    # 1. Day 1 Lunch
    {
        "id": "tg_20260905_lun",
        "bg": "istanbul_sunset.jpg",
        "category": "💡 TIL VA QABUL HAQIQATI",
        "title": "TÖMER Turk Tili Kursi:\nTil Bilmasdan O'qish Mumkinmi?",
        "bullets": [
            ("Shartli Qabul (Şartlı Kabul)", "Universitetga kirishda turk tilini oldindan bilish shart emas."),
            ("1 Yillik Rasmiy TÖMER Kursi", "Universitet huzuridagi markazda A1 dan C1 gacha til o'rganiladi."),
            ("Tez va Oson Moslashuv", "Turk va o'zbek tillari yaqinligi tufayli talabalar tez so'zlashadi."),
            ("1-Kursga To'g'ridan-to'g'ri Start", "C1 sertifikatini olgach, asosiy mutaxassislik darslari boshlanadi.")
        ]
    },
    # 2. Day 1 Evening
    {
        "id": "tg_20260905_eve",
        "bg": "campus_students.jpg",
        "category": "🛡️ AMALIY HAMROHLIK",
        "title": "Aeroportdan Yotoqxonagacha:\nTurkiyada Ilk Qadamlar",
        "bullets": [
            ("Aeroportda Shaxsan Kutib Olish", "Talabani kutib olib, tayyorlangan yotoqxonaga xavfsiz yetkazamiz."),
            ("Turk SIM-Kartasi", "Ota-ona bilan bog'lanish uchun qulay tarifli mahalliy raqam ochamiz."),
            ("Talabalik Bank Hisobi", "Xalqaro to'lovlar va stipendiya uchun Ziraat Bank kartasi rasmiylashtiriladi."),
            ("İkamet (Yashash Guvohnomasi)", "Qonuniy yashash ruxsatnomasi arizasi to'liq topshiriladi.")
        ]
    },
    # 3. Day 2 Lunch
    {
        "id": "tg_20260906_lun",
        "bg": "galata_tower.jpg",
        "category": "📊 REAL XARAJATLAR SMETASI",
        "title": "Turkiyada Talaba Oylik Xarajati:\nReal Hisob-Kitob Qancha?",
        "bullets": [
            ("Davlat (KYK) Yotoqxonasi", "Oyiga 40-70$ (issiq nonushta va kechki ovqat bepul taqdim etiladi)."),
            ("Shahar Transporti (İstanbulkart)", "Talaba kartasi bilan 80% arzon yurish (oyiga taxminan 8-12$)."),
            ("Universitet Oshxonasi", "4 xil issiq taomdan iborat to'yimli tushlik 1-1.5$ atrofida."),
            ("Umumiy Oylik Byudjet", "O'rtacha 200-300$ bilan talaba Turkiyada xotirjam yashay oladi.")
        ]
    },
    # 4. Day 2 Evening
    {
        "id": "tg_20260906_eve",
        "bg": "istanbul_mosque.jpg",
        "category": "⚖️ HUQUQIY KAFOLAT",
        "title": "Turkiya Diplomi O'zbekistonda\nTan Olinadimi? (Denklik)",
        "bullets": [
            ("YÖK Akkreditatsiyasi Shart", "Oliygoh Turkiya Oliy Ta'lim Kengashi tomonidan tan olingan bo'lishi lozim."),
            ("Kunduzgi (Yuzma-Yuz) Ta'lim", "Bilimni baholash agentligi faqat kunduzgi ta'lim shaklini tan oladi."),
            ("Apostil va Rasmiy Tasdiq", "Diplom va baholar ilovasi Turkiya idoralari tomonidan apostil qilinadi."),
            ("100% Qonuniy Dasturlar", "Arkadaş Consulting faqat nostrifikatsiyadan to'liq o'tuvchi oliygohlarga yo'naltiradi.")
        ]
    },
    # 5. Day 3 Lunch
    {
        "id": "tg_20260907_lun",
        "bg": "campus_students.jpg",
        "category": "🏛️ QABUL STRATEGIYASI",
        "title": "Davlatmi Yoki Xususiy Oliyгоh?\nQaysi Biri Sizga Mos?",
        "bullets": [
            ("Davlat: Hamyonbop Kontrakt", "Yillik 300 - 1,200$ kontrakt, qabul TR-YÖS yoki attestat kvotasi orqali."),
            ("Xususiy: Attestat Bilan Qabul", "Imtihonsiz, maktab attestati baholari asosida to'g'ridan-to'g'ri qabul."),
            ("Arkadaş Maxsus Chegirmalari", "Xususiy universitetlarda 50% gacha stipendiya va grant imtiyozlari."),
            ("Zamonaviy Texnoparklar", "Ingliz tilidagi dasturlar va xalqaro amaliyot imkoniyatlari.")
        ]
    },
    # 6. Day 3 Evening
    {
        "id": "tg_20260907_eve",
        "bg": "istanbul_sunset.jpg",
        "category": "🤝 SHAFFAF SHARTNOMA",
        "title": "Nega Yuridik Shartnoma Muhim?\nFiribgarlardan Himoyalaning",
        "bullets": [
            ("Rasmiy Davlat Litsenziyasi", "Faoliyatimiz qonuniy me'yorlar asosida to'liq ro'yxatdan o'tgan."),
            ("Ikki Tomonlama Shartnoma", "Har bir mijoz bilan huquqiy shartnoma tuzilib, majburiyatlar ochiq belgilanadi."),
            ("Hujjatlarni Xatosiz Topshirish", "Arizalar xalqaro talablarga muvofiq professional tayyorlanadi."),
            ("To'liq Jarayon Nazorati", "Viza va qabuldan to Turkiyadagi darslargacha mutaxassislar nazoratida bo'lasiz.")
        ]
    },
    # 7. Day 4 Lunch
    {
        "id": "tg_20260908_lun",
        "bg": "istanbul_bosphorus.jpg",
        "category": "🎯 MUTAXASSISLIK TAHLILI",
        "title": "Turkiyada Eng Talabgir Kasblar:\nDiplom Bilan Qanday Ish Topiladi?",
        "bullets": [
            ("Dasturiy Ta'minot va IT", "Universitet texnoparklarida xalqaro loyihalarda amaliyot o'tash imkoni."),
            ("Mexatronika va Muhandislik", "Turkiya sanoat va mashinasozlikda Yevropaning yetakchi ishlab chiqaruvchisi."),
            ("Xalqaro Logistika va Savdo", "Yevropa va Osiyo o'rtasidagi ulkan transport xabi mutaxassislari."),
            ("Amaliy Ko'nikmalar", "Nazariya bilan birga real korxonalarda majburiy amaliyot tizimi.")
        ]
    },
    # 8. Day 4 Evening
    {
        "id": "tg_20260908_eve",
        "bg": "campus_students.jpg",
        "category": "🌍 YEVROPA IMKONIYATI",
        "title": "Turkiyada O'qib, Yevropada Grant:\nErasmus+ Dasturi Qanday Ishlaydi?",
        "bullets": [
            ("Yevropada 1 Semestr Bepul", "2-kursda Germaniya, Italiya, Polsha kabi davlatlarda bepul ta'lim olish."),
            ("Oylik 400 - 600€ Stipendiya", "Yevropa Ittifoqi yashash va yo'l xarajatlari uchun bepul mablag' beradi."),
            ("To'liq Tan Olinadigan Kreditlar", "Yevropada o'qilgan fanlar Turkiya diplomingizga to'g'ridan-to'g'ri hisoblanadi."),
            ("Xalqaro Tajriba va Ingliz Tili", "Butun dunyodan kelgan talabalar bilan do'stlashish va dunyoqarash kengayishi.")
        ]
    },
    # 9. Day 5 Lunch
    {
        "id": "tg_20260909_lun",
        "bg": "galata_tower.jpg",
        "category": "🏠 TURAR-JOY QO'LLANMASI",
        "title": "Turkiyada Qayerda Yashash Qulay?\nYotoqxonalar Haqida Xolis Tahlil",
        "bullets": [
            ("Davlat (KYK) Yotoqxonalari", "Oyiga 30-50$, 24/7 xavfsizlik, nonushta va kechki issiq ovqat bepul."),
            ("Xususiy Talaba Yotoqxonalari", "Oyiga 150-250$, qulay xonalar, sportzal, kirxona va Wi-Fi mavjud."),
            ("Do'stlar Bilan Uy Ijarasi", "2-3 kishi 2 xonali kvartira olsa, kishi boshiga 100-150$ tushadi."),
            ("Xavfsizlik Birinchi O'rinda", "Barcha talaba turar-joylarida qat'iy xavfsizlik va nazorat o'rnatilgan.")
        ]
    },
    # 10. Day 5 Evening
    {
        "id": "tg_20260909_eve",
        "bg": "istanbul_mosque.jpg",
        "category": "📋 BIRINCHI 30 KUN",
        "title": "Turkiyaga Borgach Ilk 30 Kunda\nBajariladigan 4 Asosiy Ish",
        "bullets": [
            ("Universitetda Yakuniy Ro'yxat (Kayıt)", "Asl hujjatlar topshirilib, talabalik guvohnomasi (Öğrenci Belgesi) olinadi."),
            ("İkamet Yashash Guvohnomasi", "Göç İdaresi portalida qonuniy talabalik yashash arizasi to'ldiriladi."),
            ("GSS Davlat Tibbiy Sug'urtasi", "Davlat talaba sug'urtasi faollashtirilib, bepul shifoxona huquqi ochiladi."),
            ("Talaba Transport Kartasi", "Universitet ma'lumotnomasi bilan chegirmali shahar kartasi rasmiylashtiriladi.")
        ]
    },
    # 11. Day 6 Lunch
    {
        "id": "tg_20260910_lun",
        "bg": "campus_students.jpg",
        "category": "🌟 TALABA TAJRIBASI",
        "title": "'Boshida Qo'rqqan Edim, Hozir\nGuruh Sardoriman' — Talaba Hikoyasi",
        "bullets": [
            ("Nol Til Bilan Qabul", "Samarqandlik Javohir turk tilini bilmasdan universitetga qabul qilindi."),
            ("TÖMER da 1-Oydan O'zgarish", "O'qituvchilarning samimiy munosabati sababli tezda gapirib ketdi."),
            ("Ota-Onaning Xotirjamligi", "Aeroportda kutib olib, yotoqxonaga joylashtirilgach barcha xavotirlar ketdi."),
            ("1-Kursda A'lochi Natija", "Hozirda guruh sardori va eng faol xalqaro talabalardan biri.")
        ]
    },
    # 12. Day 6 Evening
    {
        "id": "tg_20260910_eve",
        "bg": "istanbul_sunset.jpg",
        "category": "🏥 TIBBIY HIMOYА",
        "title": "Turkiyada Talaba Salomatligi:\nGSS Davlat Sug'urtasi Qanday Ishlaydi?",
        "bullets": [
            ("Davlat Tibbiy Sug'urtasi (GSS)", "Har bir qonuniy xalqaro talaba ushbu davlat sug'urtasiga a'zo bo'la oladi."),
            ("Shifoxonalar Bepul", "Barcha davlat shifoxonalarida bepul tekshiruv, tahlil va davolanish huquqi."),
            ("Dorilarga 80-90% Chegirma", "Shifokor yozgan rasmiy retsept bo'yicha dorilar arzonlashtirib beriladi."),
            ("24/7 Tez Yordam (112)", "Shoshilinch tibbiy yordam barcha uchun to'liq bepul ishlaydi.")
        ]
    },
    # 13. Day 7 Lunch
    {
        "id": "tg_20260911_lun",
        "bg": "galata_tower.jpg",
        "category": "💳 TO'LOVLAR TARTIBI",
        "title": "Kontrakt Qanday To'lanadi?\n1 Yillik Birdan To'lanadimi?",
        "bullets": [
            ("Semestrma-Semestr To'lov", "Turkiyada kontraktlar 1 yillik emas, 2 ga bo'lib (har semestrda) to'lanadi."),
            ("To'g'ridan-to'g'ri Rasmiy IBAN", "Mablag' universitetning rasmiy davlat bank hisobiga talaba nomidan o'tadi."),
            ("Bo'lib To'lash Imkoniyati", "Xususiy universitetlarda 4-8 oylik qulay bo'lib to'lash jadvallari mavjud."),
            ("Shaffoflik va Xavfsizlik", "Hech qanday noqonuniy vositachiga qo'lma-qo'l pul berilmaydi.")
        ]
    },
    # 14. Day 7 Evening
    {
        "id": "tg_20260911_eve",
        "bg": "istanbul_mosque.jpg",
        "category": "❓ HAFTALIK SAVOL-JAVOB",
        "title": "Abituriyentlar Eng Ko'p Beradigan\n4 Muhim Savolga Aniq Javob",
        "bullets": [
            ("Attestat Baholari Yetarlimi?", "O'rtacha 4 va 5 baholi attestat bilan nufuzli oliygohlarga kirish mumkin."),
            ("Yosh Cheklovi Bormi?", "Bakalavr yoki magistratura uchun hech qanday yosh chegarasi yo'q."),
            ("Darslar Qaysi Tilda?", "100% turk tili yoki 100% ingliz tilidagi ta'lim dasturlari mavjud."),
            ("Hujjat Topshirish Vaqti", "Joylar va arzon kvotalar tez to'lishi sababli hozirdan boshlash zarur.")
        ]
    }
]

print("--- GENERATING 14 BRANDED CARDS ---")
card_paths = {}
for spec in card_specs:
    fname = f"card_{spec['id']}.png"
    p = create_branded_card(
        category=spec["category"],
        title=spec["title"],
        bullets=spec["bullets"],
        output_filename=fname,
        bg_choice=spec.get("bg")
    )
    card_paths[spec["id"]] = f"output/cards/{fname}"
    print(f"[OK] Generated {fname}")

# Update scheduled_telegram_posts.json with photo_path
if POSTS_FILE.exists():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updated = 0
    for post in data.get("posts", []):
        pid = post.get("id")
        if pid in card_paths:
            post["photo_path"] = card_paths[pid]
            updated += 1
    
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] {updated} posts updated with photo_path in {POSTS_FILE}")
