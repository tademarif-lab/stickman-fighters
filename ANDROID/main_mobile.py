# -*- coding: utf-8 -*-
"""ANDROID / APK GIRIS NOKTASI  (p4a bunu `main.py` olarak kullanir)

NEDEN BOYLE BIR DOSYA VAR?
-------------------------
Telefonda Python hatasi gorunmez (logcat yoksa) ve NATIVE crash
(SIGSEGV) `try/except` ile YAKALANAMAZ. Bu yuzden:

  1) Her riskli adimdan once/sonra EKRANA buyuk bir renk + numara basilir.
     Uygulama olurse ekranda KALAN son numara nerede oldugunu soyler.
  2) Ayni bilgi `SAVE/hata.log` dosyasina da yazilir (flush'li).
  3) `set_mode` SADECE BIR KEZ cagrilir. Iki kez cagrilmak Android
     EGL tarafinda native crash yapiyordu.
  4) `pygame.SCALED` Android'da guvenilir degil -> kullanilmaz.
"""
import os
import sys
import time
import traceback

os.environ.setdefault("SDL_VIDEO_X11_FORCE_EGL", "1")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("P4A_BOOTSTRAP", "sdl2")

LOG = None
STEP = 0
RENK = [(58, 22, 22), (22, 40, 58), (24, 52, 32), (52, 42, 16),
        (42, 26, 54), (20, 50, 56), (54, 54, 20), (54, 26, 40)]
SURUM = 8


# ------------------------------------------------------------------ LOG
def _log_ac():
    global LOG
    if LOG is not None:
        return
    try:
        kok = os.path.dirname(os.path.abspath(__file__))
        d = os.path.join(kok, "SAVE")
        if not os.path.isdir(d):
            os.makedirs(d)
        LOG = open(os.path.join(d, "hata.log"), "a")
    except Exception:
        LOG = False


def yaz(*a):
    """Ekrana + dosyaya + logcat'a yaz."""
    s = " ".join(str(x) for x in a)
    try:
        print("[SF]", s)
    except Exception:
        pass
    _log_ac()
    if LOG:
        try:
            LOG.write(time.strftime("%H:%M:%S ") + s + "\n")
            LOG.flush()
        except Exception:
            pass


# ------------------------------------------------------------------ ADIM
def adim(no, baslik):
    """Ekrana buyuk renk + numara bas. Native crash sonrasi son gorunen
    adim nerede oldugunu gosterir."""
    global STEP
    STEP = no
    yaz("ADIM %d: %s" % (no, baslik))
    try:
        import pygame
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.init()
        ekran = pygame.display.get_surface()
        if ekran is None:
            return
        w, h = ekran.get_size()
        if w < 8 or h < 8:
            return
        ekran.fill(RENK[no % len(RENK)])
        try:
            f = pygame.font.Font(None, int(h * 0.28))
            fs = pygame.font.Font(None, max(16, int(h * 0.045)))
        except Exception:
            pygame.display.flip()
            return
        y = int(h * 0.22)
        ekran.blit(f.render(str(no), True, (255, 255, 255)),
                   (int(w * 0.42), y))
        y += int(h * 0.34)
        # baslik: sigmaya gore kirpar
        m = max(6, int(w * 0.045))
        parca = baslik
        while parca and fs.size(parca)[0] > w - int(w * 0.1):
            parca = parca[:-1]
        ekran.blit(fs.render(parca, True, (255, 255, 255)),
                   (int(w * 0.05), y))
        ekran.blit(fs.render("SF " + str(SURUM), True, (200, 200, 200)),
                   (int(w * 0.05), int(h * 0.08)))
        pygame.display.flip()
    except Exception:
        pass


def hata_yaz(hata):
    metin = "".join(traceback.format_exception(type(hata), hata,
                                              hata.__traceback__))
    yaz("!!! HATA !!!")
    for ln in metin.splitlines():
        yaz(ln)
    return metin


# ------------------------------------------------------------------ EKRAN
def cihaz_boyutu():
    """Cihaz ekraninin gercek boyutu."""
    # 1) p4a ANDROID_ARGUMENT
    try:
        a = os.environ.get("ANDROID_ARGUMENT", "")
        x = y = 0
        for p in a.split(" "):
            if p.startswith("--display-x="):
                x = int(p.split("=")[1])
            elif p.startswith("--display-y="):
                y = int(p.split("=")[1])
        if x > 0 and y > 0:
            return x, y
    except Exception:
        pass
    # 2) env
    try:
        x = int(os.environ.get("ANDROID_WIDTH", 0))
        y = int(os.environ.get("ANDROID_HEIGHT", 0))
        if x > 0 and y > 0:
            return x, y
    except Exception:
        pass
    return 0, 0


def ekran_ac():
    """`set_mode` SADECE BIR KEZ cagrilir. FULLSCREEN, SCALED yok."""
    import pygame
    adim(1, "pygame.init")
    pygame.init()
    pygame.display.init()

    w, h = cihaz_boyutu()
    if w <= 0 or h <= 0:
        try:
            sizes = pygame.display.get_desktop_sizes()
            if sizes:
                w, h = max(sizes, key=lambda s: s[0] * s[1])
        except Exception:
            pass
    if w <= 0 or h <= 0:
        w, h = 1280, 720
    yaz("cihaz boyutu: %dx%d" % (w, h))

    adim(2, "ekran aciliyor")
    # once 1x1 deneme: EGL bazen 0 boyutlu istegi kabul edip
    # native crash veriyor
    ekran = None
    for boyut in ((w, h), (1280, 720), (800, 480)):
        try:
            ekran = pygame.display.set_mode(boyut, pygame.FULLSCREEN)
            if ekran is not None and ekran.get_width() > 0:
                break
        except Exception as e:
            yaz("set_mode %s basarisiz: %s" % (boyut, e))
            ekran = None
    if ekran is None:
        raise RuntimeError("set_mode hicbir boyutta calismadi")

    sw, sh = ekran.get_size()
    yaz("ekran: %dx%d" % (sw, sh))
    if sw != w or sh != h:
        w, h = sw, sh

    adim(3, "ekran hazir %dx%d" % (w, h))
    return w, h, ekran


# ------------------------------------------------------------------ ANA
def main():
    w, h, ekran = ekran_ac()

    adim(4, "oyun modulleri")
    try:
        import oyun_ana as game_main
    except ImportError:
        import main as game_main
    yaz("oyun modulu: %s" % game_main.__name__)

    adim(5, "oyun kuruluyor")
    oyun = game_main.Game(w, h, mobile=True, surface=ekran)

    adim(6, "oyun basliyor")
    oyun.run()
    yaz("oyun bitti")


def baslat():
    _log_ac()
    yaz("===== STICKMAN FIGHTERS basladi (v%d) =====" % SURUM)
    yaz("python %s" % sys.version.split()[0])
    yaz("cwd %s" % os.getcwd())
    yaz("dosya %s" % os.path.abspath(__file__))
    try:
        main()
        yaz("normal bitti")
        return 0
    except KeyboardInterrupt:
        yaz("kesildi")
        return 0
    except BaseException as e:
        metin = hata_yaz(e)
        adim(9, "HATA VAR")
        # hatayi ekranda goster + dosyaya yazdik
        try:
            import pygame
            ekran = pygame.display.get_surface()
            if ekran is not None:
                w, h = ekran.get_size()
                ekran.fill((40, 8, 8))
                try:
                    f = pygame.font.Font(None, max(16, int(h * 0.04)))
                except Exception:
                    f = None
                if f:
                    y = int(h * 0.12)
                    for ln in metin.splitlines()[-20:]:
                        s = ln
                        while s and f.size(s)[0] > w - int(w * 0.1):
                            s = s[:-1]
                        if y > h - int(h * 0.1):
                            break
                        ekran.blit(f.render(s, True, (255, 200, 200)),
                                   (int(w * 0.05), y))
                        y += int(h * 0.045)
                pygame.display.flip()
                b = time.time() + 45
                while time.time() < b:
                    for ev in pygame.event.get():
                        if ev.type in (pygame.QUIT, pygame.FINGERDOWN,
                                       pygame.KEYDOWN):
                            return 1
                    pygame.time.wait(60)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(baslat())
