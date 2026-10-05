# -*- coding: utf-8 -*-
"""ANDROID / APK GIRIS NOKTASI.

python-for-android (p4a) tarafindan main.py olarak kullanilir.
- Tam ekran (immersive)
- Dokunmatik kontroller (touch.py) otomatik acilir
- Android geri tusu = ESC
- Cozunurluk cihaz ekranina gore ayarlanir
"""
import os
import sys

os.environ.setdefault("SDL_VIDEO_X11_FORCE_EGL", "1")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("P4A_BOOTSTRAP", "sdl2")

import pygame

import settings
import main as game_main

PACKAGE = "com.katil5019.stickmanfighters"


def android_screen():
    """Cihaz ekraninin gercek piksel boyutu."""
    try:
        if "ANDROID_ARGUMENT" in os.environ:
            d = os.environ["ANDROID_ARGUMENT"]
            for part in d.split(" "):
                if part.startswith("--display-x="):
                    return int(part.split("=")[1]), None
    except Exception:
        pass
    return 0, 0


def main():
    pygame.init()
    # ekran modunu once kur (cozunurluk buradan geliyor)
    pygame.display.init()
    info = pygame.display.Info()
    w, h = android_screen()
    if not w:
        w, h = info.current_w, info.current_h
    if not w or not h:
        w, h = 1280, 720
    try:
        os.environ["SDL_VIDEO_WINDOW_FULLSCREEN_DISPLAY"] = str(h)
    except Exception:
        pass

    # tam ekran imleci gizle
    flags = pygame.FULLSCREEN | pygame.SCALED
    try:
        scr = pygame.display.set_mode((w, h), flags)
    except Exception:
        scr = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    if settings.ORIENTATION_LOCK == "portrait":
        try:
            pygame.display.rotate = lambda v: None
        except Exception:
            pass

    g = game_main.Game(w, h, mobile=True)
    g.run()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
