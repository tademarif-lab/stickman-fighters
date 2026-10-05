# -*- coding: utf-8 -*-
"""TELEFONDA CALISTIR - Pydroid 3 / Termux icin.

Bu dosyayi calistirinca oyun tam ekran, dokunmatik kontrollerle baslar.
Oyun dosyalari bu klasorun (proje kokunun) icinde olmali.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    os.environ.setdefault("SDL_VIDEO_X11_FORCE_EGL", "1")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
except Exception:
    pass

import pygame

import main as game_main


def main():
    pygame.init()
    pygame.display.init()
    try:
        info = pygame.display.Info()
        w, h = info.current_w, info.current_h
    except Exception:
        w, h = 0, 0
    if not w or not h:
        w, h = 960, 540
    # dikey telefonu yatay dondur
    if h > w:
        w, h = h, w
    try:
        pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.SCALED)
    except Exception:
        pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    g = game_main.Game(w, h, mobile=True)
    g.run()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("\nHATA:", e)
        print("pygame kurulu mu?  Pydroid: Pip -> pygame")
        try:
            input("\nCikmak icin Enter")
        except Exception:
            pass
