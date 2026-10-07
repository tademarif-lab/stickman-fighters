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
#     SDK_DIR     Android SDK yolu
#     NDK_DIR     Android NDK yolu
#
#  p4a'da `--launcher` secenegi kaldirilmistir. Giris noktasi,
#  `--private` dizinindeki `main.py` dosyasidir.
# -----------------------------------------------------------------------------
#
#  Disaridan cagrilir:  bash ANDROID/build_apk_docker.sh
# ==============================================================================
set -euo pipefail

ARCH="${ARCH:-arm64-v8a}"
PACKAGE="${PACKAGE:-com.katil5019.stickmanfighters}"
APP_NAME="${APP_NAME:-STICKMAN FIGHTERS}"
VERSION="${VERSION:-1.4.0}"
REQUIREMENTS="${REQUIREMENTS:-python3,pygame,setuptools}"
SDK_DIR="${SDK_DIR:-/home/user/.android/android-sdk}"
NDK_DIR="${NDK_DIR:-/home/user/.android/android-ndk}"
P4A_VENV="${P4A_VENV:-/home/user/app/venv}"
LOCAL_RECIPES="${LOCAL_RECIPES:-/home/user/app/andtools/local_recipes}"
KEYSTORE="${KEYSTORE:-/home/user/app/andtools/uygulama.keystore}"
ICON="${ICON:-/home/user/app/andtools/oyun_ikon.png}"
PRESPLASH="${PRESPLASH:-/home/user/app/andtools/kapak.png}"

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
# YEREL TARIF: python3 + hostpython3 surumunu 3.10'a sabitler
# ---------------------------------------------------------------------
# p4a varsayilan olarak Python 3.14 derliyor, ama pygame 2.1.0
# Python 3.12+'da derlenemiyor (longintrepr.h kaldirilmis).
# p4a ayrica python3 ile hostpython3 surumlerinin ayni olmasini zorunlu
# tutuyor, bu yuzden IKISI DE 3.10.14'e cekiliyor.
# LOCAL_RECIPES ortam degiskeniyle gelir (ANDROID/ salt-okunur baglanir,
# bu yuzden app dizinine kopyalanmaz -> APK'ya girmez).
if [ -d "$LOCAL_RECIPES/python3" ] && [ -d "$LOCAL_RECIPES/hostpython3" ]; then
  echo
  echo "--- yerel tarif (python3 + hostpython3 -> 3.10.14) ---"
  # Yamalar p4a'nin kendi tarif dizininden cozuluyor (get_recipe_dir
  # override'i), bu yuzden kopyalama gerekmiyor. Sadece dogrula.
  for r in python3 hostpython3; do
    SRC=$(python -c "import os, pythonforandroid.recipes.$r as m; print(os.path.dirname(os.path.abspath(m.__file__)))" 2>/dev/null)
    if [ -n "$SRC" ] && [ -d "$SRC" ]; then
      echo "  $r: p4a tarifi $SRC"
      echo "     yamalar: $(ls "$SRC"/*.patch "$SRC"/patches/*.patch "$SRC"/patches/*.diff 2>/dev/null | wc -l) adet"
    else
      echo "  $r: p4a tarifi bulunamadi ($SRC)"
    fi
  done
else
  echo
  echo "UYARI: $LOCAL_RECIPES/python3 veya hostpython3 eksik,"
  echo "       p4a varsayilan Python surumunu kullanir (pygame derlenemez)"
fi

echo
# ---------------------------------------------------------------------
# IMRALA
# ---------------------------------------------------------------------
# --release verilince p4a imzasiz APK uretir
# ("...-release-unsigned.apk") ve Android kurulumunu REDDEDER.
#
# Imza anahtari (keystore) repoda SABILIR: ANDROID/uygulama.keystore
# Boylece her derlemede ayni imza kullanilir ve kullanicilar uygulamayi
# GUNCELLEYEBILIR (farkli imza = "uygulama zaten yuklu" hatasi verir).
#
# NOT: bu anahtar oyunun kimligini belgeler, gizli bir sir degildir
# (zaten APK'nin icinde imza olarak bulunur).
KEYSTORE_PW="${KEYSTORE_PW:-katil5019}"
KEY_ALIAS="${KEY_ALIAS:-stickman}"

if [ ! -f "$KEYSTORE" ]; then
  echo "HATA: keystore bulunamadi: $KEYSTORE"
  echo "      (repoda ANDROID/uygulama.keystore olmali)"
  exit 1
fi
echo "--- keystore ---"
echo "  dosya : $KEYSTORE"
echo "  alias : $KEY_ALIAS"
keytool -list -keystore "$KEYSTORE" -storepass "$KEYSTORE_PW" 2>&1 \
  | grep -iE "alias|entry|valid" | head -4 || true

# ---------------------------------------------------------------------
# IKON / PRESPLASH
# ---------------------------------------------------------------------
# Verilmezse Android varsayilan bos ikonunu kullanir ( telefonda
# gri kare gorunur). 256x256 ikon + kapak presplash olarak kullanilir.
echo
echo "--- ikon / presplash ---"
for f in "$ICON" "$PRESPLASH"; do
  if [ -f "$f" ]; then
    echo "  VAR  $f"
  else
    echo "  YOK  $f  (varsayilan ikon kullanilacak)"
  fi
done

echo
echo "=== DERLEME BASLADI (10-120 dakika surebilir) ==="
# DIKKAT: p4a argumanlari (guncel surum):
#  - `--dir` p4a seviyesinde YOK; kaynak dizin `--private` ile verilir
#    (`--dir` sadece bootstrap'un build.py'sine p4a tarafindan iletilir).
#  - Sondaki konumsal `.` argumani da kaldirilmis.
#  - IMBALAMA: --keystore/--signkey/--keystorepw/--signkeypw p4a'ya
#    verilir; p4a bunlari P4A_RELEASE_* ortam degiskenlerine cevirip
#    gradle'a gecirir.
#  - `--sign` ise bootstrap'un KENDI build.py'sine ait bayrak. Gradle
#    sablonu imzalama blokunu `{% if args.sign %}` ile yaziyor:
#        build.tmpl.gradle:54  {% if args.sign -%} signingConfigs {...}
#        build.tmpl.gradle:78  release { signingConfig signingConfigs.release }
#    p4a bu bayragi OTOMATIK GEÇIRMEZ; `unknown_args` sayesinde dogrudan
#    bootstrap'a ulasir. YOKSA APK "IMZASIZ" uretilir, Android KURMAZ.
p4a apk \
  --arch="$ARCH" \
  --bootstrap=sdl2 \
  --sdk-dir="$SDK_DIR" \
  --ndk-dir="$NDK_DIR" \
  --android-api="$API" \
  --local-recipes="$LOCAL_RECIPES" \
  --private . \
  --release \
  --sign \
  --keystore="$KEYSTORE" \
  --signkey="$KEY_ALIAS" \
  --keystorepw="$KEYSTORE_PW" \
  --signkeypw="$KEYSTORE_PW" \
  --package="$PACKAGE" \
  --name="$APP_NAME" \
  --version="$VERSION" \
  --requirements="$REQUIREMENTS" \
  --icon="$ICON" \
  --presplash="$PRESPLASH" \
  --permission=INTERNET \
  --dist-name="STICKMAN-FIGHTERS-$VERSION"

echo
echo "=== DERLEME BITTI ==="
echo "--- uretilen APK dosyalari ---"
find . -maxdepth 3 -name '*.apk' 2>/dev/null | head -10
ls -la ./*.apk ./dist/*.apk 2>/dev/null || echo "(apk listelenemedi)"

# ---------------------------------------------------------------------
# IMBALAMA KONTROLU
# ---------------------------------------------------------------------
# p4a'nin `--sign` bayragi bootstrap'un build.py'sine gecer ve gradle
# sablonunu yeniden yazar. AMA bootstrap onbellekten geliyorsa
# (p4a-cache) sablon YENIDEN YAZILMAZ ve APK imzasiz kalir.
# Bu yuzden emin olmak icin APK'yi burada KENDIMIZ imzalariz.
#
# DIKKAT: Android 7+ (minApi 24) icin v1 (JAR) imzasi YETMEZ,
# v2/v3 (APK Signing Block) gerekir. Bu yuzden apksigner kullanilir
# (build-tools icinde gelir). jarsigner TEK BASINA yetmez.
echo
echo "=== IMBALAMA KONTROLU ==="

APK_OUT=""
for d in . ./dist; do
  a=$(ls -1 "$d"/*.apk 2>/dev/null | head -n1)
  if [ -n "$a" ]; then APK_OUT="$a"; break; fi
done

if [ -z "$APK_OUT" ]; then
  echo "HATA: APK dosyasi bulunamadi"
  exit 1
fi
echo "  APK: $APK_OUT ($(stat -c%s "$APK_OUT") bayt)"

imzali_mi() {
  unzip -l "$1" 2>/dev/null | grep -qiE 'META-INF/.*\.(RSA|DSA|EC)$'
}

if imzali_mi "$APK_OUT"; then
  echo "  durum: zaten IMZALI (p4a --sign calismis)"
else
  echo "  durum: IMZASIZ -> apksigner ile imzalaniyor"

  # build-tools icinden en yeni apksigner'i bul
  APKSIGNER=""
  for bt in $(ls -1d "$SDK_DIR"/build-tools/*/ 2>/dev/null | sort -V -r); do
    if [ -x "${bt}apksigner" ]; then APKSIGNER="${bt}apksigner"; break; fi
  done
  if [ -z "$APKSIGNER" ] && command -v apksigner >/dev/null 2>&1; then
    APKSIGNER=$(command -v apksigner)
  fi
  if [ -z "$APKSIGNER" ]; then
    echo "HATA: apksigner bulunamadi (SDK build-tools eksik)"
    echo "      APK imzasiz kalir -> telefona KURULAMAZ"
    exit 1
  fi
  echo "  apksigner: $APKSIGNER"

  mv "$APK_OUT" "${APK_OUT%.apk}.imzasiz.apk"
  set +e
  "$APKSIGNER" sign \
    --ks "$KEYSTORE" \
    --ks-key-alias "$KEY_ALIAS" \
    --ks-pass "pass:$KEYSTORE_PW" \
    --key-pass "pass:$KEYSTORE_PW" \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    --out "$APK_OUT" \
    "${APK_OUT%.apk}.imzasiz.apk" 2>&1 | tail -12
  rc=$?
  set -e
  rm -f "${APK_OUT%.apk}.imzasiz.apk"

  if imzali_mi "$APK_OUT"; then
    echo "  durum: IMZANDI ✓  ($(stat -c%s "$APK_OUT") bayt)"
    unzip -l "$APK_OUT" | grep -iE 'META-INF/.*\.(RSA|DSA|EC)$' | head -3
  else
    echo "HATA: imzalama basarisiz (apksigner rc=$rc)"
    exit 1
  fi
fi
