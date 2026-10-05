# STICKMAN FIGHTERS — ANDROID APK

Bu klasör **derleme** dosyalarını içerir. Kendisi kurulamaz; önce APK derlenir.

## 📖 Rehberler

| Dosya | Ne |
|---|---|
| **`../APK_YAPIMI.md`** | **⭐ ANA REHBER** — Antigravity prompt'u + 4 yöntem |
| `BUILD_APK.md` | Adım adım APK rehberi |
| `TELEFONDA_KURULUM.txt` | Telefonda okunacak düz metin (3 yöntem) |

## 🚀 En hızlı yol (telefonla bile olur)

GitHub Actions:
1. Kodu GitHub'a yükle
2. **Actions** → **ANDROID APK** → **Run workflow**
3. 20-25 dk bekle
4. **Artifacts** → `.apk` indir → telefona gönder → kur

## 🤖 Antigravity ile

`../APK_YAPIMI.md` içindeki **ANTIGRAVITY'E VERECEĞİN PROMPT** bölümünü kopyala yapıştır.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `prepare.py` | Oyun dosyalarını `app/` içine kopyalar (p4a kökte bekler) |
| `main_mobile.py` | APK giriş noktası (tam ekran + dokunmatik + çözünürlük) |
| `build_apk.sh` | p4a ile APK derler (Linux/mac/WSL) |
| `build_docker.sh` | Docker içinde derler |
| `build.bat` | Windows'ta WSL üzerinden derler |
| `app/` | Oyun kaynakları + `requirements.txt` |
| `../.github/workflows/android-apk.yml` | Bulut derleme iş akışı |

## Hedef

| | |
|---|---|
| Paket | `com.katil5019.stickmanfighters` |
| Sürüm | 1.4.0 |
| Mimari | arm64-v8a |
| Yönelim | Yatay (sensorLandscape) |
| İzinler | INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK |
| Beklenen boyut | ~60-95 MB (pygame + Python + SDL2) |