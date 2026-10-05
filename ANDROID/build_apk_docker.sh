#!/usr/bin/env bash
# ==============================================================================
#  STICKMAN FIGHTERS - APK DERLEME
#  python-for-android'in RESMI docker imajini kullanir.
#
#  Neden docker?  Cunku p4a'nin ihtiyacı olan Android SDK / NDK / SDL2
#  derleme ortamini (p4a bootstrap) kurmak 30-45 dakika ve sürekli bozuluyor.
#  Imajda her sey hazir gelir: SDK + NDK + JDK17 + Cython + p4a.
#
#  Kullanim:
#      python3 ANDROID/prepare.py        # oyun dosyalarini hazirla
#      bash ANDROID/build_apk_docker.sh  # APK'yi derle
#
#  Cikti:
#      ANDROID/app/dist/STICKMAN-FIGHTERS-<surum>.apk
# ==============================================================================
set -euo pipefail

IMG="${P4A_IMAGE:-kivy/python-for-android:latest}"
ARCH="${ARCH:-arm64-v8a}"
PACKAGE="${PACKAGE:-com.katil5019.stickmanfighters}"
APP_NAME="${APP_NAME:-STICKMAN FIGHTERS}"
VERSION="${VERSION:-1.4.0}"
REQUIREMENTS="${REQUIREMENTS:-python3,pygame,setuptools}"
LAUNCHER="${LAUNCHER:-main_mobile.py}"
CACHE_MOUNT="${CACHE_MOUNT:-0}"

AND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$AND_DIR/app"
CACHE_DIR="$AND_DIR/.p4a-cache"

# p4a icinde python3 + p4a kurulmus sanal ortamin tam yolu
P4A_VENV="/home/user/app/venv"

# Android SDK / NDK yollari.
# DIKKAT: p4a bu yollari OTOMATIK BULMAZ, mutlaka --sdk-dir/--ndk-dir
# verilmesi gerekir (p4a'nin kendi CI'i da boyle yapar).
# Kaynak: python-for-android/ci/makefiles/android.mk
SDK_DIR="${SDK_DIR:-/home/user/.android/android-sdk}"
NDK_DIR="${NDK_DIR:-/home/user/.android/android-ndk}"

# ---------------------------------------------------------------- hazirlik
if [ ! -d "$APP_DIR" ]; then
  echo "HATA: $APP_DIR yok. Once 'python3 ANDROID/prepare.py' calistir."
  exit 1
fi
if [ ! -f "$APP_DIR/$LAUNCHER" ]; then
  echo "HATA: $APP_DIR/$LAUNCHER bulunamadi."
  exit 1
fi

echo "=============================================="
echo " STICKMAN FIGHTERS - APK DERLEME"
echo "=============================================="
echo "  imaj       : $IMG"
echo "  mimari     : $ARCH"
echo "  paket      : $PACKAGE"
echo "  surum      : $VERSION"
echo "  uygulama   : $APP_NAME"
echo "  gerekenler : $REQUIREMENTS"
echo "  giris       : $LAUNCHER"
echo "  SDK         : $SDK_DIR"
echo "  NDK         : $NDK_DIR"
echo "  onbellek   : $([ "$CACHE_MOUNT" = "1" ] && echo acik || echo kapali)"
echo "=============================================="
echo

# Docker konteyneri uid 1000 ile calisir, GitHub Actions calisma dizini
# ise uid 1001'e ait. dist/ icine yazabilmesi icin her seyi acilir yap.
chmod -R a+rwX "$APP_DIR" 2>/dev/null || true

# ---------------------------------------------------------------- onbellek
MOUNT=()
if [ "$CACHE_MOUNT" = "1" ]; then
  mkdir -p "$CACHE_DIR"
  chmod -R a+rwX "$CACHE_DIR"
  # bootstrap derlemesi en pahali kisim; onu bir sonraki kosuda
  # yeniden kullanmak icin konteynere baglanir.
  MOUNT=(-v "$CACHE_DIR:/home/user/.python-for-android")
  echo ">> onbellek baglandi: $CACHE_DIR"
else
  echo ">> onbellek kapali (ilk kosu onerilir, sonra CACHE_MOUNT=1 dene)"
fi

echo ">> docker imaji indiriliyor (buyuk olabilir, birkac dakika)..."
docker pull "$IMG"
echo

# ---------------------------------------------------------------- derleme
echo ">> APK derleniyor (30-45 dakika surebilir)..."
echo ">> Takilirsa: https://github.com/kivy/python-for-android/releases"
echo

docker run --rm \
  ${MOUNT[@]+"${MOUNT[@]}"} \
  -v "$APP_DIR:/home/user/app/work" \
  -w /home/user/app/work \
  -e LANG=en_US.UTF-8 \
  "$IMG" \
  bash -lc "
    set -euo pipefail
    . $P4A_VENV/bin/activate
    echo '--- konteyner icinde ---'
    python --version
    p4a --version
    java -version 2>&1 | head -1
    echo
    echo '--- SDK/NDK kontrolu ---'
    for d in '$SDK_DIR' '$NDK_DIR'; do
      if [ -d \"\$d\" ]; then
        echo \"  VAR  \$d\"
      else
        echo \"  YOK  \$d   <-- p4a burayi bulamaz!\"
        ls -la \$(dirname \$d) || true
        exit 1
      fi
    done
    echo \"  sdkmanager: \$(find '$SDK_DIR' -name sdkmanager -o -name avdmanager | head -3 | tr '\n' ' ')\"
    echo
    echo '--- derleme ---'
    p4a apk \
      --arch='$ARCH' \
      --bootstrap=sdl2 \
      --sdk-dir='$SDK_DIR' \
      --ndk-dir='$NDK_DIR' \
      --release \
      --package='$PACKAGE' \
      --name='$APP_NAME' \
      --version='$VERSION' \
      --requirements='$REQUIREMENTS' \
      --launcher='$LAUNCHER' \
      --permission=INTERNET \
      --dist-name=STICKMAN-FIGHTERS-$VERSION \
      .
    echo '--- bitti ---'
  "

# ---------------------------------------------------------------- sonuc
APK_DIR="$APP_DIR/dist"
echo
echo "=============================================="
if ls "$APK_DIR"/*.apk >/dev/null 2>&1; then
  echo " DERLEME BASARILI"
  echo "=============================================="
  ls -lh "$APK_DIR"/*.apk
  echo
  echo "APK: $APK_DIR"
  cp -f "$APK_DIR"/*.apk "$AND_DIR/../APK_CIKTI_STICKMAN-FIGHTERS.apk" 2>/dev/null || true
else
  echo " DERLEME BASARISIZ - APK bulunamadi"
  echo "=============================================="
  echo "Kontrol: ANDROID/app/dist/ ve yukari taraftaki hata mesaji"
  exit 1
fi
