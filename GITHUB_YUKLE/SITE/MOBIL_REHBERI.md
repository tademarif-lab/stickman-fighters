# 📱 STICKMAN FIGHTERS — MOBİL PORT

## Kurulum

```
SETUP\MOBIL_KURULUM.bat
```

Açılan ekranda:
- **CİHAZ**: TELEFON (dikey) / TELEFON (yatay) / TABLET (yatay)
- **HEDEF ÇÖZÜNÜRLÜK**: 540×960 / 960×540 / 1280×800
- **KONTROL DÜZENİ**: KABA (parmak) / İNCE (jilet)
- **DOKUNMATİK GÖSTERGE**: açık / kapalı
- **KAYIT KLASÖRÜ**: `SAVE` klasörünü açar

**KURULUMU BİTİR** → `MOBIL/` klasörü oluşur (oyun dosyalarının kopyası + `mobil_config.json`).

---

## 🎮 Dokunmatik Kontroller

`touch.py` — mevcut oyun mantığıyla birebir aynı girdiyi üretir, yani
oyunda hiçbir değişiklik gerekmez.

| Kontrol | Konum | İşlev |
|---|---|---|
| 🕹️ **Joystick** | sol alt | sola/sağa hareket |
| **1** | sağ alt (en üst) | 1. özellik |
| **2** | sağ alt | 2. özellik |
| **3** | sağ alt | 3. özellik |
| **U** | sağ alt (ulti yanı) | Ulti |
| **↑** | sağ alt köşe | Zıpla |
| **↓** | sağ alt | Eğil (kaçınma) |

---

## 💾 Kayıt Sistemi

Kayıtlar her iki sürümde de aynı yerde:
```
SAVE/oyun_kayit.json
```
İçinde: **Ruby**, açılan **paketler**, **karakterler**, **seviyeler**, **istatistikler**.

Telefonda oynayıp PC'de `SAVE` klasörünü kopyalarsan ilerleme taşınır.
`mobil_setup.py` içindeki **KAYIT KLASÖRÜ** butonu klasörü direkt açar.

---

## 🔧 Notlar

- Mobil sürüm aynı Python dosyalarını kullanır (pygame).
- Hedef platform: **Android** (Termux / Pydroid 3) ve **iPad** (a-Shell / Pythonista).
- `mobil_config.json` cihaz ve düzen ayarlarını tutar.
- Mobilde **online mod** de çalışır (aynı ağdaki sunucuya bağlanılır).

---

# 📦 APK KURULUMU

`.bat` telefonda **çalışmaz**. Bu yüzden APK sürümü hazırlandı.

## En kolay yol: Bulut (GitHub Actions) — ücretsiz

1. GitHub'da yeni repo oluştur
2. Bu oyun klasörünü yükle (`.github` klasörü **gizli olmamalı**)
3. **Actions** → **ANDROID APK** → **Run workflow** → yeşil **Run**
4. 15-25 dk bekle
5. **Artifacts** → `STICKMAN-FIGHTERS-apk` → indir
6. Zip'i aç, içindeki `.apk` dosyasını **telefonuna gönder**
7. Telefonda dosyaya dokun → "Bilinmeyen kaynaklardan kur" iznini ver → **Kur**

## Kendi bilgisayarında

```powershell
wsl --install -d Ubuntu
```
Sonra Ubuntu içinde:
```bash
cd /mnt/c/.../STİCKMAN.FIGHTERS
bash ANDROID/build_apk.sh
```

Docker varsa:
```bash
bash ANDROID/build_docker.sh
```

APK → `APK_CIKTI/` klasörüne düşer.

## Telefonda kurulum

1. APK'yı telefona taşı (WhatsApp / e-posta / Drive)
2. Dosyaya dokun
3. **"Bilinen kaynaklardan yükleme"** uyarısı → Ayarlar → izin ver
4. **Kur** → aç

## APK bilgileri

| | |
|---|---|
| Paket adı | `com.katil5019.stickmanfighters` |
| Sürüm | 1.3.0 |
| Mimari | arm64-v8a (tüm modern telefonlar) |
| Yönelim | Yatay (sensorLandscape) |
| İzinler | INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK |
