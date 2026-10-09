# -*- coding: utf-8 -*-
"""ANDROID / APK GIRIS NOKTASI.

python-for-android (p4a) tarafindan `main.py` olarak kullanilir.
- Tam ekran (immersive)
- Dokunmatik kontroller (touch.py) otomatik acilir
- Android geri tusu = ESC
- Cozunurluk cihaz ekranina gore ayarlanir

HATA RAPORLAMA
--------------
Telefonda logcat olmadan calistigimiz icin herhangi bir hatayi:
  1) `SAVE/hata.log` dosyasina yaziyoruz
  2) Ekranda kirmizi uzerine hata metnini BASIYORUZ (ekran goruntusu alinca
     hatanin tamamini gorebiliriz)
  3) logcat'a da yaziyoruz (adb bagliysa gorulur)

Bu olmadan Android'de "uygulama aniden kapandi" gorunur ve sebep
bulunamaz.
"""
import os
import sys
import traceback

os.environ.setdefault("SDL_VIDEO_X11_FORCE_EGL", "1")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("P4A_BOOTSTRAP", "sdl2")

import pygame

import settings

try:
    # APK icinde p4a giris noktasi `main.py` olmak ZORUNDA.
    # Oyunun asil girisi bu yuzden `oyun_ana.py` adiyla kopyalanir.
    import oyun_ana as game_main
except ImportError:
    # PC'de / telefonda calistirirken oyun dosyasi `main.py` olarak durur
    import main as game_main

PACKAGE = "com.katil5019.stickmanfighters"


# ------------------------------------------------------------------ HATA
def _hata_dosyasi():
    """Oyunun yanindaki SAVE klasoru (yazilabilir alan)."""
    kok = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(kok, "SAVE", "hata.log")


def hata_yaz(hata):
    """Hata metnini dosyaya + logcat'a yaz."""
    metin = "".join(traceback.format_exception(type(hata), hata,
                                              hata.__traceback__))
    try:
        d = os.path.dirname(_hata_dosyasi())
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(_hata_dosyasi(), "a") as f:
            f.write(metin + "\n")
    except Exception:
        pass
    # logcat (tag: Python)
    try:
        for ln in metin.splitlines():
            print("[SF-ERROR]", ln)
    except Exception:
        pass
    return metin


def hata_goster(metin, baslik="OYUN BASLATILAMADI"):
    """Hata metnini ekrana bas (ekran goruntusu alinca sebep gorulur)."""
    try:
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.init()
        ekran = pygame.display.get_surface()
        if ekran is None:
            ekran = pygame.display.set_mode((720, 1280), pygame.FULLSCREEN)
        w, h = ekran.get_size()
        ekran.fill((24, 8, 8))

        # eski bir yazi nesnesi varsa onu temizle
        try:
            eski = ekran.get_at((0, 0))
        except Exception:
            eski = None

        def yazi(boyut, renk):
            try:
                return pygame.font.Font(None, boyut)
            except Exception:
                return pygame.font.SysFont("monospace", boyut)

        f1 = yazi(int(h * 0.055), (255, 90, 90))
        f2 = yazi(max(14, int(h * 0.032)), (255, 215, 215))

        y = int(h * 0.06)
        ekran.blit(f1.render(baslik, True, (255, 90, 90)), (int(w * 0.06), y))
        y += int(h * 0.075)

        # satirlari sar (uzun satirlar ekrandan tasmasin)
        satir = max(18, int(h * 0.032) + 8)
        for ham in metin.splitlines()[-24:]:
            s = ham.rstrip()
            while s:
                parca, s = _kirp(s, f2, w - int(w * 0.12))
                if y + satir > h - int(h * 0.04):
                    break
                ekran.blit(f2.render(parca, True, (255, 215, 215)),
                           (int(w * 0.06), y))
                y += satir
            if y + satir > h - int(h * 0.04):
                break

        # alt bilgi
        f3 = yazi(max(12, int(h * 0.026)), (150, 150, 160))
        ekran.blit(f3.render("Detay: SAVE/hata.log", True, (150, 150, 160)),
                   (int(w * 0.06), h - int(h * 0.06)))
        pygame.display.flip()

        # dokunulana kadar bekle (veya 60 sn sonra cik)
        import time
        bitis = time.time() + 60
        while time.time() < bitis:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN,
                              pygame.KEYDOWN):
                    return
            pygame.display.flip()
            pygame.time.wait(60)
    except Exception:
        pass


def _kirp(metin, font, max_px):
    """Metni piksel genisligine gore kirpar."""
    if font.size(metin)[0] <= max_px:
        return metin, ""
    lo, hi = 1, len(metin)
    while lo < hi:
        orta = (lo + hi + 1) // 2
        if font.size(metin[:orta])[0] <= max_px:
            lo = orta
        else:
            hi = orta - 1
    return metin[:lo], metin[lo:]


# ------------------------------------------------------------------ EKRAN
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


def ekran_kur():
    pygame.init()
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

    # once SCALED dene, olmezse FULLSCREEN, sonra pencereli
    scr = None
    for bayraklar in ((pygame.FULLSCREEN | pygame.SCALED),
                      (pygame.FULLSCREEN,),
                      (pygame.RESIZABLE,)):
        try:
            scr = pygame.display.set_mode((w, h), bayraklar)
            if scr is not None:
                break
        except Exception:
            scr = None
    if scr is None:
        scr = pygame.display.set_mode((w, h))

    try:
        pygame.mouse.set_visible(False)
    except Exception:
        pass
    if getattr(settings, "ORIENTATION_LOCK", "portrait") == "portrait":
        try:
            pygame.display.rotate = lambda v: None
        except Exception:
            pass
    return w, h


# ------------------------------------------------------------------ ANA
def main():
    # ---- 1) oyun modunu ac (AYRI adim: hata cikarsa ekranda gorunur)
    w, h = ekran_kur()

    # ---- 2) oyunu kur
    oyun = game_main.Game(w, h, mobile=True)

    # ---- 3) calistir
    oyun.run()
    pygame.quit()


def baslat():
    try:
        main()
        return 0
    except KeyboardInterrupt:
        return 0
    except SystemExit:
        raise
    except BaseException as hata:          # Exception + SystemError
        metin = hata_yaz(hata)
        try:
            hata_goster(metin)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(baslat())
