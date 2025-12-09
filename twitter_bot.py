# -*- coding: utf-8 -*-
import tweepy
import requests
import time
import random
import signal

# TWITTER API KEYS
API_KEY = "****LdUxh0"  # TAM HALINI BURAYA YAPISTIR
API_SECRET = "BURAYA_TAM_API_SECRET"  # Reveal edip buraya yapistir
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKin5wEAAAAA1OIBENrtc5fjIjkN3pHeBQS8QNs%3DOTm9FKWu5O53N1YJQ7GGBoTE62ltAA5eXUgIJbRCxohpxNdelu"
ACCESS_TOKEN = "1902506551245729792-ynKv6rM7eUFnePI1TDkmuqO3ymuQmb"
ACCESS_SECRET = "EwdVnjJUxKkzetHR4rH1lCnmEpebIs1Z9YD2FFehk40Az"

# TELEGRAM BOT
TELEGRAM_TOKEN = '8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg'
TELEGRAM_KANAL = '@arkadasuz'

# METINLER (280 karakter max Twitter icin)
metinler_twitter = [
    "🎓 Turkiyada o'qish orzuyingizmi?\n\n✅ 100% gacha grant\n✅ Visa yordami\n✅ Imtihonsiz qabul\n\nBatafsil: t.me/arkadasuz",
    
    "��🇷 2025 qabul boshlandi!\n\n🔥 Chegirmalar 70% gacha\n🏆 TOP universitetlar\n✈️ Bepul airport transfer\n\nAloqa: t.me/arkadasuz",
    
    "💡 Orzuyingizdagi kasbni Turkiyada organing!\n\n⚕️ Tibbiyot\n👨‍💻 IT\n🏗️ Arxitektura\n\nMaslahat: t.me/arkadasuz",
    
    "📢 ARKADAS Consulting\n\nTurkiyada universitet:\n✅ Grant 100% gacha\n✅ ID va turar joy\n✅ Sogliq sugurtasi\n\nt.me/arkadasuz",
    
    "⚠️ DIQQAT!\n\nQabul muddati tugayapti!\n\n🕐 Vaqt otmoqda\n📉 Joylar kamaymoqda\n\nZudlik bilan: t.me/arkadasuz",
]

metinler_telegram = [
    """🎓 Turkiyada o'qish orzuyingmi? Endi bu orzu rostdan ham amalga oshadi!

"Arkadaş" bilan sizga mos universitet tanlashdan tortib, ro'yxatdan o'tish, vizani olish, sim-karta, bank hisobi va yashash uchun hujjatlarni rasmiylashtiirishgacha — hammasida yoningizdamiz.

✅ Universitetga ariza
✅ Elchixonadan denklik olish
✅ Hujjatlar rasmiy tarjimasi 📄
✅ Universitetga qabul xati 🎓
✅ Airoportda kutib olish 🤝✈️

99% muvaffaqiyat darajasi
Pulni qaytarish kafolati

🌍 Qabul davom etmoqda!
📩 @arkadasuzz""",

    """📢 ARKADAŞ Consulting — rasmiy ta'lim konsalting agentligi

Biz Turkiyadagi barcha davlat va xususiy universitetlarning joylashtiirish jarayonlari haqida ma'lumot beramiz.

✅ 100%, 75%, 50% va 25% grant
✅ Yashash guvohnomasi (ID)
✅ Hamyonbop talabalar turar joyi

📞 @arkadasuzz""",
]

def signal_handler(sig, frame):
    print('Signal qabul qilindi, bot davom etadi...', flush=True)
    
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Twitter client
try:
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    twitter_aktif = True
    print("Twitter client yuklandi!", flush=True)
except Exception as e:
    print(f"Twitter yuklanmadi: {e}", flush=True)
    twitter_aktif = False

print('Bot ishga tushdi! Twitter + Telegram', flush=True)

while True:
    try:
        # TWITTER
        if twitter_aktif:
            try:
                tweet_text = random.choice(metinler_twitter)
                response = client.create_tweet(text=tweet_text)
                print(f'Twitter: Yuborildi - {tweet_text[:40]}...', flush=True)
            except Exception as e:
                print(f'Twitter xato: {e}', flush=True)
        
        # TELEGRAM
        try:
            telegram_text = random.choice(metinler_telegram)
            r = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
                json={'chat_id': TELEGRAM_KANAL, 'text': telegram_text},
                timeout=30
            )
            print(f'Telegram: Yuborildi - {telegram_text[:40]}...', flush=True)
        except Exception as e:
            print(f'Telegram xato: {e}', flush=True)
            
    except Exception as e:
        print(f'Umumiy xato: {e}', flush=True)
        time.sleep(5)
        continue
    
    print('6 soat kutilmoqda...', flush=True)
    time.sleep(21600)  # 6 soat
