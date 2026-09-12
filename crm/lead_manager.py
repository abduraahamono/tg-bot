#!/usr/bin/env python3
"""
Arkadaş Consulting - CRM Lead Manager
Handles:
1. Local CRM lead persistence (JSON & CSV)
2. Instant sync to Google Sheets via Webhook (Apps Script)
3. Excel/CSV export generation for Admin Telegram downloads
4. Automatic lead parsing and status tracking
"""

import os
import sys
import csv
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).parent.parent
CRM_DIR = BASE_DIR / "crm"
LEADS_JSON_FILE = CRM_DIR / "leads.json"
LEADS_CSV_FILE = CRM_DIR / "leads.csv"
CONFIG_FILE = BASE_DIR / "bot_config.json"

class CRMLeadManager:
    def __init__(self):
        CRM_DIR.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_google_sheets_url(self) -> str:
        """Returns the configured Google Apps Script Webhook URL, if any."""
        return self.config.get("google_sheets_webhook_url", os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL", "")).strip()

    def set_google_sheets_url(self, url: str):
        """Saves Google Apps Script Webhook URL to config."""
        self.config["google_sheets_webhook_url"] = url.strip()
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CRM Error] Failed to save config: {e}", flush=True)

    def load_leads(self) -> List[Dict[str, Any]]:
        if not LEADS_JSON_FILE.exists():
            return []
        try:
            with open(LEADS_JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a lead locally (JSON & CSV) and pushes to Google Sheets if configured.
        """
        leads = self.load_leads()
        
        # Standardize lead format
        record = {
            "id": len(leads) + 1,
            "timestamp": lead_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": lead_data.get("name") or "Noma'lum",
            "phone": lead_data.get("phone") or "",
            "interest": lead_data.get("interest") or "Turkiyada ta'lim",
            "current_status": lead_data.get("current_status") or "Yangi ariza (Kutilmoqda)",
            "user_id": str(lead_data.get("user_id") or ""),
            "username": lead_data.get("username") or "",
            "notes": lead_data.get("first_message") or lead_data.get("notes") or ""
        }

        # Check if phone already exists, update or append
        existing_idx = None
        for i, l in enumerate(leads):
            if record["phone"] and l.get("phone") == record["phone"]:
                existing_idx = i
                break
            if record["user_id"] and str(l.get("user_id")) == record["user_id"] and not record["phone"]:
                existing_idx = i
                break

        if existing_idx is not None:
            leads[existing_idx].update({k: v for k, v in record.items() if v})
            record = leads[existing_idx]
        else:
            leads.append(record)

        # Save JSON
        try:
            with open(LEADS_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(leads, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CRM Error] Failed to write leads.json: {e}", flush=True)

        # Update CSV
        self._export_to_csv(leads)

        # Send to Google Sheets Webhook if configured
        sync_result = self.sync_to_google_sheets(record)
        return {"lead": record, "google_sheets_synced": sync_result}

    def _export_to_csv(self, leads: List[Dict[str, Any]]):
        """Writes all leads to a UTF-8 BOM CSV compatible with Excel."""
        fieldnames = [
            "Tartib raqami",
            "Sana va Vaqt",
            "Ism va Familiya",
            "Telefon Raqami",
            "Qiziqqan Yo'nalishi / Maqsad",
            "Hozirgi Holati",
            "Telegram Foydalanuvchi",
            "Telegram ID",
            "Izoh va Xabari"
        ]
        try:
            with open(LEADS_CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(fieldnames)
                for idx, l in enumerate(leads, 1):
                    username_str = f"@{l.get('username')}" if l.get('username') else ""
                    writer.writerow([
                        idx,
                        l.get("timestamp", ""),
                        l.get("name", ""),
                        l.get("phone", ""),
                        l.get("interest", ""),
                        l.get("current_status", ""),
                        username_str,
                        l.get("user_id", ""),
                        l.get("notes", "")
                    ])
        except Exception as e:
            print(f"[CRM Error] Failed to write leads.csv: {e}", flush=True)

    def generate_excel_export(self) -> Path:
        """Returns the path to the CSV file ready for downloading."""
        leads = self.load_leads()
        self._export_to_csv(leads)
        return LEADS_CSV_FILE

    def sync_to_google_sheets(self, lead: Dict[str, Any]) -> bool:
        """Sends the lead payload to Google Apps Script Webhook."""
        webhook_url = self.get_google_sheets_url()
        if not webhook_url or not webhook_url.startswith("https://script.google.com"):
            return False

        payload = {
            "timestamp": lead.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "name": lead.get("name", ""),
            "phone": lead.get("phone", ""),
            "interest": lead.get("interest", ""),
            "status": lead.get("current_status", "Yangi ariza"),
            "username": f"@{lead.get('username')}" if lead.get("username") else "",
            "user_id": str(lead.get("user_id", "")),
            "notes": lead.get("notes", "")
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=data_bytes,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_txt = resp.read().decode("utf-8")
                return "success" in res_txt.lower() or resp.status in [200, 302]
        except Exception as e:
            print(f"[Google Sheets Sync Warning]: {e}", flush=True)
            return False

    @staticmethod
    def get_google_apps_script_code() -> str:
        """Returns the ready-to-paste Google Apps Script code for Google Sheets."""
        return '''// Arkadaş Consulting - Google Sheets CRM Webhook
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // Agar sarlavhalar hali qo'yilmagan bo'lsa, birinchi qatorga yozamiz
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Sana va Vaqt",
        "Ism va Familiya",
        "Telefon Raqami",
        "Maqsad / Yo'nalish",
        "Hozirgi Holat",
        "Telegram Username",
        "Telegram ID",
        "Izoh / Dastlabki Xabar"
      ]);
      sheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#d9ead3");
    }

    var data = JSON.parse(e.postData.contents);
    sheet.appendRow([
      data.timestamp || new Date().toLocaleString(),
      data.name || "Noma'lum",
      data.phone || "",
      data.interest || "Turkiyada ta'lim",
      data.status || "Yangi ariza (Kutilmoqda)",
      data.username || "",
      data.user_id || "",
      data.notes || ""
    ]);

    return ContentService.createTextOutput(JSON.stringify({"status": "success"}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
'''
