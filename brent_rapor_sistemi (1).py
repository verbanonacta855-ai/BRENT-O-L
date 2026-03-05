#!/usr/bin/env python3
"""
🛢️ BRENT HAM PETROL OTOMATİK RAPOR SİSTEMİ
Sabah 07:00 ve Akşam 20:00 - Türkiye Saati
"""

import os
import smtplib
import schedule
import time
import logging
import requests
from datetime import datetime
import pytz

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
TARGET_EMAIL   = "burakcetindagli@gmail.com"
FROM_EMAIL     = "brent@resend.dev"
TURKEY_TZ      = pytz.timezone("Europe/Istanbul")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PROMPT = """Sen dünyanın en iyi petrol piyasası analistisisin. Brent ham petrol hakkında KAPSAMLI Türkçe rapor hazırla.

1. 📊 TEKNİK ANALİZ: RSI, MACD, Bollinger, 20/50/200 MA, destek/direnç, Fibonacci
2. 🛢️ TEMEL ANALİZ: EIA stokları, OPEC+ kararları, arz/talep, ABD üretimi
3. 🌍 JEOPOLİTİK: Orta Doğu, Rusya-Ukrayna, İran, Libya, Hürmüz Boğazı
4. 💹 MAKRO: DXY, Fed faiz beklentileri, Çin ekonomisi, küresel PMI
5. 📈 POZİSYONLAR: COT raporu, spekülatif pozisyonlar, opsiyon piyasası
6. 🔮 SENARYO: Boğa/Ayı/Baz ve olasılıkları
7. 📅 YAKLAŞAN VERİLER: Bu hafta kritik veriler
8. 🎯 ÖZET: Fiyat, hedef, stop, GÜÇLÜ AL/AL/BEKLE/SAT/GÜÇLÜ SAT kararı

Türkçe, profesyonel ve detaylı yaz."""


def generate_report(report_type: str) -> str:
    now = datetime.now(TURKEY_TZ).strftime("%d %B %Y, %A - %H:%M")
    prompt = PROMPT + f"\n\nTarih: {now}\n{'SABAH' if report_type=='sabah' else 'AKSAM'} raporu hazırla."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 4000, "temperature": 0.7}
    }
    response = requests.post(url, json=payload, timeout=120)
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def report_to_html(text: str, report_type: str) -> str:
    now = datetime.now(TURKEY_TZ).strftime("%d %B %Y %H:%M")
    icon = "☀️" if report_type == "sabah" else "🌙"
    label = "SABAH" if report_type == "sabah" else "AKŞAM"
    lines = []
    for line in text.split("\n"):
        if line.startswith("# "):
            lines.append(f"<h1 style='color:#f59e0b'>{line[2:]}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2 style='color:#fbbf24;border-bottom:1px solid #374151'>{line[3:]}</h2>")
        elif line.startswith("- ") or line.startswith("• "):
            lines.append(f"<div style='margin:4px 0'>▸ {line[2:]}</div>")
        elif line.strip() == "":
            lines.append("<br>")
        else:
            lines.append(f"<p style='margin:6px 0;line-height:1.8'>{line}</p>")
    body = "\n".join(lines)
    return f"""<!DOCTYPE html><html><head><meta charset='UTF-8'></head>
<body style='background:#0d1117;color:#e5e7eb;font-family:monospace;max-width:800px;margin:0 auto;padding:32px'>
<div style='background:#111827;border:1px solid #374151;border-radius:16px;padding:32px'>
<div style='text-align:center;margin-bottom:24px;border-bottom:1px solid #374151;padding-bottom:16px'>
<div style='font-size:3rem'>{icon}</div>
<h1 style='color:#f59e0b;letter-spacing:4px;font-size:1.4rem;margin:8px 0'>BRENT HAM PETROL</h1>
<div style='color:#6b7280;font-size:0.8rem'>{label} RAPORU • {now}</div></div>
{body}
<div style='margin-top:24px;border-top:1px solid #374151;padding-top:12px;text-align:center;color:#4b5563;font-size:0.7rem'>
Brent Analiz Sistemi • Otomatik Rapor</div></div></body></html>"""


def send_email(report_text: str, report_type: str):
    now = datetime.now(TURKEY_TZ).strftime("%d.%m.%Y %H:%M")
    icon = "☀️" if report_type == "sabah" else "🌙"
    subject = f"{icon} Brent Petrol {report_type.capitalize()} Raporu — {now}"

    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={
            "from": f"Brent Bot <{FROM_EMAIL}>",
            "to": [TARGET_EMAIL],
            "subject": subject,
            "html": report_to_html(report_text, report_type),
            "text": report_text
        }
    )
    log.info(f"✅ Gönderildi: {subject} | {response.status_code}")


def send_morning_report():
    log.info("⏰ Sabah raporu...")
    try:
        send_email(generate_report("sabah"), "sabah")
    except Exception as e:
        log.error(f"❌ {e}")


def send_evening_report():
    log.info("⏰ Akşam raporu...")
    try:
        send_email(generate_report("aksam"), "aksam")
    except Exception as e:
        log.error(f"❌ {e}")


if __name__ == "__main__":
    import sys
    log.info("🛢️ Brent Petrol Rapor Sistemi Başlatıldı")
    if "--test" in sys.argv:
        log.info("🧪 Test maili gönderiliyor...")
        send_morning_report()
        sys.exit(0)
    schedule.every().day.at("07:00").do(send_morning_report)
    schedule.every().day.at("20:00").do(send_evening_report)
    log.info("✅ Aktif. Sabah 07:00 / Akşam 20:00")
    while True:
        schedule.run_pending()
        time.sleep(30)
