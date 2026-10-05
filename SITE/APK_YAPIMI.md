# 📦 APK YAPIMI

APK, **python-for-android'in (p4a) resmî Docker imajı** ile derlenir.
Bilgisayarına Android SDK/NDK kurmana gerek yok — imajda her şey hazır.

---

## ⚡ YÖNTEM A — GitHub Actions (EN KOLAY, ücretsiz)

Bilgisayarına hiçbir şey kurmana gerek yok.

1. Repoya yükle (`.github/workflows/android-apk.yml` dahil)
2. **Actions** sekmesi → **ANDROID APK**
3. **Run workflow**

| Ayar | Değer | Ne yapar |
|---|---|---|
| `arch` | `arm64-v8a` | Telefon mimarisi (2017+ Android) |
| `cache` | `hayir` | İlk koşuda `hayir` bırak (2. koşuda `evet` yap, hızlı) |
| `release` | `evet` | Bitince Releases'a otomatik yükler |

4. **35–55 dakika** bekle
5. Bittiğinde iki yerden APK çıkar:
   - **Artifacts** → `STICKMAN-FIGHTERS-apk` (zip)
   - **Releases** → `STICKMAN-FIGHTERS-1.4.0.apk` (doğrudan)

### Site butonu neden çalışmıyordu?

`SITE/index.html` APK'yı şu adresten çeker:
```
https://github.com/tademarif-lab/stickman-fighters/releases/latest/download/STICKMAN-FIGHTERS-1.4.0.apk
```
Bu dosya ancak iş akışı `release: evet` ile bitince oluşur.

---

## 🐳 YÖNTEM B — Kendi bilgisayarında Docker

Docker Desktop kuruluysa (Windows'ta WSL2 backend):

```powershell
python ANDROID\prepare.py
bash ANDROID/build_apk_docker.sh
```

APK → `ANDROID/app/dist/`

Onbellegi kullanmak (2. koşudan sonra hızlı):
```powershell
$env:CACHE_MOUNT="1"; bash ANDROID/build_apk_docker.sh
```

Başka mimari:
```powershell
$env:ARCH="armeabi-v7a"; bash ANDROID/build_apk_docker.sh
```

---

## 🧱 NASIL ÇALIŞIYOR?

```
ANDROID/prepare.py            oyun dosyalarını ANDROID/app/ içine kopyalar
ANDROID/app/main_mobile.py    APK giriş noktası (tam ekran + dokunmatik)
ANDROID/app/requirements.txt  python3 / pygame / setuptools
ANDROID/build_apk_docker.sh   p4a docker imajını çalıştırır
```

`prepare.py` neden gerekli? python-for-android kaynak dosyaları
**çalışma dizininin kökünde** bekler. Oyunu `ANDROID/app/` içine
kopyalıyoruz ki p4a nokta işaretlemesin.

p4a komutu (script içinde):

```
p4a apk --arch=arm64-v8a --bootstrap=sdl2 --release \
  --package=com.katil5019.stickmanfighters \
  --name="STICKMAN FIGHTERS" --version=1.4.0 \
  --requirements=python3,pygame,setuptools \
  --launcher=main_mobile.py --permission=INTERNET \
  --dist-name=STICKMAN-FIGHTERS-1.4.0 .
```

---

## 🔧 SORUN GİDERME

| Hata | Çözüm |
|---|---|
| `No recipe named: pygame2` | requirements'ta **`pygame`** olmalı, `pygame2` değil (p4a 2026'da ad `pygame`) |
| `Cython version mismatch` | Docker imajında Cython 0.29.36 kurulu — elle pip kurma, imajı kullan |
| `NDK not found` | Sorun değil, imajda NDK hazır. `--sdk-dir`/`--ndk-dir` **verme** |
| `bootstrap` saatlerce sürüyor | İlk koşu normal. 2. koşuda `cache: evet` seç |
| `APK bulunamadi` | `ANDROID/app/dist/` içine bak, loglarda `--- bitti ---` var mı kontrol et |
| Dockerfile `cp: permission denied` | `chmod -R a+rwX` eklenmiş; elle çalıştırıyorsan `icacls` gerekebilir |
| APK telefona kurulmuyor | Android 7+ olmalı. `arm64-v8a` = 64-bit telefon (eski 32-bit için `armeabi-v7a`) |
| Oyun açılıp kapanıyor | `--release` yerine `--debug` koy, logu `adb logcat` ile oku |
| Siyah ekran | `main_mobile.py` içinde `SCALED` yerine `FULLSCREEN` dene |

---

## ⚡ GERÇEKÇİ SÜRELER

| Aşama | Süre |
|---|---|
| Docker imajını indir (~4 GB) | 3–6 dk |
| p4a bootstrap (SDL2 + Python + NDK) | 20–35 dk |
| tarifleri derle (pygame, Pillow…) | 8–15 dk |
| gradle + paketleme | 5–10 dk |
| **Toplam (ilk koşu)** | **~40–60 dk** |
| Toplam (önbellekli) | 8–15 dk |

> GitHub Actions aylık 2000 dakika ücretsiz (public repo'da sınırsız).
> GitHub'da Actions **dakikası bitmeyen** makinede çalışır, süre limiti 6 saat.

---

## 📱 TELEFONDA KURULUM

1. `.apk` dosyasını telefona gönder (WhatsApp / Drive / USB)
2. Dosyaya dokun
3. **"Bu uygulama tanınmayan bir geliştiriciden geliyor"** uyarısı
4. → **Ayarlar** → **İzin ver** → geri dön
5. **Kur** → aç

## 🎮 KONTROLLER

| | |
|---|---|
| 🕹️ sol alt joystick | sola / sağa |
| **1 2 3** | yetenekler |
| **U** (pembe) | Ulti |
| **↑ ↓** | zıpla / eğil |
| menüler | her yere dokun |

## 💾 KAYIT

```
Android/data/com.katil5019.stickmanfighters/files/SAVE/oyun_kayit.json
```

Bu klasörü PC'ye kopyalarsan Ruby + paketler + karakterler taşınır.
