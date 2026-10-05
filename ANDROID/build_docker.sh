#!/usr/bin/env bash
# Docker ile APK derleme (her platformda calisir)
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."

docker run --rm \
  -v "$PWD":/work \
  -w /work \
  -e ANDROIDAPI=31 \
  -e NDKAPI=21 \
  ubuntu:22.04 \
  bash -c '
    set -e
    apt-get update -qq
    apt-get install -y -qq --no-install-recommends \
      git zip unzip openjdk-17-jdk-headless python3 python3-pip ccache \
      libffi-dev libssl-dev build-essential autoconf libtool pkg-config \
      zlib1g-dev libbz2-dev libncurses-dev libncursesw5-dev xz-utils \
      libjpeg-dev cmake ca-certificates
    pip3 install --break-system-packages -q --upgrade pip wheel
    pip3 install --break-system-packages -q python-for-android cython==0.29.37
    python3 ANDROID/prepare.py
    p4a bootstrap --sdl2 --arch=arm64-v8a
    for r in libffi openssl setuptools six packaging pyparsing \
             kivy sdl2-image sdl2-mixer sdl2-ttf pillow numpy cython; do
      p4a build_recipes --sdl2 --arch=arm64-v8a "$r" || true
    done
    cd ANDROID/app
    p4a create --arch=arm64-v8a \
      --package=com.katil5019.stickmanfighters \
      --name="STICKMAN FIGHTERS" --version=1.3.0 \
      --requirements=python3,pygame2,android,setuptools \
      --launcher=main_mobile.py --release \
      --permission=INTERNET --bootstrap=sdl2 .
    cd /work
    mkdir -p APK_CIKTI
    find "$HOME/.python-for-android/build" -name "*.apk" -exec cp {} APK_CIKTI/ \;
    ls -lh APK_CIKTI
  '

echo "APK -> APK_CIKTI/ klasöründe"