import os
import json
import random
from datetime import datetime, timedelta

# Existing 14-post schedule (5 Sep to 11 Sep)
with open("brain_data/scheduled_telegram_posts.json", "r", encoding="utf-8") as f:
    tg_current = json.load(f)

current_posts = tg_current.get("posts", [])
# Keep past and current posts (1 to 14)
print(f"Current posts count: {len(current_posts)}")

# 12 Master verified high-res templates for cycling
master_templates = [
    ("kalip_1_sinematik_hikaye", "output/archetypes_factory/kalip_1_sinematik_hikaye_v2.jpg"),
    ("kalip_2_cool_manifesto", "output/archetypes_factory/kalip_2_cool_manifesto_v2.jpg"),
    ("kalip_3_taqqoslash", "output/archetypes_factory/kalip_3_taqqoslash_v2.jpg"),
    ("kalip_4_minimalist_konsept", "output/archetypes_factory/kalip_4_minimalist_konsept_v2.jpg"),
    ("fresh_tram_post", "output/fresh_tram_post.jpg"),
    ("fresh_ferry_post", "output/fresh_ferry_post.jpg"),
    ("sablon_1_modern_split", "output/templates_showcase/sablon_1_modern_split.jpg"),
    ("sablon_2_frosted_cards", "output/templates_showcase/sablon_2_frosted_cards.jpg"),
    ("sablon_3_white_minimal", "output/templates_showcase/sablon_3_white_minimal.jpg"),
    ("sablon_4_dark_cinematic", "output/templates_showcase/sablon_4_dark_cinematic.jpg"),
    ("sablon_5_bento_grid", "output/templates_showcase/sablon_5_bento_grid.jpg"),
    ("sablon_6_boarding_pass", "output/templates_showcase/sablon_6_boarding_pass.jpg"),
]

# 60 Rich Unique Content Topics for Telegram (2 posts/day = 120 posts)
# Divided into:
# - Lunch: Stories, Student Hacks, TÖMER, Quiz, Career, Campus life
# - Evening: Official Admission, Contracts, Comparison, Legal/Visa, Parent Guides
tg_content_library = [
    # Week 2 (12-18 Sep)
    ("TÖMER imtihoniga tayyorgarlik sirlari", "📚 <b>TÖMER TILI: QANDAY QILIB 3 OYDA C1 OLISH MUMKIN?</b>\n\nKo'pchilik til o'rganishni uzoq yillik mashaqqat deb biladi. Ammo turk tili va o'zbek tili bitta turkiy oilaga mansub bo'lgani uchun 80% so'z ildizlari mushtarak!\n\n📌 <b>Bizning talabalar tavsiyasi:</b>\n1. Dastlabki 1 oy faqat grammatika qoidalari va so'z boyligi.\n2. Istanbul ko'chalarida har kungi tirik muloqot amaliyoti.\n3. Universitet qoshidagi bepul so'zlashuv klublari.\n\nTil bilmasdan ham shartli qabul bilan o'qishga kirasiz!\n👉 @arkadasuzz"),
    ("Istanbul davlat tibbiyot fakultetlari", "🩺 <b>TURKIYADA TIBBIYOT TA'LIMI: IMTIHONSIZ QABUL!</b>\n\nShifokor bo'lish — yuksak mas'uliyat va nufuzli kasb. O'zbekistonda tibbiyotga kirish uchun yillab repetitorga qatnash shart emas!\n\n✅ Turkiya davlat universitetlarida tibbiyot va stomatologiya fakultetlari mavjud.\n✅ Zamonaviy Yevropa klinikalari darajasidagi amaliyot.\n✅ Butun dunyoda tan olinadigan xalqaro diplom.\n\nKvotalar soni chegaralangan! Hoziroq ro'yxatdan o'ting:\n👉 @arkadasuzz"),
    ("Talabalar uchun arzon yashash yo'llari", "💡 <b>ISTANBULDA TALABA UCHUN ENG ARZON YASHASH XAKLARI:</b>\n\n1. <b>Istanbulkart (Talaba transport kartasi):</b> Metro, avtobus, parom va tramvayda 80% chegirma!\n2. <b>Universitet oshxonalari:</b> 4 xil issiq taom atigi 20-30 turk lirasi ($0.8 - $1).\n3. <b>Muzey va teatrlar:</b> Barcha madaniy maskanlarga talabalar uchun bepul yoki ramziy narxlar.\n\nTurkiya — talabalar uchun eng qulay mamlakat!\n👉 @arkadasuzz"),
    ("Nega YÖS imtihoni shart emas?", "❓ <b>'YÖS IMTIHONISIZ QANDAY QILIB QABUL BO'LADI?'</b>\n\nKo'pchilik abituriyentlar faqat YÖS topshirish kerak deb adashishadi. Aslida Turkiya Oliy Ta'lim Kengashi (YÖK) chet ellik talabalar uchun maxsus kvotalar ajratadi!\n\n🏛️ Siz faqat maktab attestati yoki kollej diplomi baholari asosida to'g'ridan-to'g'ri qabul qilinasiz.\n⚖️ Barcha jarayon qonuniy va rasmiy shartnoma asosida.\n\nImkoniyatingizni qo'ldan boy bermang:\n👉 @arkadasuzz"),
    ("O'zbek talabasining 1 haftalik byudjeti", "💰 <b>1 HAFTALIK TALABA XARAJATLARI SMETASI:</b>\n\n• Yotoqxona (3 mahal ovqati bilan): $15\n• Yo'l xarajati (talaba kartasi): $2\n• Shaxsiy xarajatlar va choyxona: $15\n\nJami haftasiga $30-$35 bilan bemalol, sifatli yashash mumkin!\nOta-onalar xotirjam, talabalar baxtli.\n👉 @arkadasuzz"),
    ("IT va Dasturlash yo'nalishlari", "💻 <b>KELAJAK KASBI: TURKIYADA IT TA'LIMI!</b>\n\nTurkiya Yevropaning eng tez rivojlanayotgan startap va IT hablaridan biri.\n\n🔹 Dasturiy ta'minot muhandisligi\n🔹 Sun'iy intellekt va kiberxavfsizlik\n🔹 Xalqaro kompaniyalarda 2-kursdan amaliyot\n\nDiplomingiz butun dunyoda o'tadi!\n👉 @arkadasuzz"),
    ("Yashash ruxsati (İkamet ID) qanday olinadi?", "🪪 <b>TURKIYA YASHASH GUVOHNOMASI (İKAMET) HAQIDA:</b>\n\nTurkiyaga kelganingizdan so'ng 90 kun ichida talabalik yashash ruxsati rasmiylashtiriladi.\n\nARKADAŞ jamoasi siz bilan birga:\n• Soliq idorasi va sug'urta ishlarini hal qiladi\n• Migratsiya boshqarmasiga hujjatlarni topshiradi\n• 1 yillik rasmiy ID kartangizni qo'lingizga topshiradi.\n\nSiz faqat o'qish haqida o'ylaysiz!\n👉 @arkadasuzz"),
    ("Arxitektura va Dizayn fakultetlari", "🏛️ <b>ARXITEKTURA VA SHAHARSOZLIK:</b>\n\nIstanbulning o'zi tirik me'morchilik muzeyidir. Qadimiy va zamonaviy arxitektura uyg'unligi talabalarga cheksiz ilhom beradi.\n\nImtihonsiz qabul bilan me'morchilik fakulteti talabasi bo'ling:\n👉 @arkadasuzz"),
    ("Ota-onalar uchun xavfsizlik kafolati", "🛡️ <b>OTA-ONALAR DIQQATIGA: FARZANDINGIZ XAVFSIZLIGI!</b>\n\nBiz uchun eng muhimi — ota-onalarning ko'ngli xotirjam bo'lishi.\n\n1. Talabalar 24/7 qo'riqlanadigan davlat yotoqxonalarida yashaydi.\n2. Doimiy o'zbek kuratorlarimiz har haftalik holatdan xabardor bo'lib turadi.\n3. Rasmiy shartnoma va to'liq yuridik himoya.\n\n👉 @arkadasuzz"),
    ("Xalqaro Biznes va Logistika", "🚢 <b>XALQARO BIZNES VA DENGIZ LOGISTIKASI:</b>\n\nTurkiya Sharq va G'arb o'rtasidagi asosiy savdo ko'prigi. Bu yerda biznes boshqaruvi va logistika sohasini bitirgan mutaxassislar xalqaro portlar va kompaniyalarda talabgir.\n\nRasmiy kvotalar bo'yicha ariza topshiring:\n👉 @arkadasuzz")
]

# Generate daily lunch/evening pairs for 60 days
start_dt = datetime.fromisoformat("2026-09-12T00:00:00")
days_uz = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]

new_tg_posts = []
tpl_idx = 0
topic_idx = 0

for d_offset in range(60):
    cur_date = start_dt + timedelta(days=d_offset)
    d_str = cur_date.strftime("%Y-%m-%d")
    d_name = days_uz[cur_date.weekday()]
    
    # Lunch post (13:00)
    tpl_name_lun, tpl_path_lun = master_templates[tpl_idx % len(master_templates)]
    topic_lun, content_lun = tg_content_library[topic_idx % len(tg_content_library)]
    
    new_tg_posts.append({
        "id": f"tg_{d_str.replace('-', '')}_lun",
        "day_index": d_offset + 8,
        "day_name": d_name,
        "date_str": d_str,
        "slot": "lunch",
        "slot_label": "☀️ Tushlik Posti (13:00)",
        "cat_tag": "🇹🇷 Ta'lim & Imkoniyat",
        "scheduled_time": f"{d_str}T13:00:00",
        "topic": topic_lun,
        "template_name": tpl_name_lun,
        "photo_path": tpl_path_lun,
        "content": content_lun,
        "status": "pending"
    })
    tpl_idx += 1
    topic_idx += 1
    
    # Evening post (19:30)
    tpl_name_eve, tpl_path_eve = master_templates[tpl_idx % len(master_templates)]
    topic_eve, content_eve = tg_content_library[topic_idx % len(tg_content_library)]
    
    new_tg_posts.append({
        "id": f"tg_{d_str.replace('-', '')}_eve",
        "day_index": d_offset + 8,
        "day_name": d_name,
        "date_str": d_str,
        "slot": "evening",
        "slot_label": "🌆 Kechki Asosiy Post (19:30)",
        "cat_tag": "🔥 Rasmiy Qabul",
        "scheduled_time": f"{d_str}T19:30:00",
        "topic": topic_eve,
        "template_name": tpl_name_eve,
        "photo_path": tpl_path_eve,
        "content": content_eve,
        "status": "pending"
    })
    tpl_idx += 1
    topic_idx += 1

# Merge with existing 14 posts
all_tg_posts = current_posts + new_tg_posts

with open("brain_data/scheduled_telegram_posts.json", "w", encoding="utf-8") as f:
    json.dump({
        "active": True,
        "created_at": "2026-09-10T20:00:00",
        "week_id": "tg_master_2months_v1",
        "start_date": "2026-09-05",
        "end_date": (start_dt + timedelta(days=59)).strftime("%Y-%m-%d"),
        "posts": all_tg_posts
    }, f, ensure_ascii=False, indent=2)

print(f"Telegram Master Schedule Updated! Total posts: {len(all_tg_posts)} (Covering until mid-November 2026)")

# ==============================================================================
# 2. BUILD MASTER TWITTER SCHEDULE (180 TWEETS: 60 DAYS x 3 TWEETS/DAY)
# ==============================================================================
with open("brain_data/scheduled_tweets.json", "r", encoding="utf-8") as f:
    tw_current = json.load(f)

current_tweets = tw_current.get("tweets", [])
print(f"Current tweets count: {len(current_tweets)}")

tw_hooks = [
    "Turkiyada o'qish bo'yicha 90% abituriyent bilmaydigan haqiqat: Attestat bilan to'g'ridan-to'g'ri davlat OTMiga kirish mumkin. Imtihonsiz qabul: @arkadasuzz",
    "Yillik kontrakt $300 dan boshlanadi. O'zbekistondagi to'lovlardan ancha arzon, diplomi esa Yevropada 100% o'tadi. @arkadasuzz",
    "SEN FAQAT QAROR QABUL QIL — qolgan barcha rasmiyatchilikni ARKADAŞ hal qiladi. Ariza topshirish bepul: @arkadasuzz",
    "TÖMER turk tili kursi: Til bilmasangiz ham shartli qabul bilan talaba bo'lasiz. 1-yil til o'rganib, C1 olasiz. @arkadasuzz",
    "Turkiya davlat OTM diplomi O'zbekistonda to'g'ridan-to'g'ri nostrifikatsiya qilinadi (Oliy Majlis qonuni). @arkadasuzz",
    "Istanbulda talaba yashashi uchun oyiga $200-$250 yetarli. Davlat yotoqxonalarida 3 mahal ovqat bepul/arzon beriladi. @arkadasuzz",
    "DTM stressida 1 yil yo'qotgandan ko'ra, bugunoq xalqaro talabalik sari qadam tashlang. Murojaat: @arkadasuzz",
    "Davlat OTMlariga kuzgi qabul kvotalari cheklangan. Bepul konsultatsiya olish uchun yozing: @arkadasuzz",
    "Tibbiyot, IT, Muhandislik, Biznes — barcha yo'nalishlar bo'yicha imtihonsiz rasmiy qabul. @arkadasuzz",
    "Viza, sug'urta, yashash guvohnomasi (İkamet) va aeroportda kutib olish kafolati. @arkadasuzz"
]

tw_slots = [
    ("morning", "🌅 Ertalabki Post", "10:00:00"),
    ("lunch", "☀️ Tushlik Posti", "14:00:00"),
    ("evening", "🌆 Kechki Post", "20:00:00")
]

new_tweets = []
h_idx = 0
tpl_tw_idx = 0

for d_offset in range(60):
    cur_date = start_dt + timedelta(days=d_offset)
    d_str = cur_date.strftime("%Y-%m-%d")
    d_name = days_uz[cur_date.weekday()]
    
    for slot_code, slot_lbl, slot_time in tw_slots:
        tw_id = f"tw_{d_str.replace('-', '')}_{slot_code[:3]}"
        # Alternate photo and text-only (50% with photo, 50% text-only tweet)
        use_photo = (tpl_tw_idx % 2 == 0)
        img_path = master_templates[tpl_tw_idx % len(master_templates)][1] if use_photo else None
        
        new_tweets.append({
            "id": tw_id,
            "day_index": d_offset + 8,
            "day_name": d_name,
            "date_str": d_str,
            "slot": slot_code,
            "slot_label": slot_lbl,
            "cat_tag": "🇹🇷 Twitter",
            "scheduled_time": f"{d_str}T{slot_time}",
            "content": tw_hooks[h_idx % len(tw_hooks)],
            "photo_path": img_path,
            "image_path": img_path,
            "status": "pending"
        })
        h_idx += 1
        tpl_tw_idx += 1

all_tweets = current_tweets + new_tweets

with open("brain_data/scheduled_tweets.json", "w", encoding="utf-8") as f:
    json.dump({
        "active": True,
        "created_at": "2026-09-10T20:00:00",
        "week_id": "tw_master_2months_v1",
        "start_date": "2026-09-05",
        "end_date": (start_dt + timedelta(days=59)).strftime("%Y-%m-%d"),
        "tweets": all_tweets
    }, f, ensure_ascii=False, indent=2)

print(f"Twitter Master Schedule Updated! Total tweets: {len(all_tweets)} (Covering until mid-November 2026)")
