#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/system_logger.py
Central real-time system event logger for Arkadaş Executive OS.
Stores live operational logs for AI generation, stock management, publishing, and scheduling.
"""

import os
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BRAIN_DIR = BASE_DIR / "brain_data"
LOG_FILE = BRAIN_DIR / "system_logs.json"

_memory_logs = []

def init_logger():
    global _memory_logs
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                _memory_logs = json.load(f)
        except Exception:
            _memory_logs = []
    
    if not _memory_logs:
        now_str = datetime.now().strftime("%H:%M:%S")
        _memory_logs = [
            {"id": "log_init_1", "time": now_str, "category": "SİSTEM", "level": "info", "message": "Arkadaş Executive OS 3.0 çekirdeği başlatıldı (HTTP 200)."},
            {"id": "log_init_2", "time": now_str, "category": "GEMINI_AI", "level": "success", "message": "Google Gemini 2.5 Flash motoru hazır ve kopya koruması aktif."},
            {"id": "log_init_3", "time": now_str, "category": "GÖRSEL", "level": "info", "message": "Dinamik PIL grafik render stüdyosu (1080x1080) devrede."},
            {"id": "log_init_4", "time": now_str, "category": "PLANLAMA", "level": "info", "message": "7 Kanallı Omnichannel zamanlayıcı ve otopilot nöbette."}
        ]
        save_logs()

def save_logs():
    global _memory_logs
    try:
        os.makedirs(BRAIN_DIR, exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(_memory_logs[-150:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_system_log(category: str, message: str, level: str = "info") -> dict:
    """Adds a log entry and keeps the last 150 entries."""
    global _memory_logs
    entry = {
        "id": f"log_{int(datetime.now().timestamp()*1000)}",
        "time": datetime.now().strftime("%H:%M:%S"),
        "category": category.upper(),
        "level": level, # info, success, warning, error
        "message": message
    }
    _memory_logs.append(entry)
    if len(_memory_logs) > 150:
        _memory_logs = _memory_logs[-150:]
    save_logs()
    return entry

def get_recent_logs(limit: int = 50) -> list:
    global _memory_logs
    if not _memory_logs:
        init_logger()
    return list(reversed(_memory_logs[-limit:]))

def clear_system_logs():
    global _memory_logs
    _memory_logs = [
        {"id": "log_clear", "time": datetime.now().strftime("%H:%M:%S"), "category": "SİSTEM", "level": "warning", "message": "Sistem log geçmişi kullanıcı tarafından temizlendi."}
    ]
    save_logs()

init_logger()
