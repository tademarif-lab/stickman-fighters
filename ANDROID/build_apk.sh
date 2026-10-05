#!/usr/bin/env bash
# ============================================================
#  STICKMAN FIGHTERS - ANDROID APK DERLEME
#  python-for-android (p4a) + SDL2
#  Calistir:  bash ANDROID/build_apk.sh
#  Platform: Linux / macOS / WSL  (Docker da calisir: build_docker.sh)
# ============================================================
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
APP="$HERE/app"
OUT="$ROOT/APK_CIKTI"

export ANDROIDAPI=31
export NDKAPI=21
export ARCH=arm64-v8a

mkdir -p "$OUT"

echo "############################################################"
echo " 1/5) Kaynak dosyalar hazirlaniyor"
echo "############################################################"
cd "$ROOT"
python3 ANDROID/prepare.py

echo
echo "############################################################"
echo " 2/5) Bagimliliklar kuruluyor"
echo "############################################################"
if command -v apt-get >/dev/null 2>&1; then
  SUDO=sudo
  [ "$(id -u)" = "0" ] && SUDO=""
  $SUDO apt-get update -qq
  $SUDO apt-get install -y -qq --no-install-recommends \
    git zip unzip openjdk-17-jdk-headless python3-pip ccache \
    autoconf automake libtool pkg-config cmake \
    libffi-dev libssl-dev zlib1g-dev libbz2-dev \
    libncurses-dev libncursesw5-dev xz-utils libjpeg-dev \
    python3-dev build-essential
fi

echo
echo "############################################################"
echo " 3/5) Python for Android kuruluyor"
echo "############################################################"
python3 -m pip install -q --upgrade pip wheel 2>/dev/null || \
  pip3 install -q --upgrade pip wheel
python3 -m pip install -q "cython==0.29.37" "python-for-android" 2>/dev/null || \
  pip3 install -q "cython==0.29.37" "python-for-android"

echo
echo "############################################################"
echo " 4/5) Toolchain olusturuluyor (ilk seferde 10-20 dk)"
echo "############################################################"
p4a bootstrap --sdl2 --arch="$ARCH"

echo
echo " 4b) Gerekli tarifler derleniyor..."
for r in libffi openssl setuptools six packaging pyparsing cython \
         kivy sdl2_image sdl2_mixer sdl2_ttf pillow numpy; do
  echo "   -> $r"
  p4a build_recipes --sdl2 --arch="$ARCH" "$r" || echo "      (atlandi: $r)"
done

echo
echo "############################################################"
echo " 5/5) APK derleniyor (10-25 dk)"
echo "############################################################"
cd "$APP"
p4a create \
  --arch="$ARCH" \
  --package=com.katil5019.stickmanfighters \
  --name="STICKMAN FIGHTERS" \
  --version=1.4.0 \
  --requirements="$(cat requirements.txt | tr '\n' ',' | sed 's/,$//')" \
  --launcher=main_mobile.py \
  --release \
  --permission=INTERNET \
  --bootstrap=sdl2 \
  .

echo
echo "############################################################"
echo " APK araniyor..."
echo "############################################################"
find "$HOME/.python-for-android/build" -name "*.apk" -exec cp {} "$OUT"/ \; 2>/dev/null || true
ls -lh "$OUT" || true
echo
echo "APK klasoru: $OUT"
echo "Telefona at, dokun, 'bilinmeyen kaynaklardan kur' iznini ver."
