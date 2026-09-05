#!/usr/bin/env python3
"""
Arkadaş Consulting - Video Downloader & Aesthetic Music-Reels Processor
Supports:
1. Downloading clean vertical 9:16 videos from YouTube Shorts, TikTok, Instagram, Pinterest via yt-dlp
2. Trimming video to 7-12 seconds
3. Mixing trending chill Turkish / acoustic background music (assets/audio/)
4. Overlying aesthetic editorial typography (Italic hook + Bold headline) and Arkadaş sticker
"""

import os
import sys
import random
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ASSETS_DIR = BASE_DIR / "assets"
CLEAN_VIDEOS_DIR = ASSETS_DIR / "clean_videos"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"

from templates.template5_video import create_aesthetic_overlay

class VideoProcessor:
    def __init__(self):
        CLEAN_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def download_clean_clip(self, url: str) -> Path:
        """Downloads a video from YouTube / TikTok / Pinterest using yt-dlp."""
        clip_id = f"clip_{random.randint(1000, 9999)}"
        out_template = str(CLEAN_VIDEOS_DIR / f"{clip_id}.%(ext)s")

        cmd = [
            "yt-dlp",
            "--max-filesize", "50M",
            "-f", "bv*+ba/b",
            "--no-playlist",
            "-o", out_template,
            url
        ]

        print(f"[INFO] Downloading video via yt-dlp: {url}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[yt-dlp Error]:", res.stderr)
            raise RuntimeError(f"Video download failed: {res.stderr}")

        # Find downloaded file
        downloaded = list(CLEAN_VIDEOS_DIR.glob(f"{clip_id}.*"))
        if not downloaded:
            raise FileNotFoundError("Downloaded clip not found")

        print(f"[OK] Downloaded: {downloaded[0].name}")
        return downloaded[0]

    def build_aesthetic_music_reel(
        self,
        input_video_path: Path,
        italic_hook: str = "Turkiyada o'qish orzuyingizmi?",
        bold_headline: str = "ARKADAŞ BILAN 100% GRANT ASOSIDA TALABA BO'LING!",
        sub_tagline: str = "Oldindan to'lov yo'q — Kafolatli qabul!",
        output_filename: str = None,
        duration: int = 8
    ) -> Path:
        """
        Takes ANY clean video, mixes background acoustic/chill music,
        overlays aesthetic typography and Arkadaş logo, outputs vertical 9:16 MP4.
        """
        out_name = output_filename or f"aesthetic_reel_{random.randint(1000, 9999)}.mp4"
        out_mp4 = OUTPUT_DIR / out_name
        temp_overlay = OUTPUT_DIR / f"temp_proc_overlay_{random.randint(100, 999)}.png"

        # 1. Overlay
        create_aesthetic_overlay(
            width=1080,
            height=1920,
            italic_hook=italic_hook,
            bold_headline=bold_headline,
            sub_tagline=sub_tagline,
            output_png=temp_overlay
        )

        # 2. Audio selection
        audios = list(AUDIO_DIR.glob("*.mp3"))
        chosen_audio = random.choice(audios) if audios else None

        # 3. FFmpeg render
        ffmpeg_cmd = [
            FFMPEG_BIN,
            "-y",
            "-ss", "00:00:00",
            "-i", str(input_video_path),
            "-i", str(temp_overlay)
        ]

        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
            "[bg][1:v]overlay=0:0[v]"
        )

        if chosen_audio:
            ffmpeg_cmd.extend([
                "-i", str(chosen_audio),
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "2:a",
                "-af", f"volume=0.35,afade=t=in:ss=0:d=1,afade=t=out:st={duration-1.5}:d=1.5",
                "-shortest"
            ])
        else:
            ffmpeg_cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "[v]"
            ])

        ffmpeg_cmd.extend([
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "21",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_mp4)
        ])

        print(f"[INFO] Rendering Aesthetic Music Reel with FFmpeg...")
        res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("FFmpeg rendering failed")

        if temp_overlay.exists():
            temp_overlay.unlink()

        print(f"[SUCCESS] Aesthetic Music Reel Generated: {out_mp4}")
        return out_mp4

if __name__ == "__main__":
    vp = VideoProcessor()
    print("VideoProcessor initialized.")
