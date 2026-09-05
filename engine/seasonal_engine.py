#!/usr/bin/env python3
"""
Arkadaş Consulting - Turkish Academic Seasonal Engine
Detects the real-time calendar month and season to give AI posts
authentic, timely relevance to what students and parents are facing right now:

- Dekabr - Fevral (Qish): Türkiye Bursları (bepul hukumat grantlari), bahorgi semestr qabullari
- Mart - Aprel (Bahor): Erta ro'yxatdan o'tish (Erken Kayıt), xususiy OTMlarda 50%-75% grant davri
- May - Iyun (Yoz ostonasi): Attestat olish, imtihonsiz qabulning eng qizg'in bosqichi
- Iyul - Avgust (Katta yoz): Davlat universitetlari kvotalari, joylar to'lishi, shoshilinch qabul
- Sentyabr - Oktyabr (Kuz): O'qishning boshlanishi, kutib olish, yotoqxona va ikamet rasmiylashtirish
- Noyabr: Kelgusi yil rejalari, TÖMER va xalqaro til sertifikatlari
"""

from datetime import datetime
from typing import Dict, Any

MONTH_SEASONS = {
    1: {
        "season_uz": "Qish",
        "title": "Türkiye Bursları va Bahorgi Semestr",
        "focus": "Turkiya hukumati to'liq bepul grant dasturi (Türkiye Bursları) arizalari va bahorgi qabullar",
        "urgency_tip": "Bepul grant arizalari muddatini o'tkazib yubormang! Bahorgi semestr uchun so'nggi imkoniyat."
    },
    2: {
        "season_uz": "Qish",
        "title": "Türkiye Bursları yakuni va Bahorgi Qabul",
        "focus": "Grant dasturining so'nggi kunlari va yangi o'quv yili uchun dastlabki maslahatlar",
        "urgency_tip": "Grantga ulgurmaganlar uchun imtihonsiz xususiy va davlat OTMlariga rejalashtirish davri."
    },
    3: {
        "season_uz": "Bahor",
        "title": "Erta Ro'yxatdan O'tish (Erken Kayıt)",
        "focus": "Universitetlarning erta qabul dasturlari va 50%-75% gacha grant chegirmalari",
        "urgency_tip": "Hujjatlarni erta topshirgan talabalar eng yuqori kontrakt chegirmalariga ega bo'lishadi."
    },
    4: {
        "season_uz": "Bahor",
        "title": "TR-YÖS va Attestat bilan Erta Qabul",
        "focus": "Imtihonli va imtihonsiz qabul kvotalarini band qilish, yo'nalishlarni to'g'ri tanlash",
        "urgency_tip": "Tibbiyot, Stomatologiya va IT yo'nalishlarida xalqaro kvotalar tez to'lmoqda."
    },
    5: {
        "season_uz": "Yoz ostonasi",
        "title": "Maktab bitiruvchilari va Attestat davri",
        "focus": "Maktab, litsey va kollej bitiruvchilari uchun attestat bilan imtihonsiz qabul",
        "urgency_tip": "Attestat baholaringiz bilan imtihonsiz to'g'ridan-to'g'ri qabul xatini oling."
    },
    6: {
        "season_uz": "Yoz",
        "title": "Davlat Universitetlarining Asosiy Qabuli",
        "focus": "Arzon kontraktli nufuzli davlat universitetlariga arizalar topshirish boshlanishi",
        "urgency_tip": "Davlat universitetlari kvotalari cheklangan, 1-bosqich arizalariga kech qolmaslik zarur."
    },
    7: {
        "season_uz": "Katta Yoz",
        "title": "Eng qizg'in qabul davri va Natijalar",
        "focus": "Rasmiy qabul xatlari (Acceptance letter) chiqishi, elchixona suhbatiga tayyorgarlik",
        "urgency_tip": "Joylar soni keskin kamaymoqda, hujjatlarni tezkor topshirish talab etiladi."
    },
    8: {
        "season_uz": "Katta Yoz",
        "title": "So'nggi Kvotalar va Viza Hujjatlari",
        "focus": "Konsullikdan talabalik vizasi olish, biletlar va yotoqxonalarni band qilish",
        "urgency_tip": "Sentabrdagi darslarga kechikmaslik uchun viza arizasini zudlik bilan topshiring."
    },
    9: {
        "season_uz": "Kuz",
        "title": "Universitetlarning Ochilishi va Kutib Olish",
        "focus": "Turkiyaga yetib borish, aeroportda kutib olish, yotoqxona va ikamet rasmiylashtirish",
        "urgency_tip": "Turkiyadagi ilk kunlaringizda Arkadaş jamoasi siz bilan birga bo'ladi."
    },
    10: {
        "season_uz": "Kuz",
        "title": "O'quv Yilining Boshlanishi va Qo'shimcha Qabul (Ek Kontenjan)",
        "focus": "Universitet darslari boshlanishi, bo'sh qolgan o'rinlarga qo'shimcha qabullar",
        "urgency_tip": "Ulgurmaganlar uchun bahorgi semestr yoki qo'shimcha kvotalarga imkoniyat mavjud."
    },
    11: {
        "season_uz": "Kuz",
        "title": "TÖMER va Kelgusi Yil Rejalari",
        "focus": "Turk tili tayyorlov guruhlari, til o'rganish va kelasi yilgi qabulga puxta tayyorgarlik",
        "urgency_tip": "Tilni erta boshlagan talaba sentyabrda 1-kursni bemalol boshlaydi."
    },
    12: {
        "season_uz": "Qish ostonasi",
        "title": "Yangi Yil Qabul Kampaniyalari Starti",
        "focus": "Kelasi yilgi qabul kvotalari e'loni, bepul konsultatsiyalar va hujjatlarni ekvivalentlash",
        "urgency_tip": "Yangi o'quv yili uchun eng birinchi bo'lib joyingizni band qiling."
    }
}

def get_current_season_info() -> Dict[str, Any]:
    """
    Returns current season info based on current month.
    """
    now = datetime.now()
    month = now.month
    info = MONTH_SEASONS.get(month, MONTH_SEASONS[9])
    info["current_month_num"] = month
    info["current_year"] = now.year
    return info

def get_seasonal_prompt_context() -> str:
    """
    Returns a prompt instruction string injecting current academic context.
    """
    info = get_current_season_info()
    return (
        f"AQLLI FASL KONTEKSTI ({info['season_uz']} fasli, {info['current_year']}-yil):\n"
        f"- Joriy davr mavzusi: {info['title']}\n"
        f"- Diqqat markazi: {info['focus']}\n"
        f"- Dolzarblik eslatmasi: {info['urgency_tip']}\n"
        "Postda mana shu faslga mos haqiqiy dolzarblik hissi aks etsin."
    )
