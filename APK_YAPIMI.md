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
| gradle + paketleme | 5–10 dk |
| Aşama | Süre |
|---|---|
| Docker imajını indir (~4 GB) | 3–6 dk |
| **İlk koşu:** bootstrap + 12 tarif derleme | 60–120 dk |
| gradle + paketleme | 1–2 dk |
| **Önbellekli koşu** (`cache: evet`) | **8–15 dk** |

> `cache: evet` önbelleği **hata olsa bile** kaydeder (`if: always()`), yani
> başarısız koşudan sonra bir sonraki hızlıdır.
> GitHub Actions public repo'da sınırsız; süre limiti 6 saat.

---

## 🔧 BU PROJEDE ÇÖZÜLMÜŞ p4a TUZAKLARI

p4a sürümleri arasında çok şey değişmiş. Bu projede gerçekten takılılan
yerler ve çözümleri (tekrar yaşamaması için):

| # | Hata | Sebep | Çözüm |
|---|---|---|---|
| 1 | `Could not find 'android' or 'sdkmanager' binaries` | p4a SDK/NDK yolunu **otomatik bulmaz** | `--sdk-dir` + `--ndk-dir` ver. İmajda: `/home/user/.android/android-sdk`, `.../android-ndk` |
| 2 | `Requested API target 33 is not available` | İmajda API **36** kurulu, p4a 33 istiyor | `platforms/`'den **kurulu en yüksek** sürümü bul, `--android-api` ile ver |
| 3 | `python3 should have same version as hostpython3` | `python3` ve `hostpython3` **ayı sürüm** ister | **İkisini de** yerel tarifle aynı sürüme sabitle |
| 4 | `'longintrepr.h' file not found` | p4a Python **3.14** kuruyor; pygame 2.1.0 Python 3.12+'da derlenmiyor (`longintrepr.h` 3.12'de kaldırıldı) | `local_recipes/python3` **ve** `local_recipes/hostpython3` → **3.10.14** |
| 5 | `AttributeError: no attribute 'recipe_dir'` | p4a'da `recipe_dir` yok, **`get_recipe_dir()`** var | Yerel tarifte `get_recipe_dir()`'ı override et, p4a'nın kendi tarif dizinini döndür |
| 6 | `argument --launcher: ignored explicit argument` | `--launcher` artık **bayrak**, dosya adı almıyor | Giriş noktası `--private` içindeki `main.py`; `--launcher` **argümansız** |
| 7 | `unrecognized arguments: .` | Sondaki konumsal `.` kaldırılmış | Yazma |
| 8 | `unrecognized arguments: --dir` | `--dir` p4a seviyesinde **yok** | Yazma; kaynak dizin `--private` ile verilir |
| 9 | APK bulunamadı | p4a APK'yı `dist/` değil **çalışma dizinine** kopyalar | Önce app köküne, sonra `dist/`e bak |
| 10 | APK **imzasız** → Android kurmaz | `--keystore` tek başına yetmez; gradle şablonu `{% if args.sign %}` ile imzalama bloğunu yazar, **bootstrap önbellekten gelirse şablon yeniden yazılmaz** | `--sign` ekle **ve** derleme sonrası `apksigner` ile doğrula/gerekirse imzala |

### Neden Python 3.10?

p4a'nın `pygame` tarifi **pygame 2.1.0** (2021) derliyor. Bu sürüm
Python 3.6–3.10 arasını destekliyor ve C kodu `longintrepr.h` kullanıyor:

```
p4a python3 3.14.2  +  pygame 2.1.0   ->  derlenemez
p4a python3 3.10.14 +  pygame 2.1.0   ->  ✓
```

Oyunun kendi kodu da 3.10 uyumlu (3.11+ özelliği kullanılmıyor).

### İmza neden `apksigner` ile?

Android 7+ (`minApi 24`) için **v2/v3 APK Signing Block** gerekir.
`jarsigner` yalnızca **v1 (JAR)** üretir ve yetmez. `apksigner` v1+v2+v3
üretir → imajdaki `build-tools/*/apksigner` kullanılır.

| Toplam (önbellekli) | 8–15 dk |


---

## 📱 TELEFONDA KURULUM

1. **⬇ TELEFON SÜRÜMÜNÜ AL** düğmesine bas, ya da doğrudan:
   `https://github.com/tademarif-lab/stickman-fighters/releases/latest/download/STICKMAN-FIGHTERS-1.4.0.apk`
2. Dosyaya dokun
3. **"Bu uygulama tanınmayan bir geliştiriciden geliyor"** uyarısı
4. → **Ayarlar** → **İzin ver** → geri dön
5. **Kur** → aç

> 💡 Aynı imza anahtarı kullanıldığı için yeni sürümleri **güncelleme**
> olarak kurabilirsin (önceki sürümü silmen gerekmez).

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
