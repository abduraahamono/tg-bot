# -*- coding: utf-8 -*-
import requests, time, random

TOKEN = '8452859083:AAHOAYEwbYYVq9Yg1z1GonHqKnaJ4qi6-Cg'
KANAL = '@arkadasuz'

metinler = [
    "Salom dostlar! 👋\n\nTurkiyada oqish - orzuyingiz emasmikan?\nBizga yozing: @arkadasuzz",
    "Turkiyada oqish osonmi? 🤔\nHa, togri joyni tanlasang - oson!\n👉 @arkadasuzz",
    "🎯 2025 qabul boshlandi!\n🔥 Chegirmalar 70% gacha\n👉 @arkadasuzz"
]

print('Bot ishga tushdi!')

while True:
    matn = random.choice(metinler)
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', json={'chat_id': KANAL, 'text': matn})
    print(f'Yuborildi: {matn[:40]}...')
    time.sleep(21600)
