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
if [ ! -f "$APP_DIR/main.py" ]; then
  echo "HATA: $APP_DIR/main.py bulunamadi."
  echo "      (p4a giris noktasi = --private dizinindeki main.py)"
  exit 1
fi
for r in python3 hostpython3; do
  if [ ! -f "$AND_DIR/local_recipes/$r/__init__.py" ]; then
    echo "HATA: $AND_DIR/local_recipes/$r/__init__.py yok."
    echo "      (bu tarifler pygame'in Python 3.12+ ile derlenmesini engeller)"
    exit 1
  fi
done
# imza anahtari: ayni imzali APK uretebilmek icin sabit olmali
KEYSTORE="$AND_DIR/uygulama.keystore"
if [ ! -f "$KEYSTORE" ]; then
  echo "HATA: $KEYSTORE yok."
  echo "      Repoda olmali; yoksa APK imzasiz uretilir ve telefona kurulamaz."
  echo "      Olusturma:  keytool -genkeypair -v -keystore uygulama.keystore \\"
  echo "                  -storepass katil5019 -keypass katil5019 -alias stickman \\"
  echo "                  -keyalg RSA -keysize 2048 -validity 10000 \\"
  echo "                  -dname 'CN=STICKMAN FIGHTERS, O=KATIL5019, C=TR'"
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
echo "  giris       : main.py (p4a --private .)"
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

# p4a komutu ayri dosyada: ANDROID/p4a_apk.sh
# Boylece ic ice tirnak gommeden, sozdizimi yerinde dogrulanabilir.
P4A_SH="$AND_DIR/p4a_apk.sh"
if [ ! -f "$P4A_SH" ]; then
  echo "HATA: $P4A_SH bulunamadi"
  exit 1
fi
# konteynerde de erisilebilir olmasi icin app dizinine kopyala
cp -f "$P4A_SH" "$APP_DIR/p4a_apk.sh"
chmod a+rx "$APP_DIR/p4a_apk.sh"

# yerel tarifler (python3 3.10 sabitlemesi) de kopyalanir
rm -rf "$APP_DIR/local_recipes"
cp -r "$AND_DIR/local_recipes" "$APP_DIR/local_recipes"
find "$APP_DIR/local_recipes" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
chmod -R a+rwX "$APP_DIR/local_recipes"
echo ">> yerel tarifler kopyalandi:" $(ls "$APP_DIR/local_recipes")

# imza anahtari kopyalanir (p4a calisma dizininden okuyor)
cp -f "$KEYSTORE" "$APP_DIR/uygulama.keystore"
chmod a+rw "$APP_DIR/uygulama.keystore"
echo ">> keystore kopyalandi"

docker run --rm \
  ${MOUNT[@]+"${MOUNT[@]}"} \
  -v "$APP_DIR:/home/user/app/work" \
  -w /home/user/app/work \
  -e LANG=en_US.UTF-8 \
  -e ARCH="$ARCH" \
  -e PACKAGE="$PACKAGE" \
  -e APP_NAME="$APP_NAME" \
  -e VERSION="$VERSION" \
  -e REQUIREMENTS="$REQUIREMENTS" \
  -e SDK_DIR="$SDK_DIR" \
  -e NDK_DIR="$NDK_DIR" \
  -e P4A_VENV="$P4A_VENV" \
  "$IMG" \
  bash /home/user/app/work/p4a_apk.sh

# ---------------------------------------------------------------- sonuc
# p4a APK'yi `dist/` DEGIL, calisma dizininin KOKUNE kopyalar.
# (log: "# Android package renamed to ... .apk" -> cp ... -> work dir)
# Yine de her iki yeri de kontrol ediyoruz.
APK=""
for d in "$APP_DIR" "$APP_DIR/dist"; do
  if ls "$d"/*.apk >/dev/null 2>&1; then
    a=$(ls -1 "$d"/*.apk | head -n1)
    APK="$a"
    break
  fi
done

echo
echo "=============================================="
if [ -n "$APK" ]; then
  echo " DERLEME BASARILI"
  echo "=============================================="
  ls -lh "$APK"
  echo
  echo "APK: $APK"
  mkdir -p "$AND_DIR/../APK_CIKTI"
  cp -f "$APK" "$AND_DIR/../APK_CIKTI/STICKMAN-FIGHTERS-$VERSION.apk"
  echo "Kopya: $AND_DIR/../APK_CIKTI/STICKMAN-FIGHTERS-$VERSION.apk"
  # imzali mi kontrol et
  if ls "$AND_DIR/../APK_CIKTI"/*.keystore >/dev/null 2>&1; then
    echo "Keystore: $AND_DIR/../APK_CIKTI/*.keystore (sonraki derlemeler ayni imzayi kullanir)"
  fi
else
  echo " DERLEME BASARISIZ - APK bulunamadi"
  echo "=============================================="
  echo "Aranan yerler:"
  echo "  $APP_DIR"
  echo "  $APP_DIR/dist"
  echo
  echo "Mevcut dosyalar:"
  ls -la "$APP_DIR" 2>/dev/null | head -30 || true
  exit 1
fi
