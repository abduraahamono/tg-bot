import time
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
    twitter = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    print("✅ Twitter Bağlantısı Başarılı!", flush=True)
except Exception as e: 
    print(f"❌ Twitter Bağlantı Hatası: {e}", flush=True)

TELEGRAM_BOT_TOKEN = "8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg"
TELEGRAM_KANAL_ADI = "@dostxabar"
KAYNAK_URL = "https://t.me/s/bpthaber"

# 🛠️ ÖZEL SÖZLÜK (Hatalı Google çevirilerini buraya ekleyip düzelttirebilirsin)
DUZELTMELER = {
    "So'nggi daqiqa": "Tezkor Xabar",
    "ovoz chiqarib o‘ylayapman": "o'zim uchun xulosa qilyapman",
    "mantiqan to'g'ri": "aqlga muvofiq"
}

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        # disable_web_page_preview: Linkin altındaki çirkin site önizlemesini kapatır
        r = requests.post(url, data={"chat_id": TELEGRAM_KANAL_ADI, "text": mesaj, "parse_mode": "Markdown", "disable_web_page_preview": True})
        print(f"📱 Telegram Yanıtı: {r.status_code}", flush=True)
    except Exception as e: print(f"❌ TG Hata: {e}", flush=True)

def tweet_at(mesaj):
    try:
        temiz = mesaj.replace("**", "").replace("_", "").replace("[📢 Rasmiy Kanalimiz - Dost Xabar](https://t.me/dostxabar)", "")
        if len(temiz) > 270: temiz = temiz[:267] + "..."
        twitter.create_tweet(text=temiz)
        print("🐦 Twitter Başarılı", flush=True)
    except Exception as e: print(f"❌ Twitter Hata: {e}", flush=True)

def cevir(metin):
    try:
        if len(metin) < 5: return metin
        ozbekce = GoogleTranslator(source='tr', target='uz').translate(metin)
        
        # Filtre/Sözlük Düzeltmesi
        for tr_hata, uz_dogru in DUZELTMELER.items():
            ozbekce = ozbekce.replace(tr_hata, uz_dogru)
        return ozbekce
    except: return metin

print("🚀 BPT Haber Botu Aktif...", flush=True)
son_haber = ""
ilk_calisma = True

while True:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(KAYNAK_URL, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        mesajlar = soup.find_all('div', class_='tgme_widget_message_text')
        
        if mesajlar:
            orijinal_metin = mesajlar[-1].get_text(separator="\n")
            
            if ilk_calisma or orijinal_metin != son_haber:
                print("🔔 Yeni haber işleniyor...", flush=True)
                
                # Çeviri işlemi
                ozbekce_metin = cevir(orijinal_metin)
                
                # "Son Dakika" Kontrolü ve Başlık Atama
                if "SON DAKİKA" in orijinal_metin.upper():
                    ozbekce_metin = ozbekce_metin.replace("SON DAKİKA:", "").replace("SON DAKİKA.", "").strip()
                    tg_msg = f"🚨 **TEZKOR XABAR**\n\n{ozbekce_metin}\n\n[📢 Rasmiy Kanalimiz - Dost Xabar](https://t.me/dostxabar)"
                else:
                    tg_msg = f"{ozbekce_metin}\n\n[📢 Rasmiy Kanalimiz - Dost Xabar](https://t.me/dostxabar)"

                telegrama_gonder(tg_msg)
                tweet_at(tg_msg)
                
                son_haber = orijinal_metin
                ilk_calisma = False
                
    except Exception as e: print(f"❌ Döngü Hatası: {e}", flush=True)
    time.sleep(180)
