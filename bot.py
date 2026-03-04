import time
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import tweepy
from keep_alive import keep_alive

# --- SUNUCUYU UYANIK TUT ---
keep_alive()

# --- TWITTER (X) ŞİFRELERİN ---
API_KEY = "BURAYA_YAZ"
API_SECRET = "BURAYA_YAZ"
ACCESS_TOKEN = "BURAYA_YAZ"
ACCESS_SECRET = "BURAYA_YAZ"

try:
    twitter = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    print("✅ Twitter Bağlantısı Başarılı!")
except: pass

# --- TELEGRAM KANAL AYARLARIN ---
TELEGRAM_BOT_TOKEN = "8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg"
TELEGRAM_KANAL_ADI = "@dosthabar"

# --- KAYNAK KANAL ---
KAYNAK_URL = "https://t.me/s/bpthaber"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_KANAL_ADI, "text": mesaj, "parse_mode": "Markdown"})
    except: pass

def tweet_at(mesaj):
    try:
        temiz_mesaj = mesaj.replace("**", "").replace("_", "")
        if len(temiz_mesaj) > 270:
            temiz_mesaj = temiz_mesaj[:267] + "..."
        twitter.create_tweet(text=temiz_mesaj)
    except: pass

def cevir(metin):
    try:
        if len(metin) < 5: return metin
        return GoogleTranslator(source='tr', target='uz').translate(metin)
    except: return metin

# --- BOT DÖNGÜSÜ ---
print("🚀 BPT Haber Okuyucu Bot Başladı...")
son_haber = ""

while True:
    try:
        # BPT'nin web sayfasını gizlice oku
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(KAYNAK_URL, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Son mesajı bul
        mesajlar = soup.find_all('div', class_='tgme_widget_message_text')
        if mesajlar:
            yeni_haber = mesajlar[-1].get_text(separator="\n")
            
            # Eğer haber yeniyse işlem yap
            if yeni_haber != son_haber:
                ozbekce_haber = cevir(yeni_haber)
                
                # Mesaj Şablonları
                tg_mesaj = f"🚨 **SON DAKİKA**\n\n{ozbekce_haber}\n\n👉 Kanalimiz: @dosthabar"
                tw_mesaj = f"🚨 {ozbekce_haber}\n\n#Xabar #BPT"
                
                # Gönder
                telegrama_gonder(tg_mesaj)
                tweet_at(tw_mesaj)
                print("✅ Yeni haber paylaşıldı!")
                
                son_haber = yeni_haber
                
    except Exception as e:
        print(f"Xato: {e}")
        
    print("⏳ 3 Dakika bekleniyor...")
    time.sleep(180) # 3 dakikada bir kontrol eder
