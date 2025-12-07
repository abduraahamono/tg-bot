# -*- coding: utf-8 -*-
import requests, time, random, signal, sys

TOKEN = '8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg'
KANAL = '@arkadasuz'

metinler = [
    "Salom dostlar! 👋\n\nTurkiyada oqish - orzuyingiz emasmikan?\nBizga yozing: @arkadasuzz",
    "Turkiyada oqish osonmi? 🤔\nHa, togri joyni tanlasang - oson!\n👉 @arkadasuzz",
    "🎯 2025 qabul boshlandi!\n🔥 Chegirmalar 70% gacha\n👉 @arkadasuzz"
]

# Railway uchun signal handler
def signal_handler(sig, frame):
    print('Signal qabul qilindi, lekin bot davom etadi...', flush=True)
    
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print('Bot ishga tushdi!', flush=True)

# Sonsuz loop - hech qachon to'xtamaydi
while True:
    try:
        matn = random.choice(metinler)
        r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', json={'chat_id': KANAL, 'text': matn}, timeout=30)
        
        if r.status_code == 200:
            print(f'Yuborildi: {matn[:40]}...', flush=True)
        else:
            print(f'Telegram xato: {r.status_code}', flush=True)
            
    except Exception as e:
        print(f'Xato yuz berdi: {e}', flush=True)
        print('5 soniyadan keyin qayta uriniladi...', flush=True)
        time.sleep(5)
        continue
    
    # 6 soat kutish
    print('6 soat kutilmoqda...', flush=True)
    time.sleep(21600)
