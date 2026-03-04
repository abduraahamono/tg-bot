import time
import sys
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import tweepy
from keep_alive import keep_alive

keep_alive()

# --- TWITTER ŞİFRELERİ ---
API_KEY = "BURAYA_YAZ"
API_SECRET = "BURAYA_YAZ"
ACCESS_TOKEN = "BURAYA_YAZ"
ACCESS_SECRET = "BURAYA_YAZ"

try:
    twitter = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    print("✅ Twitter Bağlantısı Başarılı!", flush=True)
except Exception as e: 
    print(f"❌ Twitter Bağlantı Hatası: {e}", flush=True)

TELEGRAM_BOT_TOKEN = "8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg"
TELEGRAM_KANAL_ADI = "@dostxabar"
KAYNAK_URL = "https://t.me/s/bpthaber"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELEGRAM_KANAL_ADI, "text": mesaj, "parse_mode": "Markdown"})
        print(f"📱 Telegram Yanıtı: {r.status_code} -> {r.text}", flush=True)
    except Exception as e: 
        print(f"❌ Telegram Çökme Hatası: {e}", flush=True)

def tweet_at(mesaj):
    try:
        temiz_mesaj = mesaj.replace("**", "").replace("_", "")
        if len(temiz_mesaj) > 270: temiz_mesaj = temiz_mesaj[:267] + "..."
        yanit = twitter.create_tweet(text=temiz_mesaj)
        print(f"🐦 Twitter Yanıtı: Başarılı", flush=True)
    except Exception as e: 
        print(f"❌ Twitter Gönderme Hatası: {e}", flush=True)

def cevir(metin):
    try:
        if len(metin) < 5: return metin
        return GoogleTranslator(source='tr', target='uz').translate(metin)
    except: return metin

print("🚀 BPT Haber Botu (HATA TESPİT MODU) Başladı...", flush=True)
son_haber = ""
ilk_calisma = True

while True:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(KAYNAK_URL, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        mesajlar = soup.find_all('div', class_='tgme_widget_message_text')
        
        if not mesajlar:
            print("⚠️ BPT sayfasından mesaj çekilemedi! (Telegram engeli olabilir)", flush=True)
        else:
            if ilk_calisma:
                print("🛠️ Test: Son 1 haber çekiliyor...", flush=True)
                metin = mesajlar[-1].get_text(separator="\n")
                ozbekce = cevir(metin)
                tg_msg = f"🚨 **SON DAKİKA**\n\n{ozbekce}\n\n👉 Kanalimiz: @dostxabar"
                tw_msg = f"🚨 {ozbekce}\n\n#Xabar #BPT"
                
                print("⏳ Mesajlar gönderiliyor...", flush=True)
                telegrama_gonder(tg_msg)
                tweet_at(tw_msg)
                
                son_haber = metin
                ilk_calisma = False
            else:
                yeni_haber = mesajlar[-1].get_text(separator="\n")
                if yeni_haber != son_haber:
                    print("🔔 Yeni haber bulundu, gönderiliyor!", flush=True)
                    ozbekce = cevir(yeni_haber)
                    telegrama_gonder(f"🚨 **SON DAKİKA**\n\n{ozbekce}\n\n👉 Kanalimiz: @dostxabar")
                    tweet_at(f"🚨 {ozbekce}\n\n#Xabar #BPT")
                    son_haber = yeni_haber
                
    except Exception as e:
        print(f"❌ Genel Döngü Hatası: {e}", flush=True)
        
    print("⏳ 3 Dakika beklemede...", flush=True)
    time.sleep(180)
