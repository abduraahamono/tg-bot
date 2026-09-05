import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import tweepy
from keep_alive import keep_alive

keep_alive()

# --- AYARLAR (Şifrelerini Gir) ---
GEMINI_API_KEY = "AIzaSyAZGrHDF1Jb1TYyi8p_ufTwIqqQVDuvNSM"
TW_API_KEY = "..."
TW_API_SECRET = "..."
TW_ACCESS_TOKEN = "..."
TW_ACCESS_SECRET = "..."

# Yapay Zeka Kurulumu
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Twitter Kurulumu
try:
    twitter = tweepy.Client(consumer_key=TW_API_KEY, consumer_secret=TW_API_SECRET, access_token=TW_ACCESS_TOKEN, access_token_secret=TW_ACCESS_SECRET)
    print("✅ Twitter Bağlantısı Tamam.")
except: pass

TELEGRAM_BOT_TOKEN = "8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg"
TELEGRAM_KANAL_ADI = "@dostxabar"
KAYNAK_URL = "https://t.me/s/bpthaber"

def ai_islem(metin):
    """Hem filtreleme hem de kaliteli çeviri yapar"""
    prompt = f"""
    Aşağıdaki haberi analiz et:
    1. Bu haber Türkiye'nin yerel bir magazin haberi mi yoksa sadece Türkiye'yi ilgilendiren küçük bir olay mı? (Evet/Hayır)
    2. Eğer haber küresel veya önemliyse, bunu doğal ve akıcı bir Özbekçe'ye çevir. (Kelime kelime değil, anlamlı çevir).

    Metin: {metin}

    Cevabı şu formatta ver:
    Filtre: [Evet/Hayır]
    Ceviri: [Özbekçe Metin]
    """
    try:
        response = model.generate_content(prompt)
        res_text = response.text
        filtre = "Evet" in res_text.split("Ceviri:")[0]
        cevirisi = res_text.split("Ceviri:")[1].strip() if "Ceviri:" in res_text else ""
        return filtre, cevirisi
    except:
        return False, ""

def telegrama_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_KANAL_ADI, "text": mesaj, "parse_mode": "Markdown", "disable_web_page_preview": True})

def tweet_at(mesaj):
    try:
        clean = mesaj.replace("**", "").split("[📢")[0].strip()
        twitter.create_tweet(text=clean[:275])
    except: pass

print("🚀 Akıllı Bot Nöbette...")
son_haber = ""

while True:
    try:
        r = requests.get(KAYNAK_URL, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        mesajlar = soup.find_all('div', class_='tgme_widget_message_text')
        
        if mesajlar:
            ham_metin = mesajlar[-1].get_text(separator="\n")
            
            if ham_metin != son_haber:
                print("🧠 AI Analiz ediyor...")
                yerel_mi, ozbekce = ai_islem(ham_metin)
                
                if not yerel_mi and ozbekce:
                    # Başlık Belirleme
                    baslik = "🚨 **TEZKOR XABAR**" if "SON DAKİKA" in ham_metin.upper() else "📢 **XABAR**"
                    
                    final_msg = f"{baslik}\n\n{ozbekce}\n\n[📢 Rasmiy Kanalimiz - Dost Xabar](https://t.me/dostxabar)"
                    
                    telegrama_gonder(final_msg)
                    tweet_at(final_msg)
                    print("✅ Paylaşıldı.")
                else:
                    print("⏩ Haber yerel/gereksiz bulunduğu için atlandı.")
                
                son_haber = ham_metin
    except Exception as e: print(f"Hata: {e}")
    time.sleep(180)
