# -*- coding: utf-8 -*-
"""MOBİL KURULUM EKRANI - telefon/tablet portu icin hazirlik.

Bu ekran:
  * cihaz tipi secimi (telefon / tablet)
  * yon (dikey / yatay)
  * kontrol duzeni (kaba / ince)
  * dokunmatik gosterge ac/kapa
  * kayit klasorunu gosterir (SAVE klasoru)
  * kurulum dosyalarini hazirlar (MOBIL klasoru + yapilandirma)

Calistirma:  SETUP\\MOBIL_KURULUM.bat
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import pygame

import settings
from settings import python_no_window, draw_text, blend, GOLD, get_font

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(ROOT, "SAVE")
MOBIL_DIR = os.path.join(ROOT, "MOBIL")
CONF_PATH = os.path.join(MOBIL_DIR, "mobil_config.json")

DEVICES = ["TELEFON (PORTRAIT)", "TELEFON (YATAY)", "TABLET (YATAY)"]
DEV_SIZE = [(540, 960), (960, 540), (1280, 800)]
LAYOUTS = [("KABA (PARMAK)", "coarse"), ("İNCE (JİLET)", "fine")]


def load_conf():
    d = {"device": 0, "layout": "coarse", "show_touch": True,
         "hud_scale": 1.0, "sensitivity": 1.0}
    try:
        with io.open(CONF_PATH, "r", encoding="utf-8") as f:
            d.update(json.load(f))
    except Exception:
        pass
    return d


def save_conf(d):
    try:
        if not os.path.isdir(MOBIL_DIR):
            os.makedirs(MOBIL_DIR)
        with io.open(CONF_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=2))
        return True
    except Exception as e:
        print("kayit hatasi:", e)
        return False


class MobileSetup:
    def __init__(self):
        python_no_window()
        pygame.init()
        self.W, self.H = 900, 640
        self.scr = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("STICKMAN FIGHTERS - MOBİL KURULUM")
        self.clock = pygame.time.Clock()
        self.bg = (16, 20, 34)
        self.t = 0.0
        self.conf = load_conf()
        self.msg = "Ayarları değiştir, sonra KURULUMU BİTİR"
        self.msg_col = (170, 178, 200)
        self.buttons = {}
        self._build()

    def _build(self):
        cx = self.W // 2
        self.buttons["cihaz"] = pygame.Rect(cx - 170, 150, 340, 46)
        self.buttons["yon"] = pygame.Rect(cx - 170, 208, 340, 46)
        self.buttons["duzen"] = pygame.Rect(cx - 170, 266, 340, 46)
        self.buttons["gosterge"] = pygame.Rect(cx - 170, 324, 340, 46)
        self.buttons["kaydet"] = pygame.Rect(cx - 170, 392, 340, 54)
        self.buttons["cikis"] = pygame.Rect(cx - 120, 560, 240, 46)
        self.buttons["klasor"] = pygame.Rect(cx - 170, 462, 340, 40)

    def handle(self, e):
        if e.type == pygame.QUIT:
            return False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return False
            if e.key in (pygame.K_UP, pygame.K_w):
                self._cycle(-1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self._cycle(1)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self._focus == "kaydet":
                    self.apply()
                else:
                    self._cycle(1)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for k, r in self.buttons.items():
                if r.collidepoint(e.pos):
                    if k == "cihaz":
                        self.conf["device"] = (self.conf["device"] + 1) % 3
                    elif k == "duzen":
                        self.conf["layout"] = ("coarse" if self.conf["layout"]
                                               == "fine" else "fine")
                    elif k == "gosterge":
                        self.conf["show_touch"] = not self.conf["show_touch"]
                    elif k == "kaydet":
                        self.apply()
                    elif k == "cikis":
                        return False
                    elif k == "klasor":
                        os.startfile(SAVE_DIR) if os.path.isdir(SAVE_DIR) else None
                    return True
            return True
        return True

    _focus = "cihaz"

    def _cycle(self, d):
        order = ["cihaz", "yon", "duzen", "gosterge", "kaydet"]
        self._focus = order[(order.index(self._focus) + d) % len(order)]

    def apply(self):
        self.conf["device"] = self.conf["device"]
        save_conf(self.conf)
        self._make_mobile_files()
        self.msg = "Kurulum tamam! MOBİL klasörü hazır. Kayıtlar SAVE içinde."
        self.msg_col = (130, 240, 160)

    def _make_mobile_files(self):
        try:
            if not os.path.isdir(MOBIL_DIR):
                os.makedirs(MOBIL_DIR)
            files = ["touch.py", "savegame.py", "classes.py", "skills.py",
                     "settings.py", "netproto.py", "online.py", "chars.py",
                     "hud.py", "maps.py", "stickman.py", "fight.py", "ui.py",
                     "main.py"]
            lines = ["# STICKMAN FIGHTERS - MOBIL PAKETI",
                     "# Klasik PC surumuyle ayni dosyalari kullanir.",
                     "# Uygulama kabugu bu klasoru okur.",
                     ""]
            for f in files:
                src = os.path.join(ROOT, f)
                dst = os.path.join(MOBIL_DIR, f)
                if os.path.isfile(src):
                    with io.open(src, "rb") as a, io.open(dst, "wb") as b:
                        b.write(a.read())
                    lines.append("kopya: %s" % f)
            lines.append("kayit klasoru: %s" % SAVE_DIR)
            with io.open(os.path.join(MOBIL_DIR, "MOBIL_IÇERİK.txt"), "w",
                         encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception as e:
            self.msg = "Hata: %s" % e
            self.msg_col = (250, 130, 130)

    # ------------------------------------------------------------ cizim
    def draw(self, surf):
        self.t += self.clock.tick(60) / 1000.0
        surf.fill(self.bg)
        for y in range(0, self.H, 4):
            f = y / max(1, self.H)
            pygame.draw.line(surf, (int(16 + 10 * f), int(20 + 12 * f),
                                    int(34 + 20 * f)), (0, y), (self.W, y))
        draw_text(surf, "STICKMAN FIGHTERS", 34, GOLD, (self.W // 2, 44))
        draw_text(surf, "MOBİL KURULUM", 24, (235, 240, 250), (self.W // 2, 84))
        draw_text(surf, "Telefon ve tablet için hazırlık ekranı",
                  15, (150, 158, 180), (self.W // 2, 116))

        w, h = DEV_SIZE[self.conf["device"]]
        dev = DEVICES[self.conf["device"]]
        lay = "KABA (PARMAK)" if self.conf["layout"] == "coarse" else "İNCE (JİLET)"
        show = "AÇIK" if self.conf["show_touch"] else "KAPALI"

        self._opt(surf, "cihaz", "CİHAZ", "%s   (%dx%d)" % (dev, w, h))
        self._opt(surf, "yon", "HEDEF ÇÖZÜNÜRLÜK", "%d x %d  |  FPS 60" % (w, h))
        self._opt(surf, "duzen", "KONTROL DÜZENİ", lay)
        self._opt(surf, "gosterge", "DOKUNMATİK GÖSTERGE", show)
        self._opt(surf, "klasor", "KAYIT KLASÖRÜ", SAVE_DIR)

        r = self.buttons["kaydet"]
        pulse = 0.5 + 0.5 * math.sin(self.t * 4)
        pygame.draw.rect(surf, blend((40, 46, 66), GOLD, pulse * 0.4), r,
                         border_radius=10)
        pygame.draw.rect(surf, GOLD, r, 3, border_radius=10)
        draw_text(surf, "KURULUMU BİTİR", 22, (255, 255, 255), r.center)

        rb = self.buttons["cikis"]
        pygame.draw.rect(surf, (40, 44, 60), rb, border_radius=8)
        pygame.draw.rect(surf, (110, 120, 150), rb, 2, border_radius=8)
        draw_text(surf, "KAPAT", 18, (235, 240, 250), rb.center)

        draw_text(surf, self.msg, 15, self.msg_col, (self.W // 2, 520))
        draw_text(surf, "↑ ↓ seç   ENTER uygula   ESC kapat", 13,
                  (130, 138, 160), (self.W // 2, self.H - 18))
        pygame.display.flip()

    def _opt(self, surf, key, label, value):
        r = self.buttons[key]
        active = (self._focus == key)
        pygame.draw.rect(surf, (24, 28, 44), r, border_radius=9)
        pygame.draw.rect(surf, GOLD if active else (70, 80, 110), r, 2,
                         border_radius=9)
        draw_text(surf, label, 12, (150, 158, 180),
                  (r.x + 14, r.y + 14), align="left")
        draw_text(surf, value, 16, (232, 238, 250),
                  (r.right - 14, r.y + 14), align="right")


def main():
    app = MobileSetup()
    run = True
    while run:
        for e in pygame.event.get():
            run = app.handle(e)
        app.draw(app.scr)
    pygame.quit()


if __name__ == "__main__":
    main()