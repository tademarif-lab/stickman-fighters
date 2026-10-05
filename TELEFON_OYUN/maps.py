import math
import pygame
from settings import *


class GrassMap:
    def __init__(self):
        self.name = "GRASS"
        self.disp_name = "ÇİM"
        self.w = WORLD_W
        self.solids = []
        self.clouds = [(130, 130, 1.0), (460, 80, 0.7), (760, 190, 1.2), (930, 110, 0.9)]

    def draw(self, surf, cam):
        self._sky(surf, cam)
        self._ground(surf, cam)

    def _sky(self, surf, cam):
        w, h = surf.get_size()
        pygame.draw.rect(surf, SKY, (0, 0, w, h))
        for wx, wy, s in self.clouds:
            x = int(wx - cam.x)
            y = int(wy - cam.y * 0.2)
            if x < -180 or x > w + 180:
                continue
            self._cloud(surf, x, y, int(32 * s))

    def _cloud(self, surf, x, y, r):
        pygame.draw.circle(surf, CLOUD, (x, y), r)
        pygame.draw.circle(surf, CLOUD, (x + int(r * 0.9), y + int(r * 0.15)), int(r * 0.7))
        pygame.draw.circle(surf, CLOUD, (x - int(r * 0.9), y + int(r * 0.15)), int(r * 0.7))
        pygame.draw.rect(surf, CLOUD, pygame.Rect(x - int(r * 0.9), y, int(r * 1.8), int(r * 0.7)))

    def _ground(self, surf, cam):
        w, h = surf.get_size()
        gy = int(GROUND_Y - cam.y)
        total = WORLD_H - GROUND_Y
        pygame.draw.rect(surf, GRASS_TOP, (0, gy, w, total))
        pygame.draw.rect(surf, GRASS_BOTTOM, (0, gy + TILE, w, total - TILE))
        start = int(cam.x // 26) * 26
        for i in range(0, w + 52, 26):
            wx = start + i
            x = int(wx - cam.x)
            if x < -30 or x > w + 30:
                continue
            hh = 10 + (wx % 13)
            pygame.draw.polygon(surf, blend(GRASS_TOP, (255, 255, 255), 0.15),
                                [(x, gy), (x + 5, gy - hh), (x + 9, gy)])
        pygame.draw.rect(surf, (70, 130, 45), (0, gy, w, 3))


class VillageMap:
    SKY_TOP = (128, 190, 222)
    SKY_BOT = (214, 235, 240)
    DIRT = (158, 122, 74)
    DIRT_BOT = (134, 100, 58)
    WALL = (228, 199, 150)
    WALL_DARK = (168, 134, 92)
    ROOF = (150, 74, 46)
    ROOF_DARK = (112, 52, 34)
    OUTLINE = (74, 54, 36)

    def __init__(self):
        self.name = "VILLAGE"
        self.disp_name = "KÖY"
        self.w = WORLD_W
        self.houses = [
            pygame.Rect(30, GROUND_Y - 230, 200, 230),
            pygame.Rect(250, GROUND_Y - 300, 180, 300),
            pygame.Rect(500, GROUND_Y - 200, 150, 200),
            pygame.Rect(700, GROUND_Y - 245, 180, 245),
        ]
        self.crate = pygame.Rect(938, GROUND_Y - 44, 48, 44)
        self.well = pygame.Rect(880, GROUND_Y - 56, 56, 56)
        self.trees = [(-30, 1.0), (235, 0.9), (455, 1.1), (620, 0.85), (940, 0.8),
                      (150, 1.0), (330, 0.95), (690, 1.05), (820, 0.9), (30, 0.9),
                      (560, 1.0), (760, 0.8), (980, 0.95), (10, 0.7), (995, 1.0)]
        self.solids = list(self.houses) + [self.crate, self.well]
        self.clouds = [(120, 120, 1.1), (330, 200, 0.8), (520, 90, 0.9),
                       (760, 180, 1.0), (930, 120, 1.2)]

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend(self.SKY_TOP, self.SKY_BOT, t), (0, y), (w, y))
        for wx, wy, s in self.clouds:
            x = int(wx - cam.x)
            y = int(wy - cam.y * 0.2)
            if x < -180 or x > w + 180:
                continue
            self._cloud(surf, x, y, int(34 * s))
        sun_x = int(850 - cam.x)
        if -80 < sun_x < w + 80:
            pygame.draw.circle(surf, (255, 240, 150),
                               (sun_x, int(90 - cam.y * 0.2)), 46)
        self._hills(surf, cam)
        self._ground(surf, cam)
        for wx, s in self.trees:
            self._tree_draw(surf, cam, wx, s)
        self.crate_rect(surf, cam)
        self._well_draw(surf, cam)
        for i, hh in enumerate(self.houses):
            self._house_draw(surf, cam, hh, i)

    def _tree_draw(self, surf, cam, wx, s):
        x = int(wx - cam.x)
        y = int(GROUND_Y - cam.y)
        if x < -60 or x > surf.get_width() + 60:
            return
        trunk_h = int(44 * s)
        pygame.draw.rect(surf, (120, 80, 46), (x - 5, y - trunk_h, 10, trunk_h))
        pygame.draw.circle(surf, (84, 150, 62), (x, y - trunk_h - int(18 * s)),
                           int(26 * s))
        pygame.draw.circle(surf, (66, 132, 52), (x - int(14 * s), y - trunk_h - int(6 * s)),
                           int(18 * s))
        pygame.draw.circle(surf, (66, 132, 52), (x + int(14 * s), y - trunk_h - int(6 * s)),
                           int(18 * s))

    def _cloud(self, surf, x, y, r):
        pygame.draw.circle(surf, (255, 255, 255), (x, y), r)
        pygame.draw.circle(surf, (255, 255, 255), (x + int(r * 0.9), y + int(r * 0.15)), int(r * 0.7))
        pygame.draw.circle(surf, (255, 255, 255), (x - int(r * 0.9), y + int(r * 0.15)), int(r * 0.7))
        pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(x - int(r * 0.9), y, int(r * 1.8), int(r * 0.7)))

    def _hills(self, surf, cam):
        w = surf.get_width()
        base = GROUND_Y
        for offset, amp, col in ((-120, 50, (96, 140, 92)), (-40, 70, (110, 156, 100))):
            pts = []
            step = 60
            x0 = int(cam.x // step) * step - step
            for ww in range(-step, w + 2 * step, step):
                wx = x0 + ww
                x = int(wx - cam.x)
                hill = (wx + offset) % 900
                hh = int(hill / 900.0 * 2 * amp)
                pts.append((x, int(base - cam.y) - amp + hh))
            pts += [(w + 60, int(base - cam.y)), (-60, int(base - cam.y))]
            pygame.draw.polygon(surf, col, pts)

    def _ground(self, surf, cam):
        w = surf.get_width()
        gy = int(GROUND_Y - cam.y)
        total = WORLD_H - GROUND_Y
        pygame.draw.rect(surf, self.DIRT, (0, gy, w, total))
        pygame.draw.rect(surf, self.DIRT_BOT, (0, gy + TILE, w, total - TILE))
        start = int(cam.x // 44) * 44
        for i in range(0, w + 88, 44):
            wx = start + i
            x = int(wx - cam.x)
            if x < -6 or x > w + 6:
                continue
            if (wx // 44) % 5 == 0:
                pygame.draw.rect(surf, self.OUTLINE, (x, gy - 5, 3, 10))
            else:
                pygame.draw.circle(surf, (188, 150, 96), (x, gy + 5), 2)
        pygame.draw.rect(surf, self.OUTLINE, (0, gy, w, 3))

    def _rect(self, r, cam):
        return pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)

    def crate_rect(self, surf, cam):
        r = self._rect(self.crate, cam)
        if not surf.get_rect().colliderect(r):
            return
        pygame.draw.rect(surf, (168, 120, 66), r)
        pygame.draw.rect(surf, self.OUTLINE, r, 3)
        pygame.draw.line(surf, self.OUTLINE, (r.left, r.top), (r.right, r.bottom), 3)
        pygame.draw.line(surf, self.OUTLINE, (r.right, r.top), (r.left, r.bottom), 3)

    def _well_draw(self, surf, cam):
        r = self._rect(self.well, cam)
        if not surf.get_rect().colliderect(r):
            return
        pygame.draw.rect(surf, (150, 150, 158), r)
        pygame.draw.rect(surf, self.OUTLINE, r, 3)
        pygame.draw.ellipse(surf, (90, 110, 130), pygame.Rect(r.x + 10, r.y - 8, r.w - 20, 20))
        pygame.draw.rect(surf, (120, 70, 40), (r.centerx - 4, r.y - 22, 8, 18))
        pygame.draw.line(surf, self.OUTLINE, (r.centerx, r.y - 22), (r.centerx, r.y - 30), 4)

    def _house_draw(self, surf, cam, hh, idx):
        r = self._rect(hh, cam)
        if not surf.get_rect().colliderect(r):
            return
        body = pygame.Rect(r.x, r.y + 20, r.w, r.h - 20)
        pygame.draw.rect(surf, self.WALL, body)
        pygame.draw.rect(surf, self.OUTLINE, body, 3)
        roof = pygame.Rect(r.x, r.y, r.w, 20)
        pygame.draw.rect(surf, self.ROOF, roof)
        pygame.draw.rect(surf, self.ROOF_DARK, (r.x + 6, r.y, r.w - 12, 6))
        pygame.draw.rect(surf, self.OUTLINE, roof, 3)
        ridge = (r.centerx, r.y - 10)
        pygame.draw.polygon(surf, self.ROOF_DARK, [(r.x - 8, r.y), ridge, (r.x + 8, r.y)])
        chimney = pygame.Rect(r.x + r.w // 2 - 10, r.y - 30, 16, 28)
        pygame.draw.rect(surf, (188, 158, 118), chimney)
        pygame.draw.rect(surf, self.OUTLINE, chimney, 3)
        door = pygame.Rect(r.centerx - 18, r.bottom - 52, 36, 52)
        pygame.draw.rect(surf, (110, 72, 44), door)
        pygame.draw.rect(surf, self.OUTLINE, door, 3)
        pygame.draw.circle(surf, (230, 200, 120), (door.right - 6, door.centery), 3)
        win = pygame.Rect(r.x + 22, r.y + r.h - 100, 38, 32)
        pygame.draw.rect(surf, (255, 236, 190), win)
        pygame.draw.rect(surf, self.OUTLINE, win, 3)
        pygame.draw.line(surf, self.OUTLINE, (win.centerx, win.top), (win.centerx, win.bottom), 3)
        pygame.draw.line(surf, self.OUTLINE, (win.left, win.centery), (win.right, win.centery), 3)


class CityMap:
    SKY_TOP = (36, 52, 88)
    SKY_BOT = (112, 138, 176)
    ASPHALT = (46, 48, 56)
    SIDEWALK = (128, 126, 122)
    OUTLINE = (28, 34, 48)

    def __init__(self):
        self.name = "CITY"
        self.disp_name = "ŞEHİR"
        self.w = WORLD_W
        widths = [100, 90, 120, 80, 90, 100, 100]
        heights = [300, 430, 260, 400, 520, 330, 250]
        self.buildings = []
        x = 10
        for i, (bw, bh) in enumerate(zip(widths, heights)):
            top = GROUND_Y - bh
            self.buildings.append(pygame.Rect(x, top, bw, GROUND_Y - top))
            x += bw + 50
        self.streets = [pygame.Rect(110, GROUND_Y, 50, 160),
                        pygame.Rect(250, GROUND_Y, 50, 160),
                        pygame.Rect(420, GROUND_Y, 50, 160),
                        pygame.Rect(550, GROUND_Y, 50, 160),
                        pygame.Rect(690, GROUND_Y, 50, 160),
                        pygame.Rect(840, GROUND_Y, 50, 160)]
        self.pits = [250, 690]
        self.ground = [pygame.Rect(0, GROUND_Y, 250, WORLD_H - GROUND_Y),
                       pygame.Rect(300, GROUND_Y, 390, WORLD_H - GROUND_Y),
                       pygame.Rect(740, GROUND_Y, WORLD_W - 740, WORLD_H - GROUND_Y)]
        self.solids = list(self.buildings) + self.ground
        self.park = pygame.Rect(110, GROUND_Y, 50, 160)
        self.clouds = [(80, 90, 1.0), (320, 60, 0.8), (560, 120, 1.1), (860, 70, 0.9)]
        self.skyline = [(0, 220, 130), (140, 160, 100), (250, 200, 120), (380, 150, 90),
                        (500, 230, 140), (640, 170, 110), (760, 210, 130), (890, 150, 110)]

    def _to_rect(self, r, cam):
        return pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend(self.SKY_TOP, self.SKY_BOT, t), (0, y), (w, y))
        for wx, wy, s in self.clouds:
            x = int(wx - cam.x * 0.4)
            y = int(wy - cam.y * 0.15)
            if x < -180 or x > w + 180:
                continue
            pygame.draw.ellipse(surf, (170, 185, 210), (x, y, int(72 * s), int(26 * s)))
        moon_x = int(880 - cam.x * 0.2)
        pygame.draw.circle(surf, (225, 232, 245), (moon_x, int(80 - cam.y * 0.15)), 30)
        for sx, top, sw_ in self.skyline:
            r = pygame.Rect(int(sx - cam.x), int(top - cam.y), sw_, WORLD_H - top)
            if r.right < -10 or r.x > w + 10:
                continue
            pygame.draw.rect(surf, (26, 36, 60), r)
        self._streets(surf, cam)
        self._park_draw(surf, cam)
        for i, b in enumerate(self.buildings):
            self._building_draw(surf, cam, b, i)

    def _streets(self, surf, cam):
        w = surf.get_width()
        for g in self.ground:
            r = pygame.Rect(int(g.x - cam.x), int(g.y - cam.y), g.w, g.h)
            pygame.draw.rect(surf, self.ASPHALT, r)
            side = pygame.Rect(r.x, r.y, r.w, 12)
            pygame.draw.rect(surf, self.SIDEWALK, side)
            pygame.draw.rect(surf, (86, 86, 88), (r.x, r.y, r.w, 12), 2)
            for px in range(r.x + 8, r.right - 4, 26):
                pygame.draw.rect(surf, (150, 150, 150), (px, r.y + 3, 18, 3))
            for ly in range(r.y + 30, r.bottom - 16, 34):
                dashes = pygame.Rect(r.x, ly, r.w, 4)
                pygame.draw.rect(surf, (86, 88, 96), dashes)
                for dx in range(r.x + 14, r.right - 12, 60):
                    pygame.draw.rect(surf, (230, 220, 120), (dx, ly, 34, 4))
        for i, st in enumerate(self.streets):
            rx = int(st.x - cam.x)
            if rx < -60 or rx > w + 60:
                continue
            top = int(GROUND_Y - cam.y)
            if st.x in self.pits:
                pygame.draw.rect(surf, (12, 14, 18), (rx, top, st.w, st.h))
                pygame.draw.rect(surf, (200, 120, 40), (rx, top, st.w, 6))
                for px in range(rx, rx + st.w, 14):
                    pygame.draw.line(surf, (120, 60, 20), (px, top + 6), (px + 14, top + 12), 3)
                pygame.draw.line(surf, (70, 74, 84), (rx + st.w // 2, top), (rx + st.w // 2, top + st.h), 4)
            elif st.x == 110:
                pass
            else:
                for pw in range(rx + 4, rx + st.w - 8, 16):
                    pygame.draw.rect(surf, (200, 204, 208), (pw, top + 20, 8, 26))
                    pygame.draw.rect(surf, (90, 92, 96), (pw, top + 20, 8, 26), 1)

    def _park_draw(self, surf, cam):
        r = self.park
        rd = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if rd.right < -30 or rd.x > surf.get_width() + 30:
            return
        pygame.draw.rect(surf, (66, 122, 64), rd)
        pygame.draw.rect(surf, (52, 96, 52), (rd.x, rd.y, rd.w, 10))
        pygame.draw.rect(surf, (120, 120, 116), (rd.x + 4, rd.y, rd.w - 8, 44))
        for tx in (rd.x + 18, rd.right - 18):
            pygame.draw.circle(surf, (50, 110, 55), (tx, rd.y + 66), 20)
            pygame.draw.circle(surf, (38, 92, 46), (tx - 10, rd.y + 74), 13)
            pygame.draw.circle(surf, (38, 92, 46), (tx + 10, rd.y + 74), 13)
            pygame.draw.rect(surf, (110, 78, 48), (tx - 3, rd.y + 78, 6, 60))

    def _building_draw(self, surf, cam, b, idx):
        r = self._to_rect(b, cam)
        if not surf.get_rect().colliderect(r):
            return
        tints = [(96, 116, 150), (120, 104, 138), (94, 128, 152), (138, 116, 122),
                 (104, 106, 140), (86, 118, 146), (128, 112, 128), (102, 96, 132)]
        body = tints[idx % len(tints)]
        pygame.draw.rect(surf, body, r)
        pygame.draw.rect(surf, self.OUTLINE, r, 3)
        pygame.draw.rect(surf, blend(body, (255, 255, 255), 0.30), (r.x, r.y, r.w, 6))
        step_y = 62
        step_x = 52
        for wy in range(r.y + 10, r.bottom - 96, step_y):
            for wx in range(r.x + 8, r.right - 12, step_x):
                lit = (wx + wy) % 130 < 46
                wc = (245, 220, 140) if lit else (180, 198, 218)
                win = pygame.Rect(wx, wy, 30, 34)
                pygame.draw.rect(surf, wc, win)
                pygame.draw.rect(surf, blend(body, (0, 0, 0), 0.35), win, 2)
        store = pygame.Rect(r.x, r.bottom - 92, r.w, 92)
        pygame.draw.rect(surf, blend(body, (0, 0, 0), 0.30), store)
        pygame.draw.rect(surf, self.OUTLINE, store, 3)
        sx = r.x + 8
        while sx < r.right - 40:
            pygame.draw.rect(surf, (220, 235, 250), (sx, r.bottom - 74, 30, 52))
            pygame.draw.rect(surf, (60, 70, 90), (sx, r.bottom - 74, 30, 52), 2)
            pygame.draw.line(surf, (170, 210, 240), (sx + 8, r.bottom - 78), (sx + 28, r.bottom - 78), 3)
            sx += 42
        door = pygame.Rect(r.centerx - 14, r.bottom - 54, 28, 54)
        pygame.draw.rect(surf, (30, 30, 36), door)
        pygame.draw.rect(surf, (10, 10, 14), door, 2)
        pygame.draw.circle(surf, (240, 220, 130), (door.right - 7, door.centery + 8), 3)
        aw = pygame.Rect(r.centerx - 26, r.bottom - 64, 52, 12)
        pygame.draw.rect(surf, (150, 60, 50), aw)
        pygame.draw.rect(surf, (110, 40, 36), aw, 2)
        for px in range(aw.x + 4, aw.right - 2, 10):
            pygame.draw.polygon(surf, (150, 60, 50),
                                [(px, aw.bottom), (px + 5, aw.bottom + 8), (px + 10, aw.bottom)])
        self._roof_extra(surf, r, (idx * 37) % 3)

    def _roof_extra(self, surf, r, mode):
        if mode == 0:
            unit = pygame.Rect(r.right - 58, r.y - 34, 26, 34)
            pygame.draw.rect(surf, (150, 152, 156), unit)
            pygame.draw.rect(surf, (80, 82, 88), unit, 2)
            fan = pygame.Rect(unit.centerx - 8, unit.y - 8, 16, 8)
            pygame.draw.rect(surf, (110, 112, 118), fan)
        elif mode == 1:
            tank = pygame.Rect(r.x + 12, r.y - 40, 28, 40)
            pygame.draw.rect(surf, (110, 116, 122), tank)
            pygame.draw.rect(surf, (60, 64, 70), tank, 2)
            pygame.draw.line(surf, (60, 64, 70), (tank.centerx, tank.y - 6), (tank.centerx, tank.y), 4)
        else:
            pygame.draw.line(surf, (70, 76, 88), (r.x + 40, r.y - 6), (r.x + 40, r.y - 56), 4)
            pygame.draw.line(surf, (70, 76, 88), (r.x + 40, r.y - 56), (r.x + 64, r.y - 56), 3)


class TrucksMap:
    ROAD = (52, 55, 62)
    ROAD_LINE = (225, 225, 120)

    def __init__(self):
        self.name = "TRUCKS"
        self.disp_name = "KAMYON"
        self.w = WORLD_W
        self.solids = []
        self.bar = [(15, 612, 95), (120, 632, 115), (245, 602, 135), (390, 622, 120),
                    (520, 642, 110), (640, 618, 135), (780, 628, 110), (900, 606, 100)]
        self.pylons = [(70, 1.0), (190, 0.85), (320, 1.1), (430, 0.9), (560, 1.0),
                       (665, 1.2), (730, 0.8), (855, 0.9), (955, 1.0)]
        self.boards = [(115, 1.0), (395, 0.9), (645, 1.1), (890, 0.95)]

    def _draw_pylon(self, surf, cam, wx, s):
        x = int(wx - cam.x)
        w = surf.get_width()
        if x < -30 or x > w + 30:
            return
        hgt = int(120 * s)
        pygame.draw.line(surf, (60, 70, 90), (x, int(GROUND_Y - cam.y)),
                         (x, int(GROUND_Y - cam.y) - hgt), 6)
        pygame.draw.line(surf, (60, 70, 90), (x - int(18 * s), int(GROUND_Y - cam.y) - hgt + 10),
                         (x + int(18 * s), int(GROUND_Y - cam.y) - hgt + 10), 6)

    def draw(self, surf, cam):
        w, h = surf.get_size()
        pygame.draw.rect(surf, (96, 120, 168), (0, 0, w, h))
        for x, top, bw in self.bar:
            r = pygame.Rect(int(x - cam.x), int(top - cam.y), bw, WORLD_H - top)
            pygame.draw.rect(surf, (70, 86, 120), r)
            pygame.draw.rect(surf, (52, 64, 92), r, 3)
        sun_x = int(500 - cam.x)
        pygame.draw.circle(surf, (255, 235, 150), (sun_x, int(120 - cam.y)), 50)
        gy = int(GROUND_Y - cam.y)
        total = WORLD_H - GROUND_Y
        pygame.draw.rect(surf, self.ROAD, (0, gy, w, total))
        pygame.draw.rect(surf, self.ROAD_LINE, (0, gy, w, 4))
        pygame.draw.rect(surf, (140, 140, 60), (0, gy + total - 18, w, 14))
        for wx in range(int(cam.x // 70) * 70, int(cam.x) + w + 140, 140):
            x = int(wx - cam.x)
            pygame.draw.rect(surf, self.ROAD_LINE, (x, gy + total // 2, 60, 5))
        for x, s in self.pylons:
            self._draw_pylon(surf, cam, x, s)
        for bx, s in self.boards:
            x = int(bx - cam.x)
            if x < -60 or x > w + 60:
                continue
            hgt = int(92 * s)
            py = int(GROUND_Y - cam.y) - hgt
            pygame.draw.rect(surf, (60, 70, 90), (x - 3, py, 6, hgt))
            board = pygame.Rect(x - int(34 * s), py - int(26 * s), int(68 * s), int(26 * s))
            pygame.draw.rect(surf, (150, 170, 200), board)
            pygame.draw.rect(surf, (40, 50, 70), board, 3)
            for i in range(3):
                pygame.draw.circle(surf, (255, 205 + i * 12, 80), (board.x + 8 + i * int(18 * s), board.centery + 2), int(6 * s))


class MineMap:
    N_GRASS = (96, 168, 66)
    N_DIRT = (134, 96, 64)
    N_DARK = (108, 76, 50)
    N_WATER = (56, 130, 216)
    STONE = (128, 122, 132)         # orman taşı (kırılabilir, +taş)
    STONE_DARK = (74, 70, 84)
    MINE_ROCK = (110, 118, 132)     # yeni: kırılmaz maden taşı
    MINE_ROCK_DARK = (66, 74, 88)
    L_TOP = (120, 34, 30)
    L_ROCK = (58, 56, 66)
    L_LAVA = (255, 120, 30)
    E_SKY = (24, 16, 46)
    E_ROCK = (86, 78, 120)
    E_STONE = (120, 116, 160)

    ORE_ACCENT = {"demir": (222, 158, 92), "altın": (240, 205, 90), "elmas": (140, 235, 245),
                  "kömür": (86, 86, 92)}
    DOOM = (66, 52, 66)      # enderman rock
    NB_TOP = (88, 30, 30)    # nether brick
    NB_DARK = (60, 20, 20)

    FOREST_END = 1540
    MINE_FLOOR_Y = 1350
    ORE_Y = MINE_FLOOR_Y - 40
    # DERİN MADEN: aşağı inen 4 basamak. Her kat aşağı indikçe değerli cevher.
    DEEP_LEVELS = [
        (2800, 3200, 1350),   # 1. kat: kömür + demir
        (3240, 3560, 1430),   # 2. kat: demir + altın
        (3600, 3880, 1510),   # 3. kat: altın + elmas
        (3920, 4240, 1590),   # 4. kat (en derin): elmas + obsidyen
    ]
    world_h = DEEP_LEVELS[-1][2] + 120   # kamera en derine kadar iner

    def __init__(self):
        self.name = "MINESTICK"
        self.disp_name = "MİNECRAFT"
        self.w = MINE_WORLD_W
        self.stage = "normal"
        self.ground = pygame.Rect(0, GROUND_Y, self.w, WORLD_H - GROUND_Y)
        self._base_blocks = self._gen_terrain()
        self._boulder_ids = {id(b) for b in self._boulders}
        self._dirt_ids = {id(b) for b in self._dirt_steps}
        self._rock_ids = {id(b) for b in self._mine_rock}
        self._base_ores = self._gen_ores()
        self.blocks = list(self._base_blocks) + [o["rect"] for o in self._base_ores]
        self.ores = [dict(o) for o in self._base_ores]
        # tek bir su gölü ve tek bir lav gölü (ormanın içinde birer açıklık)
        self.water = [pygame.Rect(620, GROUND_Y - 40, 260, 40)]
        # yüzey lav gölü (nether portalı burada yanar)
        self.mine_lava = [pygame.Rect(920, GROUND_Y - 46, 200, 46)]
        self.lava_pools = [pygame.Rect(265, GROUND_Y - 46, 55, 46),
                           pygame.Rect(415, GROUND_Y - 46, 55, 46),
                           pygame.Rect(585, GROUND_Y - 46, 50, 46),
                           pygame.Rect(730, GROUND_Y - 46, 55, 46),
                           pygame.Rect(890, GROUND_Y - 46, 30, 46),
                           pygame.Rect(620, GROUND_Y - 46, 380, 46),
                           pygame.Rect(2800, GROUND_Y - 46, 1000, 46)]
        self.portal = None
        self.portal_blocks = []
        self.portal_lit = False
        # lav kovasından dökülen lav birikintileri (kaza riskli alan, portal yakabilir)
        self.poured_lava = []
        # end portal (crafted frame, watered)
        self.end_frames = []
        self.end_portal_active = False
        self.end_portal = None
        # nether'deki tek portal: önündeki 3 netherite kırılınca açılır (ayrı tutulur)
        self.nether_end_active = False
        self.nether_end_portal = None
        self.netherite = []
        # R ile yerleştirilen bloklar (crafting table / end cersevesi etc.)
        self.placements = []
        # nether structures
        self.nether_rocks = []
        self._make_nether()
        self.trees = []
        # ORMAN: göllerin (620-880 su, 920-1120 lav) ve başlangıcın dışında
        # sabit/rastgele olmayan ağaç kuşağı
        for i, x in enumerate((270, 360, 450, 520, 1150, 1240, 1330, 1420)):
            s = (1.0, 0.9, 1.1, 0.85, 0.95, 1.05, 0.9, 0.85)[i]
            self.trees.append({"x": float(x), "s": s,
                               "trunk": pygame.Rect(int(x - 5), GROUND_Y - int(48 * s), 10, int(48 * s))})
        self._trunk_ids = {id(t["trunk"]) for t in self.trees}
        self.clouds = [(120, 120, 1.0), (400, 170, 1.1), (700, 90, 0.9), (1180, 150, 1.2)]
        self.refresh_solids()

    def _gen_terrain(self):
        blocks = []
        # orman taşları (taş verir, kırılabilir)
        self._boulders = [pygame.Rect(200, GROUND_Y - 60, 70, 60),
                          pygame.Rect(330, GROUND_Y - 45, 60, 45),
                          pygame.Rect(1240, GROUND_Y - 60, 70, 60),
                          pygame.Rect(1480, GROUND_Y - 60, 70, 60)]
        blocks += self._boulders
        # aşağı inen yol: rampa basamakları (dirt steps) 840 -> 1224,
        # son basamaktan 1. maden katına inilir. KIRILMAZ arazidir.
        self._dirt_steps = []
        for i in range(9):
            top = GROUND_Y + i * 48
            r = pygame.Rect(1560 + i * 132, top, 132, 60)
            self._dirt_steps.append(r)
            blocks.append(r)
        # DERİN MADEN: 4 aşağı inen kat (kırılmaz MADEN TAŞI).
        # Her kat üzerine basılan birer zemin; aralarından aşağı düşülünce
        # bir alt kata inilir.
        self._mine_rock = []
        for (sx, ex, top) in self.DEEP_LEVELS:
            r = pygame.Rect(sx, top, ex - sx, self.world_h - top)
            self._mine_rock.append(r)
            blocks.append(r)
        # mağara güvenlik zemini: merdivenlerin altı (dipsiz çukur olmasın)
        r = pygame.Rect(1560, 1400, 2748 - 1560, self.world_h - 1400)
        self._mine_rock.append(r)
        blocks.append(r)
        # KIRILMAZ arazi (toprak basamaklar + maden taşı)
        self._terrain_blocks = self._dirt_steps + self._mine_rock
        self._terrain_ids = {id(b) for b in self._terrain_blocks}
        return blocks

    def _gen_ores(self):
        self._pending_ores = []

        def add(typ, xs, y):
            for x in xs:
                self._pending_ores.append({"rect": pygame.Rect(x, y, TILE, TILE),
                                           "type": typ})

        # her cevherden belirtilen sayıda; derine indikçe değerli cevher.
        # her cevher yığını aynı türden olup zeminden tam destekli, hiçbiri yüzemez
        # 1. kat (1350): kömür 10 (barem + üstüstte dizili stack'ler)
        add("kömür", (2860, 2900, 2940, 2980, 3020, 3060), 1310)
        add("kömür", (2860, 2900, 2980, 3060), 1270)
        # 1. kat: taş 5 (taş kazma yapımı için kolay erişilebilir, 'tas' eşyası verir)
        add("tas", (3100, 3140, 3180), 1310)
        add("tas", (3140, 3180), 1270)
        # 2. kat (1430): demir 10
        add("demir", (3240, 3280, 3320, 3360, 3400, 3440, 3480), 1390)
        add("demir", (3280, 3360, 3440), 1350)
        # 3. kat (1510): altın 10
        add("altın", (3640, 3680, 3720, 3760, 3800), 1470)
        add("altın", (3640, 3680, 3720, 3760, 3800), 1430)
        # 4. kat (1590, en derin): obsidyen 14 + elmas 10, yan yana ayrı sütunlar
        add("obsidyen", (3920, 3960, 4000, 4040), 1550)
        add("obsidyen", (3920, 3960, 4000, 4040), 1510)
        add("obsidyen", (3920, 4040), 1470)
        add("obsidyen", (3920, 4040), 1430)
        add("obsidyen", (3920, 4040), 1390)
        add("elmas", (4080, 4120, 4160, 4200), 1550)
        add("elmas", (4080, 4120, 4160, 4200), 1510)
        add("elmas", (4080, 4160), 1470)
        return self._pending_ores

    def _spawn_cluster(self, oy, items):
        for typ, cx, n in items:
            for k in range(n):
                self._pending_ores.append({"rect": pygame.Rect(cx + k * 40, oy, TILE, TILE),
                                           "type": typ})

    def _make_nether(self):
        # kırılabilir nether kayası rafları (nether_tasi verir)
        self.nether_rocks = [
            pygame.Rect(80, GROUND_Y - 40, 120, 40),
            pygame.Rect(320, GROUND_Y - 40, 40, 40),
            pygame.Rect(470, GROUND_Y - 40, 60, 40),
            pygame.Rect(640, GROUND_Y - 40, 40, 40),
            pygame.Rect(820, GROUND_Y - 40, 40, 40),
            pygame.Rect(1040, GROUND_Y - 40, 400, 40),
            pygame.Rect(1500, GROUND_Y - 40, 500, 40),
            pygame.Rect(2520, GROUND_Y - 40, 80, 40),
            pygame.Rect(3960, GROUND_Y - 40, 40, 40),
        ]
        # tek end portalı + önündeki 3 netherite bloğu (elmas kazma gerektirir)
        self._netherite_base = [pygame.Rect(3780, GROUND_Y - 40, 40, 40),
                                pygame.Rect(3820, GROUND_Y - 40, 40, 40),
                                pygame.Rect(3860, GROUND_Y - 40, 40, 40)]
        self.netherite = list(self._netherite_base)
        self.nether_end_portal = pygame.Rect(3910, GROUND_Y - 80, 44, 80)
        self.nether_end_active = False

    def refresh_solids(self):
        if self.stage == "normal":
            # orman zemini sadece orman bölgesinde; maden tarafı açık çukur
            # (merdivenlerden aşağı inilir)
            self.ground = pygame.Rect(0, GROUND_Y, self.FOREST_END + 20,
                                      WORLD_H - GROUND_Y)
        else:
            self.ground = pygame.Rect(0, GROUND_Y, self.w, WORLD_H - GROUND_Y)
        self.solids = [self.ground] + self.blocks
        if self.stage == "normal":
            self.solids += [t["trunk"] for t in self.trees]
            self.solids += [p["rect"] for p in self.placements]
            if self.portal_blocks and not self.portal_lit:
                self.solids += self.portal_blocks
            if self.end_frames and not self.end_portal_active:
                self.solids += self.end_frames
        elif self.stage == "nether":
            self.solids += self.nether_rocks + self.netherite

    def hazard_zones(self):
        if self.stage == "normal":
            return ([("water", r) for r in self.water]
                    + [("lava", r) for r in self.mine_lava]
                    + [("lava", r) for r in self.poured_lava])
        if self.stage == "nether":
            return [("lava", r) for r in self.lava_pools + self.poured_lava]
        return []

    def draw(self, surf, cam):
        if self.stage == "normal":
            self._draw_forest(surf, cam)
        elif self.stage == "nether":
            self._draw_nether(surf, cam)
        else:
            self._draw_end(surf, cam)

    def _sky(self, surf, top, bottom):
        w, h = surf.get_size()
        pygame.draw.rect(surf, top, (0, 0, w, h))
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend(top, bottom, t), (0, y), (w, y))

    def _block_mat(self, r):
        """Rekt bu blok hangi malzeme? (Kırılmaz maden taşı / toprak / taş)"""
        rid = id(r)
        if rid in self._rock_ids:
            return (MineMap.MINE_ROCK, MineMap.MINE_ROCK_DARK, None)
        if rid in self._dirt_ids:
            return (MineMap.N_DIRT, MineMap.N_DARK, None)
        if rid in self._boulder_ids:
            return (MineMap.STONE, MineMap.STONE_DARK, None)
        if rid in self._trunk_ids:
            return ((108, 74, 44), (84, 54, 30), None)
        return None

    def _draw_block(self, surf, cam, r, body=None, dark=None, top=None):
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        if body is None:
            if self.stage == "normal":
                body, dark, top = self.N_DIRT, self.N_DARK, self.N_GRASS
            elif self.stage == "nether":
                body, dark, top = self.L_ROCK, (44, 42, 50), None
            else:
                body, dark, top = self.E_ROCK, (64, 58, 96), None
        pygame.draw.rect(surf, body, rr)
        if dark is not None:
            pygame.draw.rect(surf, dark, rr, 2)
        if top is not None:
            pygame.draw.rect(surf, top, (rr.x, rr.top, rr.w, 8))
        elif self.stage == "nether" and rr.h == 40:
            for x in range(rr.left + 8, rr.right - 8, 20):
                pygame.draw.circle(surf, (120, 50, 34), (x, rr.top + 6), 6)

    def _ore_draw(self, surf, cam, o):
        r = o["rect"]
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        typ = o["type"]
        if typ == "obsidyen":
            pygame.draw.rect(surf, (44, 38, 58), rr)
            pygame.draw.rect(surf, (130, 70, 190), rr, 2)
            pygame.draw.circle(surf, (96, 60, 150), (rr.x + 12, rr.y + 12), 6)
            pygame.draw.circle(surf, (96, 60, 150), (rr.right - 12, rr.bottom - 12), 6)
            return
        pc = self.ORE_ACCENT.get(typ, (200, 200, 200))
        for (px, py, s) in ((6, 6, 6), (20, 14, 5), (28, 26, 6), (12, 24, 5)):
            pygame.draw.circle(surf, pc, (rr.x + px, rr.y + py), s)
            pygame.draw.circle(surf, blend(pc, (40, 30, 20), 0.4), (rr.x + px, rr.y + py), s, 2)

    def _obsidian_draw(self, surf, cam, r):
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        pygame.draw.rect(surf, (40, 34, 54), rr)
        pygame.draw.rect(surf, (130, 70, 190), rr, 2)
        pygame.draw.circle(surf, (90, 56, 140), (rr.x + 10, rr.y + 10), 5)
        pygame.draw.circle(surf, (90, 56, 140), (rr.right - 10, rr.bottom - 10), 5)

    def _end_frame_draw(self, surf, cam, r):
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        pygame.draw.rect(surf, (58, 84, 66), rr)
        pygame.draw.rect(surf, (150, 235, 170), rr, 2)
        pygame.draw.rect(surf, (40, 50, 42), (rr.x + 6, rr.y + 6, rr.w - 12, rr.h - 12))
        pygame.draw.circle(surf, (170, 255, 190), (rr.centerx, rr.centery), 6)

    def _placement_draw(self, surf, cam, pl):
        r = pl["rect"]
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        if pl["item"] == "crafting_table":
            pygame.draw.rect(surf, (166, 126, 86), rr)
            pygame.draw.rect(surf, (206, 176, 138), (rr.x + 4, rr.y + 2, rr.w - 8, 10))
            pygame.draw.rect(surf, (110, 80, 54), rr, 2)
            pygame.draw.circle(surf, (220, 190, 150), (rr.x + 10, rr.y + 12), 4)
            pygame.draw.circle(surf, (220, 190, 150), (rr.right - 10, rr.y + 12), 4)
        else:  # yatak
            pygame.draw.rect(surf, (196, 128, 156), rr)
            pygame.draw.rect(surf, (240, 200, 220), (rr.x + 4, rr.y + 4, rr.w - 8, 12))
            pygame.draw.rect(surf, (150, 90, 116), rr, 2)

    def _draw_forest(self, surf, cam):
        w = surf.get_width()
        self._sky(surf, (122, 192, 235), (210, 235, 245))
        for wx, wy, s in self.clouds:
            x = int(wx - cam.x)
            if x < -90 or x > w + 90:
                continue
            pygame.draw.ellipse(surf, (255, 255, 255),
                                (x, int(wy - cam.y * .2), int(64 * s), int(26 * s)))
        for b in self.blocks + [t["trunk"] for t in self.trees]:
            mat = self._block_mat(b)
            if mat:
                self._draw_block(surf, cam, b, *mat)
            else:
                self._draw_block(surf, cam, b)
        for o in self.ores:
            self._ore_draw(surf, cam, o)
        for r in self.portal_blocks:
            self._obsidian_draw(surf, cam, r)
        for r in self.end_frames:
            self._end_frame_draw(surf, cam, r)
        for pl in self.placements:
            if pl["item"] == "end_cerceve":
                continue
            self._placement_draw(surf, cam, pl)
        self._draw_block(surf, cam, self.ground)
        top = pygame.Rect(int(self.ground.x - cam.x), int(self.ground.y - cam.y),
                          self.ground.w, 16)
        pygame.draw.rect(surf, self.N_GRASS, top)
        for x in range(top.x, top.right + 12, 24):
            pygame.draw.line(surf, (76, 152, 52), (x, top.bottom), (x - 12, top.bottom + 16), 2)
        # derin bölgeyi karart: zeminin altı
        deep_top = int(self.MINE_FLOOR_Y - cam.y)
        dark = pygame.Surface((w, max(0, int(280)),), pygame.SRCALPHA)
        dark.fill((14, 10, 26, 110))
        surf.blit(dark, (int(2600 - cam.x), deep_top - 24))
        self._draw_water(surf, cam, self.water, (56, 130, 216), (180, 220, 255))
        self._draw_water(surf, cam, self.mine_lava, (255, 120, 30), (255, 220, 120))
        self._draw_water(surf, cam, self.poured_lava, (255, 120, 30), (255, 220, 120))
        self._draw_trees(surf, cam)
        self._draw_portal(surf, cam)
        self._draw_end_portal(surf, cam)
        # derinlik işareti
        draw_text(surf, "DERİN MADEN", 22, (222, 226, 255),
                  (int(3230 - cam.x), int(self.MINE_FLOOR_Y - 210 - cam.y)))

    def _draw_water(self, surf, cam, pools, fill, line):
        for r in pools:
            rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
            if not surf.get_rect().colliderect(rr):
                continue
            wf = pygame.Surface((rr.w, rr.h), pygame.SRCALPHA)
            wf.fill(fill + (170,))
            surf.blit(wf, (rr.x, rr.y))
            pygame.draw.line(surf, line, (rr.x, rr.y + 2), (rr.right, rr.y + 2), 2)

    def _draw_trees(self, surf, cam):
        w = surf.get_width()
        base = int(GROUND_Y - cam.y)
        for t in self.trees:
            x = int(t["x"] - cam.x)
            if x < -70 or x > w + 70:
                continue
            s = t["s"]
            trh = t["trunk"].h
            pygame.draw.rect(surf, (108, 74, 44), (x - 4, base - trh, 8, trh))
            pygame.draw.rect(surf, (84, 54, 30), (x - 4, base - trh, 8, trh), 2)
            cy = base - trh - int(20 * s)
            pygame.draw.circle(surf, (66, 140, 60), (x, cy), int(24 * s))
            pygame.draw.circle(surf, (52, 118, 50), (x - int(12 * s), cy + int(6 * s)), int(16 * s))
            pygame.draw.circle(surf, (52, 118, 50), (x + int(12 * s), cy + int(6 * s)), int(16 * s))

    def _portal_rect(self):
        if not self.portal_blocks:
            return self.portal
        lx = min(r.x for r in self.portal_blocks)
        rx = max(r.right for r in self.portal_blocks)
        ty = min(r.top for r in self.portal_blocks)
        by = max(r.bottom for r in self.portal_blocks)
        return pygame.Rect(lx - 20, ty, rx - lx + 40, by - ty)

    def _end_frame_rect(self):
        if not self.end_frames:
            return None
        lx = min(r.x for r in self.end_frames)
        rx = max(r.right for r in self.end_frames)
        ty = min(r.top for r in self.end_frames)
        by = max(r.bottom for r in self.end_frames)
        return pygame.Rect(lx - 20, ty, rx - lx + 40, by - ty)

    def _draw_portal(self, surf, cam):
        r = self.portal
        if r is None:
            return
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        for side in (0, 1):
            fx = rr.x - 2 if side == 0 else rr.right + 2 - 8
            pygame.draw.rect(surf, (44, 38, 58), (fx, rr.y, 8, rr.h))
            pygame.draw.rect(surf, (130, 70, 190), (fx, rr.y, 8, rr.h), 2)
        cols = [(130, 40, 190), (150, 55, 210), (95, 30, 160), (170, 80, 230), (115, 36, 180)]
        for i in range(len(cols)):
            pygame.draw.rect(surf, cols[i], (rr.x + i * 9, rr.y, 9, rr.h))
            pygame.draw.rect(surf, (40, 30, 50), (rr.x + i * 9, rr.y, 9, rr.h), 1)
        pygame.draw.circle(surf, (235, 205, 255), (rr.centerx, rr.centery), 12)
        pygame.draw.circle(surf, (255, 255, 255), (rr.centerx, rr.centery + 4), 5)
        if rr.w > 50:
            for i in range(-1, 2):
                pygame.draw.circle(surf, (235, 205, 255),
                                   (rr.centerx + i * 16, rr.centery), 10)

    def _draw_end_portal(self, surf, cam):
        r = self.end_portal
        if r is None or not self.end_portal_active:
            return
        rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
        if not surf.get_rect().colliderect(rr):
            return
        for side in (0, 1):
            fx = rr.x - 2 if side == 0 else rr.right + 2 - 8
            pygame.draw.rect(surf, (58, 84, 66), (fx, rr.y, 8, rr.h))
            pygame.draw.rect(surf, (150, 235, 170), (fx, rr.y, 8, rr.h), 2)
        cols = [(30, 190, 120), (50, 230, 150), (20, 140, 90), (90, 255, 180), (35, 200, 140)]
        for i in range(len(cols)):
            pygame.draw.rect(surf, cols[i], (rr.x + i * 9, rr.y, 9, rr.h))
        pygame.draw.circle(surf, (210, 255, 230), (rr.centerx, rr.centery), 12)
        seq = [r for r in self.end_frames]
        by = max((r.bottom for r in seq), default=GROUND_Y)
        draw_text(surf, "ENDER", 12, (200, 255, 225), (rr.centerx, by - 4 - cam.y))

    def _draw_nether(self, surf, cam):
        w = surf.get_width()
        self._sky(surf, (96, 34, 34), (20, 10, 12))
        for wx in range(int(cam.x // 120) * 120, int(cam.x) + w + 200, 120):
            x = int(wx - cam.x)
            pygame.draw.circle(surf, (200, 90, 30), (x, int(60 - cam.y * .2)), 8)
        # netherite blokları (elmas kazma ile kırılır)
        for r in self.netherite:
            rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
            if not surf.get_rect().colliderect(rr):
                continue
            pygame.draw.rect(surf, (42, 42, 52), rr)
            pygame.draw.rect(surf, (20, 20, 28), rr, 3)
            pygame.draw.rect(surf, (150, 148, 165), (rr.x + 5, rr.y + 5, rr.w - 10, rr.h - 10))
            pygame.draw.rect(surf, (42, 42, 52), (rr.x + 5, rr.y + 5, rr.w - 10, rr.h - 10), 2)
        for r in self.nether_rocks:
            self._draw_block(surf, cam, r)
        self._draw_block(surf, cam, self.ground)
        self._draw_water(surf, cam, self.lava_pools, (255, 120, 30), (255, 220, 120))
        self._draw_water(surf, cam, self.poured_lava, (255, 120, 30), (255, 220, 120))
        self._draw_portal(surf, cam)
        self._draw_end_portal(surf, cam)
        # tek portal: aktifken mor parlıyor, kapalıyken karanlık görünür
        r = self.nether_end_portal
        if r is not None:
            rr = pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)
            if surf.get_rect().colliderect(rr):
                for side in (0, 1):
                    fx = rr.x - 3 if side == 0 else rr.right + 3 - 8
                    pygame.draw.rect(surf, (48, 40, 60), (fx, rr.y, 8, rr.h))
                    pygame.draw.rect(surf, (150, 60, 220) if self.nether_end_active else (70, 58, 90),
                                     (fx, rr.y, 8, rr.h), 2)
                cols = ([(120, 30, 180), (150, 55, 210), (80, 20, 150),
                         (180, 90, 240), (105, 32, 170)]
                        if self.nether_end_active else
                        [(34, 30, 40), (40, 36, 48), (30, 27, 36), (44, 40, 52), (32, 29, 38)])
                for i in range(len(cols)):
                    pygame.draw.rect(surf, cols[i], (rr.x + i * 9, rr.y, 9, rr.h))
                    pygame.draw.rect(surf, (24, 20, 30), (rr.x + i * 9, rr.y, 9, rr.h), 1)
                pygame.draw.circle(surf, (235, 205, 255) if self.nether_end_active else (110, 95, 130),
                                   (rr.centerx, rr.centery), 12)
                draw_text(surf, "END PORTALI", 12,
                          (220, 190, 255) if self.nether_end_active else (150, 140, 170),
                          (rr.centerx, rr.bottom - 4 - cam.y))
        if not self.nether_end_active and self.netherite:
            draw_text(surf, "3 NETHERITE KIR (ELMAS KAZMA)", 12, (180, 190, 210),
                      (round(self.netherite[0].centerx - cam.x),
                       int(self.netherite[0].top - cam.y - 30)))

    def _draw_end(self, surf, cam):
        w = surf.get_width()
        self._sky(surf, self.E_SKY, (44, 34, 84))
        for wx in range(int(cam.x // 90) * 90, int(cam.x) + w + 200, 180):
            x = int(wx - cam.x)
            pygame.draw.circle(surf, (150, 150, 200), (x, int(50 - cam.y * .2)), 5)
        for b in self.solids:
            if b.bottom <= WORLD_H:
                self._draw_block(surf, cam, b)
        self._draw_block(surf, cam, self.ground, self.E_ROCK, (64, 58, 96), (150, 148, 200))


class HouseMap:
    WALL = (227, 209, 178)
    WALL_DARK = (140, 118, 90)
    WALL_LINE = (120, 96, 68)
    FLOOR = (176, 138, 98)
    FLOOR_DARK = (138, 102, 70)
    CEIL_H = 560

    def __init__(self):
        self.name = "HOUSE"
        self.disp_name = "EV"
        self.w = WORLD_W
        self.CEIL_H = 560
        self.floor = pygame.Rect(0, GROUND_Y, WORLD_W, WORLD_H - GROUND_Y)
        self.lslab = self.floor
        self.rslab = self.floor
        self.lwall = pygame.Rect(30, GROUND_Y - 560, 26, 560)
        self.rwall = pygame.Rect(WORLD_W - 56, GROUND_Y - 560, 26, 560)
        self.koltuk = pygame.Rect(380, GROUND_Y - 66, 150, 66)
        self.masa = pygame.Rect(430, GROUND_Y - 40, 60, 40)
        self.yemek = pygame.Rect(620, GROUND_Y - 48, 90, 48)
        self.solids = [self.floor, self.lwall, self.rwall, self.koltuk, self.masa,
                       self.yemek]
        self.red_zone = pygame.Rect(110, GROUND_Y - 40, 40, 40)
        self.wall_art = [(70, 450), (910, 450), (910, 200)]

    def _rect(self, r, cam):
        return pygame.Rect(int(r.x - cam.x), int(r.y - cam.y), r.w, r.h)

    def draw(self, surf, cam):
        w, h = surf.get_size()
        pygame.draw.rect(surf, (214, 196, 164), (0, 0, w, h))
        ceiling = int(GROUND_Y - self.CEIL_H - cam.y)
        pygame.draw.rect(surf, (238, 230, 212), (0, 0, w, max(0, ceiling)))
        gy = int(GROUND_Y - cam.y)
        fr = pygame.Rect(int(self.floor.x - cam.x), gy, self.floor.w, self.floor.h)
        pygame.draw.rect(surf, self.FLOOR, fr)
        for wx in range(int(cam.x // 82) * 82, int(cam.x) + w + 164, 82):
            x = int(wx - cam.x)
            if x < -41 or x > w + 41:
                continue
            pygame.draw.line(surf, self.FLOOR_DARK, (x, gy), (x, gy + 88), 3)
            pygame.draw.line(surf, self.FLOOR_DARK, (x + 41, gy), (x + 41, gy + 88), 3)
        rug = pygame.Rect(int(420 - cam.x), gy, 180, 10)
        pygame.draw.rect(surf, (188, 120, 96), rug)
        pygame.draw.rect(surf, (150, 88, 66), (rug.x, rug.y, rug.w, 10), 2)
        pygame.draw.line(surf, self.WALL_LINE, (0, gy), (w, gy), 4)
        for wall in (self.lwall, self.rwall):
            rr = self._rect(wall, cam)
            if not surf.get_rect().colliderect(rr):
                continue
            pygame.draw.rect(surf, self.WALL, rr)
            pygame.draw.rect(surf, self.WALL_LINE, rr, 4)
            pygame.draw.rect(surf, (196, 178, 148), (rr.x, rr.bottom - 10, rr.w, 10))
            for y in range(rr.y + 16, rr.bottom - 60, 96):
                pygame.draw.line(surf, (128, 104, 76), (rr.x + 8, y), (rr.right - 8, y), 3)
            win = pygame.Rect(rr.x + 4, rr.y + 120, rr.w - 8, 130)
            pygame.draw.rect(surf, (188, 218, 248), win)
            pygame.draw.rect(surf, (150, 128, 100), win, 4)
            pygame.draw.line(surf, (150, 128, 100), (win.centerx, win.top), (win.centerx, win.bottom), 3)
            pygame.draw.line(surf, (150, 128, 100), (win.left, win.centery), (win.right, win.centery), 3)
        door = pygame.Rect(int(58 - cam.x), gy - 150, 54, 150)
        pygame.draw.rect(surf, (120, 96, 66), door)
        pygame.draw.rect(surf, (92, 72, 48), door, 3)
        pygame.draw.rect(surf, (196, 178, 148), (door.x + 8, door.y + 20, 12, 90))
        pygame.draw.circle(surf, (200, 180, 120), (door.right - 14, door.centery), 4)
        self._draw_picture(surf, cam, 95)
        lampx = int(500 - cam.x)
        pygame.draw.line(surf, (140, 116, 84), (lampx, ceiling + 2), (lampx, ceiling + 26), 4)
        pygame.draw.circle(surf, (255, 221, 130), (lampx, ceiling + 34), 22)
        pygame.draw.circle(surf, (150, 128, 96), (lampx, ceiling + 34), 22, 2)
        pygame.draw.circle(surf, (255, 190, 90), (lampx, ceiling + 46), 10)
        self._draw_fixture(surf, cam, self.koltuk, "couch")
        self._draw_fixture(surf, cam, self.masa, "sehpa")
        self._draw_fixture(surf, cam, self.yemek, "masa")
        pulse = (math.sin(pygame.time.get_ticks() * 0.008) + 1.0) / 2.0
        rzr = pygame.Rect(int(self.red_zone.x - cam.x), int(self.red_zone.y - cam.y),
                          self.red_zone.w, self.red_zone.h)
        if surf.get_rect().colliderect(rzr):
            pygame.draw.rect(surf, blend((255, 45, 45), (150, 25, 25), pulse), rzr)
            pygame.draw.rect(surf, (90, 12, 12), rzr, 3)
        for xart, topoff in self.wall_art:
            ar = pygame.Rect(int(xart - cam.x), int(GROUND_Y - 560 + topoff - cam.y), 52, 44)
            if not surf.get_rect().colliderect(ar):
                continue
            pygame.draw.rect(surf, (140, 112, 76), ar)
            pygame.draw.rect(surf, (96, 72, 46), ar, 3)
            pygame.draw.circle(surf, (245, 215, 130), (ar.centerx, ar.y + 14), 8)
            pygame.draw.polygon(surf, (105, 160, 80),
                                [(ar.centerx, ar.bottom - 6), (ar.x + 8, ar.bottom - 4), (ar.right - 8, ar.bottom - 4)])

    def _draw_picture(self, surf, cam, wx):
        fr = pygame.Rect(int(wx - cam.x), int(GROUND_Y - 480 - cam.y), 60, 80)
        pygame.draw.rect(surf, (120, 96, 66), fr)
        pygame.draw.rect(surf, (92, 72, 48), fr, 3)
        pygame.draw.rect(surf, (150, 130, 160), (fr.x + 6, fr.y + 6, fr.w - 12, fr.h - 24))
        pygame.draw.circle(surf, (250, 214, 130), (fr.centerx, fr.y + 30), 9)
        pygame.draw.polygon(surf, (110, 150, 70),
                            [(fr.centerx, fr.y + 58), (fr.x + 8, fr.bottom - 8), (fr.right - 8, fr.bottom - 8)])

    def _draw_fixture(self, surf, cam, f, kind):
        rr = self._rect(f, cam)
        if not surf.get_rect().colliderect(rr):
            return
        if kind == "plat":
            pygame.draw.rect(surf, (150, 106, 66), rr)
            pygame.draw.rect(surf, (96, 64, 38), rr, 4)
            for x in range(rr.left + 12, rr.right - 4, 48):
                pygame.draw.line(surf, (120, 82, 50), (x, rr.top + 4), (x, rr.bottom - 4), 3)
            rail = (int(rr.left - cam.x), int(rr.top - cam.y) - 44)
            for rx in (rr.left, rr.right):
                pygame.draw.line(surf, (120, 84, 52), (rx, rr.top), (rx, rr.top - 46), 5)
                pygame.draw.circle(surf, (120, 84, 52), (rx, rr.top - 48), 5)
            pygame.draw.line(surf, (140, 100, 64), (rr.left, rr.top - 44), (rr.right, rr.top - 44), 5)
        elif kind == "step":
            pygame.draw.rect(surf, (140, 98, 60), rr)
            pygame.draw.rect(surf, (92, 62, 36), rr, 3)
            pygame.draw.rect(surf, (200, 170, 120), (rr.x, rr.top, rr.w, 5))
        elif kind == "dolap":
            pygame.draw.rect(surf, (150, 112, 78), rr)
            pygame.draw.rect(surf, (110, 76, 50), rr, 4)
            pygame.draw.line(surf, (110, 76, 50), (rr.left, rr.centery), (rr.right, rr.centery), 4)
            for dx in (10, rr.w // 2 + 6):
                pygame.draw.circle(surf, (220, 190, 140), (rr.x + dx, rr.y + rr.h // 4), 4)
                pygame.draw.circle(surf, (220, 190, 140), (rr.x + dx, rr.y + rr.h * 3 // 4), 4)
        elif kind == "couch":
            pygame.draw.rect(surf, (168, 92, 66), rr)
            pygame.draw.rect(surf, (120, 62, 44), rr, 4)
            pygame.draw.rect(surf, (200, 160, 100), (rr.x + 10, rr.y + 6, rr.w - 20, 22))
            pygame.draw.rect(surf, (134, 68, 48), (rr.x + 6, rr.y + 26, 20, rr.h - 30))
            pygame.draw.rect(surf, (134, 68, 48), (rr.right - 26, rr.y + 26, 20, rr.h - 30))
            for sx in (rr.x + 52, rr.x + 90):
                pygame.draw.rect(surf, (134, 68, 48), (sx, rr.y + 30, 14, 26))
                pygame.draw.circle(surf, (134, 68, 48), (sx + 7, rr.y + 28), 7)
        elif kind == "sehpa":
            pygame.draw.line(surf, (112, 78, 46), (rr.centerx - 18, rr.bottom), (rr.centerx - 18, rr.bottom + 14), 5)
            pygame.draw.line(surf, (112, 78, 46), (rr.centerx + 18, rr.bottom), (rr.centerx + 18, rr.bottom + 14), 5)
            pygame.draw.rect(surf, (156, 118, 76), rr)
            pygame.draw.rect(surf, (112, 78, 46), rr, 4)
            pygame.draw.rect(surf, (210, 180, 140), (rr.x + 8, rr.y + 4, rr.w - 16, 6))
            for (ix, iy, ic) in ((rr.x + 12, rr.y + 14, (160, 80, 60)), (rr.right - 24, rr.y + 14, (90, 130, 180)),
                                 (rr.x + 12, rr.bottom - 10, (120, 150, 90)), (rr.right - 24, rr.bottom - 10, (200, 180, 90))):
                pygame.draw.circle(surf, ic, (ix, iy), 5)
        elif kind == "tv":
            pygame.draw.rect(surf, (118, 90, 60), rr)
            pygame.draw.rect(surf, (84, 60, 40), rr, 4)
            pygame.draw.rect(surf, (30, 38, 66), (rr.x + 8, rr.top + 8, rr.w - 16, rr.h - 20))
            pygame.draw.rect(surf, (120, 170, 235), (rr.x + 12, rr.top + 12, rr.w - 24, rr.h - 48), 2)
            pygame.draw.polygon(surf, (40, 50, 80), [(rr.x + 12, rr.top + 14), (rr.centerx, rr.centery),
                                                     (rr.right - 12, rr.top + 14)])
        elif kind == "tezgah":
            pygame.draw.rect(surf, (124, 156, 158), rr)
            pygame.draw.rect(surf, (84, 114, 116), rr, 4)
            pygame.draw.rect(surf, (170, 205, 205), (rr.x + 6, rr.y + 4, rr.w - 12, 6))
            pygame.draw.circle(surf, (60, 60, 64), (rr.x + 26, rr.y + 34), 9)
            pygame.draw.circle(surf, (60, 60, 64), (rr.x + 48, rr.y + 34), 9)
            pygame.draw.line(surf, (170, 210, 210), (rr.x + 34, rr.y - 2), (rr.x + 40, rr.y - 26), 4)
            pygame.draw.line(surf, (170, 210, 210), (rr.x + 40, rr.y - 26), (rr.x + 52, rr.y - 26), 3)
            cu1 = pygame.Rect(rr.x + 6, rr.y - 66, 44, 60)
            cu2 = pygame.Rect(rr.right - 52, rr.y - 74, 46, 68)
            pygame.draw.rect(surf, (112, 144, 148), cu1)
            pygame.draw.rect(surf, (82, 112, 116), cu1, 3)
            pygame.draw.rect(surf, (112, 144, 148), cu2)
            pygame.draw.rect(surf, (82, 112, 116), cu2, 3)
            pygame.draw.rect(surf, (150, 185, 190), (cu1.x + 6, cu1.y + 8, 12, 6))
            pygame.draw.rect(surf, (150, 185, 190), (cu1.right - 18, cu1.y + 8, 12, 6))
            pygame.draw.rect(surf, (150, 185, 190), (cu2.x + 8, cu2.y + 10, 14, 6))
            pygame.draw.rect(surf, (150, 185, 190), (cu2.right - 22, cu2.y + 10, 14, 6))
            for (hx, hcol) in ((cu2.x + 16, (60, 130, 90)), (cu2.x + 34, (200, 150, 60))):
                pygame.draw.rect(surf, hcol, (hx, cu2.bottom - 40, 10, 40))
                pygame.draw.rect(surf, (40, 40, 42), (hx + 2, cu2.bottom - 48, 6, 10))
        elif kind == "fridge":
            pygame.draw.rect(surf, (224, 230, 234), rr)
            pygame.draw.rect(surf, (150, 156, 160), rr, 4)
            pygame.draw.line(surf, (150, 156, 160), (rr.x, rr.centery), (rr.right, rr.centery), 4)
            pygame.draw.rect(surf, (40, 40, 42), (rr.x + 6, rr.y + 22, rr.w - 12, 5))
            pygame.draw.rect(surf, (40, 40, 42), (rr.x + 6, rr.centery + 22, rr.w - 12, 5))
            pygame.draw.rect(surf, (196, 202, 206), (rr.right - 9, rr.y + 60, 5, 30))
        elif kind == "masa":
            for dx in (-42, 42):
                pygame.draw.line(surf, (116, 82, 48), (rr.centerx + dx, rr.bottom),
                                 (rr.centerx + dx, rr.bottom + 18), 5)
            pygame.draw.rect(surf, (160, 122, 78), rr)
            pygame.draw.rect(surf, (116, 82, 48), rr, 4)
            pygame.draw.line(surf, (210, 180, 140), (rr.x + 10, rr.y + 6), (rr.right - 10, rr.y + 6), 3)
            for (px, py) in ((rr.x + 22, rr.y + 16), (rr.centerx - 18, rr.y + 16),
                             (rr.centerx + 16, rr.y + 16), (rr.right - 34, rr.y + 16)):
                pygame.draw.rect(surf, (240, 240, 235), (px, py, 16, 12))
                pygame.draw.rect(surf, (200, 200, 195), (px, py, 16, 12), 1)
        elif kind == "bed":
            pygame.draw.rect(surf, (140, 150, 168), rr)
            pygame.draw.rect(surf, (100, 110, 130), rr, 4)
            pygame.draw.rect(surf, (240, 240, 240), (rr.x + 4, rr.top + 8, rr.w - 40, rr.h - 12))
            pygame.draw.rect(surf, (118, 70, 90), (rr.x + 4, rr.top + 8, rr.w - 46, 16))
            pygame.draw.rect(surf, (120, 60, 40), (rr.x + rr.w - 34, rr.top + 8, 30, rr.h - 46))
        elif kind == "shelf":
            pygame.draw.rect(surf, (128, 94, 62), rr)
            pygame.draw.rect(surf, (88, 60, 38), rr, 4)
            n = 4
            for i in range(n):
                y = rr.y + 6 + i * ((rr.h - 12) // n)
                pygame.draw.line(surf, (88, 60, 38), (rr.x + 3, y), (rr.right - 3, y), 3)
                for j in range(3):
                    bx = rr.x + 4 + j * 6
                    pygame.draw.circle(surf, (150 + j * 25, 90, 60), (bx + 3, y - 7), 4)


class JohnnyMap:
    def __init__(self):
        self.name = "JOHNNY"
        self.disp_name = "JOHNNY"
        self.w = WORLD_W
        self.ground = pygame.Rect(0, GROUND_Y, WORLD_W, WORLD_H - GROUND_Y)
        self.solids = [self.ground]

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend((26, 22, 44), (10, 9, 18), t), (0, y), (w, y))
        for i in range(11):
            a = i / 10.0
            c = int(500 - cam.x)
            cy = int(460 - cam.y)
            pygame.draw.circle(surf, blend((70, 46, 110), (18, 14, 30), a), (c, cy), int(230 * (1 - a)))
        gr = pygame.Rect(int(self.ground.x - cam.x), int(self.ground.y - cam.y),
                         self.ground.w, self.ground.h)
        pygame.draw.rect(surf, (46, 48, 66), gr)
        pygame.draw.rect(surf, (120, 60, 200), (gr.x, gr.y, gr.w, 8))
        banner = pygame.Rect(int(500 - cam.x) - 260, int(30 - cam.y * 0.1), 520, 26)
        pygame.draw.rect(surf, (120, 60, 200), banner)
        pygame.draw.rect(surf, (200, 160, 255), banner, 3)
        for side in (0, 1):
            basex = 30 if side == 0 else 862
            for i in range(7):
                x = int(basex + i * 20 - cam.x)
                hy = int(GROUND_Y - 34 - cam.y) - ((i + side) % 2) * 4
                if x < -16 or x > w + 16:
                    continue
                pygame.draw.circle(surf, (200 - i * 10, 140, 60), (x, hy), 7)
                pygame.draw.line(surf, (60, 46, 90), (x - 6, hy + 6), (x - 6, hy + 26), 6)
                pygame.draw.line(surf, (60, 46, 90), (x + 6, hy + 6), (x + 6, hy + 26), 6)
            bx = int((40 if side == 0 else 858) - cam.x)
            pygame.draw.rect(surf, (70, 56, 96), (bx, int(GROUND_Y - 46 - cam.y), 150, 46))
            pygame.draw.rect(surf, (40, 32, 60), (bx, int(GROUND_Y - 46 - cam.y), 150, 46), 3)
        for tx in (170, 830):
            x = int(tx - cam.x)
            base = int(GROUND_Y - cam.y)
            if x < -20 or x > w + 20:
                continue
            pillar = pygame.Rect(x - 10, base - 120, 20, 120)
            pygame.draw.rect(surf, (70, 56, 96), pillar)
            pygame.draw.rect(surf, (40, 32, 60), pillar, 3)
            pygame.draw.circle(surf, (255, 170, 40), (x, base - 132), 11)
            pygame.draw.circle(surf, (255, 220, 120), (x, base - 132), 5)
        for px in (60, 940):
            cx = int(px - cam.x)
            cy = int(GROUND_Y - 240 - cam.y)
            if cx < -80 or cx > w + 80:
                continue
            for k in range(5):
                r = 80 - k * 14
                pygame.draw.circle(surf, blend((90, 46, 150), (20, 14, 34), k / 4.0),
                                   (cx, cy), r, 4)
            pygame.draw.circle(surf, (200, 160, 255), (cx, cy), 6)


class ZombieMap:
    """ZOMBİ SURVIVAL arenası: dalga dalga zombi/örümcek/creeper saldırır."""
    def __init__(self):
        self.name = "ZOMBİ SURVIVAL"
        self.disp_name = "ZOMBİ"
        self.w = WORLD_W
        self.ground = pygame.Rect(0, GROUND_Y, WORLD_W, WORLD_H - GROUND_Y)
        self.crates = [pygame.Rect(180, GROUND_Y - 40, 90, 40),
                       pygame.Rect(440, GROUND_Y - 55, 70, 55),
                       pygame.Rect(700, GROUND_Y - 40, 90, 40)]
        self.solids = [self.ground] + self.crates

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend((70, 52, 62), (20, 14, 24), t), (0, y), (w, y))
        gr = pygame.Rect(int(self.ground.x - cam.x), int(self.ground.y - cam.y),
                         self.ground.w, self.ground.h)
        pygame.draw.rect(surf, (52, 62, 44), gr)
        pygame.draw.rect(surf, (96, 118, 54), (gr.x, gr.y, gr.w, 8))
        for c in self.crates:
            r = pygame.Rect(int(c.x - cam.x), int(c.y - cam.y), c.w, c.h)
            pygame.draw.rect(surf, (116, 84, 52), r)
            pygame.draw.rect(surf, (70, 50, 30), r, 3)
            pygame.draw.line(surf, (70, 50, 30), (r.x, r.y), (r.right, r.bottom), 3)
            pygame.draw.line(surf, (70, 50, 30), (r.right, r.y), (r.x, r.bottom), 3)
        banner = pygame.Rect(int(500 - cam.x) - 220, int(40 - cam.y * 0.1), 440, 26)
        pygame.draw.rect(surf, (96, 118, 54), banner)
        pygame.draw.rect(surf, (190, 210, 130), banner, 3)
        draw_text(surf, "ZOMBİ SURVIVAL • HAYATTA KAL", 20, (255, 255, 255), banner.center)


class FootMap:
    """FUTBOL stadyumu: iki oyuncu + top + iki kale."""
    def __init__(self):
        self.name = "FUTBOL"
        self.disp_name = "FUTBOL"
        self.w = WORLD_W
        self.ground = pygame.Rect(0, GROUND_Y, WORLD_W, WORLD_H - GROUND_Y)
        self.goal_left = [pygame.Rect(60, GROUND_Y - 90, 10, 90),
                          pygame.Rect(60, GROUND_Y - 22, 48, 22)]
        self.goal_right = [pygame.Rect(930, GROUND_Y - 90, 10, 90),
                           pygame.Rect(932, GROUND_Y - 22, 48, 22)]
        self.side_walls = [pygame.Rect(FOOT_ARENA_LEFT - 6, GROUND_Y - 180, 6, 180),
                           pygame.Rect(FOOT_ARENA_RIGHT, GROUND_Y - 180, 6, 180)]
        self.solids = [self.ground] + self.goal_left + self.goal_right + self.side_walls

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend((54, 86, 150), (22, 34, 66), t), (0, y), (w, y))
        gr = pygame.Rect(int(self.ground.x - cam.x), int(self.ground.y - cam.y),
                         self.ground.w, self.ground.h)
        pygame.draw.rect(surf, (66, 170, 86), gr)
        pygame.draw.rect(surf, (46, 130, 66), (gr.x, gr.y, gr.w, 6))
        gy = gr.y
        for i in range(0, 14):
            x = int(i * 80 - cam.x)
            pygame.draw.rect(surf, (90, 200, 110), (x, gy, 40, 6))
        pygame.draw.rect(surf, (255, 255, 255), (int(500 - cam.x) - 2, gy, 4, gr.h))
        pygame.draw.circle(surf, (255, 255, 255), (int(500 - cam.x), gy), 60, 4)
        for goal in (self.goal_left, self.goal_right):
            for b in goal:
                r = pygame.Rect(int(b.x - cam.x), int(b.y - cam.y), b.w, b.h)
                pygame.draw.rect(surf, (235, 235, 240), r)
                pygame.draw.rect(surf, (120, 120, 130), r, 3)
        draw_text(surf, "FUTBOL • İLK 3 GOL", 20, (255, 255, 255),
                  (int(500 - cam.x), int(60 - cam.y * 0.1)))


class LaserRunMap:
    """LAZER RUN: platform + sağdan gelen bloklar + sonundaki lazerler."""
    def __init__(self):
        self.name = "LAZER RUN"
        self.disp_name = "LAZER"
        self.w = WORLD_W
        self.ground = pygame.Rect(0, GROUND_Y, WORLD_W, WORLD_H - GROUND_Y)
        # Platform: uzun ince zemin
        self.platform = pygame.Rect(100, GROUND_Y - 200, 800, 20)
        # Lazer alanları (platformun sonundaki iki kale benzeri)
        self.lasers = [
            pygame.Rect(880, GROUND_Y - 300, 20, 300),   # alt lazer
            pygame.Rect(880, GROUND_Y - 550, 20, 250),   # üst lazer
        ]
        self.solids = [self.ground, self.platform] + self.lasers

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend((20, 10, 30), (5, 2, 10), t), (0, y), (w, y))
        gr = pygame.Rect(int(self.ground.x - cam.x), int(self.ground.y - cam.y),
                         self.ground.w, self.ground.h)
        pygame.draw.rect(surf, (30, 20, 40), gr)
        # Platform çiz
        pr = pygame.Rect(int(self.platform.x - cam.x), int(self.platform.y - cam.y),
                         self.platform.w, self.platform.h)
        pygame.draw.rect(surf, (80, 60, 100), pr)
        pygame.draw.rect(surf, (120, 100, 140), pr, 2)
        # Lazerler
        for lr in self.lasers:
            rr = pygame.Rect(int(lr.x - cam.x), int(lr.y - cam.y), lr.w, lr.h)
            pygame.draw.rect(surf, (255, 40, 60), rr)
            pygame.draw.rect(surf, (255, 180, 100), rr, 2)
            # lazer ışıklı efekti
            for i in range(3):
                pygame.draw.line(surf, (255, 200, 50),
                                 (rr.centerx, rr.top + i * 8),
                                 (rr.centerx, rr.bottom - i * 8), 1)
        draw_text(surf, "LAZER RUN • BLOKLARDAN KAÇ • LAZERLERE DOKUNMA", 18,
                  (255, 255, 255), (int(500 - cam.x), int(50 - cam.y * 0.1)))


class BossMap:
    """BOSS FIGHTS arenası: 100 boss (20 tier x 5 tema) ile dövüş."""
    def __init__(self):
        self.name = "BOSS FIGHTS"
        self.disp_name = "BOSS"
        self.w = WORLD_W
        self.ground = pygame.Rect(0, GROUND_Y, WORLD_W, WORLD_H - GROUND_Y)
        self.walls = [pygame.Rect(30, GROUND_Y - 130, 24, 130),
                      pygame.Rect(WORLD_W - 54, GROUND_Y - 130, 24, 130)]
        self.solids = [self.ground] + self.walls

    def draw(self, surf, cam):
        w, h = surf.get_size()
        for y in range(h):
            t = y / float(max(1, h - 1))
            pygame.draw.line(surf, blend((54, 30, 74), (14, 8, 22), t), (0, y), (w, y))
        gr = pygame.Rect(int(self.ground.x - cam.x), int(self.ground.y - cam.y),
                         self.ground.w, self.ground.h)
        pygame.draw.rect(surf, (64, 46, 74), gr)
        pygame.draw.rect(surf, (150, 90, 220), (gr.x, gr.y, gr.w, 8))
        for b in self.walls:
            r = pygame.Rect(int(b.x - cam.x), int(b.y - cam.y), b.w, b.h)
            pygame.draw.rect(surf, (84, 64, 96), r)
            pygame.draw.rect(surf, (44, 32, 54), r, 3)
        banner = pygame.Rect(int(500 - cam.x) - 220, int(40 - cam.y * 0.1), 440, 26)
        pygame.draw.rect(surf, (150, 90, 220), banner)
        pygame.draw.rect(surf, (220, 180, 255), banner, 3)
        draw_text(surf, "BOSS FIGHTS • 15 BOSS", 20, (255, 255, 255), banner.center)


MAP_OBJECTS = {"grass": GrassMap, "village": VillageMap, "city": CityMap, "trucks": TrucksMap,
                "minestick": MineMap, "house": HouseMap, "johnny": JohnnyMap,
                "zombi": ZombieMap, "football": FootMap, "laserrun": LaserRunMap, "boss": BossMap}