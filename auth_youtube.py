#!/usr/bin/env python3
"""
One-time interactive YouTube OAuth2 Authorizer.
Uses port 8085 (or dynamic available port) to avoid conflict.
"""
import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CRED_FILE = Path("social_credentials.json")
TOKEN_FILE = Path("youtube_token.json")

def main():
    with open(CRED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    yt_conf = data.get("youtube", {})
    client_id = yt_conf.get("client_id")
    client_secret = yt_conf.get("client_secret")

    if not client_id or not client_secret:
        print("[ERROR] Client ID or Secret missing in social_credentials.json!")
        return

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8085/"]
        }
    }

    print("\n--- Arkadaş Consulting YouTube Shorts Yetkilendirme ---")
    print("Tarayıcınız açılacak, lütfen YouTube kanalınızın bağlı olduğu Google hesabını seçip izin verin.\n")

    # Port 8085 to avoid 8080 conflict
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=8085, prompt="consent", access_type="offline")

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    # Update social_credentials.json with refresh token
    if creds.refresh_token:
        yt_conf["refresh_token"] = creds.refresh_token
        yt_conf["enabled"] = True
        with open(CRED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ Refresh token social_credentials.json dosyasına başarıyla kaydedildi!")

    print(f"🎉 Yetkilendirme Başarılı! Token dosyası oluşturuldu: {TOKEN_FILE}")

if __name__ == "__main__":
    main()
