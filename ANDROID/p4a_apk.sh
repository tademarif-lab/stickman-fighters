#!/usr/bin/env bash
# ==============================================================================
#  STICKMAN FIGHTERS - p4a APK DERLEME (konteyner icinde calisir)
#
#  Bu dosya docker konteynerinin icinde calisir. Ortam degiskenleri ile
#  yapilandirilir:
#     ARCH        mimari              (arm64-v8a)
#     PACKAGE     paket adi
#     APP_NAME    uygulama adi
#     VERSION     surum
#     REQUIREMENTS  p4a gereksinimleri
#     LAUNCHER    giris noktasi dosyasi
#     SDK_DIR     Android SDK yolu
#     NDK_DIR     Android NDK yolu
#
#  Disaridan cagrilir:  bash ANDROID/build_apk_docker.sh
# ==============================================================================
set -euo pipefail

ARCH="${ARCH:-arm64-v8a}"
PACKAGE="${PACKAGE:-com.katil5019.stickmanfighters}"
APP_NAME="${APP_NAME:-STICKMAN FIGHTERS}"
VERSION="${VERSION:-1.4.0}"
REQUIREMENTS="${REQUIREMENTS:-python3,pygame,setuptools}"
LAUNCHER="${LAUNCHER:-main_mobile.py}"
SDK_DIR="${SDK_DIR:-/home/user/.android/android-sdk}"
NDK_DIR="${NDK_DIR:-/home/user/.android/android-ndk}"
P4A_VENV="${P4A_VENV:-/home/user/app/venv}"

echo "--- ortam ---"
# shellcheck disable=SC1090
. "$P4A_VENV/bin/activate"
python --version
p4a --version
java -version 2>&1 | head -1

echo
echo "--- SDK / NDK kontrolu ---"
for d in "$SDK_DIR" "$NDK_DIR"; do
  if [ -d "$d" ]; then
    echo "  VAR   $d"
  else
    echo "  YOK   $d   <-- p4a burayi bulamaz!"
    ls -la "$(dirname "$d")" 2>/dev/null || true
    exit 1
  fi
done
echo "  araclar: $(find "$SDK_DIR" -name sdkmanager -o -name avdmanager 2>/dev/null | head -3 | tr '\n' ' ')"

echo
echo "--- Android platform surumleri ---"
ls "$SDK_DIR/platforms" 2>/dev/null || echo "  (platforms klasoru yok)"

# p4a varsayilan API 33 ister ama imajda farkli bir surum kurulu olabilir.
# Kurulu olan EN YUKSEK surumu kullan.
API=$(ls "$SDK_DIR/platforms" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
if [ -z "$API" ]; then
  echo "HATA: SDK icinde android platformu bulunamadi"
  exit 1
fi
echo "  kullanilan API: $API"

# ---------------------------------------------------------------------
# YEREL TARIF: python3 surumunu 3.10'a sabitler
# ---------------------------------------------------------------------
# p4a varsayilan olarak Python 3.14 derliyor, ama pygame 2.1.0
# Python 3.12+'da derlenemiyor (longintrepr.h kaldirilmis).
# Yerel tarif python3 -> 3.10.14.
LOCAL_RECIPES="./local_recipes"
if [ -d "$LOCAL_RECIPES/python3" ]; then
  echo
  echo "--- yerel tarif (python3 3.10.14) ---"
  # p4a'nin kendi yama klasorunu kopyala (recipe_dir orijinale cevriliyor
  # ama --local-recipes verildiginde p4a once yerel dizini arar)
  P4A_SRC=$(python -c "import os, pythonforandroid.recipes.python3 as m; print(os.path.dirname(os.path.abspath(m.__file__)))")
  echo "  p4a kaynak: $P4A_SRC"
  if [ -d "$P4A_SRC/patches" ]; then
    cp -r "$P4A_SRC/patches" "$LOCAL_RECIPES/python3/" 2>/dev/null || true
    echo "  yamalar kopyalandi: $(ls "$LOCAL_RECIPES/python3/patches" | wc -l) adet"
  else
    echo "  UYARI: yama klasoru bulunamadi ($P4A_SRC/patches)"
  fi
  LOCAL_FLAG="--local-recipes=$LOCAL_RECIPES"
else
  echo
  echo "UYARI: $LOCAL_RECIPES/python3 yok, p4a varsayilan Python surumunu kullanir"
  echo "       (pygame derlenemeyebilir)"
  LOCAL_FLAG=""
fi

echo
echo "=== DERLEME BASLADI (40-60 dakika surebilir) ==="
p4a apk \
  --arch="$ARCH" \
  --bootstrap=sdl2 \
  --sdk-dir="$SDK_DIR" \
  --ndk-dir="$NDK_DIR" \
  --android-api="$API" \
  $LOCAL_FLAG \
  --release \
  --package="$PACKAGE" \
  --name="$APP_NAME" \
  --version="$VERSION" \
  --requirements="$REQUIREMENTS" \
  --launcher="$LAUNCHER" \
  --permission=INTERNET \
  --dist-name="STICKMAN-FIGHTERS-$VERSION" \
  .

echo
echo "=== DERLEME BITTI ==="
ls -la ./dist 2>/dev/null || echo "(dist klasoru yok)"
