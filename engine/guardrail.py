#!/usr/bin/env python3
"""
Arkadaş Consulting - Content Guardrail & Safety Filter
Protects brand reputation by sanitizing AI-generated content:
1. Strictly eliminates false guarantees ('0% rad', 'viza kafolati', '100% viza', etc.)
2. Eliminates gimmicky/cheap slogans ('0$ risk', '0 risk', 'nol risk', 'dollar risk', etc.)
3. Eliminates exaggerated salary claims ('$2000', '$3000', '$5000', etc.)
4. Eliminates dead website URLs ('arkadas.uz') and non-working phone numbers ('+998')
5. Ensures contact strictly points to Telegram @arkadasuzz
"""

import re
from typing import List

FORBIDDEN_PATTERNS = [
    # False / gimmicky risk and dollar claims
    (r"(?i)\b0\s*\$\s*risk\b", "Oldindan to'lovsiz"),
    (r"(?i)\b0\s*risk\b", "Xavfsiz va shaffof"),
    (r"(?i)\bnol\s*risk\b", "Ishonchli va kafolatli"),
    (r"(?i)\b0\s*\$\s*xavf\b", "Oldindan to'lovsiz"),
    (r"(?i)\b0\s*xavf\b", "To'liq xavfsiz"),
    (r"(?i)0\$\s*oldindan\s*to'lov", "Oldindan to'lovsiz"),
    (r"(?i)0\$\s*to'lov", "Oldindan to'lovsiz"),

    # False visa promises
    (r"(?i)0%\s*rad(?:\s*javobi)?", "yuqori qabul ko'rsatkichi"),
    (r"(?i)rad\s*etilishi\s*0%", "yuqori qabul ko'rsatkichi"),
    (r"(?i)viza\s*rad\s*etilishi\s*(?:deyarli\s*)?0(?:\s*%)?", "Elchixona uchun to'liq hujjatlar tayyorlanadi"),
    (r"(?i)viza\s*(?:kafolati|kafolatlangan|100%)", "Viza hujjatlarini professional tayyorlash"),
    (r"(?i)100%\s*viza", "Viza bo'yicha professional yo'riqnoma"),

    # Exaggerated salaries
    (r"(?i)\$2000\s*-\s*\$5000", ""),
    (r"(?i)\$1500\s*-\s*\$3000", ""),
    (r"(?i)\$2000", ""),
    (r"(?i)\$3000", ""),
    (r"(?i)\$5000", ""),

    # Dead website and phone numbers
    (r"(?i)https?://[^\s]*arkadas\.uz[^\s]*", "@arkadasuzz"),
    (r"(?i)www\.arkadas\.uz", "@arkadasuzz"),
    (r"(?i)arkadas\.uz", "@arkadasuz"),
    (r"(?i)\+998\s*\(?[0-9]{2}\)?\s*[0-9]{3}[-\s]?[0-9]{2}[-\s]?[0-9]{2}", "@arkadasuzz"),
    (r"(?i)\+998[0-9]{9}", "@arkadasuzz"),

    # Exaggerated hype & inappropriate terms (jannat, sehr, mo'jiza)
    (r"(?i)\btalabalar\s+uchun\s+jannat\b", "Talabalar uchun qulay maskan"),
    (r"(?i)\bjannat\b", "qulay maskan"),
    (r"(?i)\bjannati\b", "qulayligi"),
    (r"(?i)\bmo'?jiza\b", "ajoyib imkoniyat"),
    (r"(?i)\bmo'?jizalari\b", "imkoniyatlari"),
    (r"(?i)\bsehrli\b", "jozibali"),
    (r"(?i)\bsehri\b", "afzalliklari"),
    (r"(?i)\baqlbovar\s*qilmas\b", "katta")
]

def sanitize_post(text: str) -> str:
    """
    Sanitizes post text by applying regex replacements and cleaning up formatting.
    """
    if not text:
        return ""

    cleaned = text
    for pattern, replacement in FORBIDDEN_PATTERNS:
        cleaned = re.sub(pattern, replacement, cleaned)

    # Clean double spaces or double commas created by replacements
    cleaned = re.sub(r" {2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Ensure CTA consistency if telegram contact is mentioned
    cleaned = re.sub(r"(?i)@arkadasuz_bot", "@arkadasuzz", cleaned)

    return cleaned.strip()

def check_guardrail_violations(text: str) -> List[str]:
    """
    Returns a list of violations detected in the text, if any.
    """
    violations = []
    checks = [
        ("0$ risk yoki 0 risk", r"(?i)\b0\s*(\$)?\s*(risk|xavf)\b"),
        ("Asossiz viza kafolati", r"(?i)(0%\s*rad|viza\s*kafolat)"),
        ("Soxta maoshlar ($2000+)", r"(?i)\$[2-5]000"),
        ("Taqiqlangan telefon raqam", r"(?i)\+998"),
        ("Taqiqlangan veb-sayt", r"(?i)arkadas\.uz")
    ]
    for label, pat in checks:
        if re.search(pat, text):
            violations.append(label)
    return violations
