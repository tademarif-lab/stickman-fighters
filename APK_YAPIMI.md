# 📦 APK YAPIMI — KOPYALA YAPIŞTIR

Antigravity'ye (ya da Cursor/Claude/ChatGPT'ye) aşağıdaki metni
**olduğu gibi** ver. Projeyi inceleyip APK'yı derlemesini iste.

---

## 🤖 ANTIGRAVITY'E VERECEĞİN PROMPT

````
Bu Python/pygame oyununu Android APK olarak derle.

PROJE: STICKMAN FIGHTERS (Minecraft temalı 2D stickman dövüş oyunu)
KONUM: Bu klasördeki oyun dosyaları (main.py, ui.py, fight.py, classes.py,
       skills.py, touch.py, savegame.py, online.py vb.)

HEDEF: com.katil5019.stickmanfighters paket adlı, arm64-v8a, sürüm 1.4.0
       imzalı (release) bir APK üret. Çıktıyı APK_CIKTI/ klasörüne koy.

ŞU DOSYALAR ZATEN HAZIR — ÖNCE BUNLARI OKU VE KULLAN:
- ANDROID/prepare.py      → oyun dosyalarını ANDROID/app/ içine kopyalar
                            (p4a kaynak dosyaları kökte bekler)
- ANDROID/build_apk.sh    → tüm derleme akışı (p4a bootstrap + create)
- ANDROID/main_mobile.py  → APK giriş noktası (tam ekran + dokunmatik)
- ANDROID/app/requirements.txt

ÇALIŞTIR:
1) python3 ANDROID/prepare.py
2) bash ANDROID/build_apk.sh
   (p4a zaten kuruluysa sadece 5. adım gerekir:
    p4a create --arch=arm64-v8a \
      --package=com.katil5019.stickmanfighters \
      --name="STICKMAN FIGHTERS" --version=1.4.0 \
      --requirements=python3,pygame2,setuptools \
      --launcher=main_mobile.py --release \
      --permission=INTERNET --bootstrap=sdl2 .)

SORUN ÇIKARSA:
- 'recipe not found'      → p4a build_recipes --sdl2 --arch=arm64-v8a <tarif>
- cython sürüm hatası     → pip install "cython==0.29.37"
- NDK/SDK hatası          → ANDROIDAPI=31 NDKAPI=21 değişkenlerini kullan
- pygame import çalışmıyor→ requirements'ta 'pygame2' yerine 'pygame' dene
- derleme çok yavaş        → yalnızca arm64-v8a kullan, tüm mimarileri derleme

BİTİNCE:
- APK_CIKTI/ klasöründeki .apk dosyasının tam yolunu ve boyutunu bildir
- Derleme loglarındaki son 20 satırı özetle
````

---

## 🖥️ SEN (Antigravity kullanmadan) NASIL YAPARSIN

### Yöntem A — GitHub Actions (EN KOLAY, ücretsiz, 20-25 dk)
Bilgisayarına hiçbir şey kurmana gerek yok.

1. **github.com** → ücretsiz üye ol
2. **New repository** oluştur (Private olabilir)
3. Bu oyun klasörünü repoya yükle
   - ⚠️ **`.github` klasörü gizli olmamalı** (zaten var)
4. Repo sayfasında **Actions** sekmesi
5. Solda **ANDROID APK** iş akışını seç
6. **Run workflow** → 🟢 yeşil **Run workflow**
7. 20-25 dakika bekle (derleme ilerleme çubuğunda görünür)
8. Bittiğinde sayfada **Artifacts** çıkar
9. **STICKMAN-FIGHTERS-apk** → indir (zip)
10. Zip'i aç → `.apk` dosyasını telefona gönder
11. Telefonda dosyaya dokun →
    **"Bilinen kaynaklardan yükleme"** uyarısı → izin ver → **Kur** 🎉

> GitHub Actions ayda 2000 dakika ücretsiz; bu derleme ~20 dk.

### Yöntem B — Antigravity / Cursor / Claude Code (bilgisayarda)
1. Bu klasörü Antigravity'de aç
2. Yukarıdaki **ANTIGRAVITY'E VERECEĞİN PROMPT** bölümünü yapıştır
3. Ajanın derlemesini bekle
4. `APK_CIKTI/` klasöründe `.apk` çıkacak

### Yöntem C — WSL ile kendin
```powershell
wsl --install -d Ubuntu
```
Sonra Ubuntu içinde:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip ccache \
  autoconf automake libtool pkg-config cmake libffi-dev libssl-dev \
  zlib1g-dev libbz2-dev libncurses-dev libncursesw5-dev xz-utils \
  libjpeg-dev python3-dev build-essential
cd /mnt/c/.../STİCKMAN.FIGHTERS
bash ANDROID/build_apk.sh
```
APK → `APK_CIKTI/`

### Yöntem D — Docker
```bash
bash ANDROID/build_docker.sh
```

---

## ⚡ DERLEME ÖNCESİ BEKLENEN SÜRE

| Adım | Süre |
|---|---|
| p4a bootstrap (ilk sefer) | 10-20 dk |
| tarifleri derleme | 5-10 dk |
| APK derleme | 5-15 dk |
| **Toplam (ilk)** | **~30-45 dk** |
| Toplam (sonraki) | 10-15 dk |

---

## 🔧 SORUN GİDERME

| Hata | Çözüm |
|---|---|
| `No recipe named: pygame2` | `p4a build_recipes --sdl2 --arch=arm64-v8a pygame2` |
| `Cython version mismatch` | `pip install "cython==0.29.37"` |
| `NDK not found` | `ANDROIDAPI=31 NDKAPI=21 p4a bootstrap --sdl2` |
| `apk: package not found` | `p4a --version` kontrol et, `pip install -U python-for-android` |
| Oyun açılıp kapanıyor | `p4a create` sonuna `--debug` ekle → `tart` klasöründeki loga bak |
| Siyah ekran | `main_mobile.py` içinde `pygame.SCALED` kaldır, `FULLSCREEN` dene |
| Çok büyük APK (~90 MB normal) | `--arch` sadece `arm64-v8a` kalsın, `--release` kullan |

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