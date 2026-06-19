# KargoBot

Geliver API uzerinden kargo yonetimi yapan Telegram botu.

## Ozellikler

- Fiyat sorgulama — Paket boyutlarina gore farkli kargo firmalarindan fiyat teklifi alma
- Adres yonetimi — Gonderici ve alici adresleri ekleme, listeleme, silme
- Kargo gonderme — Adres secip teklifler arasindan secim yaparak kargo olusturma
- Kargo takibi — Tum kargolari listeleme, detay goruntuleme, iptal etme
- Iade talebi — Mevcut gonderiler icin iade olusturma
- Webhook yonetimi — Takip guncellemeleri icin webhook ekleme/silme/test etme

## Gereksinimler

- Python 3.11+
- Geliver API hesabi
- Telegram Bot Token

## Kurulum

```bash
git clone https://github.com/kullanici/kargo.git
cd kargo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Yapilandirma

`.env.example` dosyasini `.env` olarak kopyalayip bilgilerinizi girin:

```bash
cp .env.example .env
```

| Degisken | Aciklama |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram botunuzun tokeni (@BotFather) |
| `GELIVER_API_TOKEN` | Geliver API tokeniniz |
| `GELIVER_ORGANIZATION_ID` | Geliver organizasyon ID'niz |
| `ALLOWED_USER_IDS` | Botu kullanabilecek Telegram kullanici ID'leri (virgulle ayirin) |

## Calistirma

```bash
python -m bot.main
```

## Docker ile Calistirma

```bash
docker build -t kargobot .
docker run -d --env-file .env kargobot
```

## Lisans

MIT
