# 📦 STICKMAN FIGHTERS — ANDROID APK REHBERİ

`.bat` dosyaları telefonda **çalışmaz** — bu yüzden oyunun gerçek bir
**APK** sürümü hazırlandı. Telefona kurulabilir.

---

## 🚀 Yöntem 1 — BULUT (ÖNERİLEN, ücretsiz, 15-25 dk)

Bilgisayarına **hiçbir şey kurmana gerek yok**. Sadece internet + GitHub hesabı.

1. **GitHub'da yeni repo oluştur** (Private olabilir)
2. Tüm bu oyun klasörünü o repoya yükle
   (`.github/workflows/android-apk.yml` klasörü **gizli olmamalı**)
3. Repoda **Actions** sekmesine git
4. **"ANDROID APK"** workflow'unu bul → **Run workflow** → yeşil **Run**
5. ~15-25 dakika bekle (derleme sırasında ilerleme çubuğu görürsün)
6. Bitince job'un altında **Artifacts** bölümünde
   **`STICKMAN-FIGHTERS-apk`** görünür
7. Onu indir (zip), içinden `.apk` dosyasını çıkar
8. APK'yı **telefonuna gönder** (WhatsApp, e-posta, Google Drive…)
9. Telefonda dosyaya dokun → **"Bilinmeyen kaynaklardan yükleme"** iznini ver → **Kur**

> ⚠️ GitHub Actions ayda **2000 dakika** ücretsiz. APK derlemesi ~20 dk sürer.

---

## 🖥️ Yöntem 2 — Kendi bilgisayarında (WSL / Docker)

**Windows'ta:**
```powershell
wsl --install -d Ubuntu
```
Sonra Ubuntu içinde:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip ccache \
  libffi-dev libssl-dev build-essential autoconf libtool pkg-config \
  zlib1g-dev libbz2-dev libncurses-dev libncursesw5-dev xz-utils \
  libjpeg-dev cmake

cd /mnt/c/Users/KULLANICI/Masaüstü/STİCKMAN.FIGHTERS
bash ANDROID/build_apk.sh
```

APK → `APK_CIKTI/` klasörüne düşer.

**Docker varsa (her platformda):**
```bash
docker run --rm -v "$PWD":/work -w /work ubuntu:22.04 bash ANDROID/build_docker.sh
```

---

## 📂 ANDROID Klasöründe Ne Var?

| Dosya | Görevi |
|---|---|
| `main_mobile.py` | APK'nın giriş noktası (tam ekran, dokunmatik, çözünürlük) |
| `prepare.py` | Oyun dosyalarını + ikonu Android klasörüne kopyalar |
| `build_apk.sh` | p4a ile APK derler |
| `build_docker.sh` | Docker içinde derler |
| `build.bat` | Windows'ta WSL üzerinden derlemeyi başlatır |
| `app/` | Android projesi (derlenirken buraya oyun dosyaları gelir) |
| `../.github/workflows/android-apk.yml` | Bulut derleme iş akışı |

---

## 📱 Telefonda Kurulum

APK **"normal"** uygulama gibi kurulur:

1. APK dosyasını telefona taşı
2. Dosyaya dokun
3. **"Bilinen kaynaklardan yükleme"** uyarısı çıkar → **Ayarlar** → aç
4. **Geri** → **Kur**

---

## 🎮 Telefonda Kontroller

| Kontrol | İşlev |
|---|---|
| 🕹️ Sol alt **joystick** | Sola / sağa hareket |
| **1** | 1. özellik |
| **2** | 2. özellik |
| **3** | 3. özellik |
| **U** (pembe) | Ulti |
| **↑** | Zıpla |
| **↓** | Eğil (kaçınma) |

Menülerde her şey **dokunmayla** çalışır.

---

## 💾 Kayıt (Ruby, paketler, karakterler)

```
SAVE/oyun_kayit.json
```
Telefonda oynayıp bu klasörü PC'ye kopyalarsan ilerlemen taşınır.
(Sağlık verisi: `Android/data/com.katil5019.stickmanfighters/files/SAVE/`)

---

## ⚙️ Ayarlar

`MOBIL/mobil_config.json`:
```json
{
  "device": 0,          // 0 = telefon dikey, 1 = telefon yatay, 2 = tablet
  "layout": "coarse",   // "coarse" = parmak, "fine" = ince
  "show_touch": true,   // dokunmatik göstergesi
  "hud_scale": 1.0,
  "sensitivity": 1.0
}
```

Değiştirirsen **tekrar APK derlemen** gerekir.

---

## 🐛 Derleme Hatası mı Aldın?

| Hata | Çözüm |
|---|---|
| `cython` hatası | `pip install cython==0.29.37` (build script zaten yapıyor) |
| `recipe not found` | `p4a build_recipes --sdl2 pygame2` tek tek çalıştır |
| `NDK/SDK` hatası | GitHub Actions zaten doğru sürümleri kuruyor — Yöntem 1'i kullan |
| Oyun açılıp kapanıyor | `pygame2` yerine `pygame` dene (requirements'ta değiştir) |
| Siyah ekran | `p4a create` komutuna `--debug` ekle, loglara bak |