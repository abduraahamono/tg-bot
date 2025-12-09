# -*- coding: utf-8 -*-
import requests, time, random, signal

TOKEN = '8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg'
KANAL = '@arkadasuz'

metinler = [
    """🎓 Turkiyada o'qish orzuyingmi? Endi bu orzu rostdan ham amalga oshadi!

"Arkadaş" bilan sizga mos universitet tanlashdan tortib, ro'yxatdan o'tish, vizani olish, sim-karta, bank hisobi va yashash uchun hujjatlarni rasmiylashtiirishgacha — hammasida yoningizdamiz.

✅ Universitetga ariza
✅ Elchixonadan denklik olish
✅ Hujjatlar rasmiy tarjimasi 📄
✅ Universitetga qabul xati 🎓
✅ Airoportda kutib olish 🤝✈️
✅ 1 kunlik Istanbul sayohati 🏛️🚶
✅ Sog'liqni saqlash sug'urtasi 🏥
✅ Yashash uchun ruxsatnoma (kimlik) 🆔
✅ SIM karta + bank hisobi raqami 📱💳
✅ 1 yillik TÖMER 🗣️🇹🇷
✅ 4 yillik to'liq grant kelishuvi 💡📚

99% muvaffaqiyat darajasi
Pulni qaytarish kafolati

🌍 Qabul davom etmoqda — joylar cheklangan!
📩 Hoziroq bizga yozing va Turkiyada yangi hayotingizni boshlang!

👉 @arkadasuzz""",

    """📢 ARKADAŞ Consulting — rasmiy ta'lim konsalting agentligi

Biz Turkiyadagi barcha davlat va xususiy universitetlarning joylashtiirish jarayonlari, kontrakt miqdorlari, o'tish ballari va barcha muhim ma'lumotlarini WhatsApp va Telegram platformasida e'lon qilmoqdamiz.

📌 Xizmatlarimiz (kanal tavsifida ham ko'rsatilgan):

✅ Turkiyada o'qishni istaganlar uchun universitetga joylashtiirish va maslahat xizmatlari

✅ Turkiyadagi davlat va xususiy universitetlariga kirish bo'yicha maslahatlar

✅ Universitetlarga 100%, 75%, 50% va 25% grant asosida joylashtirish

✅ Yashash guvohnomasi (ID) bo'yicha maslahat xizmatlari

✅ Universitetga yaqin, hamyonbop narxlardagi talabalar yotoqxonalarini tanlash

📌 Bular kabi yana ko'plab xizmatlarimiz mavjud.

Bizning maqsadimiz — ushbu muhim mavsumda sizga yordam berishdir. Agar sizga yordam bera olsak, bu biz uchun katta baxtdir!

🔹 Aloqa raqamimiz 👇
@arkadasuzz""",

    """Salom do'stlar! 👋

Turkiyada o'qish — orzuyingiz emasmikan?
Hamma gap nimadan boshlashda. Imtihon bormi? Grant topiladimi? Viza-uy-telefon-tilchi-til?!

Xavotir olma 😊
ARKADAŞ bilan aynan shuning uchun bor.

Biz seni imtihonsiz qabul qiladigan universitetlarga yo'naltiramiz.
💯 gacha Grant
🏠 Hujjat, ID, yotoqxona — bor!
�� Sog'liq sug'urtasi va yashash ruxsatnomasi — hammasi!

Har yili minglab o'zbek yoshlari Turkiyada o'qishni tanlaydi. Negaki?

🎓 Sifatli ta'lim
🌍 Xalqaro tajriba  
💼 Karyera imkoniyatlari
🏙️ Zamonaviy hayot

Siz ham ulardan biri bo'lishni xohlaysizmi?

Boshlash juda oson:
1️⃣ Bizga yozing
2️⃣ Universitet tanlang
3️⃣ Hujjat topshiring
4️⃣ Turkiyada o'qing!

📩 @arkadasuzz""",

    """⚠️ DIQQAT! Son cheklangan!

Turkiyaning eng yaxshi universitetlariga qabul faqat bir necha hafta qoldi!

🕐 Vaqt o'tmoqda
📉 Joylar tugamoqda  
🎯 Grant imkoniyatlari kamaymoqda

Hozir harakat qilmasangiz — kech bo'lishi mumkin!

📊 STATISTIKA:
- Har yil 50,000+ xorijiy talaba Turkiyaga keladi
- Grant olish imkoniyati 75% gacha
- Diplomlar 150+ davlatda tan olinadi
- O'rtacha ish topish davri: 3 oy

🎓 ENG MASHHUR YO'NALISHLAR:
- Tibbiyot va farmatsevtika
- Muhandislik va texnologiya
- Biznes va iqtisod
- Arxitektura va dizayn
- IT va dasturlash

✅ Bugun ariza topshiring
✅ Ertaga javob oling
✅ Keyingi oy Turkiyada bo'ling!

📞 Zudlik bilan: @arkadasuzz
⏰ 24/7 yordam xizmati""",

    """🌟 Muvaffaqiyat yo'lingiz Turkiyadan boshlanadi!

Har yili minglab o'zbek yoshlari Turkiyada o'qishni tanlaydi.
Negaki?

🎓 SIFATLI TA'LIM:
- Evropa standartidagi dasturlar
- Zamonaviy laboratoriyalar
- Xalqaro o'qituvchilar
- Ingliz tilida dasturlar

🌍 XALQARO TAJRIBA:
- Erasmus+ almashinuv dasturi
- Xalqaro konferensiyalar
- Global kompaniyalarda amaliyot
- Ko'p madaniyatli muhit

💼 KARYERA IMKONIYATLARI:
- Turkiyada ish topish oson
- Xalqaro kompaniyalar
- Yuqori ish haqi (2000-5000$)
- Doimiy yashash imkoniyati

🏙️ ZAMONAVIY HAYOT:
- Istanbul, Ankara, Izmir
- Rivojlangan infratuzilma
- Xavfsiz muhit
- Qulay narxlar

💰 MOLIYAVIY IMKONIYATLAR:
- 100% gacha grant
- Stipendiya dasturlari
- Part-time ish (20 soat/hafta)
- Hamyonbop turar joy

Siz ham ulardan biri bo'lishni xohlaysizmi?

📩 Biz bilan bog'laning: @arkadasuzz""",
]

def signal_handler(sig, frame):
    print('Signal qabul qilindi, bot davom etadi...', flush=True)
    
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print('Bot ishga tushdi! Uzun matinlar bilan', flush=True)

while True:
    try:
        matn = random.choice(metinler)
        r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', json={'chat_id': KANAL, 'text': matn}, timeout=30)
        print(f'Yuborildi: {matn[:60]}...', flush=True)
    except Exception as e:
        print(f'Xato: {e}', flush=True)
        time.sleep(5)
        continue
    
    time.sleep(21600)
