#!/usr/bin/env python3
import json
from pathlib import Path

POSTS_FILE = Path("brain_data/scheduled_telegram_posts.json")

if not POSTS_FILE.exists():
    print("Xato: scheduled_telegram_posts.json topilmadi")
    exit(1)

with open(POSTS_FILE, "r", encoding="utf-8") as f:
    plan = json.load(f)

posts = plan.get("posts", [])
posts_json = json.dumps(posts, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<title>Arkadaş Consulting — 1 Haftalik Telegram Takvimi</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #090d10;
    --surface: #11171d;
    --surface-hover: #182028;
    --border: #222d38;
    --primary: #2aabee;
    --accent: #00d26a;
    --amber: #ffb400;
    --purple: #9d72ff;
    --text-main: #f0f4f8;
    --text-muted: #8b9baa;
    --text-dim: #546575;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text-main);
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding: 28px 36px 80px;
    min-height: 100vh;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid var(--border);
    padding-bottom: 24px;
    margin-bottom: 28px;
    flex-wrap: wrap;
    gap: 20px;
  }}
  .brand-tag {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: var(--primary);
    text-transform: uppercase;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .title {{
    font-size: 26px;
    font-weight: 800;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .stats-bar {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .stat-pill {{
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 12px;
  }}
  .stat-pill b {{ color: var(--text-main); font-family: 'JetBrains Mono', monospace; }}
  
  .calendar-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
  }}
  .day-col {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}
  .day-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
  }}
  .day-name {{
    font-size: 15px;
    font-weight: 700;
    color: #fff;
  }}
  .day-date {{
    font-size: 12px;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
  }}
  
  .slot-card {{
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .slot-card:hover {{
    background: var(--surface-hover);
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(42,171,238,0.12);
  }}
  .slot-meta {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .time-badge {{
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(42,171,238,0.15);
    color: var(--primary);
  }}
  .cat-badge {{
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 500;
  }}
  .card-pill {{
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(0, 210, 106, 0.15);
    color: var(--accent);
    font-weight: 600;
  }}
  .slot-topic {{
    font-size: 13px;
    font-weight: 600;
    line-height: 1.4;
    color: #e2e8f0;
  }}
  .click-hint {{
    font-size: 11px;
    color: var(--text-dim);
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  /* Modal */
  .modal-overlay {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(6px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 20px;
  }}
  .modal-overlay.active {{ display: flex; }}
  .modal {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    width: 100%;
    max-width: 680px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 16px 40px rgba(0,0,0,0.6);
  }}
  .modal-head {{
    padding: 18px 22px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}
  .modal-img-container {{
    text-align: center;
    padding: 16px 20px 0;
  }}
  .modal-img {{
    max-height: 380px;
    max-width: 100%;
    border-radius: 12px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  }}
  .modal-body {{
    padding: 20px;
    overflow-y: auto;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-main);
    white-space: pre-wrap;
    background: var(--bg);
    margin: 14px 20px;
    border-radius: 10px;
    border: 1px solid var(--border);
    font-family: inherit;
  }}
  .modal-body b {{ color: #fff; font-weight: 700; }}
  .modal-foot {{
    padding: 16px 22px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }}
  .btn {{
    padding: 9px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.15s;
  }}
  .btn-primary {{
    background: var(--primary);
    color: #fff;
  }}
  .btn-primary:hover {{ background: #1a9ee0; }}
  .btn-ghost {{
    background: rgba(255,255,255,0.06);
    color: var(--text-muted);
    border: 1px solid var(--border);
  }}
  .btn-ghost:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}
  .close-btn {{
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 22px;
    cursor: pointer;
    line-height: 1;
  }}
  .close-btn:hover {{ color: #fff; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="brand-tag">🏛️ Arkadaş Consulting — Telegram Marketing</div>
    <h1 class="title">🗓️ 1 Haftalik Rejali Postlar Takvimi</h1>
  </div>
  <div class="stats-bar">
    <div class="stat-pill">Davr: <b>{plan.get("start_date")} — {plan.get("end_date")}</b></div>
    <div class="stat-pill">Jami: <b>{len(posts)} ta post</b></div>
    <div class="stat-pill">Dizayn Kartalari: <b style="color: var(--accent);">14/14 Tayyor 🖼️</b></div>
    <div class="stat-pill">Kanal: <b>@arkadasuz</b></div>
    <div class="stat-pill">Holat: <b style="color: var(--accent);">🟢 Faol Reja</b></div>
  </div>
</div>

<div class="calendar-grid" id="grid"></div>

<!-- DETAIL MODAL -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <div class="modal-head">
      <div>
        <div style="font-size: 11px; color: var(--primary); font-weight: 700; margin-bottom: 4px;" id="modalSlot"></div>
        <div style="font-size: 17px; font-weight: 700; color: #fff;" id="modalTitle"></div>
      </div>
      <button class="close-btn" onclick="closeModalDirect()">&times;</button>
    </div>
    
    <div class="modal-img-container" id="modalImgBox" style="display: none;">
      <img id="modalCardImg" class="modal-img" src="" alt="Dizayn Kartasi" />
    </div>

    <div class="modal-body" id="modalContent"></div>

    <div class="modal-foot">
      <span style="font-size: 12px; color: var(--text-dim);" id="modalCharCount"></span>
      <div style="display: flex; gap: 8px;">
        <button class="btn btn-primary" onclick="copyModalContent()">📋 Nusxa Olish</button>
        <button class="btn btn-ghost" onclick="closeModalDirect()">Yopish</button>
      </div>
    </div>
  </div>
</div>

<script>
const postsData = {posts_json};

function renderGrid() {{
  const grid = document.getElementById("grid");
  grid.innerHTML = "";

  const daysMap = {{}};
  postsData.forEach((p, idx) => {{
    p._idx = idx;
    if (!daysMap[p.day_name]) {{
      daysMap[p.day_name] = {{ date: p.date_str, posts: [] }};
    }}
    daysMap[p.day_name].posts.push(p);
  }});

  for (const [dayName, dayObj] of Object.entries(daysMap)) {{
    const col = document.createElement("div");
    col.className = "day-col";
    
    let slotsHtml = "";
    dayObj.posts.forEach(p => {{
      const timeStr = p.scheduled_time.split("T")[1].substring(0, 5);
      const cardBadge = p.photo_path ? '<span class="card-pill">🖼️ Rasm bor</span>' : '';
      slotsHtml += `
        <div class="slot-card" onclick="openModal(${{p._idx}})">
          <div class="slot-meta">
            <span class="time-badge">⏰ ${{timeStr}}</span>
            ${{cardBadge}}
            <span class="cat-badge">${{p.cat_tag || ""}}</span>
          </div>
          <div class="slot-topic">${{p.topic}}</div>
          <div class="click-hint">👉 Karta va matnni ko'rish</div>
        </div>
      `;
    }});

    col.innerHTML = `
      <div class="day-header">
        <span class="day-name">${{dayName}}</span>
        <span class="day-date">${{dayObj.date}}</span>
      </div>
      ${{slotsHtml}}
    `;
    grid.appendChild(col);
  }}
}}

function openModal(idx) {{
  const p = postsData[idx];
  if (!p) return;
  const timeStr = p.scheduled_time.split("T")[1].substring(0, 5);
  document.getElementById("modalSlot").innerText = `${{p.day_name}} — ${{timeStr}} (${{p.cat_tag}})`;
  document.getElementById("modalTitle").innerText = p.topic;
  document.getElementById("modalContent").innerHTML = p.content;
  document.getElementById("modalCharCount").innerText = `Uzunlik: ${{p.content.length}} belgi`;

  const imgBox = document.getElementById("modalImgBox");
  const imgEl = document.getElementById("modalCardImg");
  if (p.photo_path) {{
    const relPath = p.photo_path.replace("output/", "");
    imgEl.src = relPath;
    imgBox.style.display = "block";
  }} else {{
    imgBox.style.display = "none";
  }}

  document.getElementById("modalOverlay").classList.add("active");
}}

function closeModal(e) {{
  if (e.target.id === "modalOverlay") {{
    document.getElementById("modalOverlay").classList.remove("active");
  }}
}}

function closeModalDirect() {{
  document.getElementById("modalOverlay").classList.remove("active");
}}

function copyModalContent() {{
  const text = document.getElementById("modalContent").innerText;
  navigator.clipboard.writeText(text).then(() => {{
    alert("Post matni nusxalandi!");
  }});
}}

renderGrid();
</script>

</body>
</html>
"""

Path("output").mkdir(exist_ok=True)
with open("output/telegram_calendar.html", "w", encoding="utf-8") as f:
    f.write(html)
print("SUCCESS: output/telegram_calendar.html created with visual cards preview!")
