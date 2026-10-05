"""STICKMAN FIGHTERS — Kurulum (Setup) ekranı.

Yukarıdan aşağı:
    OYUNU İNDİR        (indirme/kurulum başlatır)
    PC SÜRÜMÜ          (tıklanabilir → launcher açılır)
    TELEFON SÜRÜMÜ     (devre dışı; üstüne siyah çizgi çekilir)
"""
import os
import math
import subprocess
import sys

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.abspath(os.path.join(HERE, ".."))

SW, SH = 720, 700
BG1 = (14, 16, 24)
BG2 = (34, 26, 46)
PANEL = (56, 54, 62)
PANEL_D = (33, 32, 39)
EDGE_L = (92, 90, 100)
EDGE_D = (20, 19, 24)
GOLD = (255, 205, 70)
TXT = (232, 232, 240)
TXT_D = (148, 146, 158)
GREEN = (95, 200, 95)
DIS = (84, 82, 90)
BLACK = (0, 0, 0)


def _pythonw():
    """Konsol penceresi acmayan Python (terminalin cikmamasi icin)."""
    cand = os.path.join(os.path.dirname(sys.executable or "python"), "pythonw.exe")
    return cand if os.path.isfile(cand) else (sys.executable or "python")


def check_game():
    need = ["main.py", "launcher.py", "settings.py", "chars.py", "fight.py"]
    missing = [f for f in need if not os.path.isfile(os.path.join(GAME_DIR, f))]
    return (not missing), missing


class Setup:
    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("STICKMAN FIGHTERS — Kurulum")
        self.clock = pygame.time.Clock()
        self.t = 0.0
        self.status = "Hazır"
        self.log = []
        self.ok, self.missing = check_game()
        if not self.ok:
            self.status = "Eksik dosya: %s" % ", ".join(self.missing)
        self.dl_btn = pygame.Rect(190, 404, 340, 54)
        self.pc_btn = pygame.Rect(190, 478, 340, 52)
        self.ph_btn = pygame.Rect(190, 550, 340, 52)
        self.quit_btn = pygame.Rect(SW - 118, 24, 92, 30)
        self._bg = self._make_bg()

    def _make_bg(self):
        s = pygame.Surface((SW, SH))
        for y in range(SH):
            t = y / max(1, SH - 1)
            s.fill((int(BG1[0] + (BG2[0] - BG1[0]) * t),
                    int(BG1[1] + (BG2[1] - BG1[1]) * t),
                    int(BG1[2] + (BG2[2] - BG1[2]) * t)), (0, y, SW, 1))
        return s

    def _text(self, s, center, size, color=TXT):
        img = pygame.font.SysFont("consolas", size, bold=True).render(str(s), True, color)
        self.scr.blit(img, img.get_rect(center=center))
        return img.get_rect()

    def _panel(self, rect):
        pygame.draw.rect(self.scr, PANEL_D, rect)
        pygame.draw.rect(self.scr, PANEL, rect, border_radius=5)
        pygame.draw.line(self.scr, EDGE_L, (rect.left + 2, rect.top + 1),
                         (rect.right - 2, rect.top + 1), 2)
        pygame.draw.line(self.scr, EDGE_L, (rect.left + 1, rect.top + 2),
                         (rect.left + 1, rect.bottom - 2), 2)
        pygame.draw.line(self.scr, EDGE_D, (rect.left + 2, rect.bottom - 2),
                         (rect.right - 2, rect.bottom - 2), 2)

    def _button(self, rect, label, enabled=True, blocked=False):
        if not enabled:
            self._panel(rect)
            self._text(label, rect.center, 20, DIS)
            if blocked:
                pygame.draw.line(self.scr, BLACK,
                                 (rect.left + 16, rect.centery - 10),
                                 (rect.right - 16, rect.centery + 10), 8)
                pygame.draw.line(self.scr, BLACK,
                                 (rect.left + 16, rect.centery + 10),
                                 (rect.right - 16, rect.centery - 10), 8)
            return
        hov = rect.collidepoint(pygame.mouse.get_pos())
        base = (88, 145, 66) if hov else (72, 120, 56)
        pygame.draw.rect(self.scr, base, rect, border_radius=5)
        pygame.draw.rect(self.scr, GOLD if hov else (140, 200, 120), rect, 3,
                         border_radius=5)
        self._text(label, rect.center, 20, (14, 24, 14))

    def draw(self):
        self.t += 1 / 60.0
        self.scr.blit(self._bg, (0, 0))
        bob = math.sin(self.t * 1.5) * 3
        self._text("STICKMAN FIGHTERS", (SW // 2, 74 + bob), 36, GOLD)
        self._text("KURULUM", (SW // 2, 114 + bob), 20, TXT_D)
        bar = pygame.Rect(SW // 2 - 170, 142, 340, 26)
        pygame.draw.rect(self.scr, (30, 29, 36), bar, border_radius=3)
        pygame.draw.rect(self.scr, GOLD, bar, 2, border_radius=3)
        self._text("OYUNU İNDİR", bar.center, 14, GOLD)

        p = pygame.Rect(120, 196, 480, 176)
        self._panel(p)
        self._text("BİLGİ", (p.centerx, p.y - 10), 13, GOLD)
        y = p.y + 24
        for ln, col in (("Hedef: STICKMAN FIGHTERS oyununu bilgisayarına kur.", TXT),
                        ("Sürüm: 1.1.0   •   Boyut: ~2 MB", TXT),
                        ("Gereksinim: Windows 10/11 + Python 3.11", TXT),
                        ("", TXT),
                        ("Telefon sürümü: joystick + 4 buton.", TXT_D),
                        ("Kayıtlar SAVE klasöründe saklanır.", TXT_D)):
            if ln:
                self._text(ln, (p.centerx, y), 13, col)
            y += 21

        self._button(self.dl_btn, "OYUNU İNDİR", True)
        self._button(self.pc_btn, "PC SÜRÜMÜ", True)
        self._button(self.ph_btn, "TELEFON SÜRÜMÜ", True)
        self._text("PC sürümü: tıkla, kurulum bitsin, launcher açılsın.",
                   (SW // 2, 618), 12, TXT_D)
        self._text("Telefon sürümü: dokunmatik joystick + 4 buton.",
                   (SW // 2, 638), 12, TXT_D)

        self._button(self.quit_btn, "KAPAT", True)
        self._text(self.status, (SW // 2, 672),
                   13, GREEN if self.ok else (200, 90, 90))
        pygame.display.flip()

    def install_mobile(self):
        self.status = "Mobil kurulum aciliyor..."
        self.draw()
        pygame.time.wait(400)
        try:
            subprocess.Popen([_pythonw(), "SETUP\\mobil_setup.py"],
                             cwd=GAME_DIR)
        except Exception as e:
            self.status = "HATA: %s" % e
            return
        pygame.quit()
        sys.exit(0)

    def install_pc(self):
        self.status = "Kuruluyor..."
        self.draw()
        pygame.time.wait(500)
        if not self.ok:
            self.status = "Eksik dosya: %s" % ", ".join(self.missing)
            self.draw()
            pygame.time.wait(1800)
            return
        icon = os.path.join(GAME_DIR, "oyun_ikon.png")
        self._make_shortcut(icon)
        self.status = "Kurulum tamam! Launcher açılıyor..."
        self.draw()
        pygame.time.wait(600)
        try:
            subprocess.Popen([_pythonw(), "launcher.py"], cwd=GAME_DIR)
        except Exception as e:
            self.status = "HATA: %s" % e
            return
        pygame.quit()
        sys.exit(0)

    def _make_shortcut(self, icon):
        try:
            import win32com.client
        except ImportError:
            self.log.append("pywin32 yok; kısayol elle oluşturulacak.")
            return
        try:
            desk = os.path.join(os.path.expanduser("~"), "Desktop")
            lnk = os.path.join(desk, "STICKMAN FIGHTERS.lnk")
            shell = win32com.client.Dispatch("WScript.Shell")
            sc = shell.CreateShortCut(lnk)
            sc.Targetpath = _pythonw()
            sc.Arguments = '"%s"' % os.path.join(GAME_DIR, "launcher.py")
            sc.WorkingDirectory = GAME_DIR
            sc.IconLocation = "%s,0" % icon
            sc.Description = "STICKMAN FIGHTERS"
            sc.WindowStyle = 7
            sc.save()
        except Exception as e:
            self.log.append("Kısayol hatası: %s" % e)

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
                    elif e.key == pygame.K_RETURN:
                        self.install_pc()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.dl_btn.collidepoint(e.pos) or self.pc_btn.collidepoint(e.pos):
                        self.install_pc()
                    elif self.ph_btn.collidepoint(e.pos):
                        self.install_mobile()
                        return
                        self.status = "Telefon sürümü açılıyor..."
                        pygame.time.wait(900)
                        self.status = ("Hazır" if self.ok else
                                       "Eksik dosya: %s" % ", ".join(self.missing))
                    elif self.quit_btn.collidepoint(e.pos):
                        pygame.quit()
                        sys.exit(0)
            self.draw()


if __name__ == "__main__":
    Setup().run()
