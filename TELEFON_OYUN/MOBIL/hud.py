import math
import pygame
from settings import *
import settings
from classes import SKILLS


def _hp_color(f):
    return blend((220, 40, 40), (60, 200, 70), f)


class HUD:
    def __init__(self):
        small = settings.MOBILE or settings.MENU_COMPACT
        self.hp_h = 34 if small else 58
        self.bot_h = 0 if getattr(settings, "HIDE_KEY_BAR", False) else (
            84 if not small else 68)
        self.hp_y = SCREEN_H - self.hp_h - self.bot_h
        self.bot_y = SCREEN_H - self.bot_h

    def draw(self, surf, p1, p2, t):
        self._hpstrip(surf, p1, p2)
        if self.bot_h > 0:
            self._controls(surf, p1, p2)

    def _hpstrip(self, surf, p1, p2):
        y = self.hp_y
        pygame.draw.rect(surf, (12, 14, 22), (0, y, SCREEN_W, self.hp_h))
        pygame.draw.rect(surf, (70, 78, 100), (0, y, SCREEN_W, 2))
        pygame.draw.rect(surf, (70, 78, 100), (0, self.bot_y, SCREEN_W, 2))
        mid = SCREEN_W // 2
        bar_w = mid - (56 if settings.MOBILE else 90)
        fs = 13 if settings.MOBILE else 15
        w1 = get_font(fs).size("OYUNCU 1")[0]
        w2 = get_font(15).size("OYUNCU 2")[0]
        draw_text(surf, "OYUNCU 1", fs, (235, 235, 245),
                  (10 + w1 // 2, y + 6))
        draw_text(surf, "OYUNCU 2", fs, (235, 235, 245),
                  (SCREEN_W - 10 - w2 // 2, y + 6))
        bh = 20 if settings.MOBILE else 28
        by = y + (18 if settings.MOBILE else 22)
        self._hp(surf, pygame.Rect(8, by, bar_w, bh), p1, anchor="left")
        off = 56 if settings.MOBILE else 90
        self._hp(surf, pygame.Rect(mid + off, by, bar_w, bh),
                 p2, anchor="right")
        draw_text(surf, "VS", 22 if settings.MOBILE else 30, GOLD, (mid, by))

    def _hp(self, surf, bar, fighter, anchor):
        bg = pygame.Surface((bar.w, bar.h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        surf.blit(bg, bar.topleft)
        pygame.draw.rect(surf, (60, 60, 70), bar, 2, border_radius=6)
        frac = max(0.0, fighter.hp / fighter.max_hp)
        if anchor == "left":
            fill_r = pygame.Rect(bar.x + 2, bar.y + 2, int((bar.w - 4) * frac), bar.h - 4)
        else:
            fill_r = pygame.Rect(bar.right - 2 - int((bar.w - 4) * frac), bar.y + 2,
                                 int((bar.w - 4) * frac), bar.h - 4)
        if frac > 0:
            pygame.draw.rect(surf, _hp_color(frac), fill_r, border_radius=5)
        # kalkan cubugu (can barinin hemen altinda)
        sh = float(getattr(fighter, "shield", 0.0))
        sh_max = float(getattr(fighter, "max_shield", 0.0))
        if sh_max > 0 and sh > 0:
            sfrac = max(0.0, min(1.0, sh / sh_max))
            if anchor == "left":
                sh_r = pygame.Rect(bar.x + 2, bar.bottom - 5,
                                   int((bar.w - 4) * sfrac), 4)
            else:
                sh_r = pygame.Rect(bar.right - 2 - int((bar.w - 4) * sfrac),
                                   bar.bottom - 5, int((bar.w - 4) * sfrac), 4)
            pygame.draw.rect(surf, (150, 210, 255), sh_r, border_radius=2)
        chip_cx = bar.x + 22 if anchor == "left" else bar.right - 22
        cr = 9 if settings.MOBILE else 12
        pygame.draw.circle(surf, fighter.color, (chip_cx, bar.centery), cr)
        pygame.draw.circle(surf, (255, 255, 255),
                           (chip_cx, bar.centery), cr, 1)
        # bucluk degerler net gorunsun: 1 ondalik
        num = "%.1f" % fighter.hp
        if sh_max > 0:
            num += " (+%.0f)" % sh
        num_x = bar.right - 24 if anchor == "left" else bar.x + 24
        if settings.MOBILE:
            num_x = bar.centerx
        draw_text(surf, num, 12 if settings.MOBILE else 15,
                  (255, 255, 255), (num_x, bar.centery))
        # status rozetleri
        bx = bar.x + 42 if anchor == "left" else bar.right - 42
        for k, label, col in (("poison", "Z", (140, 220, 70)),
                              ("burn", "A", (255, 140, 40)),
                              ("shock", "S", (150, 210, 255)),
                              ("stun", "!", (255, 220, 90)),
                              ("ai", "AI", (90, 255, 120))):
            st = fighter.st.get(k)
            if st and st["t"] > 0:
                pygame.draw.circle(surf, (16, 18, 28), (bx, bar.y + 8), 8)
                pygame.draw.circle(surf, col, (bx, bar.y + 8), 8, 2)
                draw_text(surf, label, 10, col, (bx, bar.y + 8))
                bx += 20 if anchor == "left" else -20

    def _controls(self, surf, p1, p2):
        y = self.bot_y
        pygame.draw.rect(surf, (12, 14, 22), (0, y, SCREEN_W, self.bot_h))
        pygame.draw.rect(surf, (44, 48, 62), (SCREEN_W // 2 - 1, y, 2, self.bot_h))
        half = SCREEN_W // 2
        self._playerbar(surf, (0, y, half, self.bot_h), p1, p2,
                        ("G", "E", "Q", "Z"), mirror=False)
        self._playerbar(surf, (half, y, half, self.bot_h), p2, p1,
                        ("SOL+SAĞ", "SOL", "SAĞ", "ORTA"), mirror=True)

    def _playerbar(self, surf, rect, fighter, opponent, keys, mirror):
        x, y, w, h = rect
        col = fighter.color
        bw, abw, gap = 56, 88, 10
        if not mirror:
            gx = x + 12
            slot_left = lambda j: x + 84 + j * (abw + gap)
        else:
            gx = x + w - 12 - bw
            slot_left = lambda j: gx - gap - (2 - j) * (abw + gap) - abw
        box = pygame.Rect(gx, y + 12, bw, bw)
        state, fill = fighter.ult_info(opponent)
        pygame.draw.rect(surf, (20, 20, 30), box, border_radius=8)
        if state == "active":
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.006)
            pygame.draw.rect(surf, blend(GOLD, (255, 255, 255), pulse * 0.5), box,
                             border_radius=8)
            label = "AKTİF!"
        elif state == "ready":
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.006)
            pygame.draw.rect(surf, blend(GOLD, (255, 255, 255), pulse * 0.4), box,
                             border_radius=8)
            label = "HAZIR!"
        else:
            pygame.draw.rect(surf, (60, 60, 70), (box.x + 3, box.y + 3, box.w - 6, box.h - 6),
                             border_radius=6)
            pygame.draw.rect(surf, blend((60, 60, 70), GOLD, fill),
                             (box.x + 3, box.y + 3 + int((box.h - 6) * (1 - fill)),
                              box.w - 6, int((box.h - 6) * fill)), border_radius=6)
            label = f"%{int(fill * 100)}"
        pygame.draw.rect(surf, col, box, 3, border_radius=8)
        draw_text(surf, "G", 20, (255, 255, 255), (box.x + 16, box.y + 15))
        draw_text(surf, label, 10, (255, 255, 255) if state != "active" else (0, 0, 0),
                  (box.centerx, box.y + 46))
        for i in range(3):
            slot = pygame.Rect(slot_left(i), y + 12, abw, 56)
            pygame.draw.rect(surf, (32, 34, 48), slot, border_radius=8)
            pygame.draw.rect(surf, (110, 120, 150), slot, 2, border_radius=8)
            sid = fighter.defn.get("abilities", [None, None, None])[i]
            slot_def = SKILLS.get(sid) or ABILITIES.get(sid, {"name": "-"})
            draw_text(surf, str(i + 1), 15, (255, 255, 255), (slot.centerx, slot.y + 14))
            nm = str(slot_def.get("name", "-"))
            fsz = 12 if len(nm) <= 8 else 11
            draw_text(surf, nm, fsz, (230, 230, 240), (slot.centerx, slot.y + 32))
            cd = fighter.cooldowns[i]
            if cd > 0:
                dark = pygame.Surface(slot.size, pygame.SRCALPHA)
                dark.fill((0, 0, 0, 185))
                surf.blit(dark, slot.topleft)
                draw_text(surf, f"{cd:.1f}", 18, (255, 255, 255),
                          (slot.centerx, slot.centery))
            draw_text(surf, keys[i + 1], 11, (205, 210, 225),
                      (slot.centerx, y + 76))
        draw_text(surf, keys[0], 11, (205, 210, 225), (box.centerx, y + 76))