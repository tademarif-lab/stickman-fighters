# 🌐 STICKMAN FIGHTERS — İNDİRME SİTESİ

7/24 açık indirme sitesi + launcher'ın 2 hali.

## 📁 Yapı

| Dosya | Ne |
|---|---|
| `SITE/index.html` | Sitenin kendisi (tek dosya, mobil uyumlu) |
| `SITE/favicon.png` | Site ikonu |
| `SITE_HAZIRLA.py` | Site ayarını yazar + PC zip'i paketler |
| `YAYIN/STICKMAN-FIGHTERS-1.4.0-PC.zip` | PC sürümü (Releases'a yüklenecek) |
| `.github/workflows/site.yml` | Siteyi GitHub Pages'e yayınlar |
| `.github/workflows/android-apk.yml` | APK derler + Releases'a yükler |
| `APK_YAPIMI.md` | APK rehberi + Antigravity prompt'u |
| `MOBIL_REHBERI.md` | Mobil kontrol rehberi |
| `ONLINE_REHBERI.md` | Online mod rehberi |

---

## 🚀 İlk kez kurulum (5 adım)

### 1) Hazırla
```powershell
python SITE_HAZIRLA.py
```
Kendine sorar: **GitHub kullanıcı adın** (örn. `KATIL5019`).
Şunları yapar:
- `SITE/index.html` içindeki `OWNER` satırına adını yazar
- `SITE/favicon.png` oluşturur
- `YAYIN/STICKMAN-FIGHTERS-1.4.0-PC.zip` paketini hazırlar

### 2) GitHub'a yükle
Yeni repo oluştur (örn. `stickman-fighters`) ve **tüm klasörü** yükle.
> ⚠️ **`.github` klasörü gizli olmamalı!** GitHub'da "Include hidden files"
> kutusu var, işaretli olsun.

### 3) Siteyi yayınla
Repo → **Actions** → **SITE** → **Run workflow** → 🟢
~1 dakika sonra site açılır:
```
https://KATIL5019.github.io/stickman-fighters/
```

### 4) APK'yı derle
**Actions** → **ANDROID APK** → **Run workflow** → 🟢
20-25 dk. Bitince:
- APK **otomatik Releases'a yüklenir** (site butonu çalışmaya başlar)
- Artifacts'ten de indirebilirsin

### 5) PC zip'i Releases'a yükle
Repo → **Releases** → **New release**
- Tag: `v1.4.0`
- Başlık: `STICKMAN FIGHTERS 1.4.0`
- Dosya: `YAYIN/STICKMAN-FIGHTERS-1.4.0-PC.zip`

---

## 🖥️ PC SÜRÜMÜ butonu

`https://github.com/KATIL5019/stickman-fighters/releases/latest/download/STICKMAN-FIGHTERS-1.4.0-PC.zip`

Bu adres **her zaman son sürümü** verir — yeni sürüm çıkınca adres değişmez.

## 📱 TELEFON SÜRÜMÜ butonu

`https://github.com/KATIL5019/stickman-fighters/releases/latest/download/STICKMAN-FIGHTERS-1.4.0.apk`

APK workflow'u her derlemede bu dosyayı Releases'a otomatik yükler.

> APK henüz derlenmemişse buton 404 verir — önce 4. adımı yap.

---

## 🖥️ LAUNCHER'IN 2 HALİ

`KATİL5019 LAUNCHER` artık iki sürüm sunuyor:

| Buton | Ne yapar |
|---|---|
| **OYNA** | Oyunu başlatır |
| **TELEFON SÜRÜMÜ** | İndirme sitesini açar (GitHub Pages) |
| **KAPAT** | Çıkış |

Sitede **TELEFON SÜRÜMÜ**'ne basınca → **GitHub'a gider** → APK indirilir.

Site adresi `launcher.py` içinde:
```python
SITE_URL = "https://KATIL5019.github.io/stickman-fighters/"
```
Kendi adınla değiştirmek istersen burayı düzenle.

---

## 🎨 Sitenin içeriği

- **PC SÜRÜMÜ** butonu → ZIP indirir
- **TELEFON SÜRÜMÜ** butonu → GitHub'daki APK'ya gider
- 30 karakter / 129 yetenek / 8 paket kartları
- Online (4 kişilik oda) bilgisi
- Sistem gereksinimleri
- Rehber bağlantıları
- "SİTE 7/24 AÇIK" göstergesi

Renkler oyunla aynı: siyah-altın-mor.

---

## ⚡ Yeni sürüm çıkarsa

```powershell
# settings.py'de VERSION ve TAG'ı güncelle
python SITE_HAZIRLA.py
```
Sonra:
1. APK workflow'unu çalıştır (APK'yi yeni isimle Releases'a atar)
2. Releases'a yeni zip'i yükle

Site butonları `TAG` değerini `SITE/index.html` içindeki
`var TAG = "1.4.0";` satırından okur.