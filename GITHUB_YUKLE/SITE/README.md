# STICKMAN FIGHTERS

Minecraft temalı 2D stickman dövüş oyunu.

## 🚀 Başlatma

| Dosya | Ne yapar |
|---|---|
| `OYUNU_BASLAT.bat` | Oyunu başlatır |
| `launcher.py` | KATİL5019 LAUNCHER |
| `SETUP\KURULUMU_BASLAT.bat` | Kurulum ekranı (PC + telefon) |
| `SETUP\MOBIL_KURULUM.bat` | Mobil kurulum ekranı |
| `SUNUCU_BASLAT.bat` | Online sunucu (4 kişilik oda) |

## 📁 Klasör yapısı

| Dosya | Görevi |
|---|---|
| `main.py` | Ana döngü, ekran yönlendirme, girdi |
| `settings.py` | Tüm sabitler, haritalar, eski yetenekler, CHANGELOG |
| `classes.py` | **30 karakter sınıfı + 129 yetenek + 8 paket** |
| `skills.py` | **Yetenek motoru** (mermi, alan, ışın, dalga, minyon, kanca…) |
| `savegame.py` | **Ruby, kayıt sistemi, paket/karakter kilitleri** |
| `fight.py` | Dövüş sahnesi, zombi/boss/futbol/laser modları |
| `stickman.py` | Oyuncu karakteri (sınıf sistemi, durum efektleri) |
| `chars.py` | Karakter/yaratık çizim kütüphanesi |
| `hud.py` | Can barı, kalkan, yetenek yuvaları, durum rozetleri |
| `ui.py` | Menü, karakter seçim, ayarlar, dükkan, güncellemeler |
| `touch.py` | Dokunmatik kontroller (mobil) |
| `netproto.py` | Online protokolü |
| `online.py` | Online lobi + maç ekranı |
| `server.py` | Online sunucu |
| `SAVE/` | Kayıt dosyası (`oyun_kayit.json`) |
| `MOBIL/` | Mobil kurulum çıktısı |

## 💎 Ruby & Paketler

Arena dışındaki modlarda oyun başına **0.5 Ruby** kazanılır.
Ruby `SAVE/oyun_kayit.json` içinde saklanır.

| Paket | Ruby | Karakterler |
|---|---|---|
| CANSIZ PAKET | 5 | Vampir, Zombi, İskelet, Mutant, G.Zombi, G.İskelet, Mutant 2.0, G.Vampir |
| ELEMENT KAOSU | 15 | Zehir Kralı, Ateş Manyağı, Madenci, Su Kralı, Yıldırım Patronsu, Element Kralı, Hava Patronsu |
| FAN CHARACTERS | 25 | Steve, Alex |
| MİNESTİK İNSANI | 15.50 | Şövalye, Okçu |
| ORTA ÇAĞ SAVAŞÇILARI | 5.50 | *(henüz eklenmedi)* |
| DARVEL CHARACTERS | 40 | Çelik Adam, Parazit |
| SAÇMA PAKET | 55 | Hırsız, Spirit, The Machine, Suikastçi, Hazine Bağımlısı |
| SKİBİDİ TOİLET | 100 | Cameraman, Speakerman, TV Man |

## 🌐 Online

Detaylı rehber: **`ONLINE_REHBERI.md`**

## 📱 Mobil / APK

`.bat` dosyaları **telefonda çalışmaz** — bu yüzden gerçek bir **APK** sürümü hazırlandı.

| Dosya | Görevi |
|---|---|
| `ANDROID/BUILD_APK.md` | **📖 APK rehberi (adım adım)** |
| `ANDROID/main_mobile.py` | APK giriş noktası (tam ekran + dokunmatik) |
| `ANDROID/prepare.py` | Oyun dosyalarını + ikonu Android klasörüne kopyalar |
| `ANDROID/build_apk.sh` | p4a ile APK derler (Linux/mac/WSL) |
| `ANDROID/build_docker.sh` | Docker içinde APK derler |
| `ANDROID/build.bat` | Windows'ta WSL üzerinden derler |
| `.github/workflows/android-apk.yml` | **Bulut (GitHub Actions) APK derleme** |
| `MOBIL_REHBERI.md` | Mobil kontrol rehberi |

**En kolay yol:** Kodu GitHub'a at → **Actions** sekmesi → **ANDROID APK** →
**Run workflow** → 20 dk sonra **Artifacts**'tan `.apk` indir.

Detaylı rehber: **`MOBIL_REHBERI.md`**