#!/usr/bin/env python3
"""
🛢️ BRENT HAM PETROL OTOMATİK RAPOR SİSTEMİ
Sabah 07:00 ve Akşam 20:00 - Türkiye Saati
Hedef: burakcetindagli@gmail.com
"""

import anthropic
import smtplib
import schedule
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz

# ==================== YAPILANDIRMA ====================
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"   # https://console.anthropic.com
GMAIL_ADDRESS    = "YOUR_GMAIL@gmail.com"        # Gönderen Gmail
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"       # Gmail > Güvenlik > Uygulama Şifresi
TARGET_EMAIL     = "burakcetindagli@gmail.com"
TURKEY_TZ        = pytz.timezone("Europe/Istanbul")
# ======================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sen dünyanın en iyi petrol piyasası analistisisin. Brent ham petrol hakkında ULTRA KAPSAMLI bir rapor hazırlıyorsun.

Raporda şunları mutlaka dahil et:

1. 📊 TEKNİK ANALİZ
   - RSI(14), MACD (sinyal çizgisi), Bollinger Bantları (üst/orta/alt)
   - 20, 50, 200 günlük hareketli ortalamalar
   - Destek ve direnç seviyeleri (en az 3 kademe)
   - Trend analizi (günlük, haftalık, aylık)
   - Stokastik osilatör, ATR, ADX
   - Fibonacci geri çekilme/uzantı seviyeleri
   - Hacim analizi, On-Balance Volume

2. 🛢️ TEMEL ANALİZ
   - EIA haftalık ham petrol ve benzin stok değişimleri
   - API stok tahminleri vs gerçekleşen
   - OPEC+ üretim kararları ve uyum oranları
   - ABD günlük ham petrol üretimi (mb/g)
   - Küresel arz/talep dengesi
   - Kırılgan/Bakken/Permian havzası üretimi
   - Rafine kapasite kullanım oranı
   - İhracat/ithalat verileri
   - Mevsimsel talep döngüsü

3. 🌍 JEOPOLİTİK & HABERLER
   - Orta Doğu gerilim barometresi (İsrail-Hamas, Suriye, Yemen)
   - Rusya-Ukrayna çatışması ve ihracat üzerindeki etkisi
   - İran nükleer anlaşma görüşmeleri ve yaptırım durumu
   - Libya üretim kesintileri
   - Nijerya güvenlik durumu
   - Irak Kürdistan bölgesi ihracat anlaşmazlıkları
   - Hürmüz Boğazı ve Süveyş Kanalı geçiş güvenliği
   - Suudi Arabistan politikaları

4. 💹 MAKRO EKONOMİ & DÖVİZ
   - DXY (Dolar Endeksi) seviyesi ve yönü — ters korelasyon analizi
   - Fed faiz beklentileri (CME FedWatch), Fed konuşmaları
   - ABD enflasyon verileri (CPI, PCE)
   - Küresel PMI verileri (ABD, Çin, AB)
   - Çin ekonomik toparlanması, Yuan kuru
   - Avrupa ekonomik durumu
   - Küresel resesyon/yumuşak iniş olasılıkları
   - Tahvil getirileri (10 yıllık ABD)

5. 🌡️ TALEP GÖSTERGELERİ
   - Çin ham petrol ithalatı (ton/ay)
   - Hindistan talep büyümesi
   - Jet yakıtı talebi ve hava yolu kapasitesi
   - Karayolu ulaşım istatistikleri
   - Mevsimsel sürüş sezonu / ısınma yakıtı talebi

6. ⚡ ALTERNATİF ENERJİ & BAĞLANTILI PİYASALAR
   - Doğal gaz fiyatları (TTF, Henry Hub) — ikame etkisi
   - Fuel oil ve mazot spread'leri
   - Yenilenebilir enerji kapasitesi büyümesi
   - EV penetrasyon hızı — uzun vadeli talep etkisi
   - Karbon emisyon fiyatları (ETS)

7. 📈 ALIM-SATIM POZİSYONLARI & AKIŞ
   - CFTC COT raporu: yönetilen para fon net pozisyonu
   - Spekülatif uzun/kısa pozisyon değişimi
   - Vadeli işlem hacimleri (CME/ICE)
   - Opsiyon piyasası: put/call oranı, implied volatility
   - Kritik açık faiz seviyeleri (büyük put/call yoğunlaşmaları)
   - ETF para akışları (USO, BNO)

8. 🔮 SENARYO ANALİZİ
   - 🐂 Boğa senaryosu (%X olasılık): Tetikleyiciler ve hedef
   - 🐻 Ayı senaryosu (%X olasılık): Tetikleyiciler ve hedef
   - ➡️ Baz senaryo (%X olasılık): Beklenti ve aralık

9. 📅 YAKLAŞAN KATALİZÖRLER
   - Bu hafta açıklanacak veriler (EIA, API, NFP, CPI vb.)
   - Önümüzdeki 2 haftada OPEC toplantısı/açıklama var mı?
   - Fed toplantıları
   - Merkez bankası kararları

10. 🎯 ÖZET & KARAR TABLOSU
    | Parametre | Değer |
    |-----------|-------|
    | Mevcut Fiyat | $XX.XX |
    | Günlük Değişim | +/-X.X% |
    | Teknik Görüş | AL/SAT/NÖTR |
    | Temel Görüş | AL/SAT/NÖTR |
    | Kısa Vade (1-3 gün) | Hedef / Stop |
    | Orta Vade (1-4 hafta) | Hedef / Stop |
    | Uzun Vade (1-3 ay) | Yön |
    | Genel Görüş | GÜÇLÜ AL / AL / BEKLE / SAT / GÜÇLÜ SAT |
    | Kritik Seviye | $XX.XX (kırılırsa yön değişir) |
    | Bugünün En Önemli Faktörü | ... |

Türkçe yaz. Güncel web verileri kullan. Raporu zengin ve detaylı yap."""


def generate_report(report_type: str) -> str:
    """Claude API ile rapor üretir (web search dahil)"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    now = datetime.now(TURKEY_TZ).strftime("%d %B %Y, %A - %H:%M")

    user_prompt = (
        f"Tarih ve Saat: {now} (Türkiye)\n\n"
        f"{'☀️ SABAH' if report_type == 'sabah' else '🌙 AKŞAM'} Brent Ham Petrol Piyasa Raporu hazırla. "
        "Web araması yaparak bugünkü en güncel gerçek verileri kullan. "
        "Kapsamlı, profesyonel ve Türkçe bir rapor oluştur."
    )

    log.info(f"Rapor üretiliyor: {report_type} | {now}")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_prompt}]
    )

    return "\n".join(
        block.text for block in response.content if block.type == "text"
    )


def report_to_html(report_text: str, report_type: str) -> str:
    """Raporu güzel HTML e-postaya çevirir"""
    now = datetime.now(TURKEY_TZ).strftime("%d %B %Y %H:%M")
    icon = "☀️" if report_type == "sabah" else "🌙"
    label = "SABAH" if report_type == "sabah" else "AKŞAM"

    # Satırları HTML'e çevir
    lines = []
    for line in report_text.split("\n"):
        if line.startswith("# "):
            lines.append(f"<h1 style='color:#f59e0b;font-size:1.5rem;margin:24px 0 8px'>{line[2:]}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2 style='color:#fbbf24;font-size:1.2rem;border-bottom:1px solid #374151;padding-bottom:4px;margin-top:20px'>{line[3:]}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3 style='color:#d97706;font-size:1rem;margin-top:16px'>{line[4:]}</h3>")
        elif line.startswith("- ") or line.startswith("• "):
            lines.append(f"<div style='margin:4px 0;padding-left:12px'>▸ {line[2:]}</div>")
        elif line.strip() == "":
            lines.append("<br>")
        elif "|" in line and line.strip().startswith("|"):
            # Tablo satırı
            cells = [c.strip() for c in line.split("|")[1:-1]]
            row = "".join(f"<td style='padding:8px 12px;border:1px solid #374151'>{c}</td>" for c in cells)
            lines.append(f"<tr>{row}</tr>")
        else:
            lines.append(f"<p style='margin:6px 0;line-height:1.8'>{line}</p>")

    body = "\n".join(lines)

    return f"""<!DOCTYPE html>
<html>
<head><meta charset='UTF-8'></head>
<body style='background:#0d1117;color:#e5e7eb;font-family:monospace;max-width:800px;margin:0 auto;padding:32px'>
  <div style='background:linear-gradient(135deg,#111827,#1f2937);border:1px solid #374151;border-radius:16px;padding:32px'>
    <div style='text-align:center;margin-bottom:32px;border-bottom:1px solid #374151;padding-bottom:24px'>
      <div style='font-size:3rem'>{icon}</div>
      <h1 style='color:#f59e0b;letter-spacing:4px;font-size:1.4rem;margin:8px 0'>BRENT HAM PETROL</h1>
      <div style='color:#6b7280;font-size:0.8rem;letter-spacing:2px'>{label} RAPORU • {now}</div>
    </div>
    <div style='line-height:1.8'>
      {body}
    </div>
    <div style='margin-top:32px;padding-top:16px;border-top:1px solid #374151;text-align:center;color:#4b5563;font-size:0.7rem'>
      Brent Analiz Sistemi • Otomatik Rapor • burakcetindagli@gmail.com
    </div>
  </div>
</body>
</html>"""


def send_email(report_text: str, report_type: str):
    """Gmail SMTP ile e-posta gönderir"""
    now = datetime.now(TURKEY_TZ).strftime("%d.%m.%Y %H:%M")
    icon = "☀️" if report_type == "sabah" else "🌙"
    subject = f"{icon} Brent Petrol {report_type.capitalize()} Raporu — {now}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = TARGET_EMAIL

    # Düz metin + HTML
    msg.attach(MIMEText(report_text, "plain", "utf-8"))
    msg.attach(MIMEText(report_to_html(report_text, report_type), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, TARGET_EMAIL, msg.as_string())

    log.info(f"✅ E-posta gönderildi: {TARGET_EMAIL} | {subject}")


def send_morning_report():
    log.info("⏰ Sabah raporu başlatılıyor...")
    try:
        report = generate_report("sabah")
        send_email(report, "sabah")
    except Exception as e:
        log.error(f"❌ Sabah raporu hatası: {e}")


def send_evening_report():
    log.info("⏰ Akşam raporu başlatılıyor...")
    try:
        report = generate_report("aksam")
        send_email(report, "aksam")
    except Exception as e:
        log.error(f"❌ Akşam raporu hatası: {e}")


if __name__ == "__main__":
    log.info("🛢️ Brent Petrol Rapor Sistemi Başlatıldı")
    log.info(f"📧 Hedef: {TARGET_EMAIL}")
    log.info("⏰ Sabah: 07:00 | Akşam: 20:00 (Türkiye)")

    # Test için hemen bir rapor gönder
    import sys
    if "--test" in sys.argv:
        log.info("🧪 TEST MODU — Rapor hemen gönderiliyor...")
        send_morning_report()
        sys.exit(0)

    # Zamanlayıcılar (Türkiye saatine göre)
    schedule.every().day.at("07:00").do(send_morning_report)
    schedule.every().day.at("20:00").do(send_evening_report)

    log.info("✅ Zamanlayıcılar aktif. Çalışıyor...")
    while True:
        schedule.run_pending()
        time.sleep(30)
