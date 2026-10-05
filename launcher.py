"""KATİL5019 LAUNCHER

Yerlesim:
  sol      -> SÜRÜMLER (secili projenin surumleri)
  sag      -> OYUNLAR  (kapak, ◀ isim ▶ oklari, OYNA)
  alt orta -> BİLGİ    (secili proje hakkinda)

Yeni proje eklemek icin: launcher_projects.py dosyasina bak.
"""
import os
import math
import subprocess
import sys

import pygame

BASE = os.path.dirname(os.path.abspath(__file__))

# 7/24 acik indirme sitesi (GitHub Pages)
SITE_URL = "https://KATIL5019.github.io/stickman-fighters/"
# Telefon surumu APK adresi (GitHub Releases)
APK_URL = ("https://github.com/KATIL5019/stickman-fighters/releases/"
           "latest/download/STICKMAN-FIGHTERS-1.4.0.apk")
if BASE not in sys.path:
    sys.path.insert(0, BASE)

import settings
import launcher_projects

LW, LH = 960, 620
PANEL = (54, 52, 60)
PANEL_D = (38, 37, 44)
EDGE_L = (92, 90, 100)
EDGE_D = (20, 19, 24)
GOLD = (255, 205, 70)
TXT = (232, 232, 240)
TXT_D = (150, 148, 160)
GREEN = (95, 200, 95)
SEL = (72, 120, 56)
RED = (205, 75, 75)


def scan_versions(proj):
    """Secili projenin surumlerini tarar: ana + versions/ klasoru."""
    root = os.path.join(BASE, proj["path"]) if proj["path"] else BASE
    out = [(settings.VERSION, root, "Ana oyun")]
    vdir = os.path.join(root, "versions")
    if os.path.isdir(vdir):
        for name in sorted(os.listdir(vdir)):
            p = os.path.join(vdir, name)
            if os.path.isfile(os.path.join(p, proj["entry"])):
                out.append((name, p, "Ek sürüm"))
    return out


def notes_for(ver):
    for v, note, lines in settings.CHANGELOG:
        if v == ver:
            return note
    return ""


class Launcher:
    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode((LW, LH))
        pygame.display.set_caption("KATİL5019 LAUNCHER")
        self.clock = pygame.time.Clock()
        self.bg = self._bg()
        self.projects = list(launcher_projects.PROJECTS)
        self.p = 0
        self.hover = -1
        self.status = "Hazır"
        self.busy = False
        self.t = 0.0
        self.rows = []
        self.icon_rect = pygame.Rect(596, 86, 316, 150)
        self.prev_btn = pygame.Rect(596, 246, 54, 42)
        self.next_btn = pygame.Rect(858, 246, 54, 42)
        self.play_btn = pygame.Rect(596, 300, 316, 58)
        self.phone_btn = pygame.Rect(596, 366, 152, 32)
        self.quit_btn = pygame.Rect(760, 366, 152, 32)
        self.info_rect = pygame.Rect(24, 412, 888, 184)
        self._load_project()

    def _load_project(self):
        proj = self.projects[self.p]
        self.versions = scan_versions(proj)
        self.sel = 0
        self.rows = [pygame.Rect(28, 110 + i * 40, 268, 34)
                     for i in range(len(self.versions))]
        self.cover = None
        cv = proj.get("cover")
        if cv:
            fp = os.path.join(BASE, proj["path"], cv) if proj["path"] \
                else os.path.join(BASE, cv)
            if os.path.isfile(fp):
                try:
                    img = pygame.image.load(fp)
                    self.cover = settings.load_cover_from(img, self.icon_rect.w,
                                                         self.icon_rect.h)
                except Exception:
                    self.cover = None
        if self.cover is None:
            self.cover = settings.load_cover(self.icon_rect.w, self.icon_rect.h)

    def _bg(self):
        s = pygame.Surface((LW, LH))
        for y in range(LH):
            t = y / max(1, LH - 1)
            s.fill((int(16 + 18 * t), int(18 + 14 * t), int(26 + 22 * t)),
                   (0, y, LW, 1))
        return s

    def _panel(self, rect, title=None):
        pygame.draw.rect(self.scr, PANEL_D, rect)
        pygame.draw.rect(self.scr, PANEL, rect, border_radius=5)
        pygame.draw.line(self.scr, EDGE_L, (rect.left + 2, rect.top + 1),
                         (rect.right - 2, rect.top + 1), 2)
        pygame.draw.line(self.scr, EDGE_L, (rect.left + 1, rect.top + 2),
                         (rect.left + 1, rect.bottom - 2), 2)
        pygame.draw.line(self.scr, EDGE_D, (rect.left + 2, rect.bottom - 2),
                         (rect.right - 2, rect.bottom - 2), 2)
        pygame.draw.line(self.scr, EDGE_D, (rect.right - 2, rect.top + 2),
                         (rect.right - 2, rect.bottom - 2), 2)
        if title:
            self._text(title, (rect.centerx, rect.y - 11), 14, GOLD)

    def _text(self, s, center, size, color=TXT):
        img = pygame.font.SysFont("consolas", size, bold=True).render(str(s), True, color)
        self.scr.blit(img, img.get_rect(center=center))
        return img.get_rect()

    def _textl(self, s, left, y, size, color=TXT):
        img = pygame.font.SysFont("consolas", size, bold=True).render(str(s), True, color)
        self.scr.blit(img, img.get_rect(midleft=(int(left), int(y))))
        return img.get_rect()

    def _logo(self):
        bob = math.sin(self.t * 1.5) * 3
        self._text("KATİL5019", (158, 26 + bob), 26, GOLD)
        self._text("LAUNCHER", (158, 54 + bob), 20, TXT)

    def _arrow(self, rect, direction, enabled):
        col = GOLD if (enabled and rect.collidepoint(pygame.mouse.get_pos())) \
            else ((200, 200, 210) if enabled else (88, 86, 94))
        pygame.draw.rect(self.scr, (44, 42, 50), rect, border_radius=5)
        pygame.draw.rect(self.scr, col, rect, 2, border_radius=5)
        cx, cy = rect.center
        d = 1 if direction > 0 else -1
        pygame.draw.polygon(self.scr, col,
                            [(cx - d * 4, cy - 11), (cx + d * 9, cy),
                             (cx - d * 4, cy + 11)])

    def draw(self):
        self.t += 1 / 60.0
        self.scr.blit(self.bg, (0, 0))
        self._logo()
        proj = self.projects[self.p]

        # ---- sol: SÜRÜMLER
        self._panel(pygame.Rect(16, 94, 284, 302), "SÜRÜMLER")
        for i, (ver, path, kind) in enumerate(self.versions):
            r = self.rows[i]
            active = i == self.sel
            hov = i == self.hover
            bg = SEL if active else ((66, 66, 74) if hov else (44, 43, 50))
            pygame.draw.rect(self.scr, bg, r, border_radius=3)
            pygame.draw.rect(self.scr, GOLD if active else (86, 85, 94), r, 2,
                             border_radius=3)
            self._text(ver, (r.left + 12, r.centery), 15,
                       (255, 255, 255) if active else TXT_D)
            self._text(kind, (r.right - 12, r.centery), 11,
                       (225, 225, 170) if active else (118, 116, 126))
        self._textl("not: %s" % notes_for(self.versions[self.sel][0]),
                    30, 372, 12, TXT_D)

        # ---- sag: OYUNLAR
        self._panel(pygame.Rect(576, 70, 356, 348), "OYUNLAR")
        ir = self.icon_rect
        pygame.draw.rect(self.scr, (22, 21, 28), ir, border_radius=5)
        pygame.draw.rect(self.scr, GOLD, ir, 2, border_radius=5)
        if self.cover is not None:
            self.scr.blit(self.cover, ir.topleft)
        else:
            self._text("KAPAK YOK", (ir.centerx, ir.centery), 16, TXT_D)
        n = len(self.projects)
        self._arrow(self.prev_btn, -1, n > 1)
        self._arrow(self.next_btn, 1, n > 1)
        self._text(proj["name"], (754, 267), 19, GOLD)
        self._text("%d / %d" % (self.p + 1, n), (754, 288), 11, TXT_D)
        pulse = 0.5 + 0.5 * math.sin(self.t * 4)
        pcol = (60, 60, 66) if self.busy else GREEN
        pygame.draw.rect(self.scr, pcol, self.play_btn, border_radius=4)
        pygame.draw.rect(self.scr, (255, 255, 255) if pulse > 0.5 else pcol,
                         self.play_btn, 3, border_radius=4)
        self._text("OYNA", self.play_btn.center, 26, (16, 26, 16))
        pygame.draw.rect(self.scr, (62, 61, 70), self.quit_btn, border_radius=3)
        pygame.draw.rect(self.scr, (104, 102, 112), self.quit_btn, 2, border_radius=3)
        self._text("KAPAT", self.quit_btn.center, 14, TXT)

        pygame.draw.rect(self.scr, (74, 58, 104), self.phone_btn, border_radius=3)
        pygame.draw.rect(self.scr, (168, 130, 220), self.phone_btn, 2, border_radius=3)
        self._text("TELEFON S\u00dcR\u00dcM\u00dc", self.phone_btn.center, 13, TXT)

        # ---- alt: BİLGİ
        self._panel(self.info_rect, "BİLGİ")
        y = self.info_rect.y + 20
        for title, text in proj.get("info", []):
            self._textl(title, self.info_rect.x + 18, y, 13, GOLD)
            x = self.info_rect.x + 140
            for part in settings.wrap_text(text, 84):
                if y > self.info_rect.bottom - 10:
                    break
                self._textl(part, x, y, 12, TXT)
                y += 15
            y += 14

        bar = pygame.Rect(16, LH - 22, 300, 18)
        pygame.draw.rect(self.scr, (26, 25, 32), bar, border_radius=3)
        pygame.draw.rect(self.scr, (74, 72, 84), bar, 1, border_radius=3)
        self._text(self.status, (bar.centerx, bar.centery), 11,
                   GREEN if self.status == "Hazır" else GOLD)
        self._text("Python %d.%d  •  pygame %s  •  F11 tam ekran"
                   % (sys.version_info[0], sys.version_info[1], pygame.version.ver),
                   (LW - 190, LH - 13), 11, (108, 106, 118))
        pygame.display.flip()

    def switch(self, d):
        if len(self.projects) < 2:
            return
        self.p = (self.p + d) % len(self.projects)
        self._load_project()
        self.status = "Proje: %s" % self.projects[self.p]["name"]

    def launch(self):
        proj = self.projects[self.p]
        ver, path, _k = self.versions[self.sel]
        if self.busy:
            return
        self.busy = True
        self.status = "Başlatılıyor..."
        self.draw()
        pygame.time.wait(250)
        kw = {}
        if os.name == "nt":
            kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            subprocess.Popen([settings.python_no_window(), proj["entry"]],
                             cwd=path, **kw)
            self.status = "Oyun başladı!"
            self.draw()
            pygame.time.wait(800)
            pygame.quit()
            sys.exit(0)
        except Exception as e:
            self.busy = False
            self.status = "HATA: %s" % e

    def open_phone(self):
        """Telefon surumu: siteyi ac (GitHub Pages) ."""
        import webbrowser
        self.status = "Telefon surumu icin site aciliyor..."
        try:
            webbrowser.open(SITE_URL, new=2)
        except Exception:
            try:
                os.startfile(SITE_URL)
            except Exception as e:
                self.status = "Site acilamadi: %s" % e
                return
        self.status = "Sitede 'TELEFON SURUMU' butonuna bas (GitHub/APK)"

    def run(self):
        while True:
            self.clock.tick(60)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
                    elif e.key in (pygame.K_UP, pygame.K_w):
                        self.sel = (self.sel - 1) % len(self.versions)
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        self.sel = (self.sel + 1) % len(self.versions)
                    elif e.key in (pygame.K_LEFT, pygame.K_a):
                        self.switch(-1)
                    elif e.key in (pygame.K_RIGHT, pygame.K_d):
                        self.switch(1)
                    elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.launch()
                elif e.type == pygame.MOUSEMOTION:
                    mx, my = e.pos
                    self.hover = -1
                    for i, r in enumerate(self.rows):
                        if r.collidepoint(mx, my):
                            self.hover = i
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if self.play_btn.collidepoint(mx, my):
                        self.launch()
                    elif self.prev_btn.collidepoint(mx, my):
                        self.switch(-1)
                    elif self.next_btn.collidepoint(mx, my):
                        self.switch(1)
                    elif self.quit_btn.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit(0)
                    elif self.phone_btn.collidepoint(mx, my):
                        self.open_phone()
                    else:
                        for i, r in enumerate(self.rows):
                            if r.collidepoint(mx, my):
                                self.sel = i
            self.draw()


if __name__ == "__main__":
    Launcher().run()