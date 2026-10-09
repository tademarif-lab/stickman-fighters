#!/usr/bin/env bash
# ==============================================================================
#  APK DOGRULAMA (aapt2 + apksigner)
#
#  Konteyner icinde calisir. Iki seyi dogrular:
#    1) aapt2 dump badging  -> paket, ikon, ekran yonu, izinler, SDK
#    2) apksigner verify    -> imza sertifikasi ve imza semasi surumu
#
#  Kullanim (docker icinden):
#    bash apk_dogrula.sh <apk-yolu>
#
#  NOT: Bu dosya AYRI tutulur cunku ic ice tirmak gommeden calistirilir
#  (workflow'ta `docker run ... bash -lc '...'` icinde $SDK kayboluyordu).
# ==============================================================================
set -uo pipefail

APK="${1:-}"
if [ -z "$APK" ]; then
  echo "Kullanim: apk_dogrula.sh <apk-yolu>"
  exit 1
fi
if [ ! -f "$APK" ]; then
  echo "HATA: APK bulunamadi: $APK"
  exit 1
fi

SDK="${SDK_DIR:-/home/user/.android/android-sdk}"
echo "APK  : $APK"
echo "SDK  : $SDK"
echo "BOYUT: $(stat -c%s "$APK") bayt"
echo

# ------------------------------------------------------------------ aapt2
AAPT=$(ls -1 "$SDK"/build-tools/*/aapt2 2>/dev/null | sort -V | tail -n1)
if [ -z "$AAPT" ]; then
  AAPT=$(find "$SDK" -name aapt2 -type f 2>/dev/null | head -n1)
fi

echo "=== 1) aapt2 dump badging ==="
if [ -n "$AAPT" ] && [ -x "$AAPT" ]; then
  echo "aapt2: $AAPT"
  "$AAPT" dump badging "$APK" 2>/dev/null | head -45
  echo
  echo "--- OZET ---"
  BADGING=$("$AAPT" dump badging "$APK" 2>/dev/null)
  echo "$BADGING" | grep -E "^package:|sdkVersion|targetSdkVersion" | head -5
  echo "$BADGING" | grep -E "application(-label|-icon)?" | head -6
  YON=$(echo "$BADGING" | grep -iE "orientation" | head -1)
  if [ -n "$YON" ]; then
    echo "$YON"
  else
    echo "orientation : (badging ciktisinda yok)"
  fi
else
  echo "aapt2 BULUNAMADI (build-tools yok)"
fi

# ------------------------------------------------------------------ apksigner
echo
echo "=== 2) apksigner verify ==="
SIG=$(ls -1 "$SDK"/build-tools/*/apksigner 2>/dev/null | sort -V | tail -n1)
if [ -z "$SIG" ]; then
  SIG=$(find "$SDK" -name apksigner -type f 2>/dev/null | head -n1)
fi
if [ -n "$SIG" ] && [ -x "$SIG" ]; then
  echo "apksigner: $SIG"
  if "$SIG" verify --verbose --print-certs "$APK" 2>&1 | head -25; then
    :
  fi
  # v1 imzasi (META-INF) var mi?
  if unzip -l "$APK" 2>/dev/null | grep -qiE 'META-INF/.*\.(RSA|DSA|EC)$'; then
    echo "v1 (META-INF) : VAR"
  else
    echo "v1 (META-INF) : YOK"
  fi
else
  echo "apksigner BULUNAMADI"
fi

echo
echo "=== 3) APK icerigi ==="
unzip -l "$APK" 2>/dev/null | grep -E "\.so$|private\.tar|\.pyc$" | head -25
echo
echo "toplam girdi: $(unzip -l "$APK" 2>/dev/null | tail -1)"
