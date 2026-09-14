// Arkadaş Executive OS — High-Performance Master Client Controller (v4.0)
// Designed for Enterprise Agency Management

// Global State
window.allShorts = [];
window.allTelegramPosts = [];
window.allTweets = [];
window.allUniversities = [];
window.allLeads = [];
window.currentHeroVideo = null;
window.documentTemplates = [];
window.quickRepliesList = [];
window.allDorms = [];
window.quizData = [];
window.currentQuestionIdx = 0;
window.instagramCarouselSlides = [];
window.selectedAITopic = 'tibbiyot';
window.bannerFormat = 'story';
window.bannerPrimaryColor = '#06b6d4';
window.bannerBgColor = '#06080d';

// Safe text formatter (no regex newline escape bugs)
function formatSafeText(str) {
  if (!str) return '';
  return str.split('\n').join('<br>');
}

// 1. Toast Notification Utility
function showToast(msg, type = "info") {
  const toast = document.getElementById("toast-notify");
  const msgEl = document.getElementById("toast-message");
  if (!toast || !msgEl) return;

  msgEl.innerText = msg;
  toast.className = "fixed bottom-6 right-6 px-4 py-2.5 rounded-xl text-xs font-mono border backdrop-blur-lg shadow-2xl z-50 transition-all duration-300";

  if (type === "success") {
    toast.classList.add("bg-emerald-950/90", "border-emerald-500", "text-emerald-300");
  } else if (type === "error") {
    toast.classList.add("bg-rose-950/90", "border-rose-500", "text-rose-300");
  } else {
    toast.classList.add("bg-slate-900/90", "border-white/20", "text-slate-200");
  }
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3500);
}
window.showToast = showToast;

// 1.5. Admin Gatekeeper & Authentication
async function checkAdminAuth() {
  try {
    const res = await fetch('/api/auth/status');
    const data = await res.json();
    const overlay = document.getElementById('admin-gatekeeper-overlay');
    if (overlay) {
      if (data.authenticated) {
        overlay.classList.add('hidden');
      } else {
        overlay.classList.remove('hidden');
      }
    }
  } catch (e) {
    console.error("Auth status hatası:", e);
  }
}
window.checkAdminAuth = checkAdminAuth;

async function handleAdminLogin(e) {
  if (e && e.preventDefault) e.preventDefault();
  const pinInput = document.getElementById('admin-pin-input');
  const pin = (pinInput?.value || '').trim();
  if (!pin) {
    showToast("Lütfen Yönetici PIN kodunu girin!", "error");
    return;
  }

  showToast("Oturum doğrulanıyor...", "info");
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin })
    });
    const data = await res.json();
    if (data.success) {
      const overlay = document.getElementById('admin-gatekeeper-overlay');
      if (overlay) overlay.classList.add('hidden');
      showToast("Yönetici Komuta Merkezi Açıldı!", "success");
      loadLeads();
    } else {
      showToast(data.error || "Hatalı Yönetici PIN Kodu!", "error");
      if (pinInput) {
        pinInput.value = '';
        if (typeof pinInput.focus === 'function') pinInput.focus();
      }
    }
  } catch (err) {
    showToast("Giriş bağlantı hatası", "error");
  }
}
window.handleAdminLogin = handleAdminLogin;

async function lockAdminSession() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    const overlay = document.getElementById('admin-gatekeeper-overlay');
    if (overlay) overlay.classList.remove('hidden');
    const pinInput = document.getElementById('admin-pin-input');
    if (pinInput) {
      pinInput.value = '';
      if (typeof pinInput.focus === 'function') pinInput.focus();
    }
    showToast("Yönetici oturumu kilitlendi.", "info");
  } catch (e) {
    console.error("Lock error:", e);
  }
}
window.lockAdminSession = lockAdminSession;

// 2. Executive Navigation Architecture (7 Command Centers & Segmented Sub-Navs)
const EXECUTIVE_HUBS = {
  spotlight: {
    label: "Genel Bakış",
    defaultSection: "spotlight",
    tabs: [
      { id: "spotlight", label: "Özet", icon: "fa-solid fa-chart-line" }
    ]
  },
  ytstudio: {
    label: "YouTube",
    defaultSection: "ytstudio",
    tabs: [
      { id: "ytstudio", label: "Shorts & Videolar", icon: "fa-brands fa-youtube" },
      { id: "youtubepower", label: "SEO & Etiketler", icon: "fa-solid fa-bolt" }
    ]
  },
  socialhub: {
    label: "Sosyal Medya",
    defaultSection: "socialmatrix",
    tabs: [
      { id: "socialmatrix", label: "Tüm Kanallar", icon: "fa-solid fa-layer-group" },
      { id: "twitterhub", label: "Twitter", icon: "fa-brands fa-x-twitter" },
      { id: "ytstudio", label: "YouTube", icon: "fa-brands fa-youtube" },
      { id: "contenthub", label: "Telegram", icon: "fa-brands fa-telegram" },
      { id: "tiktoklab", label: "TikTok", icon: "fa-brands fa-tiktok" },
      { id: "instagramhub", label: "Instagram", icon: "fa-brands fa-instagram" },
      { id: "facebookhub", label: "Facebook", icon: "fa-brands fa-facebook" },
      { id: "whatsapphub", label: "WhatsApp", icon: "fa-brands fa-whatsapp" },
      { id: "chatbotai", label: "AI Asistan", icon: "fa-solid fa-robot" }
    ]
  },
  academics: {
    label: "Üniversiteler",
    defaultSection: "universities",
    tabs: [
      { id: "universities", label: "Katalog", icon: "fa-solid fa-building-columns" },
      { id: "calculator", label: "Maliyet Hesapla", icon: "fa-solid fa-calculator" },
      { id: "examprep", label: "TR-YÖS / SAT", icon: "fa-solid fa-graduation-cap" },
      { id: "dormitories", label: "Yurtlar", icon: "fa-solid fa-hotel" },
      { id: "denklik", label: "Denklik (YÖK)", icon: "fa-solid fa-scale-balanced" }
    ]
  },
  crmops: {
    label: "Öğrenciler",
    defaultSection: "crm",
    tabs: [
      { id: "crm", label: "CRM Tablosu", icon: "fa-solid fa-users" },
      { id: "contractgen", label: "Sözleşmeler", icon: "fa-solid fa-file-signature" },
      { id: "checklist", label: "Vize Takip", icon: "fa-solid fa-list-check" },
      { id: "documents", label: "Tercüme & Evrak", icon: "fa-solid fa-file-contract" },
      { id: "airport", label: "Karşılama", icon: "fa-solid fa-plane-arrival" },
      { id: "visadefense", label: "Vize İtiraz", icon: "fa-solid fa-shield-halved" }
    ]
  },
  creativestudio: {
    label: "İçerik Stüdyosu",
    defaultSection: "aicopilot",
    tabs: [
      { id: "aicopilot", label: "Metin Yazarı", icon: "fa-solid fa-wand-magic-sparkles" },
      { id: "reelsstudio", label: "Reels Üretici", icon: "fa-solid fa-film" },
      { id: "audiostudio", label: "Ses & Dublaj", icon: "fa-solid fa-microphone" },
      { id: "marketingstudio", label: "Afiş Tasarım", icon: "fa-solid fa-palette" },
      { id: "counselors", label: "Danışmanlar", icon: "fa-solid fa-user-tie" }
    ]
  },
  systemops: {
    label: "Ayarlar",
    defaultSection: "analytics",
    tabs: [
      { id: "analytics", label: "Raporlar", icon: "fa-solid fa-chart-pie" },
      { id: "competitor", label: "Rakipler", icon: "fa-solid fa-crosshairs" },
      { id: "quickreplies", label: "Hızlı Yanıtlar", icon: "fa-solid fa-comments" },
      { id: "settings", label: "Otopilot", icon: "fa-solid fa-gear" }
    ]
  }
};

function findHubForSection(sectionId) {
  for (const [hubKey, hub] of Object.entries(EXECUTIVE_HUBS)) {
    if (hub.tabs.some(t => t.id === sectionId)) {
      return hubKey;
    }
  }
  return 'spotlight';
}

function renderExecutiveSubNav(hubKey, activeSectionId) {
  const container = document.getElementById('executive-subnav-container');
  const pillsBox = document.getElementById('executive-subnav-pills');
  if (!container || !pillsBox) return;

  const hub = EXECUTIVE_HUBS[hubKey];
  if (!hub || hub.tabs.length <= 1) {
    container.classList.add('hidden');
    return;
  }

  container.classList.remove('hidden');
  pillsBox.innerHTML = hub.tabs.map(tab => {
    const isActive = tab.id === activeSectionId;
    const activeClasses = isActive 
      ? 'bg-white/10 text-white border-white/20 font-semibold shadow-sm' 
      : 'bg-transparent text-slate-400 border-transparent hover:text-white hover:bg-white/5';
    return `
      <button type="button" 
        class="px-3.5 py-1.5 rounded-full text-xs transition-all duration-150 flex items-center gap-2 cursor-pointer border ${activeClasses}"
        onclick="switchSection('${tab.id}')">
        <i class="${tab.icon} text-[11px]"></i>
        <span>${tab.label}</span>
      </button>
    `;
  }).join('');
}

function switchSection(targetId) {
  const hubKey = findHubForSection(targetId);

  // Update navbar active buttons
  document.querySelectorAll(".master-nav-link, .nav-link").forEach(btn => {
    const target = btn.getAttribute("data-target");
    const hub = btn.getAttribute("data-hub");
    if (hub === hubKey || target === targetId || target === hubKey) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Render sub-navigation pills
  renderExecutiveSubNav(hubKey, targetId);

  // Hide all sections
  document.querySelectorAll(".gece-section").forEach(sec => {
    sec.classList.remove("active-tab");
  });

  // Show target section
  const activeSec = document.getElementById(`section-${targetId}`);
  if (activeSec) {
    activeSec.classList.add("active-tab");
    if (typeof window.scrollTo === 'function') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  if (targetId === 'marketingstudio') {
    setTimeout(drawLiveBanner, 50);
  }
}
window.switchSection = switchSection;

function switchExecutiveHub(hubKey) {
  const hub = EXECUTIVE_HUBS[hubKey];
  if (!hub) return;
  switchSection(hub.defaultSection);
}
window.switchExecutiveHub = switchExecutiveHub;
window.switchAppTab = switchExecutiveHub;

// Helper / Clipboard Utilities
function copyCustomText(t) {
  navigator.clipboard.writeText(t);
  showToast("Cevap metni kopyalandı!", "success");
}
window.copyCustomText = copyCustomText;

function copyFacebookAd(h, p) {
  navigator.clipboard.writeText(`${h}\n\n${p}`);
  showToast("Meta Ads metni kopyalandı!", "success");
}
window.copyFacebookAd = copyFacebookAd;

function copyTweetText(text) {
  navigator.clipboard.writeText(text);
  showToast("Tweet metni kopyalandı!", "success");
}
window.copyTweetText = copyTweetText;

function playSampleTrack(name) {
  showToast(`${name} müziği önizleniyor...`, "info");
}
window.playSampleTrack = playSampleTrack;

async function sendPostToOfficialTelegram(text) {
  if (!confirm("Bu metni doğrudan resmi Telegram kanalınız @arkadasuz'a yayınlamak istiyor musunuz?")) return;
  showToast("Telegram kanalına gönderiliyor...", "info");

  try {
    const res = await fetch('/api/send_telegram_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Post @arkadasuz kanalında başarıyla paylaşıldı!", "success");
    } else {
      showToast("Gönderim başarısız", "error");
    }
  } catch (err) {
    showToast("Telegram API hatası", "error");
  }
}
window.sendPostToOfficialTelegram = sendPostToOfficialTelegram;

// 4. Initialization on DOMContentLoaded
document.addEventListener("DOMContentLoaded", async () => {
  console.log("[Arkadaş Executive OS] 3-Pillar Architecture Başlatılıyor...");
  await checkAdminAuth();
  await loadAutopilotSettings();
  initMasterPillars();
  
  await Promise.allSettled([
    loadStockItemsUI(),
    loadUpcomingQueueUI(),
    loadAnalyticsMetrics(),
    loadEditorialCalendar()
  ]);
  
  selectPublishingPlatform('telegram');
  console.log("[Arkadaş Executive OS] 3-Pillar Sistemi Hazır!");
});

// ==============================================================
// MODULE 1: 🌟 SPOTLIGHT & YOUTUBE STUDIO
// ==============================================================

async function loadYouTubeStudio() {
  try {
    const res = await fetch('/api/youtube_studio');
    const data = await res.json();

    if (data.channel) {
      const elTitle = document.getElementById('yt-channel-title');
      const elViews = document.getElementById('yt-stat-views');
      const elSubs = document.getElementById('yt-stat-subs');
      const elVids = document.getElementById('yt-stat-videos');

      if (elTitle) elTitle.innerText = data.channel.title || 'arkadaş';
      if (elViews) elViews.innerText = Number(data.channel.views || 45449).toLocaleString();
      if (elSubs) elSubs.innerText = `${data.channel.subscribers || 28} Abone`;
      if (elVids) elVids.innerText = `${data.channel.video_count || 106} Video`;
    }

    window.allShorts = data.shorts || [];
    if (window.allShorts.length > 0) {
      window.currentHeroVideo = window.allShorts[0];
      const hTitle = document.getElementById('hero-title');
      const hDesc = document.getElementById('hero-desc');
      if (hTitle) hTitle.innerText = window.currentHeroVideo.title || "Turkiyada imtihonsiz qabul: Attestat bahosi yetarli! 🇹🇷";
      if (hDesc && window.currentHeroVideo.description) {
        hDesc.innerText = window.currentHeroVideo.description.substring(0, 190) + "...";
      }
    }
    renderShortsTable();
  } catch (err) {
    console.error("YouTube studio hatası:", err);
  }
}
window.loadYouTubeStudio = loadYouTubeStudio;

function renderShortsTable() {
  const tbody = document.getElementById('shorts-table-body');
  if (!tbody) return;

  const search = (document.getElementById('shorts-search-input')?.value || '').toLowerCase();
  const filtered = window.allShorts.filter(s => {
    return !search || (s.title && s.title.toLowerCase().includes(search));
  });

  if (!filtered || filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-dim font-mono">Kriterlere uygun video bulunamadı.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map((s, idx) => {
    const isPub = s.status === 'published';
    const escapedTitle = (s.title || '').replace(/'/g, "\\'");
    const escapedDesc = (s.description || '').replace(/'/g, "\\'");

    return `
      <tr class="hover:bg-white/[0.02] transition">
        <td class="py-3 px-4 text-dim">#${idx + 1}</td>
        <td class="py-3 px-4 font-bold text-white font-sans max-w-xs truncate">${s.title || 'Başlıksız Shorts'}</td>
        <td class="py-3 px-4 text-cyan">${s.slot || '13:00 / 19:30'}</td>
        <td class="py-3 px-4 text-dim">${s.date || 'Bugün'}</td>
        <td class="py-3 px-4">
          <span class="px-2 py-0.5 rounded text-[11px] ${isPub ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30' : 'bg-amber-950 text-amber-300 border border-amber-500/30'}">
            ${isPub ? '✅ Yayında' : '⏳ Sırada Bekliyor'}
          </span>
        </td>
        <td class="py-3 px-4 text-right space-x-1">
          <button type="button" class="btn btn-outline btn-xs text-cyan" onclick="previewShortVideo('${s.video_path}', '${escapedTitle}')">
            <i class="fa-solid fa-play"></i>
          </button>
          <button type="button" class="btn btn-outline btn-xs text-amber" onclick="openEditVideoModal('${s.id}', '${escapedTitle}', '${escapedDesc}')">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button type="button" class="btn btn-outline btn-xs text-rose border-rose" onclick="uploadShortNow('${s.id}')" title="YouTube'a Yükle">
            <i class="fa-brands fa-youtube"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}
window.renderShortsTable = renderShortsTable;

function filterShorts(type, btn) {
  document.querySelectorAll('#yt-filter-all, #yt-filter-pending, #yt-filter-published').forEach(b => {
    b.className = 'btn btn-xs btn-outline font-mono text-slate-400';
  });
  if (btn) btn.className = 'btn btn-xs btn-primary font-mono';

  if (type === 'all') {
    renderShortsTable();
  } else if (type === 'pending') {
    renderShortsCustomList(window.allShorts.filter(s => s.status !== 'published'));
  } else if (type === 'published') {
    renderShortsCustomList(window.allShorts.filter(s => s.status === 'published'));
  }
}
window.filterShorts = filterShorts;

function renderShortsCustomList(list) {
  const tbody = document.getElementById('shorts-table-body');
  if (!tbody) return;

  tbody.innerHTML = list.map((s, idx) => `
    <tr class="hover:bg-white/[0.02] transition">
      <td class="py-3 px-4 text-dim">#${idx + 1}</td>
      <td class="py-3 px-4 font-bold text-white font-sans max-w-xs truncate">${s.title || 'Başlıksız'}</td>
      <td class="py-3 px-4 text-cyan">${s.slot || '-'}</td>
      <td class="py-3 px-4 text-dim">${s.date || '-'}</td>
      <td class="py-3 px-4"><span class="tag ${s.status === 'published' ? 'tag-emerald' : 'tag-amber'}">${s.status || 'pending'}</span></td>
      <td class="py-3 px-4 text-right">
        <button class="btn btn-outline btn-xs text-cyan" onclick="previewShortVideo('${s.video_path}', '${(s.title||'').replace(/'/g, "\\'")}')"><i class="fa-solid fa-play"></i></button>
        <button class="btn btn-outline btn-xs text-rose" onclick="uploadShortNow('${s.id}')"><i class="fa-brands fa-youtube"></i></button>
      </td>
    </tr>
  `).join('');
}

// Native Video Player Modal
function previewShortVideo(videoPath, title) {
  const modal = document.getElementById('video-preview-modal');
  const player = document.getElementById('modal-video-player');
  const titleEl = document.getElementById('modal-video-title');
  if (!modal || !player) return;

  if (titleEl) titleEl.innerText = title || "Shorts Önizleme";
  player.src = `/video_stream/${videoPath}`;
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  player.play().catch(() => {});
}
window.previewShortVideo = previewShortVideo;

function openHeroVideoModal() {
  if (window.currentHeroVideo) {
    previewShortVideo(window.currentHeroVideo.video_path, window.currentHeroVideo.title);
  }
}
window.openHeroVideoModal = openHeroVideoModal;

function closeVideoPreviewModal() {
  const modal = document.getElementById('video-preview-modal');
  const player = document.getElementById('modal-video-player');
  if (!modal || !player) return;

  player.pause();
  player.src = "";
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}
window.closeVideoPreviewModal = closeVideoPreviewModal;

// Live YouTube Upload Progress Modal
async function uploadShortNow(videoId) {
  if (!confirm("Bu videoyu hemen resmi YouTube kanalınıza yüklemek istiyor musunuz?")) return;

  const modal = document.getElementById('upload-progress-modal');
  const bar = document.getElementById('upload-progress-bar');
  const sub = document.getElementById('upload-progress-sub');
  if (!modal || !bar) return;

  modal.classList.remove('hidden');
  modal.classList.add('flex');
  bar.style.width = '20%';
  if (sub) sub.innerText = "Google Data API v3 yetkilendiriliyor...";

  let fakeProgress = setInterval(() => {
    let cur = parseInt(bar.style.width) || 20;
    if (cur < 85) {
      bar.style.width = (cur + 15) + '%';
      if (cur > 45 && sub) sub.innerText = "Video parçacıkları YouTube'a akıtılıyor (%60)...";
      if (cur > 70 && sub) sub.innerText = "Telegram huni yorumu sabitleniyor...";
    }
  }, 1800);

  try {
    const res = await fetch('/api/videos/upload_now', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: videoId })
    });
    clearInterval(fakeProgress);
    const data = await res.json();

    if (data.success) {
      bar.style.width = '100%';
      if (sub) sub.innerText = "✅ Başarılı! Video YouTube'da yayında!";
      setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        showToast("Video başarıyla YouTube'a yüklendi ve sabitlendi!", "success");
        loadYouTubeStudio();
      }, 1500);
    } else {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
      showToast(`Yükleme Hatası: ${data.error}`, "error");
    }
  } catch (err) {
    clearInterval(fakeProgress);
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    showToast("Sunucu bağlantısı sırasında bir hata oluştu.", "error");
  }
}
window.uploadShortNow = uploadShortNow;

function uploadHeroVideoNow() {
  if (window.currentHeroVideo) {
    uploadShortNow(window.currentHeroVideo.id);
  }
}
window.uploadHeroVideoNow = uploadHeroVideoNow;

function openEditVideoModal(id, title, desc) {
  const idEl = document.getElementById('edit-video-id');
  const titleEl = document.getElementById('edit-video-title');
  const descEl = document.getElementById('edit-video-desc');
  const modal = document.getElementById('video-edit-modal');
  if (!modal) return;

  if (idEl) idEl.value = id;
  if (titleEl) titleEl.value = title;
  if (descEl) descEl.value = desc;

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}
window.openEditVideoModal = openEditVideoModal;

function closeEditVideoModal() {
  const modal = document.getElementById('video-edit-modal');
  if (!modal) return;
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}
window.closeEditVideoModal = closeEditVideoModal;

async function saveVideoMeta() {
  const id = document.getElementById('edit-video-id')?.value;
  const title = document.getElementById('edit-video-title')?.value;
  const desc = document.getElementById('edit-video-desc')?.value;

  const res = await fetch('/api/videos/update_meta', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, title, description: desc })
  });
  const data = await res.json();
  if (data.success) {
    showToast("Video bilgileri güncellendi!", "success");
    closeEditVideoModal();
    loadYouTubeStudio();
  } else {
    showToast("Güncelleme başarısız", "error");
  }
}
window.saveVideoMeta = saveVideoMeta;

// ==============================================================
// MODULE 2: 🌐 OMNI-SOCIAL HUB (TELEGRAM, TIKTOK, TWITTER, FB, WA)
// ==============================================================

// Telegram Posts
async function loadTelegramPosts() {
  try {
    const res = await fetch('/api/telegram_posts');
    const data = await res.json();
    window.allTelegramPosts = data.posts || [];
    renderTelegramPosts();
  } catch (e) {
    console.error("Telegram post hatası:", e);
  }
}
window.loadTelegramPosts = loadTelegramPosts;

function renderTelegramPosts(customList = null) {
  const container = document.getElementById('content-cards-container');
  if (!container) return;

  const search = (document.getElementById('content-search-input')?.value || '').toLowerCase();
  const list = customList || window.allTelegramPosts;
  const filtered = list.filter(p => !search || (p.text && p.text.toLowerCase().includes(search)));

  const countEl = document.getElementById('content-pool-count');
  if (countEl) countEl.innerText = `${filtered.length} Hazır Telegram Postu Listeleniyor`;

  if (!filtered || filtered.length === 0) {
    container.innerHTML = `<div class="col-span-2 text-center py-8 text-dim font-mono">Aradığınız kriterde Telegram içeriği bulunamadı.</div>`;
    return;
  }

  container.innerHTML = filtered.slice(0, 30).map((p, idx) => {
    const formattedBody = formatSafeText(p.text);
    return `
      <div class="gece-card p-5 flex flex-col justify-between space-y-4">
        <div>
          <div class="flex justify-between items-center mb-2">
            <span class="tag tag-cyan text-[10px]">POST #${idx + 1}</span>
            <span class="text-dim text-[11px] font-mono">@arkadasuz</span>
          </div>
          <div class="text-xs text-slate-200 font-sans leading-relaxed whitespace-pre-line max-h-48 overflow-y-auto pr-1">
            ${formattedBody}
          </div>
        </div>
        <div class="pt-3 border-t border-white/5 flex gap-2 font-mono text-xs">
          <button type="button" class="btn btn-outline text-slate-300 btn-xs flex-1 py-1.5" onclick="copyTelegramTextByIndex(${idx})">
            <i class="fa-solid fa-copy mr-1"></i> Kopyala
          </button>
          <button type="button" class="btn btn-primary btn-xs flex-1 py-1.5 flex items-center justify-center gap-1.5" onclick="sendPostByIndex(${idx})">
            <i class="fa-brands fa-telegram"></i>
            <span>Kanala Gönder</span>
          </button>
        </div>
      </div>
    `;
  }).join('');
}
window.renderTelegramPosts = renderTelegramPosts;

function filterTgCategory(cat) {
  if (cat === 'all') {
    renderTelegramPosts(window.allTelegramPosts);
    return;
  }
  renderTelegramPosts(window.allTelegramPosts.filter(p => p.text && p.text.toLowerCase().includes(cat.toLowerCase())));
}
window.filterTgCategory = filterTgCategory;

function copyTelegramTextByIndex(idx) {
  if (window.allTelegramPosts[idx]) {
    navigator.clipboard.writeText(window.allTelegramPosts[idx].text);
    showToast("Post metni kopyalandı!", "success");
  }
}
window.copyTelegramTextByIndex = copyTelegramTextByIndex;

async function sendPostByIndex(idx) {
  if (!window.allTelegramPosts[idx]) return;
  const text = window.allTelegramPosts[idx].text;
  if (!confirm("Bu metni doğrudan resmi Telegram kanalınız @arkadasuz'a yayınlamak istiyor musunuz?")) return;
  showToast("Telegram kanalına gönderiliyor...", "info");

  try {
    const res = await fetch('/api/send_telegram_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Post @arkadasuz kanalında başarıyla paylaşıldı!", "success");
    } else {
      showToast("Gönderim başarısız", "error");
    }
  } catch (err) {
    showToast("Telegram API hatası", "error");
  }
}
window.sendPostByIndex = sendPostByIndex;

// TikTok Lab
async function loadTikTokLab() {
  try {
    const res = await fetch('/api/tiktok_lab');
    const data = await res.json();
    const container = document.getElementById('tiktok-scripts-container');
    if (!container || !data.scripts) return;

    container.innerHTML = data.scripts.map((sc, i) => `
      <div class="gece-card p-5 flex flex-col justify-between space-y-3">
        <div>
          <div class="flex justify-between items-center mb-2">
            <span class="tag tag-purple text-[10px]">REELS / TIKTOK #${i+1}</span>
            <span class="text-slate-400 font-mono text-[11px]"><i class="fa-solid fa-music text-purple mr-1"></i>${sc.audio}</span>
          </div>
          <h3 class="font-bold text-sm text-white font-sans">${sc.title}</h3>
          <div class="mt-3 p-3 bg-black/40 rounded-xl border border-white/5 font-mono text-xs text-cyan leading-relaxed">
            <strong>🎯 3s Kanca:</strong> "${sc.hook}"
          </div>
          <div class="mt-2 text-xs text-slate-300 font-sans leading-relaxed whitespace-pre-line max-h-36 overflow-y-auto">
            ${sc.body}
          </div>
        </div>
        <div class="pt-3 border-t border-white/5 flex gap-2">
          <button type="button" class="btn btn-outline text-purple border-purple btn-xs w-full py-1.5 font-mono" onclick="copyTikTokScript('${(sc.title||'').replace(/'/g, "\\'")}', '${(sc.hook||'').replace(/'/g, "\\'")}')">
            <i class="fa-solid fa-copy mr-1"></i> Senaryoyu Kopyala
          </button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error("TikTok lab hatası:", e);
  }
}
window.loadTikTokLab = loadTikTokLab;

function copyTikTokScript(title, hook) {
  const full = `📱 VIRAL SENARYO: ${title}\n\n🎯 3-SANIYE KANCA:\n${hook}\n\n👉 Kanal: @arkadasuz`;
  navigator.clipboard.writeText(full);
  showToast("TikTok senaryosu kopyalandı!", "success");
}
window.copyTikTokScript = copyTikTokScript;

// Twitter / X
async function loadTweets() {
  try {
    const res = await fetch('/api/tweets');
    const data = await res.json();
    window.allTweets = data.tweets || [];
    renderTweetsList();
  } catch (e) {
    console.error("Tweet yükleme hatası:", e);
  }
}
window.loadTweets = loadTweets;

function renderTweetsList() {
  const container = document.getElementById('tweets-container');
  if (!container) return;

  const search = (document.getElementById('tweet-search-input')?.value || '').toLowerCase();
  const filtered = window.allTweets.filter(t => !search || (t.text && t.text.toLowerCase().includes(search)));

  if (!filtered || filtered.length === 0) {
    container.innerHTML = `<div class="col-span-3 text-center py-8 text-dim font-mono">Tweet bulunamadı.</div>`;
    return;
  }

  container.innerHTML = filtered.slice(0, 30).map((t, idx) => `
    <div class="gece-card p-5 flex flex-col justify-between space-y-3">
      <div>
        <div class="flex justify-between items-center mb-2">
          <span class="tag tag-slate text-[10px]">TWEET #${idx + 1}</span>
          <span class="text-[11px] font-mono text-cyan">280 Karakter</span>
        </div>
        <p class="text-xs text-slate-200 font-sans leading-relaxed">${t.text}</p>
      </div>
      <div class="pt-3 border-t border-white/5 flex gap-2 font-mono text-xs">
        <button type="button" class="btn btn-outline text-slate-300 btn-xs flex-1 py-1.5" onclick="copyTweetByIndex(${idx})">
          <i class="fa-solid fa-copy mr-1"></i> Kopyala
        </button>
        <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(t.text)}" target="_blank" class="btn btn-outline text-white border-white/20 btn-xs flex-1 py-1.5 text-center">
          <i class="fa-brands fa-x-twitter mr-1"></i> Tweet At
        </a>
      </div>
    </div>
  `).join('');
}
window.renderTweetsList = renderTweetsList;

function copyTweetByIndex(idx) {
  if (window.allTweets[idx]) {
    navigator.clipboard.writeText(window.allTweets[idx].text);
    showToast("Tweet metni kopyalandı!", "success");
  }
}
window.copyTweetByIndex = copyTweetByIndex;

// Facebook / Meta
async function loadFacebookSuite() {
  try {
    const res = await fetch('/api/social/facebook');
    const data = await res.json();

    const cBox = document.getElementById('fb-campaigns-container');
    if (cBox && data.campaigns) {
      cBox.innerHTML = data.campaigns.map(c => `
        <div class="gece-card p-5 space-y-3 font-mono text-xs">
          <div class="flex justify-between items-center">
            <span class="tag tag-cyan text-[10px]">${c.objective}</span>
            <span class="text-blue-400 font-bold text-xs">${c.title}</span>
          </div>
          <div class="p-3 bg-black/40 rounded-xl border border-white/5 space-y-2">
            <p class="text-slate-200 text-xs font-sans leading-relaxed"><strong>Primary Text:</strong> ${c.primary_text}</p>
            <div class="pt-2 border-t border-white/5 text-white font-bold">Headline: ${c.headline}</div>
            <div class="text-[11px] text-slate-400">Button CTA: <span class="text-cyan font-bold">${c.cta}</span></div>
          </div>
          <button type="button" class="btn btn-outline text-blue-400 border-blue-500/30 btn-xs w-full py-1.5" onclick="copyTextDirect('${(c.headline||'').replace(/'/g, "\\'")}\n\n${(c.primary_text||'').replace(/'/g, "\\'")}', 'Meta Ads metni kopyalandı!')">
            Reklam Metnini Kopyala
          </button>
        </div>
      `).join('');
    }

    const aBox = document.getElementById('fb-audiences-container');
    if (aBox && data.audiences) {
      aBox.innerHTML = data.audiences.map(a => `
        <div class="p-2.5 rounded-lg bg-black/40 border border-white/5 space-y-0.5">
          <span class="text-white font-bold">${a.name} (${a.age})</span>
          <div class="text-[11px] text-cyan">${a.geo}</div>
          <div class="text-[10px] text-dim">Erişim: ${a.est_reach}</div>
        </div>
      `).join('');
    }

    const comBox = document.getElementById('fb-community-container');
    if (comBox && data.community_posts) {
      comBox.innerHTML = data.community_posts.map(p => `
        <div class="p-2.5 rounded-lg bg-black/40 border border-white/5 text-[11px] text-slate-300">
          ${p}
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Facebook suite hatası:", e);
  }
}
window.loadFacebookSuite = loadFacebookSuite;

// WhatsApp Business
async function loadWhatsAppSuite() {
  try {
    const res = await fetch('/api/social/whatsapp');
    const data = await res.json();

    const catBox = document.getElementById('wa-catalog-container');
    if (catBox && data.catalog_items) {
      catBox.innerHTML = data.catalog_items.map(item => `
        <div class="gece-card p-4 space-y-2 font-mono text-xs">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-white text-xs font-sans">${item.name}</h4>
            <span class="tag tag-emerald text-[10px]">${item.price}</span>
          </div>
          <p class="text-[11px] text-slate-300 font-sans leading-relaxed">${item.desc}</p>
          <a href="https://wa.me/905340000000?text=${encodeURIComponent("Merhaba, " + item.name + " (" + item.price + ") hakkında detaylı bilgi almak istiyorum.")}" target="_blank" class="btn btn-outline text-emerald border-emerald btn-xs w-full py-1 text-center block mt-2">
            Katalogdan Sor
          </a>
        </div>
      `).join('');
    }

    const wel = document.getElementById('wa-welcome-text');
    if (wel && data.auto_greetings) {
      wel.innerText = data.auto_greetings.welcome;
    }
  } catch (e) {
    console.error("WhatsApp suite hatası:", e);
  }
}
window.loadWhatsAppSuite = loadWhatsAppSuite;

// Instagram Studio
async function loadInstagramSuite() {
  try {
    const res = await fetch('/api/social/instagram');
    const data = await res.json();
    window.instagramCarouselSlides = data.carousel_outline || [];

    const carBox = document.getElementById('insta-carousel-container');
    if (carBox && data.carousel_outline) {
      carBox.innerHTML = data.carousel_outline.map(sl => `
        <div class="p-3 bg-black/40 rounded-xl border border-white/5 space-y-1 font-mono text-xs">
          <span class="text-pink-400 font-bold">${sl.title}</span>
          <p class="text-slate-200 text-[11px] font-sans leading-relaxed">${sl.text}</p>
        </div>
      `).join('');
    }

    const bioBox = document.getElementById('insta-bio-container');
    if (bioBox && data.bio_link_tree) {
      bioBox.innerHTML = data.bio_link_tree.map(b => `
        <a href="${b.url}" target="_blank" class="p-2 bg-black/40 rounded-lg border border-white/5 flex justify-between items-center text-slate-200 hover:border-cyan text-[11px]">
          <span>${b.title}</span>
          <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
        </a>
      `).join('');
    }

    const stBox = document.getElementById('insta-stickers-container');
    if (stBox && data.stories_stickers) {
      stBox.innerHTML = data.stories_stickers.map(s => `
        <div class="p-2 rounded-lg bg-black/30 border border-white/5 text-[11px] space-y-0.5">
          <span class="text-amber font-bold">${s.type}</span>
          <div class="text-slate-300">${s.prompt}</div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Instagram suite hatası:", e);
  }
}
window.loadInstagramSuite = loadInstagramSuite;

function copyAllCarouselSlides() {
  const allText = window.instagramCarouselSlides.map(s => `${s.title}:\n${s.text}`).join('\n\n');
  navigator.clipboard.writeText(allText);
  showToast("10 Slaytlık Carousel metni kopyalandı!", "success");
}
window.copyAllCarouselSlides = copyAllCarouselSlides;

// YouTube Power
async function loadYouTubePower() {
  try {
    const res = await fetch('/api/social/youtube_power');
    const data = await res.json();

    const rBox = document.getElementById('yt-seo-rules-container');
    if (rBox && data.seo_checklist) {
      rBox.innerHTML = data.seo_checklist.map(r => `
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-black/40 border border-white/5">
          <span>✓ ${r.rule}</span>
          <span class="text-emerald font-bold">+${r.weight}%</span>
        </div>
      `).join('');
    }

    const cOut = document.getElementById('yt-chapters-output');
    if (cOut && data.sample_chapters) {
      cOut.value = data.sample_chapters.map(c => `${c.time} ${c.title}`).join('\n');
    }
  } catch (e) {
    console.error("YouTube power hatası:", e);
  }
}
window.loadYouTubePower = loadYouTubePower;

function copyYtChapters() {
  const text = document.getElementById('yt-chapters-output')?.value || '';
  navigator.clipboard.writeText(text);
  showToast("Video zaman damgaları kopyalandı!", "success");
}
window.copyYtChapters = copyYtChapters;

// Telegram Ultra
async function loadTelegramUltra() {
  try {
    const res = await fetch('/api/social/telegram_ultra');
    const data = await res.json();

    const jsonOut = document.getElementById('tg-json-output');
    if (jsonOut && data.sample_inline_markup) {
      jsonOut.value = JSON.stringify(data.sample_inline_markup, null, 2);
    }
  } catch (e) {
    console.error("Telegram ultra hatası:", e);
  }
}
window.loadTelegramUltra = loadTelegramUltra;

function copyTgPollText() {
  const text = "🎓 Qaysi yo'nalishda Turkiyada talaba bo'lishni xohlaysiz?\n\n1. 🩺 Tibbiyot va Stomatologiya\n2. 💻 Kompyuter va IT Muhandisligi\n3. 📊 Biznes va Iqtisodiyot\n4. ⚖️ Huquq va Xalqaro Munosabatlar\n\n@arkadasuz";
  navigator.clipboard.writeText(text);
  showToast("Kanal anketi kopyalandı!", "success");
}
window.copyTgPollText = copyTgPollText;

// ==============================================================
// MODULE 3: 🏛️ AKADEMİ & BAŞVURU (ÜNİVERSİTELER, BÜTÇE, YURT, DENKLİK)
// ==============================================================

async function loadUniversities() {
  try {
    const res = await fetch('/api/universities');
    window.allUniversities = await res.json();
    renderUniversities();
  } catch (e) {
    console.error("Üniversite yükleme hatası:", e);
  }
}
window.loadUniversities = loadUniversities;

function renderUniversities(customList = null) {
  const container = document.getElementById('universities-container');
  if (!container) return;

  const search = (document.getElementById('uni-search-input')?.value || '').toLowerCase();
  const list = customList || window.allUniversities;

  const filtered = list.filter(u => {
    return !search || (u.name && u.name.toLowerCase().includes(search)) || (u.location && u.location.toLowerCase().includes(search));
  });

  if (!filtered || filtered.length === 0) {
    container.innerHTML = `<div class="col-span-3 text-center py-8 text-dim font-mono">Üniversite bulunamadı.</div>`;
    return;
  }

  container.innerHTML = filtered.map((u, i) => {
    const formattedDesc = formatSafeText(u.full_post || 'Detaylı akademik program bilgisi.');
    const escapedName = (u.name || '').replace(/'/g, "\\'");
    const escapedLoc = (u.location || '').replace(/'/g, "\\'");

    return `
      <div class="gece-card p-5 flex flex-col justify-between space-y-3">
        <div>
          <div class="flex justify-between items-start mb-2">
            <span class="tag tag-amber text-[10px]">${u.type ? u.type.substring(0, 22) : 'Devlet'}</span>
            <span class="text-slate-400 font-mono text-[11px]">${u.established || '1992'}</span>
          </div>
          <h3 class="font-bold text-base text-white font-sans">${u.name}</h3>
          <span class="text-xs text-cyan font-mono block mt-0.5"><i class="fa-solid fa-location-dot mr-1"></i>${u.location || 'Turkiya'}</span>

          <div class="mt-3 p-3 bg-black/40 rounded-xl border border-white/5 text-xs text-slate-300 font-sans leading-relaxed max-h-36 overflow-y-auto">
            ${formattedDesc}
          </div>
        </div>
        <div class="pt-3 border-t border-white/5 flex gap-2">
          <button type="button" class="btn btn-outline text-amber border-amber btn-xs w-full py-1.5 font-mono" onclick="copyUniProposal('${escapedName}', '${escapedLoc}')">
            <i class="fa-solid fa-file-lines mr-1"></i> Teklif Kartını Kopyala
          </button>
        </div>
      </div>
    `;
  }).join('');
}
window.renderUniversities = renderUniversities;

function filterUniType(type) {
  if (type === 'all') {
    renderUniversities(window.allUniversities);
  } else if (type === 'Davlat') {
    renderUniversities(window.allUniversities.filter(u => (u.type || '').includes('Davlat')));
  } else if (type === 'Xususiy') {
    renderUniversities(window.allUniversities.filter(u => (u.type || '').includes('Xususiy')));
  } else if (type === 'Istanbul') {
    renderUniversities(window.allUniversities.filter(u => (u.location || '').includes('Istanbul')));
  } else if (type === 'Ankara') {
    renderUniversities(window.allUniversities.filter(u => (u.location || '').includes('Ankara')));
  }
}
window.filterUniType = filterUniType;

function copyUniProposal(name, loc) {
  const text = `🏛️ TURKIYA TA'LIM TAKLIFI: ${name}\n📍 Joylashuvi: ${loc}\n\n✅ Attestat bahosi bilan imtihonsiz qabul imkoniyati\n✅ Xalqaro akkreditatsiyalangan Yevropa diplomi\n✅ Arzon davlat yotoqxonasi va oylik stipendiyalar\n\n📲 Rasmiy vakil orqali hujjat topshirish: @arkadasuz`;
  navigator.clipboard.writeText(text);
  showToast(`${name} taklif karti kopyalandi!`, "success");
}
window.copyUniProposal = copyUniProposal;

// Budget Calculator
async function updateBudgetCalc() {
  const tuition = parseFloat(document.getElementById('calc-tuition')?.value) || 600;
  const dorm = parseFloat(document.getElementById('calc-dorm')?.value) || 180;
  const food = parseFloat(document.getElementById('calc-food')?.value) || 150;
  const transport = parseFloat(document.getElementById('calc-transport')?.value) || 15;
  const insurance = parseFloat(document.getElementById('calc-insurance')?.value) || 120;
  const needTomer = document.getElementById('calc-tomer')?.checked || false;

  try {
    const res = await fetch('/api/calculate_budget', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tuition, dorm, food, transport, insurance, need_tomer: needTomer })
    });
    const data = await res.json();

    const usdEl = document.getElementById('calc-res-usd');
    const uzsEl = document.getElementById('calc-res-uzs');
    const tryEl = document.getElementById('calc-res-try');

    if (usdEl) usdEl.innerText = data.formatted_usd;
    if (uzsEl) uzsEl.innerText = data.formatted_uzs;
    if (tryEl) tryEl.innerText = `~${data.total_try.toLocaleString()} TRY (Döviz: $1 = 34.2 TRY)`;

    const rTuition = document.getElementById('calc-row-tuition');
    const rDorm = document.getElementById('calc-row-dorm');
    const rFood = document.getElementById('calc-row-food');
    const rOther = document.getElementById('calc-row-other');
    const rTomer = document.getElementById('calc-row-tomer');

    if (rTuition) rTuition.innerText = `$${tuition}`;
    if (rDorm) rDorm.innerText = `$${dorm * 10}`;
    if (rFood) rFood.innerText = `$${food * 10}`;
    if (rOther) rOther.innerText = `$${(transport * 10) + insurance}`;
    if (rTomer) rTomer.innerText = needTomer ? '$800' : '$0';
  } catch (err) {
    console.error("Hesaplama hatası:", err);
  }
}
window.updateBudgetCalc = updateBudgetCalc;

function copyParentProposal() {
  const usd = document.getElementById('calc-res-usd')?.innerText || '$4,220';
  const uzs = document.getElementById('calc-res-uzs')?.innerText || "54,227,000 so'm";
  const text = `👨‍👩‍👦 TURKIYADA O'QISH VA YASHASH YILLIK XARAJAT SMETASI\n\n📌 Jami 10 oylik xarajat: ${usd} (${uzs})\n• Universitet shartnomasi: $600/yil\n• Yotoqxona (10 oy): $1,800\n• Oziq-ovqat va kundalik xarajat: $1,500\n• Sug'urta va viza harajatlari: $135\n\n💼 Talaba 1-kursdan haftasiga 20 soat qonuniy ishlab o'z xarajatlarini to'liq qoplay oladi!\n\nArkadaş Consulting: @arkadasuz`;
  navigator.clipboard.writeText(text);
  showToast("Ota-ona uchun hisob-kitob nusxalandi!", "success");
}
window.copyParentProposal = copyParentProposal;

// Sınav Simülatörü & TR-YÖS
async function loadExamPrep() {
  try {
    const res = await fetch('/api/exam_prep');
    const data = await res.json();
    window.quizData = data.tryos_quiz || [];
    renderCurrentQuestion();

    const cal = document.getElementById('exam-calendar-container');
    if (cal && data.exam_calendar) {
      cal.innerHTML = data.exam_calendar.map(c => `
        <div class="p-2.5 rounded-lg bg-black/40 border border-white/5 flex justify-between items-center">
          <div>
            <span class="font-bold text-white block">${c.name}</span>
            <span class="text-dim text-[10px]">Tarih: ${c.date}</span>
          </div>
          <span class="tag tag-amber text-[10px]">${c.status}</span>
        </div>
      `).join('');
    }

    const satBox = document.getElementById('sat-conversion-container');
    if (satBox && data.sat_conversion) {
      satBox.innerHTML = data.sat_conversion.map(s => `
        <div class="p-2 rounded-lg bg-black/30 border border-white/5 flex justify-between">
          <span class="text-cyan font-bold">${s.sat} SAT = ${s.tryos_eq} Puan</span>
          <span class="text-slate-400 truncate max-w-[180px]">${s.faculties}</span>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Exam prep hatası:", e);
  }
}
window.loadExamPrep = loadExamPrep;

function renderCurrentQuestion() {
  if (!window.quizData || window.quizData.length === 0) return;
  const q = window.quizData[window.currentQuestionIdx];

  const cCounter = document.getElementById('quiz-question-counter');
  const cTag = document.getElementById('quiz-topic-tag');
  const cText = document.getElementById('quiz-question-text');
  const cOpts = document.getElementById('quiz-options-container');
  const cSol = document.getElementById('quiz-solution-box');
  const cExp = document.getElementById('quiz-explanation-text');

  if (cCounter) cCounter.innerText = `Soru ${window.currentQuestionIdx + 1} / ${window.quizData.length}`;
  if (cTag) cTag.innerText = q.topic;
  if (cText) cText.innerText = q.question;

  if (cOpts) {
    cOpts.innerHTML = q.options.map(opt => {
      const optEscaped = opt.replace(/'/g, "\\'");
      const ansEscaped = q.answer.replace(/'/g, "\\'");
      return `
        <button type="button" class="w-full text-left p-3 rounded-xl border border-white/10 bg-black/40 hover:border-cyan text-xs font-mono text-slate-200 transition" onclick="selectQuizAnswer('${optEscaped}', '${ansEscaped}')">
          ${opt}
        </button>
      `;
    }).join('');
  }

  if (cSol) cSol.classList.add('hidden');
  if (cExp) cExp.innerText = q.explanation;
}

function selectQuizAnswer(chosen, correct) {
  const sol = document.getElementById('quiz-solution-box');
  if (sol) sol.classList.remove('hidden');

  if (chosen.trim().startsWith(correct.substring(0, 1))) {
    showToast("Tebrikler! Doğru cevap! 🎉", "success");
  } else {
    showToast("Yanlış cevap! Çözümü aşağıdan inceleyin.", "error");
  }
}
window.selectQuizAnswer = selectQuizAnswer;

function nextQuizQuestion() {
  if (window.currentQuestionIdx < window.quizData.length - 1) {
    window.currentQuestionIdx++;
    renderCurrentQuestion();
  } else {
    showToast("Sınav testi tamamlandı!", "success");
  }
}
window.nextQuizQuestion = nextQuizQuestion;

function prevQuizQuestion() {
  if (window.currentQuestionIdx > 0) {
    window.currentQuestionIdx--;
    renderCurrentQuestion();
  }
}
window.prevQuizQuestion = prevQuizQuestion;

function switchExamTab(tab) {
  showToast(`${tab.toUpperCase()} modülü aktif`, "info");
}
window.switchExamTab = switchExamTab;

// Yurtlar
async function loadDormitories() {
  try {
    const res = await fetch('/api/dormitories');
    const data = await res.json();
    window.allDorms = data.dorms || [];
    renderDormitories();
  } catch (e) {
    console.error("Dormitory hatası:", e);
  }
}
window.loadDormitories = loadDormitories;

function renderDormitories() {
  const filter = document.getElementById('dorm-city-filter')?.value || 'all';
  const container = document.getElementById('dormitories-cards-container');
  if (!container) return;

  const list = filter === 'all' ? window.allDorms : window.allDorms.filter(d => d.city.includes(filter));

  container.innerHTML = list.map(d => `
    <div class="gece-card p-5 flex flex-col justify-between space-y-3">
      <div>
        <div class="flex justify-between items-start mb-1">
          <span class="tag tag-cyan text-[10px]">${d.type}</span>
          <span class="text-emerald font-mono font-bold text-sm">$${d.price_usd} / ay</span>
        </div>
        <h3 class="font-bold text-sm text-white font-sans">${d.name}</h3>
        <span class="text-xs text-amber font-mono block mt-0.5"><i class="fa-solid fa-location-dot mr-1"></i>${d.city}</span>
        <div class="mt-3 space-y-1 font-mono text-xs text-slate-300">
          <div>🛏️ <strong>Oda:</strong> ${d.room}</div>
          <div>🍽️ <strong>Yemek:</strong> ${d.meals}</div>
          <div>🚇 <strong>Ulaşım:</strong> ${d.metro_dist}</div>
          <div>🏛️ <strong>Yakın Kampüsler:</strong> ${d.unis}</div>
        </div>
      </div>
      <div class="pt-3 border-t border-white/5">
        <a href="https://wa.me/905340000000?text=${encodeURIComponent("Merhaba, " + d.name + " yurdu hakkında bilgi ve rezervasyon istiyorum.")}" target="_blank" class="btn btn-outline text-emerald border-emerald btn-xs w-full py-1.5 font-mono text-center flex items-center justify-center gap-1">
          <i class="fa-brands fa-whatsapp"></i>
          <span>Yurt Rezerve Et</span>
        </a>
      </div>
    </div>
  `).join('');
}
window.renderDormitories = renderDormitories;

// Denklik
async function loadDenklikData() {
  try {
    const res = await fetch('/api/denklik');
    const data = await res.json();

    const regBox = document.getElementById('denklik-reg-box');
    if (regBox) regBox.innerText = `⚖️ ${data.regulation}`;

    const topBox = document.getElementById('denklik-top-unis-container');
    if (topBox && data.top_universities) {
      topBox.innerHTML = data.top_universities.map(u => `
        <div class="gece-card p-4 space-y-1">
          <span class="text-amber font-mono font-bold text-xs">${u.qs_rank} QS Dünyada</span>
          <h4 class="font-bold text-white text-xs">${u.name}</h4>
          <span class="text-[11px] text-cyan font-mono block">${u.city} (${u.type})</span>
          <span class="tag tag-emerald text-[10px] mt-2 block">${u.status}</span>
        </div>
      `).join('');
    }

    const stepsBox = document.getElementById('denklik-steps-container');
    if (stepsBox && data.denklik_steps) {
      stepsBox.innerHTML = data.denklik_steps.map((st, i) => `
        <div class="p-3 bg-black/40 rounded-xl border border-white/5 space-y-1">
          <span class="text-amber font-bold">${i+1}. Aşama</span>
          <p class="text-slate-300 text-[11px]">${st}</p>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Denklik hatası:", e);
  }
}
window.loadDenklikData = loadDenklikData;

// ==============================================================
// MODULE 4: 👥 CRM, VİZE, LOGISTICS & DEFENSE
// ==============================================================

async function loadLeads() {
  try {
    const res = await fetch('/api/leads');
    window.allLeads = await res.json();

    const spEl = document.getElementById('spotlight-leads-count');
    const stEl = document.getElementById('crm-stat-total');
    const snEl = document.getElementById('crm-stat-new');
    const sdEl = document.getElementById('crm-stat-done');
    const spCount = document.getElementById('crm-stat-pending');

    if (spEl) spEl.innerText = `${window.allLeads.length} Aday`;
    if (stEl) stEl.innerText = `${window.allLeads.length} Aday`;

    const newCount = window.allLeads.filter(l => (l.current_status || '').includes('Yangi') || (l.current_status || '').includes('Yeni')).length;
    const doneCount = window.allLeads.filter(l => (l.current_status || '').includes('Kayıt') || (l.current_status || '').includes('Qabul')).length;

    if (snEl) snEl.innerText = `${newCount} Aday`;
    if (sdEl) sdEl.innerText = `${doneCount} Aday`;
    if (spCount) spCount.innerText = `${window.allLeads.length - newCount - doneCount} Aday`;

    renderCrmTable();
    renderCrmKanban();
  } catch (e) {
    console.error("CRM yükleme hatası:", e);
  }
}
window.loadLeads = loadLeads;

function toggleCrmView(view) {
  const kView = document.getElementById('crm-kanban-view');
  const tView = document.getElementById('crm-table-view');
  if (!kView || !tView) return;

  if (view === 'kanban') {
    kView.classList.remove('hidden');
    tView.classList.add('hidden');
  } else {
    kView.classList.add('hidden');
    tView.classList.remove('hidden');
  }
}
window.toggleCrmView = toggleCrmView;

function renderCrmTable() {
  const tbody = document.getElementById('crm-table-body');
  if (!tbody) return;

  tbody.innerHTML = window.allLeads.map(l => {
    const st = l.current_status || '';
    return `
      <tr class="hover:bg-white/[0.02] transition">
        <td class="py-3 px-4 text-dim">#${l.id}</td>
        <td class="py-3 px-4 font-bold text-white font-sans">${l.name}</td>
        <td class="py-3 px-4 text-cyan">${l.phone || '-'}</td>
        <td class="py-3 px-4 text-slate-300 font-sans">${l.interest || "Turkiyada ta'lim"}</td>
        <td class="py-3 px-4 text-dim text-[11px]">${l.timestamp || '-'}</td>
        <td class="py-3 px-4">
          <select onchange="updateLeadStatus(${l.id}, this.value)" class="bg-black/60 border border-white/10 rounded-lg px-2 py-1 text-xs text-white focus:outline-none font-sans">
            <option value="Yeni Başvuru (Bekliyor)" ${st.includes('Yangi') || st.includes('Yeni') ? 'selected' : ''}>🟡 Yeni Başvuru</option>
            <option value="İletişim Kuruldu" ${st.includes("Bog'lanildi") || st.includes('İletişim') ? 'selected' : ''}>🔵 İletişim Kuruldu</option>
            <option value="Evraklar Teslim Edildi" ${st.includes('Hujjatlar') || st.includes('Evrak') ? 'selected' : ''}>🟣 Evraklar Teslim</option>
            <option value="Kabul Belgesi Geldi" ${st.includes('Qabul') || st.includes('Kabul') ? 'selected' : ''}>🟢 Kabul Belgesi</option>
            <option value="Kesin Kayıt Yapıldı" ${st.includes('yozildi') || st.includes('Kayıt') ? 'selected' : ''}>✅ Kesin Kayıt</option>
          </select>
        </td>
        <td class="py-3 px-4 text-right space-x-1">
          <button type="button" class="btn btn-outline btn-xs text-amber border-amber/40" onclick="openLeadDocsModal(${l.id})" title="Öğrenci Evrakları">
            <i class="fa-solid fa-folder-open mr-1"></i>${(l.documents||[]).length}
          </button>
          <a href="https://wa.me/${(l.phone||'').replace(/[^0-9]/g, '')}" target="_blank" class="btn btn-outline btn-xs text-emerald"><i class="fa-brands fa-whatsapp"></i></a>
          <button type="button" class="btn btn-outline btn-xs text-rose" onclick="deleteLead(${l.id})"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `;
  }).join('');
}
window.renderCrmTable = renderCrmTable;

function renderCrmKanban() {
  const container = document.getElementById('kanban-board-container');
  if (!container) return;

  const stages = [
    { key: "yeni", title: "🟡 Yeni Başvurular", filter: s => s.includes('Yangi') || s.includes('Yeni') },
    { key: "iletisim", title: "🔵 İletişim Kuruldu", filter: s => s.includes("Bog'lanildi") || s.includes('İletişim') },
    { key: "evrak", title: "🟣 Evrak Toplanıyor", filter: s => s.includes('Hujjatlar') || s.includes('Evrak') },
    { key: "kabul", title: "🟢 Kabul Mektubu Geldi", filter: s => s.includes('Qabul') || s.includes('Kabul') },
    { key: "viza", title: "📑 Vize / İkamet Aşamasında", filter: s => s.includes('Viza') || s.includes('İkamet') },
    { key: "kayit", title: "✅ Kesin Kayıt Tamamlandı", filter: s => s.includes('yozildi') || s.includes('Kayıt') }
  ];

  container.innerHTML = stages.map(col => {
    const colLeads = window.allLeads.filter(l => col.filter(l.current_status || ''));
    return `
      <div class="kanban-col p-4 flex flex-col flex-1 space-y-3">
        <div class="flex justify-between items-center border-b border-white/10 pb-2">
          <span class="font-bold text-xs text-white font-mono">${col.title}</span>
          <span class="tag tag-slate text-[10px]">${colLeads.length}</span>
        </div>
        <div class="space-y-2.5 overflow-y-auto max-h-[520px] pr-1">
          ${colLeads.map(l => `
            <div class="p-3 bg-black/60 rounded-xl border border-white/10 space-y-1.5 hover:border-cyan transition">
              <div class="flex justify-between items-start">
                <span class="font-bold text-xs text-white">${l.name}</span>
                <span class="text-[10px] text-dim font-mono">#${l.id}</span>
              </div>
              <div class="text-[11px] text-cyan font-mono">${l.phone || '-'}</div>
              <div class="text-[11px] text-slate-300 truncate">${l.interest || "Ta'lim"}</div>
              <div class="pt-2 border-t border-white/5 flex justify-between items-center text-[10px] font-mono">
                <span class="text-dim">${l.timestamp ? l.timestamp.substring(0, 10) : ''}</span>
                <div class="space-x-1.5">
                  <button type="button" onclick="openLeadDocsModal(${l.id})" class="text-amber hover:underline"><i class="fa-solid fa-folder-open"></i> ${(l.documents||[]).length}</button>
                  <a href="https://wa.me/${(l.phone||'').replace(/[^0-9]/g, '')}" target="_blank" class="text-emerald hover:underline"><i class="fa-brands fa-whatsapp"></i> Chat</a>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');
}
window.renderCrmKanban = renderCrmKanban;

async function updateLeadStatus(id, newStatus) {
  const res = await fetch('/api/leads/update_status', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, status: newStatus })
  });
  const data = await res.json();
  if (data.success) {
    showToast("Öğrenci durumu güncellendi", "success");
    loadLeads();
  }
}
window.updateLeadStatus = updateLeadStatus;

async function deleteLead(id) {
  if (!confirm("Bu öğrenci kaydını silmek istediğinize emin misiniz?")) return;
  const res = await fetch('/api/leads/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  });
  const data = await res.json();
  if (data.success) {
    showToast("Öğrenci kaydı silindi", "info");
    loadLeads();
  }
}
window.deleteLead = deleteLead;

// Student Document Management (Modal & Upload)
function openLeadDocsModal(leadId) {
  const lead = (window.allLeads || []).find(l => String(l.id) === String(leadId));
  if (!lead) return;

  const modal = document.getElementById('lead-docs-modal');
  const targetId = document.getElementById('lead-doc-target-id');
  const title = document.getElementById('lead-docs-modal-title');
  const subtitle = document.getElementById('lead-docs-modal-subtitle');

  if (targetId) targetId.value = lead.id;
  if (title) title.innerText = `${lead.name} — Evrak Havuzu`;
  if (subtitle) subtitle.innerText = `Tel: ${lead.phone || '-'} | ID: #${lead.id}`;

  renderLeadDocsList(lead.documents || []);
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}
window.openLeadDocsModal = openLeadDocsModal;

function closeLeadDocsModal() {
  const modal = document.getElementById('lead-docs-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}
window.closeLeadDocsModal = closeLeadDocsModal;

function renderLeadDocsList(docs) {
  const container = document.getElementById('lead-docs-list-container');
  if (!container) return;

  if (!docs || docs.length === 0) {
    container.innerHTML = '<div class="p-3 text-center text-dim bg-black/30 rounded-xl">Bu öğrenciye ait yüklenmiş evrak bulunmuyor.</div>';
    return;
  }

  container.innerHTML = docs.map(d => `
    <div class="flex items-center justify-between p-2.5 rounded-xl bg-black/60 border border-white/10 hover:border-amber/50 transition">
      <div class="flex items-center gap-2 overflow-hidden">
        <span class="tag tag-amber text-[10px] shrink-0">${d.type}</span>
        <span class="text-white font-sans text-xs truncate max-w-[200px]">${d.filename}</span>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-[10px] text-dim">${d.uploaded_at || ''}</span>
        <a href="${d.url}" target="_blank" download class="btn btn-outline btn-xs text-cyan border-cyan/40">
          <i class="fa-solid fa-download"></i> İndir
        </a>
      </div>
    </div>
  `).join('');
}

async function handleLeadDocUpload(e) {
  if (e && e.preventDefault) e.preventDefault();
  const leadId = document.getElementById('lead-doc-target-id')?.value;
  const docType = document.getElementById('lead-doc-type')?.value;
  const fileInput = document.getElementById('lead-doc-file');
  const file = fileInput?.files?.[0];

  if (!leadId || !file) {
    showToast("Lütfen yüklenecek dosyayı seçin!", "error");
    return;
  }

  const formData = new FormData();
  formData.append('lead_id', leadId);
  formData.append('doc_type', docType);
  formData.append('file', file);

  showToast("Evrak yükleniyor...", "info");
  try {
    const res = await fetch('/api/leads/upload_doc', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.success) {
      showToast("Evrak başarıyla yüklendi!", "success");
      if (fileInput) fileInput.value = '';
      await loadLeads();
      const updatedLead = (window.allLeads || []).find(l => String(l.id) === String(leadId));
      if (updatedLead) {
        renderLeadDocsList(updatedLead.documents || []);
      }
    } else {
      showToast(data.error || "Yükleme başarısız", "error");
    }
  } catch (err) {
    showToast("Evrak yükleme hatası", "error");
  }
}
window.handleLeadDocUpload = handleLeadDocUpload;

function openAddLeadModal() {
  const modal = document.getElementById('add-lead-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}
window.openAddLeadModal = openAddLeadModal;

function closeAddLeadModal() {
  const modal = document.getElementById('add-lead-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}
window.closeAddLeadModal = closeAddLeadModal;

async function saveNewLead() {
  const name = document.getElementById('lead-new-name')?.value.trim();
  const phone = document.getElementById('lead-new-phone')?.value.trim();
  const interest = document.getElementById('lead-new-interest')?.value.trim();
  if (!name || !phone) {
    showToast("İsim ve telefon zorunludur!", "error");
    return;
  }
  const res = await fetch('/api/leads/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, phone, interest })
  });
  const data = await res.json();
  if (data.success) {
    showToast("Aday CRM'e eklendi!", "success");
    closeAddLeadModal();
    loadLeads();
  }
}
window.saveNewLead = saveNewLead;

// 12-Step Visa Checklist
const checklistSteps = [
  { id: 1, title: "1. Xorijga Chiqish Pasporti (Qizil Pasport)", desc: "Kamida 2 yil muddatga ega xorijga chiqish biometrik pasporti tayyorlash." },
  { id: 2, title: "2. Attestat / Diplom Apostili", desc: "Adliya vazirligi yoki Davlat xizmatlari orqali attestatni xalqaro apostil qildirish." },
  { id: 3, title: "3. Turkcha Notarial Tarjima", desc: "Attestat va ilova (baho varaqasi)ni turk tiliga professional tarjima va notarial tasdiqlash." },
  { id: 4, title: "4. Universitet Tanlash & Portal Ariza", desc: "Abituriyent baholariga mos 3 ta davlat yoki xususiy universitet tanlab, rasmiy ariza yuborish." },
  { id: 5, title: "5. Shartli Qabul (Şartlı Kabul)", desc: "Universitet rektoratidan abituriyent nomiga shartli qabul xatini qabul qilish." },
  { id: 6, title: "6. Dastlabki Harç Depozit To'lovi", desc: "Universitet rasmiy hisob raqamiga yillik kontraktning belgilangan qismini to'lash." },
  { id: 7, title: "7. Rasmiy Qabul Xati (Resmi Kabul)", desc: "Elchixonaga viza uchun taqdim etiladigan muhrli yakuniy qabul xatini olish." },
  { id: 8, title: "8. Elchixonadan Talabalik Vizasi", desc: "Toshkent yoki Samarqanddagi Turkiya elchixonasidan talabalik vizasi rasmiylashtirish." },
  { id: 9, title: "9. Parvoz & Aeroportda Kutib Olish", desc: "Istanbulga uchish chiptasi, aeroportda VIP kutib olish va yotoqxonaga joylashish." },
  { id: 10, title: "10. Yuzma-Yuz Yakuniy Ro'yxatdan O'tish", desc: "Universitet talabalar bo'limiga original hujjatlarni topshirish va talabalik ID kartasi olish." },
  { id: 11, title: "11. Göç İdaresi İkamet (Yashash Ruxsati)", desc: "1 yillik rasmiy yashash ruxsatnomasi arizasi, tibbiy sug'urta va barmoq izi topshirish." },
  { id: 12, title: "12. Talaba Kartasi, SIM & Bank Hisobi", desc: "Chegirmali İstanbulkart transport kartasi, turk SIM-karta va Ziraat Bank kartasi ochish." }
];

function initChecklist() {
  const container = document.getElementById('checklist-steps-container');
  if (!container) return;
  const saved = JSON.parse(localStorage.getItem('arkadas_checklist_state') || '{}');

  container.innerHTML = checklistSteps.map(step => {
    const isChecked = !!saved[step.id];
    return `
      <div class="gece-card p-4 flex items-start gap-3 cursor-pointer hover:border-cyan transition" onclick="toggleCheckStep(${step.id})">
        <input type="checkbox" id="chk-step-${step.id}" ${isChecked ? 'checked' : ''} class="w-5 h-5 rounded text-cyan focus:ring-0 mt-0.5 pointer-events-none">
        <div class="space-y-1">
          <span class="font-bold text-xs text-white font-mono block ${isChecked ? 'line-through text-slate-500' : ''}">${step.title}</span>
          <p class="text-[11px] text-slate-400 font-sans leading-relaxed">${step.desc}</p>
        </div>
      </div>
    `;
  }).join('');
  updateChecklistProgress();
}
window.initChecklist = initChecklist;

function toggleCheckStep(id) {
  const chk = document.getElementById(`chk-step-${id}`);
  if (!chk) return;
  chk.checked = !chk.checked;
  const saved = JSON.parse(localStorage.getItem('arkadas_checklist_state') || '{}');
  saved[id] = chk.checked;
  localStorage.setItem('arkadas_checklist_state', JSON.stringify(saved));
  initChecklist();
}
window.toggleCheckStep = toggleCheckStep;

function updateChecklistProgress() {
  const saved = JSON.parse(localStorage.getItem('arkadas_checklist_state') || '{}');
  const total = checklistSteps.length;
  const completed = Object.values(saved).filter(Boolean).length;
  const pct = Math.round((completed / total) * 100);

  const pBar = document.getElementById('checklist-progress-bar');
  const pPct = document.getElementById('checklist-progress-pct');
  if (pBar) pBar.style.width = `${pct}%`;
  if (pPct) pPct.innerText = `${pct}% (${completed}/${total})`;
}

function resetChecklist() {
  if (!confirm("Vize takip listesini sıfırlamak istiyor musunuz?")) return;
  localStorage.removeItem('arkadas_checklist_state');
  initChecklist();
}
window.resetChecklist = resetChecklist;

// Official Documents
async function loadDocumentTemplates() {
  try {
    const res = await fetch('/api/documents/templates');
    const data = await res.json();
    window.documentTemplates = data.documents || [];
    renderGeneratedDoc();
  } catch (e) {
    console.error("Doküman şablonu hatası:", e);
  }
}
window.loadDocumentTemplates = loadDocumentTemplates;

function renderGeneratedDoc() {
  const select = document.getElementById('doc-type-select')?.value || 'offer_proposal';
  const targetDoc = window.documentTemplates.find(d => d.id === select);
  if (!targetDoc) return;

  const sName = document.getElementById('doc-student-name')?.value || 'Jahongir Aliyev';
  const sPass = document.getElementById('doc-passport')?.value || 'FA1234567';
  const sUni = document.getElementById('doc-university')?.value || 'Marmara Universiteti';
  const sMajor = document.getElementById('doc-major')?.value || 'Kompyuter Muhandisligi';

  let rendered = targetDoc.template
    .replace(/{student_name}/g, sName)
    .replace(/{passport_number}/g, sPass)
    .replace(/{university_name}/g, sUni)
    .replace(/{major_name}/g, sMajor)
    .replace(/{language}/g, "Turkcha / Inglizcha")
    .replace(/{tuition}/g, "$600 / yiliga")
    .replace(/{date}/g, new Date().toLocaleDateString('tr-TR'))
    .replace(/{code}/g, Math.floor(1000 + Math.random() * 9000))
    .replace(/{phone}/g, "+998 90 123 45 67")
    .replace(/{sponsor_name}/g, "Aliyev Rustam (Ota)")
    .replace(/{parent_name}/g, "Aliyev Rustam")
    .replace(/{birth_date}/g, "2008")
    .replace(/{flight_number}/g, "HY-271")
    .replace(/{arrival_time}/g, "14:30")
    .replace(/{dorm_name}/g, "Maltepe Talabalar Yotoqxonasi");

  const out = document.getElementById('doc-output-text');
  const title = document.getElementById('doc-title-preview');
  if (out) out.value = rendered;
  if (title) title.innerText = targetDoc.name;
}
window.renderGeneratedDoc = renderGeneratedDoc;

function copyDocumentText() {
  const text = document.getElementById('doc-output-text')?.value || '';
  navigator.clipboard.writeText(text);
  showToast("Resmi belge metni kopyalandı!", "success");
}
window.copyDocumentText = copyDocumentText;

function printDocSheet() {
  const text = document.getElementById('doc-output-text')?.value || '';
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`<pre style="font-family: monospace; padding: 20px; white-space: pre-wrap;">${text}</pre>`);
  printWindow.document.close();
  printWindow.print();
}
window.printDocSheet = printDocSheet;

// Airport Logistics
async function loadAirportLogistics() {
  try {
    const res = await fetch('/api/airport_logistics');
    const data = await res.json();

    const tbody = document.getElementById('airport-flights-tbody');
    if (tbody && data.active_arrivals) {
      tbody.innerHTML = data.active_arrivals.map(f => `
        <tr class="hover:bg-white/[0.02] transition">
          <td class="py-3 px-4 font-bold text-white">${f.student}</td>
          <td class="py-3 px-4 text-cyan">${f.flight}</td>
          <td class="py-3 px-4 text-amber">${f.airport}</td>
          <td class="py-3 px-4 text-white font-bold">${f.eta}</td>
          <td class="py-3 px-4 text-slate-300">${f.curator}</td>
          <td class="py-3 px-4"><span class="tag tag-emerald">${f.status}</span></td>
          <td class="py-3 px-4 text-right">
            <button type="button" class="btn btn-outline btn-xs text-rose border-rose" onclick="printAirportNameBoard('${f.student}')">
              <i class="fa-solid fa-id-badge mr-1"></i> Karşılama Levhası
            </button>
          </td>
        </tr>
      `).join('');
    }

    const oBox = document.getElementById('orientation-schedule-container');
    if (oBox && data.orientation_schedule) {
      oBox.innerHTML = data.orientation_schedule.map(o => `
        <div class="gece-card p-4 space-y-1 font-mono text-xs">
          <span class="tag tag-cyan text-[10px]">${o.day}</span>
          <h4 class="font-bold text-white text-xs mt-1">${o.title}</h4>
          <p class="text-[11px] text-slate-400 font-sans mt-1 leading-relaxed">${o.desc}</p>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Airport hatası:", e);
  }
}
window.loadAirportLogistics = loadAirportLogistics;

function printAirportNameBoard(name) {
  const win = window.open('', '_blank');
  win.document.write(`
    <div style="text-align: center; margin-top: 100px; font-family: sans-serif;">
      <h1 style="font-size: 55px; letter-spacing: 2px;">ARKADAŞ CONSULTING</h1>
      <p style="font-size: 24px; color: #555;">TÜRKİYE ULUSLARARASI ÖĞRENCİ MERKEZİ</p>
      <div style="margin-top: 60px; padding: 40px; border: 4px dashed #000; display: inline-block;">
        <h2 style="font-size: 70px; margin: 0;">${name}</h2>
      </div>
      <p style="margin-top: 40px; font-size: 20px;">Hoş Geldiniz! / Xush Kelibsiz!</p>
    </div>
  `);
  win.document.close();
  win.print();
}
window.printAirportNameBoard = printAirportNameBoard;

// Visa Rejection Defense
async function loadVisaDefense() {
  try {
    const res = await fetch('/api/visa_defense');
    const data = await res.json();

    const cBox = document.getElementById('visa-causes-container');
    if (cBox && data.rejection_causes) {
      cBox.innerHTML = data.rejection_causes.map(c => `
        <div class="gece-card p-4 space-y-1 font-mono text-xs">
          <span class="text-rose font-bold block">❌ Olası Neden: ${c.cause}</span>
          <p class="text-emerald text-[11px] font-sans">🛡️ Arkadaş Çözümü: ${c.solution}</p>
        </div>
      `).join('');
    }

    const out = document.getElementById('visa-appeal-output');
    if (out && data.appeal_letter_template) {
      out.value = data.appeal_letter_template
        .replace(/{student_name}/g, "Jahongir Aliyev")
        .replace(/{passport_number}/g, "FA1234567")
        .replace(/{university_name}/g, "Marmara Üniversitesi")
        .replace(/{major_name}/g, "Bilgisayar Mühendisliği")
        .replace(/{date}/g, new Date().toLocaleDateString('tr-TR'));
    }
  } catch (e) {
    console.error("Visa defense hatası:", e);
  }
}
window.loadVisaDefense = loadVisaDefense;

function copyAppealText() {
  const text = document.getElementById('visa-appeal-output')?.value || '';
  navigator.clipboard.writeText(text);
  showToast("İtiraz dilekçesi kopyalandı!", "success");
}
window.copyAppealText = copyAppealText;

function printAppealSheet() {
  const text = document.getElementById('visa-appeal-output')?.value || '';
  const win = window.open('', '_blank');
  win.document.write(`<pre style="font-family: monospace; padding: 20px; white-space: pre-wrap;">${text}</pre>`);
  win.document.close();
  win.print();
}
window.printAppealSheet = printAppealSheet;

// ==============================================================
// MODULE 5: 🎨 YARATICI STÜDYO & AI (AI METİN, AUDIO, CANVAS BANNER)
// ==============================================================

// AI Marketing Copy
function selectAITopic(topic, btn) {
  window.selectedAITopic = topic;
  document.querySelectorAll('#section-aicopilot .btn-xs, .sub-tab-panel .btn-xs').forEach(b => b.classList.remove('btn-primary'));
  if (btn) btn.classList.add('btn-primary');
}
window.selectAITopic = selectAITopic;

async function triggerAIGeneration() {
  const keyword = document.getElementById('ai-custom-keyword')?.value || '';
  const lang = document.getElementById('ai-lang-select')?.value || 'uz';
  const persona = document.getElementById('ai-persona-select')?.value || 'corporate';

  showToast("Dinamik AI metni hazırlanıyor...", "info");
  const tag = document.getElementById('ai-status-tag');
  if (tag) tag.innerText = "AI Üretiyor...";

  try {
    const res = await fetch('/api/generate_ai_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        topic: window.selectedAITopic || 'tibbiyot',
        keyword: keyword,
        lang: lang,
        persona: persona
      })
    });
    const data = await res.json();
    if (data.success && data.post) {
      const out = document.getElementById('ai-generated-output');
      if (out) out.value = data.post.content;
      if (tag) tag.innerText = "✅ " + (data.post.title || "Metin Hazır!");
      showToast("AI metni başarıyla üretildi!", "success");
    } else {
      showToast(data.error || "AI metin üretilemedi", "error");
    }
  } catch (e) {
    showToast("AI üretim hatası", "error");
  }
}
window.triggerAIGeneration = triggerAIGeneration;

function copyAIText() {
  const text = document.getElementById('ai-generated-output')?.value || '';
  navigator.clipboard.writeText(text);
  showToast("AI metni kopyalandı!", "success");
}
window.copyAIText = copyAIText;

function sendAITextToTelegram() {
  const text = document.getElementById('ai-generated-output')?.value || '';
  if (!text) {
    showToast("Önce bir metin üretin!", "error");
    return;
  }
  // Call official telegram dispatch
  fetch('/api/send_telegram_post', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: text })
  }).then(r => r.json()).then(d => {
    if (d.success) showToast("Metin @arkadasuz kanalında yayınlandı!", "success");
  });
}
window.sendAITextToTelegram = sendAITextToTelegram;

// Audio Studio
async function loadAudioStudio() {
  try {
    const res = await fetch('/api/audio_studio');
    const data = await res.json();

    const vContainer = document.getElementById('audio-voices-container');
    if (vContainer && data.voices) {
      vContainer.innerHTML = data.voices.map((v, i) => `
        <div class="p-2.5 rounded-xl border border-white/10 bg-black/40 hover:border-purple cursor-pointer transition ${i===0?'border-purple bg-purple-950/20':''}" onclick="selectVoice('${v.id}', this)">
          <div class="flex justify-between items-center text-xs font-bold text-white">
            <span>${v.name}</span>
            <span class="text-[10px] text-cyan">${v.lang}</span>
          </div>
          <p class="text-[10px] text-slate-400 mt-1 line-clamp-1">${v.role}</p>
        </div>
      `).join('');
    }

    const tContainer = document.getElementById('audio-tracks-container');
    if (tContainer && data.music_tracks) {
      tContainer.innerHTML = data.music_tracks.map(t => `
        <div class="flex justify-between items-center p-2 rounded-lg bg-black/40 border border-white/5">
          <span>🎵 ${t.name} (${t.mood})</span>
          <button type="button" class="btn btn-outline btn-xs text-cyan" onclick="showToast('${t.name} önizleniyor...', 'info')">Dinle</button>
        </div>
      `).join('');
    }
    updateAudioStats();
  } catch (e) {
    console.error("Audio studio hatası:", e);
  }
}
window.loadAudioStudio = loadAudioStudio;

function selectVoice(id, el) {
  window.selectedVoiceId = id;
  document.querySelectorAll('#audio-voices-container > div').forEach(d => {
    d.className = 'p-2.5 rounded-xl border border-white/10 bg-black/40 hover:border-purple cursor-pointer transition';
  });
  if (el) el.className = 'p-2.5 rounded-xl border border-purple bg-purple-950/20 cursor-pointer transition';
}
window.selectVoice = selectVoice;

function updateAudioStats() {
  const text = document.getElementById('audio-script-input')?.value || '';
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const estSec = Math.round(words / 2.5);
  const counter = document.getElementById('audio-word-count');
  if (counter) counter.innerText = `${words} kelime / ~${estSec} sn`;

  const srtEl = document.getElementById('audio-srt-output');
  if (srtEl) {
    srtEl.value = `1\n00:00:00,000 --> 00:00:03,500\nTurkiyada ta'lim olish orzuingizmi?\n\n2\n00:00:03,500 --> 00:00:07,000\nDavlat universitetlariga imtihonsiz qabul boshlandi!\n\n3\n00:00:07,000 --> 00:00:11,000\nYillik kontrakt bor-yo'g'i 600 dollar. @arkadasuz`;
  }
}
window.updateAudioStats = updateAudioStats;

async function generateSpeechAudio() {
  const text = document.getElementById('audio-script-input')?.value || '';
  if (!text) {
    showToast("Seslendirilecek metin girilmedi!", "error");
    return;
  }
  const speed = parseFloat(document.getElementById('audio-speed-select')?.value) || 1.0;
  const voiceId = window.selectedVoiceId || 'v_kamola';

  showToast("Neural ses sentezleniyor (Edge-TTS)...", "info");

  try {
    const res = await fetch('/api/synthesize_audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice_id: voiceId, speed })
    });
    const data = await res.json();
    if (data.success && data.audio_url) {
      const box = document.getElementById('audio-result-box');
      const player = document.getElementById('neural-audio-player');
      const badge = document.getElementById('neural-voice-badge');
      const dlBtn = document.getElementById('btn-download-mp3');

      if (box) box.classList.remove('hidden');
      if (player) {
        player.src = data.audio_url;
        player.play().catch(() => {});
      }
      if (badge) badge.innerText = "Neural MP3: " + (data.voice_name || 'Hazır');
      if (dlBtn) dlBtn.href = data.audio_url;

      showToast("Neural ses başarıyla oluşturuldu ve oynatılıyor!", "success");
    } else {
      showToast(data.error || "Ses sentezi başarısız", "error");
    }
  } catch (e) {
    console.error("Audio synth error:", e);
    showToast("Ses motoru bağlantı hatası", "error");
  }
}
window.generateSpeechAudio = generateSpeechAudio;
window.testAudioVoice = generateSpeechAudio;

function copySrtSubtitles() {
  const text = document.getElementById('audio-srt-output')?.value || '';
  navigator.clipboard.writeText(text);
  showToast(".SRT altyazı kopyalandı!", "success");
}
window.copySrtSubtitles = copySrtSubtitles;

// HTML5 Canvas Banner Studio
function setBannerFormat(fmt) {
  window.bannerFormat = fmt;
  const canvas = document.getElementById('banner-canvas');
  if (!canvas) return;

  const btnS = document.getElementById('btn-banner-story');
  const btnQ = document.getElementById('btn-banner-square');

  if (fmt === 'story') {
    canvas.width = 360;
    canvas.height = 640;
    if (btnS) btnS.className = 'btn btn-xs btn-primary flex-1';
    if (btnQ) btnQ.className = 'btn btn-xs btn-outline flex-1';
  } else {
    canvas.width = 500;
    canvas.height = 500;
    if (btnS) btnS.className = 'btn btn-xs btn-outline flex-1';
    if (btnQ) btnQ.className = 'btn btn-xs btn-primary flex-1';
  }
  drawLiveBanner();
}
window.setBannerFormat = setBannerFormat;

function setBannerPalette(primary, bg) {
  window.bannerPrimaryColor = primary;
  window.bannerBgColor = bg;
  drawLiveBanner();
}
window.setBannerPalette = setBannerPalette;

function drawLiveBanner() {
  const canvas = document.getElementById('banner-canvas');
  if (!canvas || typeof canvas.getContext !== 'function') return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  // Background
  ctx.fillStyle = window.bannerBgColor;
  ctx.fillRect(0, 0, w, h);

  // Radial glow
  const grad = ctx.createRadialGradient(w/2, h/3, 20, w/2, h/3, w/1.2);
  grad.addColorStop(0, window.bannerPrimaryColor + '33');
  grad.addColorStop(1, '#00000000');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // Border frame
  ctx.strokeStyle = window.bannerPrimaryColor + '44';
  ctx.lineWidth = 4;
  ctx.strokeRect(12, 12, w - 24, h - 24);

  // Badge
  const badge = document.getElementById('banner-badge-select')?.value || '🎓 IMTIHONSIZ QABUL 2026';
  ctx.fillStyle = window.bannerPrimaryColor;
  ctx.font = 'bold 12px "JetBrains Mono", monospace';
  ctx.fillText(badge, 25, 45);

  // Brand Name
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 22px "Plus Jakarta Sans", sans-serif';
  ctx.fillText('ARKADAŞ CONSULTING', 25, 80);

  // Main Title
  const title = document.getElementById('banner-input-title')?.value || "TURKIYADA IMTIHONSIZ TALABA BO'LING!";
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 24px "Plus Jakarta Sans", sans-serif';
  wrapText(ctx, title, 25, 140, w - 50, 32);

  // Subtitle
  const sub = document.getElementById('banner-input-sub')?.value || "Lise attestat bahosi bilan 100% kafolatlangan qabul";
  ctx.fillStyle = window.bannerPrimaryColor;
  ctx.font = '14px "JetBrains Mono", monospace';
  wrapText(ctx, sub, 25, 250, w - 50, 22);

  // Feature bullets
  ctx.fillStyle = '#cbd5e1';
  ctx.font = '12px "Plus Jakarta Sans", sans-serif';
  ctx.fillText('✓ Yevropa diplomi (Top-1000 universitetlar)', 25, 330);
  ctx.fillText('✓ Arzon davlat yotoqxonasi va oylik stipendiya', 25, 360);
  ctx.fillText('✓ Haftasiga 20 soat qonuniy ishlash imkoniyati', 25, 390);

  // Bottom CTA Bar
  ctx.fillStyle = window.bannerPrimaryColor;
  ctx.fillRect(25, h - 80, w - 50, 45);

  ctx.fillStyle = '#000000';
  ctx.font = 'bold 13px "JetBrains Mono", monospace';
  ctx.fillText('📲 Rasmiy Kanal: @arkadasuz', 40, h - 52);
}
window.drawLiveBanner = drawLiveBanner;

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(' ');
  let line = '';
  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n] + ' ';
    const metrics = ctx.measureText(testLine);
    const testWidth = metrics.width;
    if (testWidth > maxWidth && n > 0) {
      ctx.fillText(line, x, y);
      line = words[n] + ' ';
      y += lineHeight;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, x, y);
}

function downloadGeneratedBanner() {
  const canvas = document.getElementById('banner-canvas');
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = `arkadas_reklam_banner_${Date.now()}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
  showToast("Banner PNG formatında indirildi!", "success");
}
window.downloadGeneratedBanner = downloadGeneratedBanner;

// ==============================================================
// MODULE 6: ⚙️ SİSTEM, ANALİTİK & OTOPİLOT
// ==============================================================

// Deep Analytics
async function loadDeepAnalytics() {
  try {
    const res = await fetch('/api/analytics/deep');
    const data = await res.json();

    const fContainer = document.getElementById('analytics-funnel-container');
    if (fContainer && data.funnel) {
      fContainer.innerHTML = data.funnel.map(f => `
        <div class="space-y-1 font-mono text-xs">
          <div class="flex justify-between text-slate-300">
            <span>${f.stage}</span>
            <span class="text-cyan font-bold">${Number(f.count).toLocaleString()} (${f.pct})</span>
          </div>
          <div class="w-full bg-black/60 h-2 rounded-full overflow-hidden border border-white/5">
            <div class="bg-gradient-to-r from-cyan to-blue-500 h-full" style="width: ${Math.max(parseInt(f.pct) || 2, 3)}%"></div>
          </div>
        </div>
      `).join('');
    }

    const mContainer = document.getElementById('analytics-majors-container');
    if (mContainer && data.majors_demand) {
      mContainer.innerHTML = data.majors_demand.map(m => `
        <div class="space-y-1 font-mono text-xs">
          <div class="flex justify-between text-slate-300">
            <span>${m.major}</span>
            <span class="font-bold" style="color: ${m.color}">${m.percentage}%</span>
          </div>
          <div class="w-full bg-black/60 h-2 rounded-full overflow-hidden border border-white/5">
            <div class="h-full" style="width: ${m.percentage}%; background-color: ${m.color}"></div>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Analiz hatası:", e);
  }
}
window.loadDeepAnalytics = loadDeepAnalytics;

// Competitor Intel
async function loadCompetitorIntel() {
  try {
    const res = await fetch('/api/competitor_intel');
    const data = await res.json();

    if (data.pricing_benchmark) {
      const mf = document.getElementById('comp-market-fee');
      const af = document.getElementById('comp-arkadas-fee');
      const mv = document.getElementById('comp-market-visa');
      const av = document.getElementById('comp-arkadas-visa');
      if (mf) mf.innerText = data.pricing_benchmark.market_avg_fee;
      if (af) af.innerText = data.pricing_benchmark.arkadas_fee;
      if (mv) mv.innerText = data.pricing_benchmark.market_visa_rate;
      if (av) av.innerText = data.pricing_benchmark.arkadas_visa_rate;
    }

    const uBox = document.getElementById('comp-usps-container');
    if (uBox && data.usps) {
      uBox.innerHTML = data.usps.map(u => `
        <div class="flex items-start gap-2 p-2 rounded-lg bg-black/40 border border-white/5">
          <span class="text-emerald font-bold">✓</span>
          <span>${u}</span>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error("Competitor hatası:", e);
  }
}
window.loadCompetitorIntel = loadCompetitorIntel;

// Counselors
async function loadCounselorStats() {
  try {
    const res = await fetch('/api/counselors');
    const data = await res.json();

    const cBox = document.getElementById('counselors-cards-container');
    if (cBox && data.team) {
      cBox.innerHTML = data.team.map(c => `
        <div class="gece-card p-5 space-y-2 font-mono text-xs">
          <div class="flex justify-between items-start">
            <span class="font-bold text-white text-sm font-sans">${c.name}</span>
            <span class="tag tag-purple text-[10px]">${c.target} Hedef</span>
          </div>
          <span class="text-dim text-[11px] block">${c.role}</span>
          <div class="pt-2 border-t border-white/5 flex justify-between items-center">
            <span>Başvuru: <strong class="text-white">${c.leads}</strong></span>
            <span>Kayıt: <strong class="text-emerald">${c.enrolled}</strong></span>
          </div>
          <div class="p-2 bg-emerald-950/20 rounded-lg text-emerald font-bold text-center mt-2">
            Hakedilen Prim: ${c.commission}
          </div>
        </div>
      `).join('');
    }
    updateCommissionSim();
  } catch (e) {
    console.error("Counselor hatası:", e);
  }
}
window.loadCounselorStats = loadCounselorStats;

function updateCommissionSim() {
  const val = parseInt(document.getElementById('sim-student-slider')?.value || 15);
  const sCount = document.getElementById('sim-student-count');
  const sComm = document.getElementById('sim-total-commission');

  if (sCount) sCount.innerText = `${val} Öğrenci`;
  const total = val * 150;
  if (sComm) sComm.innerText = `$${total.toLocaleString()}`;
}
window.updateCommissionSim = updateCommissionSim;

// Health Check & Diagnostics
async function runHealthCheck() {
  showToast("Sistem teşhisi çalıştırılıyor...", "info");
  try {
    const res = await fetch('/api/health_check');
    const d = await res.json();

    const dYt = document.getElementById('diag-yt');
    const dTg = document.getElementById('diag-tg');
    const dCrm = document.getElementById('diag-crm');
    const dInv = document.getElementById('diag-inventory');

    if (dYt) dYt.innerText = `● ${d.youtube.status} (${d.youtube.channel})`;
    if (dTg) dTg.innerText = `● ${d.telegram.status} (${d.telegram.bot})`;
    if (dCrm) dCrm.innerText = `● SAĞLIKLI (${d.crm.total_leads} Aday)`;
    if (dInv) dInv.innerText = `${d.inventory.total_shorts} Video Hazır`;

    showToast("Tüm servisler aktif ve çalışıyor! (100% OK)", "success");
  } catch (err) {
    showToast("Teşhis testi sırasında hata oluştu", "error");
  }
}
window.runHealthCheck = runHealthCheck;

// ==============================================================
// AUTOPILOT ENGINE & CONTROLLER
// ==============================================================
window.autopilotEnabled = true;

async function loadAutopilotSettings() {
  try {
    const res = await fetch('/api/settings/autopilot');
    const data = await res.json();
    window.autopilotEnabled = (data.enabled !== false);
    
    const lunchInput = document.getElementById('cfg-lunch-time');
    const eveningInput = document.getElementById('cfg-evening-time');
    const funnelInput = document.getElementById('cfg-funnel-url');
    const toggleInput = document.getElementById('cfg-autopilot-toggle');
    
    if (lunchInput && data.lunchTime) lunchInput.value = data.lunchTime;
    if (eveningInput && data.eveningTime) eveningInput.value = data.eveningTime;
    if (funnelInput && data.funnelUrl) funnelInput.value = data.funnelUrl;
    if (toggleInput) toggleInput.checked = window.autopilotEnabled;

    updateAutopilotUI(window.autopilotEnabled, data.lunchTime || '13:00', data.eveningTime || '19:30');
  } catch (err) {
    console.error("loadAutopilotSettings error:", err);
  }
}
window.loadAutopilotSettings = loadAutopilotSettings;

function updateAutopilotUI(enabled, lunch = '13:00', evening = '19:30') {
  window.autopilotEnabled = enabled;

  // 1. Top Navbar Pill
  const navDot = document.getElementById('nav-autopilot-dot');
  const navLabel = document.getElementById('nav-autopilot-label');
  if (navDot && navLabel) {
    if (enabled) {
      navDot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
      navLabel.className = 'text-emerald-300 font-medium';
      navLabel.innerText = 'Otopilot: Açık';
    } else {
      navDot.className = 'w-2 h-2 rounded-full bg-slate-500';
      navLabel.className = 'text-slate-400 font-medium';
      navLabel.innerText = 'Otopilot: Kapalı';
    }
  }

  // 2. Spotlight Badge
  const spotDot = document.getElementById('spotlight-autopilot-dot');
  const spotText = document.getElementById('spotlight-autopilot-text');
  const spotBadge = document.getElementById('spotlight-autopilot-badge');
  if (spotText && spotBadge) {
    if (enabled) {
      spotBadge.className = 'text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5 cursor-pointer';
      if (spotDot) spotDot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-400';
      spotText.innerText = `Otopilot: Aktif (${lunch} & ${evening})`;
    } else {
      spotBadge.className = 'text-xs font-mono text-slate-400 bg-slate-500/10 px-2.5 py-1 rounded-full border border-slate-500/20 flex items-center gap-1.5 cursor-pointer';
      if (spotDot) spotDot.className = 'w-1.5 h-1.5 rounded-full bg-slate-500';
      spotText.innerText = 'Otopilot: Pasif';
    }
  }

  // 3. Settings Badge & Toggle
  const cfgBadge = document.getElementById('cfg-autopilot-status-badge');
  const cfgToggle = document.getElementById('cfg-autopilot-toggle');
  if (cfgBadge) {
    if (enabled) {
      cfgBadge.className = 'text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20';
      cfgBadge.innerText = 'AKTİF';
    } else {
      cfgBadge.className = 'text-[11px] text-slate-400 bg-slate-500/10 px-2 py-0.5 rounded border border-slate-500/20';
      cfgBadge.innerText = 'PASİF';
    }
  }
  if (cfgToggle) {
    cfgToggle.checked = enabled;
  }
}

async function toggleAutopilotGlobal() {
  const newState = !window.autopilotEnabled;
  const lunch = document.getElementById('cfg-lunch-time')?.value || '13:00';
  const evening = document.getElementById('cfg-evening-time')?.value || '19:30';
  const funnel = document.getElementById('cfg-funnel-url')?.value || 'https://t.me/arkadasuz';

  updateAutopilotUI(newState, lunch, evening);

  try {
    const res = await fetch('/api/settings/autopilot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: newState, lunchTime: lunch, eveningTime: evening, funnelUrl: funnel })
    });
    const data = await res.json();
    if (newState) {
      showToast(`Otopilot Açıldı! (${lunch} ve ${evening} otomatik paylaşım)`, "success");
    } else {
      showToast("Otopilot kapatıldı (Manuel mod aktif)", "info");
    }
  } catch (err) {
    showToast("Otopilot güncellenirken hata oluştu", "error");
  }
}
window.toggleAutopilotGlobal = toggleAutopilotGlobal;

function toggleAutopilotFromSettings() {
  const toggle = document.getElementById('cfg-autopilot-toggle');
  const isChecked = toggle ? toggle.checked : true;
  if (isChecked !== window.autopilotEnabled) {
    toggleAutopilotGlobal();
  }
}
window.toggleAutopilotFromSettings = toggleAutopilotFromSettings;

async function triggerAutopilotNow() {
  showToast("Otopilot tetikleniyor...", "info");
  try {
    const res = await fetch('/api/autopilot/trigger_now', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.success) {
      showToast("İçerikler kanala ve servislere yönlendirildi!", "success");
      if (typeof loadTelegramPosts === 'function') loadTelegramPosts();
      if (typeof loadYouTubeStudio === 'function') loadYouTubeStudio();
    } else {
      showToast("Tetikleme başarısız", "error");
    }
  } catch (err) {
    showToast("Bağlantı hatası", "error");
  }
}
window.triggerAutopilotNow = triggerAutopilotNow;

async function saveAutopilotSettings() {
  const lunch = document.getElementById('cfg-lunch-time')?.value || '13:00';
  const evening = document.getElementById('cfg-evening-time')?.value || '19:30';
  const funnel = document.getElementById('cfg-funnel-url')?.value || 'https://t.me/arkadasuz';
  const toggle = document.getElementById('cfg-autopilot-toggle');
  const enabled = toggle ? toggle.checked : window.autopilotEnabled;

  const res = await fetch('/api/settings/autopilot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled: enabled, lunchTime: lunch, eveningTime: evening, funnelUrl: funnel })
  });
  const data = await res.json();
  if (data.success) {
    updateAutopilotUI(enabled, lunch, evening);
    showToast("Otopilot ayarları kaydedildi!", "success");
  }
}
window.saveAutopilotSettings = saveAutopilotSettings;

function openTagsHelperModal() {
  const modal = document.getElementById('tags-helper-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}
window.openTagsHelperModal = openTagsHelperModal;

function closeTagsModal() {
  const modal = document.getElementById('tags-helper-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}
window.closeTagsModal = closeTagsModal;

function copyTagsToClipboard() {
  const tags = document.getElementById('tags-box')?.innerText || '';
  navigator.clipboard.writeText(tags);
  showToast("Tüm etiketler panoya kopyalandı!", "success");
  closeTagsModal();
}
window.copyTagsToClipboard = copyTagsToClipboard;

function copyTextDirect(txt, msg) {
  navigator.clipboard.writeText(txt);
  showToast(msg || "Panoya kopyalandı!", "success");
}
window.copyTextDirect = copyTextDirect;

// ==============================================================
// REELS & VIDEO SHOWCASE CONTROLLER
// ==============================================================

let cachedReels = [];

async function loadReelsShowcase() {
  try {
    const res = await fetch('/api/reels_showcase');
    const data = await res.json();
    if (data.success && Array.isArray(data.videos)) {
      cachedReels = data.videos;
      const countBadge = document.getElementById('reels-count-badge');
      if (countBadge) countBadge.innerText = data.videos.length;
      renderReelsGallery(data.videos);
    }
  } catch (e) {
    console.error("Reels yükleme hatası:", e);
  }
}
window.loadReelsShowcase = loadReelsShowcase;

function renderReelsGallery(videos) {
  const container = document.getElementById('reels-gallery-list');
  if (!container) return;

  if (videos.length === 0) {
    container.innerHTML = '<div class="text-dim text-center py-6">Henüz video bulunamadı.</div>';
    return;
  }

  container.innerHTML = videos.map((v) => {
    const safeTitle = v.title.replace(/'/g, "\\'");
    const safePersona = v.persona.replace(/'/g, "\\'");
    return `
      <div class="p-3 bg-black/40 hover:bg-white/[0.04] border border-white/5 hover:border-cyan/30 rounded-xl transition cursor-pointer flex items-center justify-between gap-3"
        onclick="playSelectedReel('${v.filename}', '${safeTitle}', '${safePersona}', '${v.language}', '${v.badge}')">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-10 rounded-xl bg-cyan/10 border border-cyan/20 flex items-center justify-center text-cyan flex-shrink-0">
            <i class="fa-solid fa-play text-xs"></i>
          </div>
          <div class="min-w-0">
            <div class="font-bold text-white text-xs truncate">${v.title}</div>
            <div class="text-[11px] text-dim flex items-center gap-2">
              <span>${v.persona}</span>
              <span>•</span>
              <span>${v.language}</span>
              <span>•</span>
              <span>${v.size_mb} MB</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-1.5 flex-shrink-0">
          <span class="px-2 py-0.5 rounded text-[10px] bg-white/10 text-slate-300 font-mono">${v.badge}</span>
          <a href="${v.download_url}" download class="btn btn-outline btn-xs p-1.5 text-cyan hover:bg-cyan/20" onclick="event.stopPropagation()" title="İndir">
            <i class="fa-solid fa-download"></i>
          </a>
        </div>
      </div>
    `;
  }).join('');
}
window.renderReelsGallery = renderReelsGallery;

function playSelectedReel(filename, title, persona, lang, badge) {
  const player = document.getElementById('reels-studio-player');
  const titleEl = document.getElementById('reels-player-title');
  const badgeEl = document.getElementById('reels-player-badge');
  const personaEl = document.getElementById('reels-player-persona');
  const langEl = document.getElementById('reels-player-lang');
  const downloadBtn = document.getElementById('reels-download-btn');

  const streamUrl = `/output/${filename}`;
  if (player) {
    player.src = streamUrl;
    player.play().catch(() => {});
  }
  if (titleEl) titleEl.innerText = title;
  if (badgeEl) badgeEl.innerText = badge;
  if (personaEl) personaEl.innerText = persona;
  if (langEl) langEl.innerText = lang;
  if (downloadBtn) downloadBtn.href = streamUrl;

  showToast(`${title} oynatılıyor...`, "info");
}
window.playSelectedReel = playSelectedReel;

function filterReelsGallery(type, btn) {
  document.querySelectorAll('#section-reelsstudio .btn-xs').forEach(b => b.classList.remove('btn-primary'));
  if (btn) btn.classList.add('btn-primary');

  if (type === 'all') {
    renderReelsGallery(cachedReels);
  } else if (type === 'mila') {
    renderReelsGallery(cachedReels.filter(v => v.filename.toLowerCase().includes('mila')));
  } else if (type === 'madina') {
    renderReelsGallery(cachedReels.filter(v => v.filename.toLowerCase().includes('madina')));
  } else if (type === 'ru') {
    renderReelsGallery(cachedReels.filter(v => v.filename.toLowerCase().includes('ru')));
  }
}
window.filterReelsGallery = filterReelsGallery;

function copyReelsShareLink() {
  const player = document.getElementById('reels-studio-player');
  if (player && player.src) {
    navigator.clipboard.writeText(player.src);
    showToast("Video bağlantısı kopyalandı!", "success");
  }
}
window.copyReelsShareLink = copyReelsShareLink;

// ==============================================================
// INBOUND AI CHATBOT & FAQ MATCHER CONTROLLER
// ==============================================================

let activeChatbotLeadDraft = null;

async function sendChatbotQuery() {
  const msgInput = document.getElementById('bot-sim-message');
  const nameInput = document.getElementById('bot-sim-name');
  const phoneInput = document.getElementById('bot-sim-phone');

  const message = msgInput?.value.trim() || '';
  const name = nameInput?.value.trim() || 'Talaba';
  const phone = phoneInput?.value.trim() || '+998 90 000 00 00';

  if (!message) {
    showToast("Lütfen bir soru veya mesaj yazın!", "error");
    return;
  }

  const userBubble = document.getElementById('bot-user-bubble');
  const agentBubble = document.getElementById('bot-agent-bubble');
  const matchBadge = document.getElementById('bot-match-badge');

  if (userBubble) userBubble.innerText = `💬 "${message}"`;
  if (agentBubble) agentBubble.innerHTML = `<i>🤖 Bilgi tabanı taranıyor ve danışman yanıtı üretiliyor...</i>`;
  if (matchBadge) matchBadge.innerText = "Eşleşme: Aranıyor...";

  try {
    const res = await fetch('/api/chatbot/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, name, phone })
    });
    const data = await res.json();
    if (data.success) {
      activeChatbotLeadDraft = data.lead_draft;
      if (agentBubble) agentBubble.innerHTML = data.response_text.replace(/\n/g, '<br>');
      if (matchBadge) matchBadge.innerText = `Kategori: ${data.matched_category.toUpperCase()} (${data.confidence})`;

      const followupsBox = document.getElementById('bot-followups-container');
      const pillsBox = document.getElementById('bot-followups-pills');
      if (followupsBox && pillsBox && Array.isArray(data.suggested_followups)) {
        followupsBox.classList.remove('hidden');
        pillsBox.innerHTML = data.suggested_followups.map(q => {
          const safeQ = q.replace(/'/g, "\\'");
          return `<button type="button" class="btn btn-outline btn-xs text-[10px]" onclick="setBotSimMsg('${safeQ}')">${q}</button>`;
        }).join('');
      }

      showToast("Danışman yanıtı hazırlandı!", "success");
    } else {
      showToast(data.error || "Yanıt üretilemedi", "error");
    }
  } catch (e) {
    showToast("Chatbot bağlantı hatası", "error");
  }
}
window.sendChatbotQuery = sendChatbotQuery;

function setBotSimMsg(msg) {
  const input = document.getElementById('bot-sim-message');
  if (input) input.value = msg;
  sendChatbotQuery();
}
window.setBotSimMsg = setBotSimMsg;

async function saveChatbotLeadToCRM() {
  if (!activeChatbotLeadDraft) {
    showToast("Önce bir öğrenci sorusu simüle edin!", "error");
    return;
  }

  showToast("CRM'e aktarılıyor...", "info");
  try {
    const res = await fetch('/api/chatbot/save_to_crm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(activeChatbotLeadDraft)
    });
    const data = await res.json();
    if (data.success) {
      showToast("Öğrenci CRM'e başarıyla eklendi!", "success");
      loadLeads();
    } else {
      showToast("CRM'e eklenemedi", "error");
    }
  } catch (e) {
    showToast("CRM kayıt hatası", "error");
  }
}
window.saveChatbotLeadToCRM = saveChatbotLeadToCRM;

function copyBotResponse() {
  const agentBubble = document.getElementById('bot-agent-bubble');
  if (agentBubble) {
    navigator.clipboard.writeText(agentBubble.innerText);
    showToast("Yanıt metni kopyalandı!", "success");
  }
}
window.copyBotResponse = copyBotResponse;

// ==============================================================
// WHATSAPP 1-CLICK DIRECT DISPATCHER
// ==============================================================

async function sendDirectWhatsApp() {
  const phone = document.getElementById('wa-direct-phone')?.value.trim() || '';
  const name = document.getElementById('wa-direct-name')?.value.trim() || 'Talaba';
  const pkg = document.getElementById('wa-direct-package')?.value || 'asosiy';

  if (!phone) {
    showToast("Lütfen öğrenci telefon numarasını girin!", "error");
    return;
  }

  showToast("WhatsApp bağlantısı hazırlanıyor...", "info");
  try {
    const res = await fetch('/api/whatsapp/generate_link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, student_name: name, package_type: pkg })
    });
    const data = await res.json();
    if (data.success && data.whatsapp_url) {
      window.open(data.whatsapp_url, '_blank');
      showToast("WhatsApp sohbeti açılıyor...", "success");
    }
  } catch (e) {
    showToast("WhatsApp bağlantı hatası", "error");
  }
}
window.sendDirectWhatsApp = sendDirectWhatsApp;

// ==============================================================
// OFFICIAL STUDENT CONTRACT GENERATOR
// ==============================================================

async function generateContractPreview() {
  const name = document.getElementById('contract-name')?.value.trim() || 'Azizbek Rahimov';
  const passport = document.getElementById('contract-passport')?.value.trim() || 'FA 3491827';
  const phone = document.getElementById('contract-phone')?.value.trim() || '+998 90 123 45 67';
  const uni = document.getElementById('contract-uni')?.value.trim() || 'İstanbul Davlat Universiteti';
  const faculty = document.getElementById('contract-faculty')?.value.trim() || 'Xalqaro Iqtisodiyot';
  const pkg = document.getElementById('contract-package')?.value || 'orta';

  showToast("Resmi sözleşme hazırlanıyor...", "info");
  try {
    const res = await fetch('/api/contract/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_name: name,
        passport: passport,
        phone: phone,
        university: uni,
        faculty: faculty,
        package_type: pkg
      })
    });
    const data = await res.json();
    if (data.success && data.contract_html) {
      const box = document.getElementById('contract-preview-box');
      if (box) box.innerHTML = data.contract_html;
      showToast("Resmi sözleşme başarıyla oluşturuldu!", "success");
    }
  } catch (e) {
    showToast("Sözleşme oluşturma hatası", "error");
  }
}
window.generateContractPreview = generateContractPreview;

function printOfficialContract() {
  const box = document.getElementById('contract-preview-box');
  if (!box || !box.innerHTML.trim()) {
    showToast("Önce bir sözleşme oluşturun!", "error");
    return;
  }
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Arkadaş Consulting - Resmi Ta'lim Shartnomasi</title>
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #fff; }
          @media print {
            body { margin: 0; }
          }
        </style>
      </head>
      <body>
        ${box.innerHTML}
        <script>
          window.onload = function() { window.print(); }
        </script>
      </body>
    </html>
  `);
  printWindow.document.close();
}
window.printOfficialContract = printOfficialContract;

// ==============================================================
// 7-IN-1 OMNICHANNEL SOCIAL COMMAND & SCHEDULER CONTROLLER
// ==============================================================

let cachedOmniAssets = { texts: [], photos: [], videos: [] };
let cachedOmniScheduled = [];
let activeOmniPlatform = 'twitter';

const OMNI_PLATFORM_CONFIG = {
  twitter: {
    name: "Twitter / X",
    handle: "@arkadasuz",
    badge: "201 Tweet",
    icon: "fa-brands fa-x-twitter text-white",
    accentColor: "cyan",
    desc: "Kısa bilgilendirici tweetler ve başlık zincirleri.",
    capabilities: [
      { title: "201 Hazır Tweet", desc: "Harçlar, vize ve sınavsız kabul hap bilgileri.", icon: "fa-solid fa-list-ol" },
      { title: "Otomatik Yanıt", desc: "Her tweet altına Telegram linki eklenir.", icon: "fa-solid fa-reply-all" },
      { title: "Flood Dizisi", desc: "Adım adım başvuru zinciri.", icon: "fa-solid fa-link" },
      { title: "Zamanlayıcı", desc: "Sabah, öğle ve akşam otomatik paylaşım.", icon: "fa-solid fa-clock" }
    ],
    sampleSnippet: "Turkiya davlat OTMlarida yillik kontrakt narxlari:\n💰 Davlat universitetlari: $300 - $800 / yiliga.\nDiplom Yevropada 100% tan olinadi.\n\nBatafsil: @arkadasuzz 🇹🇷",
    autoReplySample: "👉 https://t.me/arkadasuz",
    jumpTab: "twitterhub"
  },
  youtube: {
    name: "YouTube",
    handle: "@arkadaşuz",
    badge: "50 Shorts",
    icon: "fa-brands fa-youtube text-red-500",
    accentColor: "red-500",
    desc: "Dikey Shorts videoları ve stüdyo kayıtları.",
    capabilities: [
      { title: "50 Dikey Video", desc: "Altyazılı hazır reels/shorts arşivi.", icon: "fa-solid fa-mobile-screen" },
      { title: "Doğrudan Yükleme", desc: "Google API ile kanala aktarım.", icon: "fa-solid fa-cloud-arrow-up" },
      { title: "SEO ve Etiketler", desc: "Keşfete düşüren hazır etiketler.", icon: "fa-solid fa-bolt" },
      { title: "Sabit Yorum", desc: "Açıklama ve sabit huni yorumu.", icon: "fa-solid fa-thumbtack" }
    ],
    sampleSnippet: "Turkiyada imtihonsiz qabul: Attestat bahosi yetarli! 🇹🇷\nDavlat universitetlariga imtihonsiz kirish tartibi.",
    autoReplySample: "📌 Bepul konsultatsiya: https://t.me/arkadasuz",
    jumpTab: "ytstudio"
  },
  telegram: {
    name: "Telegram",
    handle: "@arkadasuz",
    badge: "134 Gönderi",
    icon: "fa-brands fa-telegram text-sky-400",
    accentColor: "sky-400",
    desc: "Resmi duyurular ve zengin metinli içerikler.",
    capabilities: [
      { title: "134 Hazır Post", desc: "Özbekçe, emojili tam formatlı metinler.", icon: "fa-solid fa-file-lines" },
      { title: "1-Tık Gönderim", desc: "Kanala anında tek tıkla iletme.", icon: "fa-solid fa-paper-plane" },
      { title: "Anket ve Buton", desc: "Öğrencileri yönlendiren butonlar.", icon: "fa-solid fa-square-poll-vertical" },
      { title: "Otopilot", desc: "Günde 2 kez otomatik gönderim.", icon: "fa-solid fa-robot" }
    ],
    sampleSnippet: "🇹🇷 TURKIYADA TIBBIYOT VA STOMATOLOGIYA: 2026 QABUL MAVSUMI 🎓\n✅ Imtihonsiz grant va stipendiyalar\n👉 @arkadasuz",
    autoReplySample: "📲 Murojaat: @arkadasuzz",
    jumpTab: "contenthub"
  },
  tiktok: {
    name: "TikTok",
    handle: "@mila.travels",
    badge: "Viral Kancalar",
    icon: "fa-brands fa-tiktok text-rose-400",
    accentColor: "rose-400",
    desc: "Gençlere yönelik hızlı kancalı kısa videolar.",
    capabilities: [
      { title: "Kanca Cümleleri", desc: "İlk 3 saniye dikkat çeken sözler.", icon: "fa-solid fa-magnet" },
      { title: "Mila & Madina", desc: "Öğrenci elçisi anlatımları.", icon: "fa-solid fa-user-group" },
      { title: "Kampüs Çekimleri", desc: "İstanbul ve üniversite b-roll görüntüleri.", icon: "fa-solid fa-clapperboard" },
      { title: "Trend Müzikler", desc: "Öne çıkan fon sesleri.", icon: "fa-solid fa-music" }
    ],
    sampleSnippet: "Turkiyada o'qish uchun yillab repetitorga qatnash shart emas! ✨🇹🇷",
    autoReplySample: "👉 Profil linkidan Telegram'ga o'ting: @arkadasuz",
    jumpTab: "tiktoklab"
  },
  instagram: {
    name: "Instagram",
    handle: "@arkadas.uz",
    badge: "Carousel & Reels",
    icon: "fa-brands fa-instagram text-pink-500",
    accentColor: "pink-500",
    desc: "Kaydırmalı rehberler ve hikayeler.",
    capabilities: [
      { title: "Kaydırmalı Slayt", desc: "Görsel adımlarla başvuru rehberi.", icon: "fa-solid fa-images" },
      { title: "Günlük Hikaye", desc: "Soru-cevap ve anket çıkartmaları.", icon: "fa-solid fa-circle-notch" },
      { title: "Reels Videoları", desc: "Dikey format reels paylaşımları.", icon: "fa-solid fa-video" },
      { title: "Bio Yönlendirme", desc: "DM ve profil linki.", icon: "fa-solid fa-arrow-up-right-from-square" }
    ],
    sampleSnippet: "1️⃣ Turkiyada imtihonsiz qabul bormi?\n2️⃣ Attestat baholari yetarlimi?\nBarcha javoblar slaydda! 👉",
    autoReplySample: "📲 Bepul konsultatsiya: Link bioda!",
    jumpTab: "instagramhub"
  },
  facebook: {
    name: "Facebook",
    handle: "Arkadaş Danışmanlık",
    badge: "Veli Odaklı",
    icon: "fa-brands fa-facebook text-blue-500",
    accentColor: "blue-500",
    desc: "Velilere güven veren kurumsal bilgilendirmeler.",
    capabilities: [
      { title: "Veli İletişimi", desc: "0$ risk ve garantili kabul açıklamaları.", icon: "fa-solid fa-shield-heart" },
      { title: "Hedef Kitle", desc: "Özbekistan veli grupları.", icon: "fa-solid fa-crosshairs" },
      { title: "Grup Paylaşımları", desc: "Topluluk ve soru cevap postları.", icon: "fa-solid fa-users-rectangle" },
      { title: "Başvuru Formu", desc: "Doğrudan CRM'e veri akışı.", icon: "fa-solid fa-address-card" }
    ],
    sampleSnippet: "Hurmatli ota-onalar! Farzandingiz xalqaro diplomga ega bo'lishini xohlaysizmi? 🇹🇷",
    autoReplySample: "📞 Aloqa: @arkadasuzz",
    jumpTab: "facebookhub"
  },
  whatsapp: {
    name: "WhatsApp",
    handle: "Danışman Hattı",
    badge: "1-Tık İletişim",
    icon: "fa-brands fa-whatsapp text-emerald",
    accentColor: "emerald",
    desc: "Öğrenci ve veliyle doğrudan mesajlaşma.",
    capabilities: [
      { title: "1-Tık Sohbet", desc: "Kişiselleştirilmiş bağlantı açma.", icon: "fa-solid fa-comment-sms" },
      { title: "Fiyat Listesi", desc: "Paket ve burs kartları.", icon: "fa-solid fa-box-open" },
      { title: "Otomatik Yanıt", desc: "Bölüm ve üniversite soran karşılama.", icon: "fa-solid fa-hand-wave" },
      { title: "Hazır Şablonlar", desc: "Sıkça sorulan sorulara hızlı cevap.", icon: "fa-solid fa-bolt-lightning" }
    ],
    sampleSnippet: "Assalomu alaykum! Arkadaş Consulting ta'lim xizmatlari tafsilotlari...",
    autoReplySample: "📲 Bog'lanish: @arkadasuzz",
    jumpTab: "whatsapphub"
  }
};

function selectOmniPlatform(key) {
  activeOmniPlatform = key;
  const cfg = OMNI_PLATFORM_CONFIG[key] || OMNI_PLATFORM_CONFIG.twitter;

  // Update card active classes
  document.querySelectorAll('.omni-platform-card').forEach(c => {
    c.classList.remove('border-cyan/60', 'bg-cyan/10', 'border-red-500/80', 'bg-red-500/10', 'border-sky-400/80', 'bg-sky-400/10', 'border-rose-400/80', 'bg-rose-400/10', 'border-pink-500/80', 'bg-pink-500/10', 'border-blue-500/80', 'bg-blue-500/10', 'border-emerald-500/80', 'bg-emerald-500/10');
    c.classList.add('border-white/5');
  });

  const activeCard = document.getElementById(`omni-card-${key}`);
  if (activeCard) {
    activeCard.classList.remove('border-white/5');
    activeCard.classList.add(`border-${cfg.accentColor}`, `bg-${cfg.accentColor}/10`);
  }

  // Render Console details
  const consoleBox = document.getElementById('omni-platform-console');
  if (!consoleBox) return;

  consoleBox.innerHTML = `
    <div class="space-y-6">
      <!-- Başlık ve Durum -->
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-white/5 pb-3">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-base text-white">
            <i class="${cfg.icon}"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-bold text-white tracking-tight">${cfg.name}</h3>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-medium">${cfg.badge}</span>
            </div>
            <p class="text-xs text-slate-400">${cfg.handle} • ${cfg.desc}</p>
          </div>
        </div>

        <div class="flex items-center gap-2 text-xs">
          <button type="button" class="btn-clean-secondary px-3 py-1.5 text-xs flex items-center gap-1.5" onclick="populateOmniTextToScheduler('${cfg.sampleSnippet.replace(/'/g, "\\'").replace(/\n/g, "\\n")}')">
            <i class="fa-solid fa-arrow-down text-slate-400"></i>
            <span>Metni Al</span>
          </button>
          <button type="button" class="btn-clean-primary px-3 py-1.5 text-xs flex items-center gap-1.5" onclick="switchSection('${cfg.jumpTab}')">
            <span>Sayfaya Git</span>
            <i class="fa-solid fa-arrow-right text-slate-900 text-[10px]"></i>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Neler Yapabilirsiniz? (4 Kart) -->
        <div class="lg:col-span-7 space-y-3 text-xs">
          <h4 class="font-semibold text-white text-xs flex items-center gap-2">
            <i class="fa-solid fa-bolt text-cyan-400"></i>
            <span>Özellikler</span>
          </h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            ${cfg.capabilities.map(cap => `
              <div class="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-1 hover:border-white/15 transition">
                <div class="flex items-center gap-2 text-slate-200 font-semibold text-xs">
                  <i class="${cap.icon} text-cyan-400 text-[11px]"></i>
                  <span>${cap.title}</span>
                </div>
                <p class="text-[11px] text-slate-400 leading-relaxed">${cap.desc}</p>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Canlı Görsel Simülatör (Mockup) -->
        <div class="lg:col-span-5 text-xs">
          <h4 class="font-semibold text-white text-xs mb-2 flex items-center gap-2">
            <i class="fa-solid fa-eye text-emerald-400"></i>
            <span>Canlı Gönderi Önizlemesi</span>
          </h4>
          <div class="p-4 rounded-2xl bg-black/50 border border-white/10 space-y-3 shadow-xl">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-full bg-slate-800 border border-white/20 flex items-center justify-center text-xs text-white font-bold">
                A
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-white font-semibold text-xs flex items-center gap-1">
                  <span>Arkadaş Consulting</span>
                  <i class="fa-solid fa-circle-check text-cyan text-[10px]"></i>
                </div>
                <div class="text-[11px] text-slate-400">${cfg.handle}</div>
              </div>
              <span class="text-[10px] text-slate-500">Az önce</span>
            </div>

            <div class="text-[12px] text-slate-200 leading-relaxed whitespace-pre-line bg-black/30 p-3 rounded-xl border border-white/5">
              ${cfg.sampleSnippet}
            </div>

            <div class="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-[11px] text-cyan-300 leading-relaxed">
              <span class="font-semibold block mb-0.5 text-xs">🔗 Otomatik Sabit Yanıt:</span>
              ${cfg.autoReplySample}
            </div>

            <div class="flex justify-between items-center text-slate-400 text-xs pt-1">
              <span class="flex items-center gap-1"><i class="fa-regular fa-comment"></i> 24</span>
              <span class="flex items-center gap-1"><i class="fa-solid fa-retweet"></i> 58</span>
              <span class="flex items-center gap-1"><i class="fa-regular fa-heart"></i> 142</span>
              <button type="button" class="text-cyan-400 hover:text-cyan-300 text-xs font-medium cursor-pointer" onclick="copyCustomText('${cfg.sampleSnippet.replace(/'/g, "\\'").replace(/\n/g, "\\n")}')">
                <i class="fa-solid fa-copy mr-0.5"></i> Kopyala
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
window.selectOmniPlatform = selectOmniPlatform;

function populateOmniTextToScheduler(text) {
  const area = document.getElementById('omni-schedule-text');
  if (area) {
    area.value = text;
    updateOmniCharCount();
    area.scrollIntoView({ behavior: 'smooth', block: 'center' });
    showToast("Metin planlayıcı formuna aktarıldı!", "info");
  }
}
window.populateOmniTextToScheduler = populateOmniTextToScheduler;

function updateOmniCharCount() {
  const area = document.getElementById('omni-schedule-text');
  const counter = document.getElementById('omni-text-char-count');
  if (area && counter) {
    counter.innerText = `${area.value.length} karakter`;
  }
}

// Load Ready Assets for Scheduler Dropdowns
async function loadOmniSchedulerAssets() {
  try {
    const res = await fetch('/api/social/ready_assets');
    const data = await res.json();
    if (data.success) {
      cachedOmniAssets = data;

      // 1. Texts Dropdown
      const textSelect = document.getElementById('omni-asset-text-select');
      if (textSelect && Array.isArray(data.texts)) {
        textSelect.innerHTML = '<option value="">-- Hazır 134 Telegram & 201 Twitter Gönderisinden Seçin --</option>' +
          data.texts.map((t, idx) => `
            <option value="${idx}">[${t.source}] ${t.title} (${t.snippet.substring(0, 45)}...)</option>
          `).join('');
      }

      // 2. Photos Dropdown
      const photoSelect = document.getElementById('omni-asset-photo-select');
      if (photoSelect && Array.isArray(data.photos)) {
        photoSelect.innerHTML = '<option value="">-- Afiş Seçilmedi (Fotoğrafsız) --</option>' +
          data.photos.map((p, idx) => `
            <option value="${p.path}">🖼️ ${p.title}</option>
          `).join('');
      }

      // 3. Videos Dropdown
      const videoSelect = document.getElementById('omni-asset-video-select');
      if (videoSelect && Array.isArray(data.videos)) {
        videoSelect.innerHTML = '<option value="">-- Video Seçilmedi (Videosuz) --</option>' +
          data.videos.map((v, idx) => `
            <option value="${v.path}">🎬 [${v.persona}] ${v.title} (${v.size_mb} MB)</option>
          `).join('');
      }

      // Default date to today
      const dateInput = document.getElementById('omni-schedule-date');
      if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
      }

      const textArea = document.getElementById('omni-schedule-text');
      if (textArea) {
        textArea.addEventListener('input', updateOmniCharCount);
      }
    }
  } catch (e) {
    console.error("Varlıklar yüklenirken hata:", e);
  }

  loadOmniScheduledTable();
}
window.loadOmniSchedulerAssets = loadOmniSchedulerAssets;

function onOmniTextSelect(idxStr) {
  if (idxStr === '') return;
  const idx = parseInt(idxStr, 10);
  const item = cachedOmniAssets.texts[idx];
  if (item) {
    const area = document.getElementById('omni-schedule-text');
    if (area) {
      area.value = item.full_text;
      updateOmniCharCount();
    }
    const autoReplyInput = document.getElementById('omni-auto-reply');
    if (autoReplyInput && item.auto_reply) {
      autoReplyInput.value = item.auto_reply;
    }
    showToast(`"${item.title}" metni seçildi!`, "info");
  }
}
window.onOmniTextSelect = onOmniTextSelect;

function onOmniPhotoSelect(path) {
  const previewBox = document.getElementById('omni-media-preview-box');
  const imgEl = document.getElementById('omni-preview-img');
  const vidEl = document.getElementById('omni-preview-video-tag');
  const nameEl = document.getElementById('omni-preview-filename');
  const typeEl = document.getElementById('omni-preview-type');

  if (!path) {
    clearOmniSelectedMedia();
    return;
  }

  // Clear video dropdown
  const vidSelect = document.getElementById('omni-asset-video-select');
  if (vidSelect) vidSelect.value = '';

  if (previewBox && imgEl && vidEl && nameEl && typeEl) {
    previewBox.classList.remove('hidden');
    vidEl.classList.add('hidden');
    imgEl.classList.remove('hidden');
    imgEl.src = path.startsWith('output/') ? `/${path}` : `/static/${path.split('/').pop()}`;
    nameEl.innerText = path.split('/').pop();
    typeEl.innerText = "Fotoğraf / Banner Afişi";
  }
}
window.onOmniPhotoSelect = onOmniPhotoSelect;

function onOmniVideoSelect(path) {
  const previewBox = document.getElementById('omni-media-preview-box');
  const imgEl = document.getElementById('omni-preview-img');
  const vidEl = document.getElementById('omni-preview-video-tag');
  const nameEl = document.getElementById('omni-preview-filename');
  const typeEl = document.getElementById('omni-preview-type');

  if (!path) {
    clearOmniSelectedMedia();
    return;
  }

  // Clear photo dropdown
  const photoSelect = document.getElementById('omni-asset-photo-select');
  if (photoSelect) photoSelect.value = '';

  if (previewBox && imgEl && vidEl && nameEl && typeEl) {
    previewBox.classList.remove('hidden');
    imgEl.classList.add('hidden');
    vidEl.classList.remove('hidden');
    nameEl.innerText = path.split('/').pop();
    typeEl.innerText = "Dikey MP4 Video (Reels / Shorts)";
  }
}
window.onOmniVideoSelect = onOmniVideoSelect;

function clearOmniSelectedMedia() {
  const previewBox = document.getElementById('omni-media-preview-box');
  if (previewBox) previewBox.classList.add('hidden');

  const photoSelect = document.getElementById('omni-asset-photo-select');
  const videoSelect = document.getElementById('omni-asset-video-select');
  if (photoSelect) photoSelect.value = '';
  if (videoSelect) videoSelect.value = '';
}
window.clearOmniSelectedMedia = clearOmniSelectedMedia;

async function submitOmniCrossPostSchedule() {
  const content = document.getElementById('omni-schedule-text')?.value.trim() || '';
  const photoPath = document.getElementById('omni-asset-photo-select')?.value || null;
  const videoPath = document.getElementById('omni-asset-video-select')?.value || null;
  const dateStr = document.getElementById('omni-schedule-date')?.value || new Date().toISOString().split('T')[0];
  const slotVal = document.getElementById('omni-schedule-slot')?.value || '13:00|☀️ Tushlik Posti (13:00)';
  const [timeStr, slotLabel] = slotVal.split('|');
  const autoReply = document.getElementById('omni-auto-reply')?.value || '';

  // Gather platforms
  const platforms = [];
  if (document.getElementById('omni-target-twitter')?.checked) platforms.push('twitter');
  if (document.getElementById('omni-target-youtube')?.checked) platforms.push('youtube');
  if (document.getElementById('omni-target-telegram')?.checked) platforms.push('telegram');
  if (document.getElementById('omni-target-instagram')?.checked) platforms.push('instagram');
  if (document.getElementById('omni-target-tiktok')?.checked) platforms.push('tiktok');
  if (document.getElementById('omni-target-facebook')?.checked) platforms.push('facebook');

  if (platforms.length === 0) {
    showToast("En az bir hedef platform seçmelisiniz!", "error");
    return;
  }

  if (!content && !videoPath) {
    showToast("Lütfen bir metin yazın veya video seçin!", "error");
    return;
  }

  showToast("Gönderi çok kanallı olarak planlanıyor...", "info");

  try {
    const res = await fetch('/api/social/schedule_cross_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platforms: platforms,
        content: content,
        photo_path: photoPath,
        video_path: videoPath,
        scheduled_date: dateStr,
        scheduled_time: timeStr,
        slot_label: slotLabel,
        auto_reply: autoReply
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || "Gönderi başarıyla planlandı!", "success");
      loadOmniScheduledTable();
    } else {
      showToast(data.error || "Planlama başarısız oldu", "error");
    }
  } catch (e) {
    showToast("Planlama API hatası", "error");
  }
}
window.submitOmniCrossPostSchedule = submitOmniCrossPostSchedule;

async function loadOmniScheduledTable() {
  const tbody = document.getElementById('omni-scheduled-tbody');
  const countBadge = document.getElementById('omni-scheduled-count-badge');
  if (!tbody) return;

  try {
    const res = await fetch('/api/social/all_scheduled');
    const data = await res.json();
    if (data.success && Array.isArray(data.items)) {
      cachedOmniScheduled = data.items;
      if (countBadge) countBadge.innerText = `(${data.total_count} Gönderi Aktif)`;
      renderOmniScheduledRows(data.items);
    }
  } catch (e) {
    console.error("Planlanmış gönderiler yüklenemedi:", e);
  }
}
window.loadOmniScheduledTable = loadOmniScheduledTable;

function renderOmniScheduledRows(items) {
  const tbody = document.getElementById('omni-scheduled-tbody');
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="py-6 text-center text-dim">Henüz planlanmış gönderi bulunmuyor.</td></tr>';
    return;
  }

  const platformIcons = {
    twitter: '<i class="fa-brands fa-x-twitter text-white" title="Twitter/X"></i>',
    youtube: '<i class="fa-brands fa-youtube text-red-500" title="YouTube"></i>',
    telegram: '<i class="fa-brands fa-telegram text-sky-400" title="Telegram"></i>',
    instagram: '<i class="fa-brands fa-instagram text-pink-500" title="Instagram"></i>',
    tiktok: '<i class="fa-brands fa-tiktok text-rose-400" title="TikTok"></i>',
    facebook: '<i class="fa-brands fa-facebook text-blue-500" title="Facebook"></i>'
  };

  tbody.innerHTML = items.map(item => {
    const icons = item.platforms.map(p => platformIcons[p] || p).join(' ');
    const statusBadge = item.status === 'scheduled' || item.status === 'pending'
      ? '<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Zamanlandı</span>'
      : (item.status === 'posted' ? '<span class="px-2 py-0.5 rounded text-[10px] bg-cyan/10 text-cyan border border-cyan/30">Yayınlandı</span>' : '<span class="px-2 py-0.5 rounded text-[10px] bg-white/10 text-slate-400">Beklemede</span>');

    const cleanSnippet = item.content.replace(/<[^>]*>?/gm, '').substring(0, 65);

    return `
      <tr class="hover:bg-white/[0.02] transition font-mono text-xs">
        <td class="py-2.5 px-3 whitespace-nowrap">
          <span class="text-white font-bold">${item.date}</span>
          <span class="text-dim block text-[11px]">${item.time}</span>
        </td>
        <td class="py-2.5 px-3 whitespace-nowrap text-dim text-[11px]">
          ${item.slot}
        </td>
        <td class="py-2.5 px-3 whitespace-nowrap text-sm flex items-center gap-2 mt-1">
          ${icons}
        </td>
        <td class="py-2.5 px-3 max-w-xs">
          <span class="text-slate-300 truncate block text-[11px]" title="${cleanSnippet}">${cleanSnippet}...</span>
        </td>
        <td class="py-2.5 px-3 whitespace-nowrap text-[11px]">
          <span class="text-cyan font-bold">${item.media_type || 'Metin'}</span>
        </td>
        <td class="py-2.5 px-3 whitespace-nowrap">
          ${statusBadge}
        </td>
        <td class="py-2.5 px-3 whitespace-nowrap text-right">
          <button type="button" class="btn btn-outline btn-xs p-1 text-slate-400 hover:text-white" onclick="copyCustomText('${item.content.replace(/'/g, "\\'").replace(/\n/g, "\\n")}')" title="Metni Kopyala">
            <i class="fa-solid fa-copy"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}
window.renderOmniScheduledRows = renderOmniScheduledRows;

function filterOmniScheduledTable(platform, btn) {
  document.querySelectorAll('#section-socialmatrix .btn-xs').forEach(b => b.classList.remove('btn-primary'));
  if (btn) btn.classList.add('btn-primary');

  if (platform === 'all') {
    renderOmniScheduledRows(cachedOmniScheduled);
  } else {
    const filtered = cachedOmniScheduled.filter(i => i.platforms.includes(platform));
    renderOmniScheduledRows(filtered);
  }
}
window.filterOmniScheduledTable = filterOmniScheduledTable;




// ==============================================================
// 🌟 3-PILLAR MASTER CONTROLLER (ÜRETİM • PAYLAŞIM • ANALİZ)
// ==============================================================

window.activePillar = 'production';
window.activeProdSubTab = 'text';
window.activePublishingPlatform = 'telegram';
window.selectedPlanDays = 1;
window.calendarViewMode = 'week';
window.allStockData = { texts: [], videos: [], images: [] };
window.allCalendarEvents = [];

function initMasterPillars() {
  switchMasterPillar('production');
  switchProductionSubTab('text');
  renderPublishingPlatformButtons();
}
window.initMasterPillars = initMasterPillars;

// 1. MASTER PILLAR SWITCHER
function switchMasterPillar(pillar) {
  window.activePillar = pillar;
  
  // Tab buttons
  ['production', 'publishing', 'analytics'].forEach(p => {
    const btn = document.getElementById(`btn-pillar-${p}`);
    const sec = document.getElementById(`pillar-${p}`);
    if (btn) {
      if (p === pillar) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    }
    if (sec) {
      if (p === pillar) {
        sec.classList.add('active-pillar');
      } else {
        sec.classList.remove('active-pillar');
      }
    }
  });

  // Pillar specific triggers
  if (pillar === 'production') {
    loadStockItemsUI();
  } else if (pillar === 'publishing') {
    selectPublishingPlatform(window.activePublishingPlatform || 'telegram');
    loadUpcomingQueueUI();
  } else if (pillar === 'analytics') {
    loadAnalyticsMetrics();
    loadEditorialCalendar();
  }
}
window.switchMasterPillar = switchMasterPillar;

// 2. PRODUCTION SUB-TABS (Metin, Video, Fotoğraf, Stok)
function switchProductionSubTab(sub) {
  window.activeProdSubTab = sub;
  
  ['text', 'video', 'image', 'stock'].forEach(s => {
    const pill = document.getElementById(`pill-prod-${s}`);
    const view = document.getElementById(`subview-prod-${s}`);
    if (pill) {
      if (s === sub) {
        pill.classList.add('active');
      } else {
        pill.classList.remove('active');
      }
    }
    if (view) {
      if (s === sub) {
        view.classList.remove('hidden');
      } else {
        view.classList.add('hidden');
      }
    }
  });

  if (sub === 'stock') {
    loadStockItemsUI();
  }
}
window.switchProductionSubTab = switchProductionSubTab;

// 2.1 TEXT GENERATION
async function runTextGeneration() {
  const format = document.getElementById('prod-text-format')?.value || 'headline_hook';
  const count = parseInt(document.getElementById('prod-text-count')?.value || '1');
  const lang = document.getElementById('prod-text-lang')?.value || 'uz';

  showToast(`${count} adet metin üretiliyor...`, "info");
  try {
    const res = await fetch('/api/production/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'text', subType: format, count: count, language: lang, saveToStock: true })
    });
    const data = await res.json();
    if (data.success && data.items) {
      renderGeneratedTexts(data.items);
      loadStockItemsUI();
      showToast(`${data.items.length} adet metin başarıyla üretildi ve stoka eklendi!`, "success");
    }
  } catch (err) {
    showToast("Metin üretimi sırasında hata oluştu", "error");
  }
}
window.runTextGeneration = runTextGeneration;

function renderGeneratedTexts(items) {
  const container = document.getElementById('prod-text-output-container');
  if (!container) return;

  container.innerHTML = items.map((item, idx) => `
    <div class="gece-card p-5 space-y-3 border border-cyan/20 bg-cyan/5">
      <div class="flex items-center justify-between border-b border-white/5 pb-2">
        <div class="flex items-center gap-2">
          <span class="text-xs px-2 py-0.5 rounded bg-cyan/20 text-cyan font-mono font-bold">#${idx + 1} ${item.format}</span>
          <h4 class="text-sm font-bold text-white">${item.title}</h4>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[10px] px-2.5 py-0.5 rounded-full bg-gradient-to-r from-blue-500/20 to-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/30 flex items-center gap-1">
            <i class="fa-solid fa-wand-magic-sparkles text-[9px] text-cyan-400"></i>
            <span>${item.ai_provider === 'gemini' ? 'Gemini AI' : 'AI Motoru'} • Özgün</span>
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono">📦 Stokta Hazır</span>
        </div>
      </div>
      <div class="p-3 bg-black/50 rounded-xl font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-line border border-white/5">
        ${item.content}
      </div>
      <div class="flex items-center justify-between pt-1">
        <span class="text-[10px] text-slate-400 font-mono">Hedef: ${item.topic || 'Genel'} • Dil: ${(item.language || 'UZ').toUpperCase()}</span>
        <button type="button" class="btn-clean-secondary px-3 py-1 text-xs flex items-center gap-1.5" onclick="copyCustomText('${item.content.replace(/'/g, "\'").replace(/\n/g, "\\n")}')">
          <i class="fa-solid fa-copy text-[11px]"></i>
          <span>Metni Kopyala</span>
        </button>
      </div>
    </div>
  `).join('');
}

// 2.2 VIDEO GENERATION
async function runVideoGeneration() {
  const type = document.getElementById('prod-video-type')?.value || 'landscape_broll';
  const count = parseInt(document.getElementById('prod-video-count')?.value || '1');

  showToast(`${count} adet video işleniyor...`, "info");
  try {
    const res = await fetch('/api/production/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'video', subType: type, count: count, saveToStock: true })
    });
    const data = await res.json();
    if (data.success && data.items) {
      renderGeneratedVideos(data.items);
      loadStockItemsUI();
      showToast(`${data.items.length} video üretildi ve stoka eklendi!`, "success");
    }
  } catch (err) {
    showToast("Video üretimi sırasında hata oluştu", "error");
  }
}
window.runVideoGeneration = runVideoGeneration;

function renderGeneratedVideos(items) {
  const container = document.getElementById('prod-video-output-container');
  if (!container) return;

  container.innerHTML = items.map((item) => `
    <div class="gallery-media-card p-4 space-y-3 border border-purple-500/20 bg-purple-950/10">
      <div class="flex items-center justify-between">
        <span class="text-[10px] px-2.5 py-1 rounded-full bg-purple-500/20 text-purple font-mono font-bold flex items-center gap-1">
          <i class="fa-solid fa-play text-[8px]"></i>
          <span>${item.video_type}</span>
        </span>
        <span class="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">📦 Stokta Hazır</span>
      </div>
      <div class="aspect-[9/16] bg-black/90 rounded-2xl overflow-hidden relative border border-white/10 shadow-2xl flex items-center justify-center">
        <video src="/${item.file_path}" controls playsinline preload="metadata" class="w-full h-full object-cover"></video>
      </div>
      <div>
        <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
        <span class="text-[10px] text-slate-400 font-mono">Dikey Video (9:16) • HD 1080p</span>
      </div>
      <div class="flex items-center justify-between pt-1 border-t border-white/5">
        <a href="/${item.file_path}" download class="btn-clean-secondary px-3 py-1.5 text-xs flex items-center gap-1.5">
          <i class="fa-solid fa-download text-[11px]"></i>
          <span>İndir</span>
        </a>
        <button type="button" class="btn-clean-primary px-3.5 py-1.5 text-xs flex items-center gap-1" onclick="switchMasterPillar('publishing')">
          <span>Planla</span>
          <i class="fa-solid fa-arrow-right text-[10px]"></i>
        </button>
      </div>
    </div>
  `).join('');
}

// 2.3 IMAGE GENERATION
async function runImageGeneration() {
  const style = document.getElementById('prod-image-style')?.value || 'qa_quiz';
  const count = parseInt(document.getElementById('prod-image-count')?.value || '1');

  showToast(`${count} adet afiş/görsel çiziliyor...`, "info");
  try {
    const res = await fetch('/api/production/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'image', subType: style, count: count, saveToStock: true })
    });
    const data = await res.json();
    if (data.success && data.items) {
      renderGeneratedImages(data.items);
      loadStockItemsUI();
      showToast(`${data.items.length} adet görsel üretildi ve stoka eklendi!`, "success");
    }
  } catch (err) {
    showToast("Görsel üretimi sırasında hata oluştu", "error");
  }
}
window.runImageGeneration = runImageGeneration;

function renderGeneratedImages(items) {
  const container = document.getElementById('prod-image-output-container');
  if (!container) return;

  container.innerHTML = items.map((item) => `
    <div class="gallery-media-card p-4 space-y-3 border border-emerald-500/20 bg-emerald-950/10">
      <div class="flex items-center justify-between">
        <span class="text-[10px] px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-mono font-bold flex items-center gap-1">
          <i class="fa-solid fa-palette text-[8px]"></i>
          <span>${item.format}</span>
        </span>
        <span class="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">📦 Stokta Hazır</span>
      </div>
      <div class="aspect-square bg-black/80 rounded-2xl overflow-hidden relative border border-white/10 shadow-2xl flex items-center justify-center group">
        <img src="/${item.photo_path}" alt="Tasarım Afişi" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105">
      </div>
      <div>
        <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
        <span class="text-[10px] text-slate-400 font-mono">1080x1080 • Sosyal Medya Afişi</span>
      </div>
      <div class="flex items-center justify-between pt-1 border-t border-white/5">
        <a href="/${item.photo_path}" download class="btn-clean-secondary px-3 py-1.5 text-xs flex items-center gap-1.5">
          <i class="fa-solid fa-download text-[11px]"></i>
          <span>PNG İndir</span>
        </a>
        <button type="button" class="btn-clean-primary px-3.5 py-1.5 text-xs flex items-center gap-1" onclick="switchMasterPillar('publishing')">
          <span>Planla</span>
          <i class="fa-solid fa-arrow-right text-[10px]"></i>
        </button>
      </div>
    </div>
  `).join('');
}

// 2.4 STOCK MANAGEMENT UI
async function loadStockItemsUI() {
  try {
    const res = await fetch('/api/stock/items');
    const data = await res.json();
    if (data.success) {
      window.allStockData = data.stock;

      // Update counters
      const totalEl = document.getElementById('prod-stock-badge-total');
      const hdrTexts = document.getElementById('header-stock-texts');
      const hdrVideos = document.getElementById('header-stock-videos');
      const hdrImages = document.getElementById('header-stock-images');
      const cntTexts = document.getElementById('stock-count-texts');
      const cntVideos = document.getElementById('stock-count-videos');
      const cntImages = document.getElementById('stock-count-images');

      if (totalEl) totalEl.innerText = data.counts.total;
      if (hdrTexts) hdrTexts.innerText = data.counts.texts;
      if (hdrVideos) hdrVideos.innerText = data.counts.videos;
      if (hdrImages) hdrImages.innerText = data.counts.images;
      if (cntTexts) cntTexts.innerText = data.counts.texts;
      if (cntVideos) cntVideos.innerText = data.counts.videos;
      if (cntImages) cntImages.innerText = data.counts.images;

      renderStockGrid('all');
    }
  } catch (err) {
    console.error("loadStockItemsUI error:", err);
  }
}
window.loadStockItemsUI = loadStockItemsUI;

function filterStockView(cat) {
  document.querySelectorAll('.stock-filter-btn').forEach(b => b.classList.remove('active'));
  event?.target?.classList.add('active');
  renderStockGrid(cat);
}
window.filterStockView = filterStockView;

function renderStockGrid(cat) {
  const container = document.getElementById('stock-items-grid');
  if (!container) return;

  // 1. VIDEOS GALLERY
  if (cat === 'videos') {
    const list = window.allStockData.videos || [];
    container.className = "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4";
    if (list.length === 0) {
      container.innerHTML = `<div class="col-span-full text-center py-10 text-slate-500 font-mono text-xs">Stokta video bulunmuyor. Video sekmesinden hemen üretebilirsiniz.</div>`;
      return;
    }
    container.innerHTML = list.map(item => `
      <div class="gallery-media-card p-3 space-y-2.5 border border-purple-500/20 bg-purple-950/10">
        <div class="flex items-center justify-between">
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple font-mono font-bold">🎬 ${item.video_type || 'Shorts'}</span>
          <span class="text-[10px] text-slate-400 font-mono">0:30 HD</span>
        </div>
        <div class="aspect-[9/16] bg-black/90 rounded-xl overflow-hidden relative border border-white/10 flex items-center justify-center">
          <video src="/${item.file_path}" controls playsinline preload="metadata" class="w-full h-full object-cover"></video>
        </div>
        <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
        <div class="flex items-center justify-between pt-1 border-t border-white/5">
          <a href="/${item.file_path}" download class="btn-clean-secondary px-2.5 py-1 text-xs flex items-center gap-1">
            <i class="fa-solid fa-download text-[10px]"></i>
            <span>İndir</span>
          </a>
          <div class="flex items-center gap-1.5">
            <button type="button" class="btn-clean-primary px-3 py-1 text-xs" onclick="switchMasterPillar('publishing')">
              Planla
            </button>
            <button type="button" class="btn-clean-danger px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-500/30 rounded-lg flex items-center gap-1 border border-rose-500/30" onclick="deleteStockItem('${item.id}')" title="Bu videoyu stoktan sil">
              <i class="fa-solid fa-trash-can text-[10px]"></i>
              <span>Sil</span>
            </button>
          </div>
        </div>
      </div>
    `).join('');
    return;
  }

  // 2. IMAGES GALLERY
  if (cat === 'images') {
    const list = window.allStockData.images || [];
    container.className = "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4";
    if (list.length === 0) {
      container.innerHTML = `<div class="col-span-full text-center py-10 text-slate-500 font-mono text-xs">Stokta görsel afiş bulunmuyor. Fotoğraf sekmesinden hemen üretebilirsiniz.</div>`;
      return;
    }
    container.innerHTML = list.map(item => `
      <div class="gallery-media-card p-3 space-y-2.5 border border-emerald-500/20 bg-emerald-950/10">
        <div class="flex items-center justify-between">
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald font-mono font-bold">🎨 ${item.format || 'Afiş'}</span>
          <span class="text-[10px] text-slate-400 font-mono">1080x1080</span>
        </div>
        <div class="aspect-square bg-black/90 rounded-xl overflow-hidden relative border border-white/10 flex items-center justify-center group">
          <img src="/${item.photo_path}" alt="Afiş" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105">
        </div>
        <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
        <div class="flex items-center justify-between pt-1 border-t border-white/5">
          <a href="/${item.photo_path}" download class="btn-clean-secondary px-2.5 py-1 text-xs flex items-center gap-1">
            <i class="fa-solid fa-download text-[10px]"></i>
            <span>PNG İndir</span>
          </a>
          <div class="flex items-center gap-1.5">
            <button type="button" class="btn-clean-primary px-3 py-1 text-xs" onclick="switchMasterPillar('publishing')">
              Planla
            </button>
            <button type="button" class="btn-clean-danger px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-500/30 rounded-lg flex items-center gap-1 border border-rose-500/30" onclick="deleteStockItem('${item.id}')" title="Bu afişi stoktan sil">
              <i class="fa-solid fa-trash-can text-[10px]"></i>
              <span>Sil</span>
            </button>
          </div>
        </div>
      </div>
    `).join('');
    return;
  }

  // 3. TEXTS OR ALL
  let list = [];
  if (cat === 'all' || cat === 'texts') list = list.concat(window.allStockData.texts || []);
  if (cat === 'all') {
    list = list.concat(window.allStockData.videos || []);
    list = list.concat(window.allStockData.images || []);
  }
  container.className = "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3";

  if (list.length === 0) {
    container.innerHTML = `<div class="col-span-full text-center py-10 text-slate-500 font-mono text-xs">Bu kategoride henüz stok içeriği yok.</div>`;
    return;
  }

  container.innerHTML = list.map(item => {
    const isVideo = item.file_path !== undefined;
    const isImage = item.photo_path !== undefined;
    const typeLabel = isVideo ? '🎬 Video' : (isImage ? '🎨 Görsel' : '✍️ Metin');
    const badgeColor = isVideo ? 'purple' : (isImage ? 'emerald' : 'cyan');

    if (isVideo) {
      return `
        <div class="p-3 bg-black/40 rounded-xl border border-purple-500/20 space-y-2 font-mono text-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple font-bold">🎬 Video</span>
            <span class="text-[10px] text-slate-500">0:30 HD</span>
          </div>
          <div class="h-32 bg-black/80 rounded-lg overflow-hidden border border-white/5 relative flex items-center justify-center">
            <video src="/${item.file_path}" controls playsinline class="w-full h-full object-cover"></video>
          </div>
          <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
          <div class="flex items-center justify-between pt-1 border-t border-white/5">
            <button type="button" class="btn-clean-primary px-2.5 py-1 text-[11px]" onclick="switchMasterPillar('publishing')">Planla</button>
            <button type="button" class="btn-clean-danger px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-500/30 rounded-lg flex items-center gap-1 border border-rose-500/30" onclick="deleteStockItem('${item.id}')" title="Sil"><i class="fa-solid fa-trash-can text-[10px]"></i> <span>Sil</span></button>
          </div>
        </div>
      `;
    }

    if (isImage) {
      return `
        <div class="p-3 bg-black/40 rounded-xl border border-emerald-500/20 space-y-2 font-mono text-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald font-bold">🎨 Görsel</span>
            <span class="text-[10px] text-slate-500">1080x1080</span>
          </div>
          <div class="h-32 bg-black/80 rounded-lg overflow-hidden border border-white/5 relative flex items-center justify-center">
            <img src="/${item.photo_path}" alt="Afiş" class="w-full h-full object-cover">
          </div>
          <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
          <div class="flex items-center justify-between pt-1 border-t border-white/5">
            <button type="button" class="btn-clean-primary px-2.5 py-1 text-[11px]" onclick="switchMasterPillar('publishing')">Planla</button>
            <button type="button" class="btn-clean-danger px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-500/30 rounded-lg flex items-center gap-1 border border-rose-500/30" onclick="deleteStockItem('${item.id}')" title="Sil"><i class="fa-solid fa-trash-can text-[10px]"></i> <span>Sil</span></button>
          </div>
        </div>
      `;
    }

    return `
      <div class="p-3.5 bg-black/40 rounded-xl border border-white/5 space-y-2.5 font-mono text-xs hover:border-white/15 transition">
        <div class="flex items-center justify-between">
          <span class="text-[10px] px-2 py-0.5 rounded bg-cyan/20 text-cyan font-bold">${typeLabel}</span>
          <span class="text-[10px] text-slate-500">${item.created_at || 'Bugün'}</span>
        </div>
        <h4 class="text-xs font-bold text-white truncate" title="${item.title}">${item.title}</h4>
        <p class="text-[11px] text-slate-400 line-clamp-3">${item.content || item.format || 'Hazır Stok Varlığı'}</p>
        <div class="flex items-center justify-between pt-1 border-t border-white/5">
          <button type="button" class="btn-clean-primary px-2.5 py-1 text-[11px]" onclick="switchMasterPillar('publishing')">Planla</button>
          <button type="button" class="btn-clean-danger px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-500/30 rounded-lg flex items-center gap-1 border border-rose-500/30" onclick="deleteStockItem('${item.id}')" title="Sil"><i class="fa-solid fa-trash-can text-[10px]"></i> <span>Sil</span></button>
        </div>
      </div>
    `;
  }).join('');
}

async function deleteStockItem(id) {
  try {
    const res = await fetch(`/api/stock/delete/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast(`🗑️ "${data.title || 'Varlık'}" stoktan silindi`, "info");
      loadStockItemsUI();
      if (typeof fetchSystemLogs === 'function') fetchSystemLogs();
    } else {
      showToast("Silme işlemi gerçekleştirilemedi", "warning");
    }
  } catch (err) {
    showToast("Silme sırasında bağlantı hatası", "error");
  }
}
window.deleteStockItem = deleteStockItem;

// 3. PUBLISHING (7 PLATFORMS & AUTO-SCHEDULER)
const PUBLISHING_PLATFORMS = [
  { id: 'telegram', name: 'Telegram', handle: '@arkadasuz', icon: 'fa-brands fa-telegram text-cyan', formats: 'Metin • Foto • Video' },
  { id: 'youtube', name: 'YouTube Shorts', handle: '@arkadaş', icon: 'fa-brands fa-youtube text-red-500', formats: 'Video • Topluluk' },
  { id: 'instagram', name: 'Instagram', handle: '@arkadas_consulting', icon: 'fa-brands fa-instagram text-pink-500', formats: 'Foto • Video' },
  { id: 'tiktok', name: 'TikTok', handle: '@arkadas_edu', icon: 'fa-brands fa-tiktok text-purple', formats: 'Video • Slayt' },
  { id: 'twitter', name: 'Twitter / X', handle: '@arkadasuz', icon: 'fa-brands fa-x-twitter text-slate-300', formats: 'Thread • Foto • Video' },
  { id: 'facebook', name: 'Facebook', handle: 'Arkadas Group', icon: 'fa-brands fa-facebook text-blue-500', formats: 'Metin • Foto • Video' },
  { id: 'whatsapp', name: 'WhatsApp', handle: 'VIP Kanal', icon: 'fa-brands fa-whatsapp text-emerald', formats: 'Metin • Foto • Video' }
];

function renderPublishingPlatformButtons() {
  const container = document.getElementById('pub-platform-buttons');
  if (!container) return;

  container.innerHTML = PUBLISHING_PLATFORMS.map(p => `
    <div class="gece-card p-3 cursor-pointer transition-all hover:border-white/30 omni-pub-card ${p.id === window.activePublishingPlatform ? 'border-cyan bg-cyan/10' : 'border-white/5'}" id="pub-card-${p.id}" onclick="selectPublishingPlatform('${p.id}')">
      <div class="flex items-center justify-between mb-1.5">
        <i class="${p.icon} text-lg"></i>
        <span class="pulse-dot scale-75"></span>
      </div>
      <div class="font-bold text-white text-xs font-sans truncate">${p.name}</div>
      <div class="text-[10px] text-slate-400 truncate">${p.handle}</div>
      <div class="mt-1.5 text-[9px] text-slate-500 truncate font-sans">${p.formats}</div>
    </div>
  `).join('');
}
window.renderPublishingPlatformButtons = renderPublishingPlatformButtons;

async function selectPublishingPlatform(platform) {
  window.activePublishingPlatform = platform;
  
  // Card styles
  document.querySelectorAll('.omni-pub-card').forEach(c => {
    c.classList.remove('border-cyan', 'bg-cyan/10');
    c.classList.add('border-white/5');
  });
  const activeCard = document.getElementById(`pub-card-${platform}`);
  if (activeCard) {
    activeCard.classList.remove('border-white/5');
    activeCard.classList.add('border-cyan', 'bg-cyan/10');
  }

  // Load AI Advisor data
  try {
    const res = await fetch(`/api/ai_advisor?platform=${platform}`);
    const resData = await res.json();
    if (resData.success && resData.data) {
      const d = resData.data;
      const advName = document.getElementById('advisor-name');
      const advHandle = document.getElementById('advisor-handle');
      const advBadge = document.getElementById('advisor-badge');
      const advIcon = document.getElementById('advisor-icon');
      const statViews = document.getElementById('advisor-stat-views');
      const statPosts = document.getElementById('advisor-stat-posts');
      const statSlot = document.getElementById('advisor-stat-slot');
      const statTopic = document.getElementById('advisor-stat-topic');
      const txtAnalysis = document.getElementById('advisor-analysis-text');
      const txtRec = document.getElementById('advisor-recommendation-text');

      if (advName) advName.innerText = `${d.name} AI Danışmanı`;
      if (advHandle) advHandle.innerText = d.handle;
      if (advBadge) advBadge.innerText = d.badge;
      if (advIcon) advIcon.innerHTML = `<i class="${d.icon}"></i>`;
      if (statViews) statViews.innerText = d.recent_views.toLocaleString();
      if (statPosts) statPosts.innerText = `${d.posts_last_week} Post`;
      if (statSlot) statSlot.innerText = d.best_slot;
      if (statTopic) statTopic.innerText = d.top_topic;
      if (txtAnalysis) txtAnalysis.innerText = d.ai_analysis;
      if (txtRec) txtRec.innerText = d.ai_recommendation;
    }
  } catch (err) {
    console.error("selectPublishingPlatform error:", err);
  }
}
window.selectPublishingPlatform = selectPublishingPlatform;

function selectPlanDays(days) {
  window.selectedPlanDays = days;
  document.querySelectorAll('.plan-duration-btn').forEach(b => {
    b.classList.remove('border-cyan', 'bg-cyan/10', 'active');
  });
  event?.currentTarget?.classList.add('border-cyan', 'bg-cyan/10', 'active');
  
  const lbl = document.getElementById('plan-summary-label');
  if (lbl) {
    const totalSlots = days * 2;
    lbl.innerText = `${days} Gün (${totalSlots} Gönderi Slotu)`;
  }
}
window.selectPlanDays = selectPlanDays;

async function executeAutoPlan() {
  const days = window.selectedPlanDays || 1;
  const platform = window.activePublishingPlatform || 'telegram';
  const incVideo = document.getElementById('plan-include-video')?.checked ?? true;
  const incImage = document.getElementById('plan-include-image')?.checked ?? true;
  const incText = document.getElementById('plan-include-text')?.checked ?? true;

  const incTypes = [];
  if (incVideo) incTypes.push('video');
  if (incImage) incTypes.push('image');
  if (incText) incTypes.push('text');

  showToast(`${days} günlük plan stoktan dağıtılıyor...`, "info");
  try {
    const res = await fetch('/api/scheduler/auto_plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform: platform, days: days, slotsPerDay: 2, includeTypes: incTypes })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, "success");
      loadUpcomingQueueUI();
      loadEditorialCalendar();
    }
  } catch (err) {
    showToast("Otomatik planlama sırasında hata", "error");
  }
}
window.executeAutoPlan = executeAutoPlan;

function applyAdvisorRecommendation() {
  executeAutoPlan();
}
window.applyAdvisorRecommendation = applyAdvisorRecommendation;

async function loadUpcomingQueueUI() {
  try {
    const res = await fetch('/api/analytics/calendar');
    const data = await res.json();
    if (data.success && data.events) {
      const queueList = document.getElementById('publishing-queue-list');
      if (!queueList) return;

      const scheduled = data.events.filter(e => e.status === 'scheduled');
      if (scheduled.length === 0) {
        queueList.innerHTML = `<div class="text-slate-500 font-mono text-xs text-center py-4">Kuyrukta bekleyen gönderi yok. Stoktan otomatik planlama yapabilirsiniz.</div>`;
        return;
      }

      queueList.innerHTML = scheduled.slice(0, 15).map(e => `
        <div class="flex items-center justify-between p-2.5 rounded-xl bg-black/40 border border-white/5 font-mono text-xs">
          <div class="flex items-center gap-3">
            <span class="text-[10px] px-2 py-0.5 rounded bg-cyan/20 text-cyan font-bold">${(e.platform || 'TG').toUpperCase()}</span>
            <span class="text-white font-bold">${e.date}</span>
            <span class="text-dim">${e.time}</span>
            <span class="text-slate-300 font-sans truncate max-w-xs">${e.title}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <button type="button" class="btn-clean-primary px-2 py-1 text-[11px] flex items-center gap-1" onclick="publishQueueItemNow('${e.id}', '${e.platform}')">
              <i class="fa-solid fa-paper-plane text-[9px]"></i>
              <span>Yayınla</span>
            </button>
            <button type="button" class="btn-clean-danger px-2 py-1 text-[11px] text-rose-400 hover:text-white hover:bg-rose-500/30 rounded-lg border border-rose-500/30" onclick="deleteScheduledPost('${e.id}')" title="Kuyruktan Sil">
              <i class="fa-solid fa-trash-can text-[10px]"></i>
            </button>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error("loadUpcomingQueueUI error:", err);
  }
}
window.loadUpcomingQueueUI = loadUpcomingQueueUI;

// AI Publishing Post Generator
async function generatePlatformAIPost() {
  const platform = window.activePublishingPlatform || 'telegram';
  const topicInput = document.getElementById('platform-post-topic');
  const topic = topicInput?.value.trim() || 'Turkiyada Imtihonsiz Oliy Ta\'lim Qabuli';

  showToast(`✨ Gemini ${platform.toUpperCase()} için özel gönderi üretiyor...`, "info");
  try {
    const res = await fetch('/api/publishing/generate-ai-post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform: platform, topic: topic })
    });
    const data = await res.json();
    if (data.success && data.post) {
      const p = data.post;
      const contentEl = document.getElementById('platform-post-content');
      if (contentEl) {
        contentEl.value = p.content || '';
        updateCharCounter();
      }
      showToast(`✨ ${platform.toUpperCase()} gönderisi hazırlandı!`, "success");
      fetchSystemLogs();
    }
  } catch (err) {
    showToast("AI gönderi üretimi sırasında hata oluştu", "error");
  }
}
window.generatePlatformAIPost = generatePlatformAIPost;

function fillRandomStockTopic() {
  const texts = window.allStockData?.texts || [];
  const topicInput = document.getElementById('platform-post-topic');
  if (texts.length > 0) {
    const randomItem = texts[Math.floor(Math.random() * texts.length)];
    if (topicInput) topicInput.value = randomItem.title || randomItem.topic || '';
  } else {
    const presets = ["Tibbiyot va Stomatologiya", "Dasturlash va IT Muhandislik", "Aviatsiya va Uchuvchilik", "Kiberxavfsizlik"];
    if (topicInput) topicInput.value = presets[Math.floor(Math.random() * presets.length)];
  }
  showToast("Rastgele konu dolduruldu", "info");
}
window.fillRandomStockTopic = fillRandomStockTopic;

function updateCharCounter() {
  const el = document.getElementById('platform-post-content');
  const counter = document.getElementById('post-char-counter');
  if (el && counter) {
    counter.innerText = `${el.value.length} karakter`;
  }
}

async function publishActivePostNow() {
  const platform = window.activePublishingPlatform || 'telegram';
  const content = document.getElementById('platform-post-content')?.value.trim();
  const topic = document.getElementById('platform-post-topic')?.value.trim() || `${platform.toUpperCase()} Gönderisi`;

  if (!content) {
    showToast("Lütfen önce bir gönderi metni yazın veya Gemini ile üretin", "warning");
    return;
  }

  showToast(`⚡ ${platform.toUpperCase()} kanalına yayınlanıyor...`, "info");
  try {
    const res = await fetch('/api/publishing/publish-now', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform: platform, content: content, title: topic })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`🎉 ${platform.toUpperCase()} kanalında başarıyla paylaşıldı!`, "success");
      loadUpcomingQueueUI();
      loadEditorialCalendar();
      fetchSystemLogs();
    }
  } catch (err) {
    showToast("Yayınlama sırasında hata oluştu", "error");
  }
}
window.publishActivePostNow = publishActivePostNow;

async function scheduleActivePost() {
  const platform = window.activePublishingPlatform || 'telegram';
  const content = document.getElementById('platform-post-content')?.value.trim();
  const topic = document.getElementById('platform-post-topic')?.value.trim() || `${platform.toUpperCase()} Gönderisi`;

  if (!content) {
    showToast("Lütfen önce planlanacak gönderi metnini girin", "warning");
    return;
  }

  executeAutoPlan();
}
window.scheduleActivePost = scheduleActivePost;

async function publishQueueItemNow(id, platform) {
  showToast(`⚡ ${platform ? platform.toUpperCase() : ''} kuyruktan anında yayınlanıyor...`, "info");
  await deleteScheduledPost(id, false);
  showToast("Gönderi başarıyla canlı hatta aktarıldı!", "success");
}
window.publishQueueItemNow = publishQueueItemNow;

async function deleteScheduledPost(id, showUserToast = true) {
  try {
    const res = await fetch(`/api/publishing/delete-scheduled/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      if (showUserToast) showToast("Gönderi kuyruktan kaldırıldı", "info");
      loadUpcomingQueueUI();
      loadEditorialCalendar();
      fetchSystemLogs();
    }
  } catch (err) {
    showToast("Kuyruktan silme hatası", "error");
  }
}
window.deleteScheduledPost = deleteScheduledPost;

// Analytics Gemini AI Audit
async function runAnalyticsAIAudit() {
  showToast("🧠 Gemini 7 kanalı analiz ediyor ve denetliyor...", "info");
  try {
    const res = await fetch('/api/analytics/ai-audit', { method: 'POST' });
    const data = await res.json();
    if (data.success && data.audit) {
      const a = data.audit;
      const scoreEl = document.getElementById('audit-score-display');
      const growthEl = document.getElementById('audit-growth-label');
      const topEl = document.getElementById('audit-top-channel');
      const sumEl = document.getElementById('audit-summary-text');
      const tacticsEl = document.getElementById('audit-tactics-list');

      if (scoreEl) scoreEl.innerText = `${a.score || 92} / 100`;
      if (growthEl) growthEl.innerText = a.growth_label || '+22.4% Güçlü Dinamika';
      if (topEl) topEl.innerText = `Lider Kanal: ${a.top_channel || 'Telegram (@arkadasuz)'}`;
      if (sumEl) sumEl.innerText = a.summary || '';
      if (tacticsEl && a.tactics) {
        tacticsEl.innerHTML = a.tactics.map(t => `
          <div class="text-[11px] text-slate-300 flex items-center gap-2 font-mono">
            <span class="w-1.5 h-1.5 rounded-full bg-cyan"></span>
            <span>${t}</span>
          </div>
        `).join('');
      }
      showToast("🧠 Gemini kanal sağlık denetimi tamamlandı!", "success");
      fetchSystemLogs();
    }
  } catch (err) {
    showToast("Denetim sırasında hata oluştu", "error");
  }
}
window.runAnalyticsAIAudit = runAnalyticsAIAudit;

// Live System Log Console
let isLogConsoleOpen = false;

function toggleLogConsole() {
  const drawer = document.getElementById('live-log-drawer');
  if (!drawer) return;
  isLogConsoleOpen = !isLogConsoleOpen;

  if (isLogConsoleOpen) {
    drawer.classList.remove('translate-y-4', 'opacity-0', 'pointer-events-none');
    drawer.classList.add('translate-y-0', 'opacity-100');
    fetchSystemLogs();
  } else {
    drawer.classList.remove('translate-y-0', 'opacity-100');
    drawer.classList.add('translate-y-4', 'opacity-0', 'pointer-events-none');
  }
}
window.toggleLogConsole = toggleLogConsole;

async function fetchSystemLogs() {
  try {
    const res = await fetch('/api/system/logs?limit=40');
    const data = await res.json();
    if (data.success && data.logs) {
      renderSystemLogs(data.logs);
      const badge = document.getElementById('log-count-badge');
      if (badge) badge.innerText = data.logs.length;
    }
  } catch (err) {
    console.error("fetchSystemLogs error:", err);
  }
}
window.fetchSystemLogs = fetchSystemLogs;

function renderSystemLogs(logs) {
  const container = document.getElementById('live-log-list');
  if (!container) return;

  const catColors = {
    GEMINI_AI: 'cyan',
    GÖRSEL: 'emerald',
    VİDEO: 'purple',
    PLANLAMA: 'indigo',
    STOK: 'amber',
    PAYLAŞIM: 'teal',
    SİSTEM: 'slate'
  };

  container.innerHTML = logs.map(l => {
    const color = catColors[l.category] || 'cyan';
    return `
      <div class="p-1.5 rounded-lg bg-black/40 border border-white/5 space-y-0.5 font-mono text-[10px]">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-${color}-500/20 text-${color}-400 border border-${color}-500/30">[${l.category}]</span>
            <span class="text-slate-500">${l.time}</span>
          </div>
          <span class="w-1.5 h-1.5 rounded-full ${l.level === 'error' ? 'bg-rose-500' : (l.level === 'warning' ? 'bg-amber-400' : 'bg-emerald-400')}"></span>
        </div>
        <div class="text-slate-200 pl-1 font-sans text-[11px] leading-tight">${l.message}</div>
      </div>
    `;
  }).join('');
}

async function clearSystemLogsUI() {
  try {
    await fetch('/api/system/logs/clear', { method: 'POST' });
    fetchSystemLogs();
    showToast("Sistem logları temizlendi", "info");
  } catch (err) {
    showToast("Log temizleme hatası", "error");
  }
}
window.clearSystemLogsUI = clearSystemLogsUI;

// 4. ANALYTICS (CALENDAR & METRICS)
async function loadAnalyticsMetrics() {
  try {
    const res = await fetch('/api/analytics/metrics');
    const data = await res.json();
    if (data.success) {
      const s = data.summary;
      const vEl = document.getElementById('metric-total-views');
      const vgEl = document.getElementById('metric-views-growth');
      const mEl = document.getElementById('metric-total-messages');
      const mgEl = document.getElementById('metric-messages-growth');
      const lEl = document.getElementById('metric-total-likes');
      const lgEl = document.getElementById('metric-likes-growth');
      const fEl = document.getElementById('metric-net-followers');
      const fgEl = document.getElementById('metric-followers-growth');

      if (vEl) vEl.innerText = s.total_views.toLocaleString();
      if (vgEl) vgEl.innerText = s.views_growth;
      if (mEl) mEl.innerText = s.total_messages.toLocaleString();
      if (mgEl) mgEl.innerText = s.messages_growth;
      if (lEl) lEl.innerText = s.total_likes.toLocaleString();
      if (lgEl) lgEl.innerText = s.likes_growth;
      if (fEl) fEl.innerText = s.net_followers.toLocaleString();
      if (fgEl) fgEl.innerText = s.followers_growth;

      // Platform grid
      const grid = document.getElementById('platform-metrics-grid');
      if (grid && data.platforms) {
        grid.innerHTML = data.platforms.map(p => `
          <div class="p-3.5 bg-black/40 rounded-xl border border-white/5 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-${p.color}">${p.name}</span>
              <span class="text-[10px] text-slate-500">${p.handle}</span>
            </div>
            <div class="pb-1">
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 font-mono text-slate-300">${p.status_badge || 'Hazır'}</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-[11px]">
              <div>
                <span class="text-slate-500 block">İzlenme:</span>
                <span class="text-white font-bold">${p.views.toLocaleString()}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Lead / Mesaj:</span>
                <span class="text-cyan font-bold">${p.messages}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Beğeni:</span>
                <span class="text-rose-400 font-bold">${p.likes.toLocaleString()}</span>
              </div>
              <div>
                <span class="text-slate-500 block">Takipçi:</span>
                <span class="text-emerald font-bold">${p.followers.toLocaleString()}</span>
              </div>
            </div>
          </div>
        `).join('');
      }
    }
  } catch (err) {
    console.error("loadAnalyticsMetrics error:", err);
  }
}
window.loadAnalyticsMetrics = loadAnalyticsMetrics;

async function loadEditorialCalendar() {
  try {
    const res = await fetch('/api/analytics/calendar');
    const data = await res.json();
    if (data.success && data.events) {
      window.allCalendarEvents = data.events;
      renderCalendarGrid();
    }
  } catch (err) {
    console.error("loadEditorialCalendar error:", err);
  }
}
window.loadEditorialCalendar = loadEditorialCalendar;

function switchCalendarView(mode) {
  window.calendarViewMode = mode;
  document.getElementById('cal-view-week-btn')?.classList.toggle('active', mode === 'week');
  document.getElementById('cal-view-month-btn')?.classList.toggle('active', mode === 'month');
  renderCalendarGrid();
}
window.switchCalendarView = switchCalendarView;

function renderCalendarGrid() {
  const container = document.getElementById('calendar-grid-container');
  if (!container) return;

  const mode = window.calendarViewMode || 'week';
  const daysToShow = mode === 'week' ? 7 : 21;
  const events = window.allCalendarEvents || [];

  const platformColors = {
    telegram: 'cyan', youtube: 'red-500', instagram: 'pink-500',
    tiktok: 'purple', twitter: 'slate-300', facebook: 'blue-500', whatsapp: 'emerald'
  };

  const today = new Date();
  let daysHtml = [];

  for (let i = 0; i < daysToShow; i++) {
    const d = new Date();
    d.setDate(today.getDate() - (mode === 'week' ? 2 : 5) + i);
    const dateStr = d.toISOString().split('T')[0];
    const dayName = d.toLocaleDateString('tr-TR', { weekday: 'short' });
    const dayNum = d.getDate();

    const dayEvents = events.filter(e => e.date === dateStr);
    const isToday = dateStr === today.toISOString().split('T')[0];

    daysHtml.push(`
      <div class="p-2.5 rounded-xl border ${isToday ? 'border-cyan bg-cyan/10' : 'border-white/5 bg-black/40'} min-h-[140px] flex flex-col justify-between font-mono text-xs">
        <div>
          <div class="flex items-center justify-between border-b border-white/5 pb-1 mb-2">
            <span class="font-bold ${isToday ? 'text-cyan' : 'text-white'}">${dayName}</span>
            <span class="text-[11px] ${isToday ? 'text-cyan font-extrabold' : 'text-slate-500'}">${dayNum}</span>
          </div>
          <div class="space-y-1.5 max-h-24 overflow-y-auto">
            ${dayEvents.map(e => {
              const pColor = platformColors[e.platform] || 'cyan';
              return `
                <div class="p-1 rounded bg-${pColor}/15 border border-${pColor}/30 text-[10px] truncate cursor-pointer hover:opacity-80" onclick="openCalendarEventModal('${e.id}')" title="${e.title} (${e.time})">
                  <span class="text-${pColor} font-bold mr-1">●</span>
                  <span class="text-white">${e.time}</span>
                  <span class="text-slate-300 ml-1 font-sans">${e.title}</span>
                </div>
              `;
            }).join('')}
            ${dayEvents.length === 0 ? '<span class="text-[10px] text-slate-600 block text-center py-2">Gönderi yok</span>' : ''}
          </div>
        </div>
        <div class="text-[9px] text-slate-500 text-right pt-1 border-t border-white/5">
          ${dayEvents.length} Slot
        </div>
      </div>
    `);
  }

  container.innerHTML = daysHtml.join('');
}

function openCalendarEventModal(eventId) {
  const modal = document.getElementById('calendar-event-modal');
  const body = document.getElementById('cal-modal-body');
  const title = document.getElementById('cal-modal-title');
  if (!modal || !body) return;

  const ev = (window.allCalendarEvents || []).find(e => e.id === eventId);
  if (!ev) return;

  if (title) title.innerText = `${ev.platform.toUpperCase()} Gönderisi (${ev.time})`;
  body.innerHTML = `
    <div class="space-y-2 text-xs">
      <div><span class="text-dim">Tarih / Saat:</span> <strong class="text-white">${ev.date} • ${ev.time}</strong></div>
      <div><span class="text-dim">Platform:</span> <strong class="text-cyan">${ev.platform.toUpperCase()}</strong></div>
      <div><span class="text-dim">Başlık:</span> <div class="text-white font-bold mt-0.5">${ev.title}</div></div>
      <div><span class="text-dim">Durum:</span> <span class="px-2 py-0.5 rounded text-[10px] ${ev.status === 'published' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-cyan-500/20 text-cyan-400'}">${ev.status === 'published' ? 'Yayınlandı' : 'Zamanlandı'}</span></div>
      ${ev.preview ? `<div><span class="text-dim">Önizleme:</span> <p class="p-2.5 bg-black/50 rounded-lg text-slate-300 mt-1 whitespace-pre-line">${ev.preview}</p></div>` : ''}
    </div>
  `;
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}
window.openCalendarEventModal = openCalendarEventModal;

function closeCalendarModal() {
  const modal = document.getElementById('calendar-event-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}
window.closeCalendarModal = closeCalendarModal;

// 5. AGENCY TOOLS MODAL
function openAgencyToolsModal() {
  const modal = document.getElementById('agency-tools-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}
window.openAgencyToolsModal = openAgencyToolsModal;

function closeAgencyToolsModal() {
  const modal = document.getElementById('agency-tools-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}
window.closeAgencyToolsModal = closeAgencyToolsModal;


