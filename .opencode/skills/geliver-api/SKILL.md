---
name: geliver-api
description: Geliver kargo API dokümantasyonu. Adres, gönderi, fiyat, webhook ve diğer endpoint'ler için kullan. Base URL: https://api.geliver.io/api/v1. Tüm istekler Bearer token ile Authorization header'ı gerektirir.
---

# Geliver API Dokümantasyonu

Base URL: `https://api.geliver.io/api/v1`
Auth: `Authorization: Bearer {GELIVER_API_TOKEN}`
Content-Type: `application/json`

Doküman ana sayfası: https://docs.geliver.io/docs/home

---

## Adresler (Addresses)

### Adresleri Listele
```
GET /addresses?page=1&limit=10
```
Response: `{ "result": true, "data": [ {...}, ... ] }`
Pagination: `page` ve `limit` query parametreleri ile sayfalama.

Address objesi:
```json
{
  "id": "uuid",
  "name": "Ad Soyad / Şirket",
  "shortName": "Kısa ad (listelerde görünür)",
  "phone": "+905xxxxxxxxx",
  "email": "email@example.com",
  "address1": "Açık adres",
  "cityCode": "34",
  "cityName": "İstanbul",
  "districtID": 123,
  "districtName": "Kadıköy",
  "zip": "34700",
  "countryCode": "TR",
  "isDefaultSenderAddress": true,
  "isDefaultReturnAddress": true,
  "isRecipientAddress": false
}
```

### Tek Adres Getir
```
GET /addresses/{id}
```

### Gönderici Adresi Oluştur
```
POST /addresses
```
Body'de gönderici adres bilgileri + `isDefaultSenderAddress: true, isRecipientAddress: false`

### Alıcı Adresi Oluştur
```
POST /addresses
```
Body'de alıcı adres bilgileri + `isRecipientAddress: true, isDefaultSenderAddress: false`

### Adres Sil
```
DELETE /addresses/{id}
```

### Şehir Listesi
```
GET /cities
```

### İlçe Listesi
```
GET /districts?cityCode={cityCode}
```

---

## Gönderiler (Shipments)

### Gönderileri Listele (Sayfalı)
```
GET /shipments?page=1&limit=10
```
Pagination: `page` ve `limit` query parametreleri.

### Tüm Gönderiler
```
GET /shipments
```
Limit olmadan tüm gönderiler (dikkatli kullan).

### Tek Gönderi Getir
```
GET /shipments/{id}
```

Shipment objesi:
```json
{
  "id": "uuid",
  "barcode": "barkod",
  "trackingNumber": "takip no",
  "trackingStatus": {
    "trackingStatusCode": "TRANSIT",
    "statusDetails": "Yolda",
    "locationName": "İstanbul",
    "statusDate": "2024-01-01"
  },
  "senderAddress": { "name": "...", ... },
  "recipientAddress": { "name": "...", ... },
  "labelURL": "https://...",
  "trackingUrl": "https://...",
  "length": 30.0,
  "width": 20.0,
  "height": 10.0,
  "weight": 2.5,
  "desi": 6.0,
  "totalAmount": 150.00,
  "currency": "TL",
  "providerCode": "SURAT"
}
```

### Kargo Takip Durum Kodları
- `CREATED` - Oluşturuldu
- `PROCESSING` - İşleniyor
- `TRANSIT` - Yolda
- `PICKED_UP` - Teslim alındı
- `OUT_FOR_DELIVERY` - Dağıtımda
- `DELIVERY` - Teslim edildi

### Gönderi Oluştur (Sağlayıcı Seçerek)
```
POST /shipments
```
Body:
```json
{
  "senderAddressId": "uuid",
  "recipientAddressId": "uuid",
  "length": 30.0,
  "width": 20.0,
  "height": 10.0,
  "weight": 2.5,
  "providerCode": "SURAT",
  "providerServiceCode": "STANDART"
}
```

### Gönderi Oluştur (İki Adımlı)
Önce fiyat teklifi alınır (`GET /priceList`), sonra teklif kabul edilir (`POST /shipments`).

### Gönderi İptal
```
DELETE /shipments/{id}
```

### Gönderi İade
```
POST /returnShipment
Body: { "shipmentId": "uuid" }
```

### Gönderi Klonla
```
POST /shipments/{id}/clone
```

### Gönderi Güncelle
```
PUT /shipments/{id}
```

---

## Fiyat Sorgulama (Prices)

### Fiyat Teklifi Al
```
GET /priceList?paramType=parcel&length=30&width=20&height=10&weight=2.5&organizationId={orgId}
```
Response'da `priceList` array'i, her biri `offers` içerir.
Her offer: `providerCode`, `providerServiceCode`, `transportType`, `totalAmount`, `currency`

### Bakiye Sorgula
```
GET /balance
```

### Sağlayıcı Servis Kodları
```
GET /providerServiceCodes
```

---

## Webhook'lar

### Webhook'ları Listele
```
GET /webhook
```

### Webhook Oluştur
```
POST /webhook
```
Body:
```json
{
  "url": "https://...",
  "eventType": "SHIPMENT_STATUS_UPDATED",
  "headers": { "X-Custom": "value" }
}
```

### Webhook Sil
```
DELETE /webhook/{id}
```

### Webhook Test
```
POST /webhook/test
```

---

## Sağlayıcı Hesapları (Providers)

### Listele
```
GET /providerAccounts
```

### Oluştur
```
POST /providerAccounts
```

### Sil
```
DELETE /providerAccounts/{id}
```

---

## Kargo Şablonları (Parcel Templates)

### Listele
```
GET /parcelTemplates
```

### Oluştur
```
POST /parcelTemplates
```

### Sil
```
DELETE /parcelTemplates/{id}
```

---

## Hata Kodları

Doküman: https://docs.geliver.io/docs/error_codes

Standart response yapısı:
```json
{
  "result": false,
  "message": "Hata mesajı",
  "additionalMessage": "Detaylı hata açıklaması"
}
```

Başarılı response:
```json
{
  "result": true,
  "data": { ... }  // veya [...]
}
```

---

## Bot'ta Kullanılan Endpoint'ler

| Endpoint | Bot'taki Kullanım |
|---|---|
| `GET /addresses?page&limit` | Adres listesi |
| `GET /addresses/{id}` | Adres detay |
| `POST /addresses` | Adres oluşturma |
| `DELETE /addresses/{id}` | Adres silme |
| `GET /cities` | Şehir listesi |
| `GET /districts?cityCode` | İlçe listesi |
| `GET /shipments?page&limit` | Gönderi listesi |
| `GET /shipments/{id}` | Gönderi detay |
| `POST /shipments` | Gönderi oluşturma |
| `DELETE /shipments/{id}` | Gönderi iptal |
| `POST /returnShipment` | Gönderi iade |
| `GET /priceList?paramType=parcel&...` | Fiyat teklifi |
| `GET /webhook` | Webhook listesi |
| `POST /webhook` | Webhook oluşturma |
| `DELETE /webhook/{id}` | Webhook silme |
| `POST /webhook/test` | Webhook test |
