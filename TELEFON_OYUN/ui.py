import math
import random
from types import SimpleNamespace
import pygame
import chars
import maps
from settings import *
from classes import PACKS as CLASS_PACKS, CLASS_BY_ID, SKILLS
import savegame
import settings


def _wrap(text, limit):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = w if not cur else cur + " " + w
    if cur:
        lines.append(cur)
    return lines


def draw_icon(surf, cx, cy, scale, color):
    def pt(x, y):
        return (int(cx + x * scale), int(cy + y * scale))
    lw = max(2, int(3 * scale))
    pygame.draw.circle(surf, color, pt(0, -30), int(9 * scale))
    pygame.draw.line(surf, color, pt(0, -20), pt(0, 2), lw)
    pygame.draw.line(surf, color, pt(0, 2), pt(-9, 14), lw)
    pygame.draw.line(surf, color, pt(0, 2), pt(9, 14), lw)
    pygame.draw.line(surf, color, pt(0, -20), pt(10, -4), lw)
    pygame.draw.line(surf, color, pt(0, -20), pt(-10, -4), lw)


def _default_bg():
    return make_bg(SCREEN_W, SCREEN_H, settings.BG_COLOR, tuple(max(0, c - 40) for c in settings.BG_COLOR))


class MenuScreen:
    def __init__(self):
        self.bg = _default_bg()
        self.t = 0.0
        self.items = ["OYNA", "ONLINE", "AYARLAR", "DÜKKAN",
                      "GÜNCELLEME KAYITLARI", "ÇIKIŞ"]
        self.hints = ["KARAKTER & HARİTA SEÇ", "4 KİŞİLİK ODA - AYNI AĞ",
                      "TUŞLAR VE ARKA PLAN", "PAKET SATIN AL",
                      "YENİLİKLER", "OYUNDAN ÇIK"]
        self.icons = ["play", "net", "gear", "coin", "book", "door"]
        self.index = 0
        self.hover = -1
        self.buttons = []
        for i, _ in enumerate(self.items):
            self.buttons.append(pygame.Rect(SCREEN_W // 2 - 190, 318 + i * 74, 380, 60))
        self.motes = [[random.uniform(0, SCREEN_W), random.uniform(0, SCREEN_H),
                     random.uniform(6, 22), random.uniform(-14, -4)]
                    for _ in range(48)]

    def update(self, dt):
        self.t += dt
        mx, my = logical_pos()
        self.hover = -1
        for i, r in enumerate(self.buttons):
            if r.collidepoint(mx, my):
                self.hover = i

    def handle_event(self, e, game):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.items)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.items)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
                self._select(self.index, game)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = logical_pos(e.pos)
            hit = -1
            for i, r in enumerate(self.buttons):
                if r.collidepoint(pos):
                    hit = i
                    break
            if hit < 0 and self.hover >= 0:
                hit = self.hover
            if hit >= 0:
                self.index = hit
                self._select(hit, game)

    def _select(self, i, game):
        if i == 0:
            game.start_select()
        elif i == 1:
            game.open_online()
        elif i == 2:
            game.open_settings()
        elif i == 3:
            game.open_shop()
        elif i == 4:
            game.open_changelog()
        else:
            game.quit()

    def _tick_motes(self, dt):
        for m in self.motes:
            m[0] += m[3] * dt
            m[1] += m[3] * dt * 0.25
            if m[1] < -10 or m[0] < -10:
                m[0] = random.uniform(SCREEN_W * 0.6, SCREEN_W + 20)
                m[1] = random.uniform(0, SCREEN_H)
                m[2] = random.uniform(6, 22)
                m[3] = random.uniform(-14, -4)

    def _icon(self, surf, cx, cy, kind, col):
        if kind == "play":
            pygame.draw.polygon(surf, col, [(cx - 9, cy - 12), (cx + 11, cy), (cx - 9, cy + 12)])
        elif kind == "gear":
            for i in range(6):
                a = i * math.pi / 3
                pygame.draw.line(surf, col, (cx, cy),
                                 (int(cx + math.cos(a) * 15), int(cy + math.sin(a) * 15)), 4)
            pygame.draw.circle(surf, col, (cx, cy), 8, 3)
        elif kind == "net":
            pygame.draw.circle(surf, col, (cx, cy), 13, 3)
            for dx in (-7, 0, 7):
                pts = [(cx + dx - 4, cy + 6), (cx + dx, cy - 8), (cx + dx + 4, cy + 6)]
                pygame.draw.lines(surf, col, True, pts, 2)
        elif kind == "coin":
            pygame.draw.circle(surf, col, (cx, cy), 13)
            pygame.draw.circle(surf, (20, 24, 38), (cx, cy), 9, 2)
            pygame.draw.line(surf, col, (cx - 5, cy), (cx + 5, cy), 3)
        elif kind == "book":
            pygame.draw.rect(surf, col, (cx - 13, cy - 11, 26, 22), 3, border_radius=3)
            pygame.draw.line(surf, col, (cx, cy - 9), (cx, cy + 9), 2)
        else:
            pygame.draw.rect(surf, col, (cx - 11, cy - 13, 22, 26), 3, border_radius=3)
            pygame.draw.circle(surf, (20, 24, 38), (cx + 7, cy), 2)

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        gem = pygame.Rect(SCREEN_W - 40, 16, 20, 20)
        pygame.draw.polygon(surf, (220, 40, 70),
                            [(gem.centerx, gem.top), (gem.right, gem.centery),
                             (gem.centerx, gem.bottom), (gem.left, gem.centery)])
        pygame.draw.polygon(surf, (255, 120, 150),
                            [(gem.centerx, gem.top), (gem.right, gem.centery),
                             (gem.centerx, gem.centery)], 2)
        draw_text(surf, "RUBY  %.2f" % savegame.ruby(), 22, (255, 170, 190),
                  (gem.left - 10, gem.centery), align="right")
        n_lock = sum(1 for r in ROSTER if r.get("locked"))
        draw_text(surf, "AÇIK %d / %d" % (len(ROSTER) - n_lock, len(ROSTER)),
                  15, (150, 155, 175), (SCREEN_W - 40, gem.bottom + 18),
                  align="right")
        self._tick_motes(1 / 60)
        for x, y, r, _v in self.motes:
            a = int(26 + 22 * (0.5 + 0.5 * math.sin(self.t * 1.6 + x * 0.02)))
            pygame.draw.circle(surf, (255, 210, 120, a), (int(x), int(y)), int(r * 0.18))
        cx = SCREEN_W // 2
        glow = pygame.Surface((760, 300), pygame.SRCALPHA)
        for rr in range(150, 0, -10):
            g = int(30 * (1 - rr / 150))
            pygame.draw.ellipse(glow, (255, 190, 60, g), (380 - rr * 2, 150 - rr,
                                                        rr * 4, rr * 2))
        surf.blit(glow, (cx - 380, 20))
        draw_text(surf, "STICKMAN", 96, GOLD, (cx, 140))
        draw_text(surf, "FIGHTERS", 96, (255, 255, 255), (cx, 232))
        badge = pygame.Rect(cx - 150, 276, 300, 32)
        pygame.draw.rect(surf, (26, 32, 50), badge, border_radius=16)
        pygame.draw.rect(surf, GOLD, badge, 2, border_radius=16)
        draw_text(surf, f"SÜRÜM {VERSION}  •  {UPDATE_NOTE}", 15, GOLD, badge.center)
        for i, (label, rect) in enumerate(zip(self.items, self.buttons)):
            active = (i == self.index) or (i == self.hover)
            body = blend((24, 30, 48), GOLD, 0.22) if active else (24, 30, 48)
            if active:
                push = 6
            else:
                push = 0
            r2 = rect.move(push, 0)
            pygame.draw.rect(surf, body, r2, border_radius=12)
            pygame.draw.rect(surf, GOLD if active else (86, 96, 124), r2, 3,
                             border_radius=12)
            if active:
                pygame.draw.rect(surf, (70, 62, 34), (r2.right + 10, r2.y + 8,
                                                       5, r2.h - 16), border_radius=3)
            col = (255, 255, 255) if active else (150, 158, 180)
            self._icon(surf, r2.x + 38, r2.centery, self.icons[i],
                       GOLD if active else (110, 120, 148))
            lx = r2.centerx + 18
            fs = 28
            while fs > 14 and get_font(fs).size(label)[0] > r2.w - 150:
                fs -= 1
            draw_text(surf, label, fs, col, (lx, r2.centery - 8))
            draw_text(surf, self.hints[i], 13,
                      GOLD if active else (110, 118, 140),
                      (lx, r2.centery + 16))
        draw_text(surf, "↑ ↓ VE TIKLAMA   •   ENTER: SEÇ   •   F11: TAM EKRAN",
                  16, (130, 140, 165), (cx, SCREEN_H - 34))


class ChangelogScreen:
    """GÜNCELLEME KAYITLARI: sürüm + not + aşağı kaydırılabilir detaylar."""
    def __init__(self):
        self.bg = _default_bg()
        self.t = 0.0
        self.scroll = 0.0
        self.view_h = 560
        self.top = 150
        self._rows = []
        for version, note, lines in CHANGELOG:
            self._rows.append((f"v{version}  •  {note}", version == VERSION, 28))
            for ln in lines:
                self._rows.append((ln, False, 20))
            self._rows.append(("", False, 8))
        self.total_h = sum(r[2] for r in self._rows)
        self.max_scroll = max(0.0, self.total_h - self.view_h)

    def update(self, dt):
        self.t += dt

    def _wheel(self, d):
        self.scroll = max(0.0, min(self.max_scroll, self.scroll - d * 34))

    def handle_event(self, e, game):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_e):
                game.to_menu()
            elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
                self._wheel(-1)
            elif e.key == pygame.K_UP or e.key == pygame.K_w:
                self._wheel(1)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 4:
                self._wheel(1)
            elif e.button == 5:
                self._wheel(-1)
        elif e.type == pygame.MOUSEWHEEL:
            self._wheel(e.y)

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        draw_text(surf, "GÜNCELLEME KAYITLARI", 46, GOLD, (SCREEN_W // 2, 64))
        draw_text(surf, f"SÜRÜM {VERSION} • {UPDATE_NOTE}  •  AŞAĞI KAYDIR (OK/FAR)",
                  16, (200, 205, 220), (SCREEN_W // 2, 104))
        y = self.top - int(self.scroll)
        if self.max_scroll > 0:
            bar_h = self.view_h * self.view_h / max(1.0, self.total_h)
            bar_y = self.top + (self.view_h - bar_h) * (self.scroll / self.max_scroll)
            pygame.draw.rect(surf, (90, 100, 130), (SCREEN_W - 18, int(bar_y), 8, int(bar_h)),
                             border_radius=4)
        for text, is_ver, h in self._rows:
            if y > self.top + self.view_h:
                return
            if y + h >= self.top:
                if is_ver:
                    draw_text(surf, text, 26, GOLD, (SCREEN_W // 2, y + h // 2))
                elif text:
                    draw_text(surf, text, 17, (225, 228, 240),
                              (SCREEN_W // 2, y + h // 2))
            y += h


class SelectScreen:
    def __init__(self):
        self.bg = make_bg(SCREEN_W, SCREEN_H, settings.BG_COLOR, tuple(max(0, c - 40) for c in settings.BG_COLOR))
        self.t = 0.0
        self.p1 = {"color": P1_COLOR, "char": 0, "cursor": 0}
        self.p2 = {"color": P2_COLOR, "char": 0, "cursor": 0}
        self.map_id = "grass"
        self.map_ids = list(maps.MAP_OBJECTS.keys())
        self.previews = {}
        prev_cams = {"grass": (500, GROUND_Y - 155), "village": (500, GROUND_Y - 155),
                     "city": (420, GROUND_Y - 330), "trucks": (500, GROUND_Y - 155),
                     "minestick": (500, GROUND_Y - 160),
                     "house": (500, GROUND_Y - 150), "johnny": (500, GROUND_Y - 150)}
        for mid in self.map_ids:
            px, py = prev_cams.get(mid, (520, GROUND_Y - 155))
            prev = pygame.Surface((300, 170))
            cam = SimpleNamespace(x=px, y=py)
            maps.MAP_OBJECTS[mid]().draw(prev, cam)
            self.previews[mid] = prev
        self.pan_w = 400
        self.pan_h = 600
        self.left = pygame.Rect(16, 78, self.pan_w, self.pan_h)
        self.right = pygame.Rect(SCREEN_W - 16 - self.pan_w, 78, self.pan_w, self.pan_h)
        self.center = pygame.Rect(436, 78, 408, self.pan_h)
        self.colors = COLOR_PRESETS
        self.sw_r = 13
        self.sw_cols = 8
        self.arrow_w = 62
        self.map_rect = pygame.Rect(self.center.centerx - 184, self.center.y + 66,
                                    368, 214)
        self.preview_cache = {}
        self.start_rect = pygame.Rect(self.center.centerx - 150, self.center.y + 476,
                                      300, 66)
        self.mode_labels = ["ARENA", "ZOMBİ", "FUTBOL", "LAZER", "BOSS"]
        self.mode_maps = ["grass", "zombi", "football", "laserrun", "boss"]
        self.mode_btns = []
        bw, bh = 68, 38
        bx0 = self.center.centerx - (5 * bw + 4 * 8) // 2
        for i in range(5):
            self.mode_btns.append(pygame.Rect(bx0 + i * (bw + 8),
                                              self.center.y + 392, bw, bh))

    def _char_at(self, idx):
        return idx if idx < len(ROSTER) else -1

    def _hero_rect(self, side):
        return pygame.Rect(side.x + 16, side.y + 146, side.w - 32, 176)

    def _prev_rect(self, side):
        hr = self._hero_rect(side)
        return pygame.Rect(hr.x + 10, hr.centery - 27, self.arrow_w, 54)

    def _next_rect(self, side):
        hr = self._hero_rect(side)
        return pygame.Rect(hr.right - self.arrow_w - 10, hr.centery - 27,
                           self.arrow_w, 54)

    def _swatch(self, side, i):
        r, c = divmod(i, self.sw_cols)
        span = self.sw_cols * 36
        x0 = side.x + (side.w - span) // 2 + 18
        return pygame.Rect(x0 + c * 36 - self.sw_r,
                           side.y + 92 + r * 32 - self.sw_r,
                           self.sw_r * 2, self.sw_r * 2)

    def _shift(self, pd, d):
        n = len(ROSTER)
        if n == 0:
            return
        pd["cursor"] = (pd["cursor"] + d) % n
        pd["char"] = pd["cursor"]

    def handle_event(self, e, game):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                game.to_menu()
                return
            self._key(e, game)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self._click(logical_pos(e.pos), game)

    def _key(self, e, game):
        name = pygame.key.name(e.key)
        if name == "a":
            self._shift(self.p1, -1)
        elif name == "d":
            self._shift(self.p1, 1)
        elif name == "left":
            self._shift(self.p2, -1)
        elif name == "right":
            self._shift(self.p2, 1)
        elif e.key == pygame.K_e:
            self.p1["char"] = self._char_at(self.p1["cursor"])
        elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.p2["char"] = self._char_at(self.p2["cursor"])

    def _click(self, pos, game):
        for side, pd in ((self.left, self.p1), (self.right, self.p2)):
            if not side.collidepoint(pos):
                continue
            if self._prev_rect(side).collidepoint(pos):
                self._shift(pd, -1)
                return
            if self._next_rect(side).collidepoint(pos):
                self._shift(pd, 1)
                return
            for i in range(len(self.colors)):
                if self._swatch(side, i).collidepoint(pos):
                    pd["color"] = self.colors[i]
                    return
        if self.map_rect.inflate(8, 8).collidepoint(pos):
            i = self.map_ids.index(self.map_id)
            self.map_id = self.map_ids[(i + 1) % len(self.map_ids)]
            return
        for i, r in enumerate(self.mode_btns):
            if r.collidepoint(pos):
                self.map_id = self.mode_maps[i]
                return
        if self.start_rect.collidepoint(pos):
            game.start_fight()

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        draw_text(surf, "KARAKTER & HARİTA SEÇİMİ", 40, (255, 255, 255),
                  (SCREEN_W // 2, 36))
        self._panel(surf, self.left, self.p1, "OYUNCU 1", 0)
        self._panel(surf, self.right, self.p2, "OYUNCU 2", 1)
        self._center(surf)
        draw_text(surf, "P1: WASD + E   •   P2: OK TUSLARI + ENTER   •   "
                        "FARE İLE SEÇ   •   ESC: MENÜ",
                  15, (150, 155, 170), (SCREEN_W // 2, SCREEN_H - 18))

    def _panel(self, surf, side, pd, label, pi):
        col = pd["color"]
        tint = blend(col, (255, 255, 255), 0.4)
        pygame.draw.rect(surf, (24, 28, 42), side, border_radius=14)
        pygame.draw.rect(surf, tint, side, 3, border_radius=14)
        draw_text(surf, label, 26, tint, (side.centerx, side.y + 28))
        pygame.draw.line(surf, blend((24, 28, 42), tint, 0.45),
                         (side.x + 22, side.y + 50), (side.right - 22, side.y + 50), 2)
        draw_text(surf, "STİCKMAN RENGI", 14, (170, 175, 190),
                  (side.centerx, side.y + 68))
        for i, c2 in enumerate(self.colors):
            r = self._swatch(side, i)
            pygame.draw.circle(surf, (16, 18, 28), (r.centerx, r.centery), self.sw_r)
            pygame.draw.circle(surf, c2, (r.centerx, r.centery), self.sw_r - 3)
            if c2 == col:
                pygame.draw.circle(surf, (255, 255, 255), (r.centerx, r.centery),
                                   self.sw_r, 2)
        hr = self._hero_rect(side)
        ch = ROSTER[pd["char"]] if ROSTER else None
        pygame.draw.rect(surf, (20, 23, 36), hr, border_radius=12)
        glow = pygame.Surface((hr.w, hr.h), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, col + (34,), (hr.w // 2 - 100, hr.h - 38, 200, 30))
        surf.blit(glow, hr.topleft)
        pygame.draw.rect(surf, blend((20, 23, 36), tint, 0.4), hr, 2, border_radius=12)
        self._preview(surf, hr, ch, tint)
        self._arrow(surf, self._prev_rect(side), -1, tint)
        self._arrow(surf, self._next_rect(side), 1, tint)
        total = ROSTER_TOTAL
        if ch is not None:
            fs = 20
            while fs > 11 and get_font(fs).size(ch["name"])[0] > side.w - 40:
                fs -= 1
            draw_text(surf, ch["name"], fs, (255, 255, 255),
                      (side.centerx, side.y + 342))
            tag = "SINIF" if ch.get("class_def") else "KARAKTER"
            draw_text(surf, "%d / %d  •  %s" % (pd["cursor"] + 1, total, tag), 13,
                      blend(tint, (255, 255, 255), 0.3), (side.centerx, side.y + 362))
            story_y = side.y + 382
            for ln in _wrap(ch.get("story", ""), 38):
                if story_y > side.y + 440:
                    break
                draw_text(surf, ln, 13, (176, 182, 200), (side.centerx, story_y))
                story_y += 16
            if ch.get("locked"):
                lbl = "KİLİTLİ %s Ruby" % ch.get("price", 0)
                tw = get_font(14).size(lbl)[0]
                lx = side.right - 14 - tw
                ly = side.y + 362
                pygame.draw.rect(surf, (255, 210, 90),
                                 (lx - 24, ly - 9, 15, 18), border_radius=3)
                pygame.draw.arc(surf, (255, 210, 90),
                                (lx - 21, ly - 17, 10, 12), 0, 3.15, 3)
                draw_text(surf, lbl, 14, (255, 210, 90), (lx + tw // 2, ly))
        draw_text(surf, "YETENEKLER + ULTİ", 13, (170, 175, 190),
                  (side.centerx, side.y + 456))
        adesc = self._adesc(ch)
        ult = self._ult_line(ch)
        boxes = [(f"{j + 1}. " + t, (30, 34, 50)) for j, t in enumerate(adesc[:3])]
        if ult:
            boxes.append((ult, (48, 40, 24)))
        bh = 31
        for j, (txt, bgc) in enumerate(boxes[:4]):
            r = pygame.Rect(side.x + 16, side.y + 470 + j * (bh + 3),
                            side.w - 32, bh)
            pygame.draw.rect(surf, bgc, r, border_radius=7)
            edge = GOLD if bgc != (30, 34, 50) else blend(bgc, tint, 0.5)
            pygame.draw.rect(surf, edge, r, 1, border_radius=7)
            fs = 10
            lines = _wrap(txt, 62)
            while fs > 7 and any(get_font(fs).size(l)[0] > r.w - 12 for l in lines[:2]):
                fs -= 1
                lines = _wrap(txt, 68)
            ty = r.centery - (min(2, len(lines)) * (fs + 2)) // 2
            for ln in lines[:2]:
                draw_text(surf, ln, fs, (226, 232, 244), (r.centerx, ty))
                ty += fs + 2

    def _adesc(self, ch):
        """Karakterin 3 yetenegi aciklamasi."""
        if not ch:
            return []
        cd = ch.get("class_def")
        if not cd:
            return list(ch.get("adesc") or [])
        out = []
        for sid in cd["abilities"][:3]:
            sk = SKILLS.get(sid, {})
            out.append("%s (%gs): %s" % (sk.get("name", "-"), sk.get("cd", 0),
                                         sk.get("desc", "")))
        return out

    def _ult_line(self, ch):
        cd = ch.get("class_def") if ch else None
        if not cd or not cd.get("ult"):
            return None
        sk = SKILLS.get(cd["ult"], {})
        return "ULTİ %s: %s" % (sk.get("name", "-"), sk.get("desc", ""))

    def _preview(self, surf, hr, ch, tint):
        if ch is None:
            return
        fam = ch.get("family")
        base = hr.bottom - 16
        if fam and fam != "insan":
            s = min(1.75, (hr.h - 30) / 62.0)
            chars.draw_creature(surf, hr.centerx, base, s, ch.get("color", tint),
                                fam, ch["id"], self.t, {"dir": 1})
        else:
            chars.draw_stickman(surf, hr.centerx, base, (hr.h - 34) / 78.0, tint,
                                1, "idle", self.t)

    def _arrow(self, surf, rect, direction, tint):
        pygame.draw.circle(surf, (34, 39, 58), rect.center, 24)
        pygame.draw.circle(surf, blend((34, 39, 58), tint, 0.55), rect.center, 24, 2)
        cx, cy = rect.center
        s = 11 if direction > 0 else -11
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(cx - s * 0.5, cy - s), (cx + s * 0.5, cy),
                             (cx - s * 0.5, cy + s)])

    def _scaled_preview(self, mid, w, h):
        key = (mid, w, h)
        if key not in self.preview_cache:
            self.preview_cache[key] = pygame.transform.smoothscale(
                self.previews[mid], (w, h))
        return self.preview_cache[key]

    def _center(self, surf):
        c = self.center
        pygame.draw.rect(surf, (26, 30, 44), c, border_radius=14)
        pygame.draw.rect(surf, (120, 130, 160), c, 2, border_radius=14)
        draw_text(surf, "HARİTA SEÇİMİ", 28, (255, 255, 255), (c.centerx, c.y + 34))
        mr = self.map_rect
        frame = mr.inflate(8, 8)
        pygame.draw.rect(surf, (18, 20, 32), frame, border_radius=14)
        pygame.draw.rect(surf, GOLD, frame, 3, border_radius=14)
        surf.blit(self._scaled_preview(self.map_id, mr.w - 10, mr.h - 14),
                  (mr.x + 5, mr.y + 7))
        label = next((m["name"] for m in MAPS if m["id"] == self.map_id), self.map_id)
        disp = next((m["disp"] for m in MAPS if m["id"] == self.map_id), self.map_id)
        draw_text(surf, disp, 30, GOLD, (c.centerx, mr.bottom + 30))
        draw_text(surf, f"{label}  •  TIKLAYARAK DEĞİŞTİR", 14, (170, 178, 196),
                  (c.centerx, mr.bottom + 56))
        draw_text(surf, "MODLAR", 16, (170, 178, 196), (c.centerx, c.y + 366))
        for i, r in enumerate(self.mode_btns):
            active = self.mode_maps[i] == self.map_id
            pygame.draw.rect(surf, (44, 54, 78) if active else (22, 28, 44), r,
                             border_radius=8)
            pygame.draw.rect(surf, GOLD if active else (110, 120, 150), r, 2,
                             border_radius=8)
            draw_text(surf, self.mode_labels[i], 16,
                      GOLD if active else (255, 255, 255), r.center)
        pulse = 0.5 + 0.5 * math.sin(self.t * 4)
        pygame.draw.rect(surf, blend((40, 46, 66), GOLD, pulse * 0.4), self.start_rect,
                         border_radius=14)
        pygame.draw.rect(surf, GOLD, self.start_rect, 3, border_radius=14)
        draw_text(surf, "DÖVÜŞE BAŞLA!", 26, (255, 255, 255), self.start_rect.center)
        draw_text(surf, "F11: TAM EKRAN   ESC: MENÜ", 14, (150, 155, 170),
                  (c.centerx, c.y + self.pan_h - 22))


class SettingsScreen:
    def __init__(self):
        self.t = 0.0
        self.center = pygame.Rect(SCREEN_W // 2 - 400, 60, 800, 600)
        self.rebinding = None  # (player, action)
        self.color_input = ""
        self.color_active = False
        self._build_ui()

    def _build_ui(self):
        c = self.center
        # P1 tuşları
        self.p1_keys = ["left", "right", "jump", "crouch", "ability1", "ability2", "ability3", "ult", "craft", "place"]
        self.p1_rects = {}
        for i, act in enumerate(self.p1_keys):
            y = c.y + 80 + i * 36
            self.p1_rects[act] = {
                "label": pygame.Rect(c.x + 40, y, 180, 30),
                "key": pygame.Rect(c.x + 240, y, 160, 30),
            }
        # P2 tuşları
        self.p2_keys = ["left", "right", "jump", "crouch", "ability1", "ability2", "ability3", "ult", "craft", "place"]
        self.p2_rects = {}
        for i, act in enumerate(self.p2_keys):
            y = c.y + 80 + i * 36
            self.p2_rects[act] = {
                "label": pygame.Rect(c.x + 440, y, 180, 30),
                "key": pygame.Rect(c.x + 600, y, 160, 30),
            }
        # Arka plan rengi
        self.bg_rect = pygame.Rect(c.x + 40, c.y + 480, 720, 40)
        self.bg_label = pygame.Rect(c.x + 40, c.y + 450, 720, 24)
        # Geri butonu
        self.back_rect = pygame.Rect(c.centerx - 100, c.y + 540, 200, 44)

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        c = self.center
        # Arka plan
        pygame.draw.rect(surf, (18, 22, 34), c, border_radius=16)
        pygame.draw.rect(surf, (60, 70, 100), c, 2, border_radius=16)
        draw_text(surf, "AYARLAR", 36, GOLD, (c.centerx, c.y + 30))
        # P1 başlık
        draw_text(surf, "OYUNCU 1 (KLAVYE)", 18, (180, 220, 255), (c.x + 130, c.y + 60))
        # P2 başlık
        draw_text(surf, "OYUNCU 2 (OK TUŞLARI / MOUSE)", 18, (180, 220, 255), (c.x + 530, c.y + 60))

        # P1 tuşları
        for act in self.p1_keys:
            r = self.p1_rects[act]
            key_name = self._key_name(KEYS_P1[act]) if not self.rebinding == ("p1", act) else "? BAS..."
            draw_text(surf, self._action_label(act), 14, (200, 200, 220), r["label"].midleft)
            col = GOLD if self.rebinding == ("p1", act) else (80, 100, 140)
            pygame.draw.rect(surf, col, r["key"], border_radius=6)
            pygame.draw.rect(surf, (180, 200, 230), r["key"], 2, border_radius=6)
            draw_text(surf, key_name, 14, (255, 255, 255), r["key"].center)

        # P2 tuşları
        for act in self.p2_keys:
            r = self.p2_rects[act]
            key_name = self._key_name(KEYS_P2[act]) if not self.rebinding == ("p2", act) else "? BAS..."
            draw_text(surf, self._action_label(act), 14, (200, 200, 220), (r["label"].x + r["label"].w + 10, r["label"].centery))
            col = GOLD if self.rebinding == ("p2", act) else (80, 100, 140)
            pygame.draw.rect(surf, col, r["key"], border_radius=6)
            pygame.draw.rect(surf, (180, 200, 230), r["key"], 2, border_radius=6)
            draw_text(surf, key_name, 14, (255, 255, 255), r["key"].center)

        # Arka plan rengi
        draw_text(surf, "ARKA PLAN RENK (RGB: 255,0,0):", 16, (200, 220, 255), self.bg_label.midleft)
        pygame.draw.rect(surf, (40, 50, 70), self.bg_rect, border_radius=8)
        pygame.draw.rect(surf, GOLD if self.color_active else (100, 120, 160), self.bg_rect, 2, border_radius=8)
        draw_text(surf, self.color_input if self.color_input else "örn: 255,100,50", 14,
                  (255, 255, 255) if self.color_input else (140, 150, 180), self.bg_rect.center)
        # Önizleme
        preview = pygame.Rect(c.x + 600, c.y + 450, 160, 70)
        pygame.draw.rect(surf, settings.BG_COLOR, preview, border_radius=8)
        pygame.draw.rect(surf, (180, 200, 230), preview, 2, border_radius=8)
        draw_text(surf, "Önizleme", 14, (170, 180, 200), preview.center)

        # Geri butonu
        pulse = 0.5 + 0.5 * math.sin(self.t * 4)
        pygame.draw.rect(surf, blend((40, 46, 66), GOLD, pulse * 0.4), self.back_rect, border_radius=10)
        pygame.draw.rect(surf, GOLD, self.back_rect, 3, border_radius=10)
        draw_text(surf, "GERİ (ESC)", 22, (255, 255, 255), self.back_rect.center)

    def _action_label(self, act):
        labels = {
            "left": "SOL", "right": "SAĞ", "jump": "ZIPLA", "crouch": "EĞİL",
            "ability1": "ÖZELLIK 1", "ability2": "ÖZELLIK 2", "ability3": "ÖZELLIK 3",
            "ult": "ULT", "craft": "CRAFT", "place": "YERLEŞTİR",
        }
        return labels.get(act, act.upper())

    def _key_name(self, key):
        if key is None:
            return "MOUSE / YOK"
        try:
            return pygame.key.name(key).upper()
        except:
            return str(key)

    def handle_event(self, e, game=None):
        global MOVE_KEYS, P1_ABILITY_KEYS
        if e.type == pygame.KEYDOWN:
            # Rebinding modundayken
            if self.rebinding:
                p, act = self.rebinding
                if e.key == pygame.K_ESCAPE:
                    self.rebinding = None
                else:
                    if p == "p1":
                        KEYS_P1[act] = e.key
                    else:
                        KEYS_P2[act] = e.key
                    self.rebinding = None
                    # MOVE_KEYS yeniden oluştur
                    global MOVE_KEYS, P1_ABILITY_KEYS
                    MOVE_KEYS.clear()
                    for action, key in KEYS_P1.items():
                        if key is not None:
                            MOVE_KEYS[key] = ("p1", action)
                    for action, key in KEYS_P2.items():
                        if key is not None:
                            MOVE_KEYS[key] = ("p2", action)
                    P1_ABILITY_KEYS.clear()
                    for action in ("ability1", "ability2", "ability3", "ult", "craft", "place"):
                        k1 = KEYS_P1.get(action)
                        if k1 is not None:
                            P1_ABILITY_KEYS[k1] = action + "_pressed"
                    return True
            # Renk input modundayken
            elif self.color_active:
                if e.key == pygame.K_RETURN:
                    try:
                        parts = [int(x.strip()) for x in self.color_input.split(",")]
                        if len(parts) == 3 and all(0 <= v <= 255 for v in parts):
                            import settings
                            settings.BG_COLOR = tuple(parts)
                            self.bg = make_bg(SCREEN_W, SCREEN_H, settings.BG_COLOR,
                                              tuple(max(0, c - 40) for c in settings.BG_COLOR))
                    except:
                        pass
                    self.color_input = ""
                    self.color_active = False
                    return True
                elif e.key == pygame.K_BACKSPACE:
                    self.color_input = self.color_input[:-1]
                elif e.unicode.isdigit() or e.unicode == ",":
                    self.color_input += e.unicode
                return True
            # Normal ESC
            elif e.key == pygame.K_ESCAPE:
                return "back"
            return True

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            # P1 tuşları
            for act in self.p1_keys:
                if self.p1_rects[act]["key"].collidepoint(mx, my):
                    self.rebinding = ("p1", act)
                    return True
            # P2 tuşları
            for act in self.p2_keys:
                if self.p2_rects[act]["key"].collidepoint(mx, my):
                    self.rebinding = ("p2", act)
                    return True
            # Arka plan rengi input
            if self.bg_rect.collidepoint(mx, my):
                self.color_active = True
                return True
            else:
                if self.color_active:
                    # Renk uygula
                    try:
                        parts = [int(x.strip()) for x in self.color_input.split(",")]
                        if len(parts) == 3 and all(0 <= v <= 255 for v in parts):
                            import settings
                            settings.BG_COLOR = tuple(parts)
                            self.bg = make_bg(SCREEN_W, SCREEN_H, settings.BG_COLOR,
                                              tuple(max(0, c - 40) for c in settings.BG_COLOR))
                    except:
                        pass
                    self.color_input = ""
                    self.color_active = False
                    return True
            # Geri butonu
            if self.back_rect.collidepoint(mx, my):
                return "back"
            return True

        return False


class ShopScreen:
    def __init__(self):
        self.t = 0.0
        self.center = pygame.Rect(SCREEN_W // 2 - 450, 40, 900, 640)
        self.selected_pack = None
        self.buy_anim = None  # (pack_id, progress, camera_pos)
        self.buy_show = False
        self.buy_t = 0.0       # animasyon süresi
        self.revealed = False  # 3 saniye sonra bilgi kartı açılır
        self._build_ui()

    def _build_ui(self):
        c = self.center
        self.pack_rects = {}
        n = len(CLASS_PACKS)
        cols = 4
        rows = (n + cols - 1) // cols
        bw = 198
        gap = 12
        x0 = c.x + (c.w - (cols * bw + (cols - 1) * gap)) // 2
        for i, pack in enumerate(CLASS_PACKS):
            x = x0 + (i % cols) * (bw + gap)
            y = c.y + 92 + (i // cols) * 214
            self.pack_rects[pack["id"]] = {
                "rect": pygame.Rect(x, y, bw, 200),
                "buy": pygame.Rect(x + 14, y + 156, bw - 28, 34),
            }
        self.back_rect = pygame.Rect(c.centerx - 100, c.y + 580, 200, 44)

    def update(self, dt):
        self.t += dt
        if self.buy_anim:
            pid, prog, cam = self.buy_anim
            self.buy_t += dt
            prog = min(1.0, prog + dt * 0.75)
            self.buy_anim = (pid, prog, cam)
            self.revealed = self.buy_t >= SHOP_REVEAL_TIME

    def draw(self, surf):
        c = self.center
        # Arka plan
        pygame.draw.rect(surf, (18, 22, 34), c, border_radius=16)
        pygame.draw.rect(surf, (60, 70, 100), c, 2, border_radius=16)
        draw_text(surf, "DÜKKAN", 34, GOLD, (c.centerx, c.y + 26))
        ruby = savegame.ruby()
        draw_text(surf, "RUBY", 15, (230, 120, 150), (c.centerx - 66, c.y + 62))
        gem = pygame.Rect(c.centerx - 30, c.y + 48, 22, 22)
        pygame.draw.polygon(surf, (220, 40, 70),
                            [(gem.centerx, gem.top), (gem.right, gem.centery),
                             (gem.centerx, gem.bottom), (gem.left, gem.centery)])
        pygame.draw.polygon(surf, (255, 120, 150),
                            [(gem.centerx, gem.top), (gem.right, gem.centery),
                             (gem.centerx, gem.centery)], 2)
        draw_text(surf, "%.2f" % ruby, 24, (255, 170, 190), (c.centerx + 62, c.y + 62))

        # Paketler
        for pack in CLASS_PACKS:
            pid = pack["id"]
            r = self.pack_rects[pid]["rect"]
            owned = savegame.owns_pack(pid)
            active = (self.selected_pack == pid)
            base = (36, 44, 64) if active else (26, 32, 50)
            if owned:
                base = blend(base, (40, 110, 70), 0.35)
            pygame.draw.rect(surf, base, r, border_radius=12)
            edge = GOLD if active else pack.get("color", (90, 100, 130))
            pygame.draw.rect(surf, edge, r, 3, border_radius=12)

            fs = 17
            while fs > 11 and get_font(fs).size(pack["name"])[0] > r.w - 18:
                fs -= 1
            draw_text(surf, pack["name"], fs, (255, 255, 255), (r.centerx, r.y + 22))

            chars = [CLASS_BY_ID[savegame.cid_of(no)] for no in pack["chars"]]
            chars = [c for c in chars if c]
            dy = r.y + 46
            if chars:
                names = ", ".join(c["name"].title() for c in chars[:3])
                if len(chars) > 3:
                    names += " +%d" % (len(chars) - 3)
                fs2 = 12
                while fs2 > 8 and get_font(fs2).size(names)[0] > r.w - 16:
                    fs2 -= 1
                draw_text(surf, names, fs2, (215, 225, 245), (r.centerx, dy))
                dy += 18
            for ln in _wrap(pack["desc"], 30)[:4]:
                draw_text(surf, ln, 12, (168, 178, 200), (r.centerx, dy))
                dy += 16

            price = pack["price"]
            draw_text(surf, "%g Ruby" % price, 19,
                      (255, 170, 190) if not owned else (140, 220, 160),
                      (r.centerx, r.y + 130))

            br = self.pack_rects[pid]["buy"]
            can_buy = (not owned) and savegame.can_afford(price)
            if owned:
                pygame.draw.rect(surf, (30, 70, 45), br, border_radius=6)
                pygame.draw.rect(surf, (120, 220, 150), br, 2, border_radius=6)
                draw_text(surf, "SAHİPSİN", 16, (190, 255, 200), br.center)
            else:
                pygame.draw.rect(surf, (40, 120, 60) if can_buy else (60, 60, 60),
                                 br, border_radius=6)
                pygame.draw.rect(surf, (180, 255, 200) if can_buy else (100, 100, 100),
                                 br, 2, border_radius=6)
                draw_text(surf, "SATIN AL", 16, (255, 255, 255), br.center)

        # Geri butonu
        pulse = 0.5 + 0.5 * math.sin(self.t * 4)
        pygame.draw.rect(surf, blend((40, 46, 66), GOLD, pulse * 0.4), self.back_rect, border_radius=10)
        pygame.draw.rect(surf, GOLD, self.back_rect, 3, border_radius=10)
        draw_text(surf, "GERİ (ESC)", 22, (255, 255, 255), self.back_rect.center)

        # Satın alma animasyonu en üstte çizilir
        if self.buy_anim:
            self._draw_buy_anim(surf)

    def _draw_sitting_icon(self, surf, cx, cy, scale, color):
        # Kameraya dönük (ön görünüm) oturan stickman; orijin kalça, +y aşağı
        def pt(x, y):
            return (int(cx + x * scale), int(cy + y * scale))
        lw = max(2, int(3 * scale))
        pygame.draw.circle(surf, color, pt(0, -24), int(8 * scale))
        # Gövde + omuzlar
        pygame.draw.line(surf, color, pt(0, -15), pt(0, 2), lw)
        pygame.draw.line(surf, color, pt(-7, -12), pt(7, -12), lw)
        # Kollar kol desteklerinde (iki yana)
        pygame.draw.line(surf, color, pt(-7, -12), pt(-15, -6), lw)
        pygame.draw.line(surf, color, pt(-15, -6), pt(-19, 0), lw)
        pygame.draw.line(surf, color, pt(7, -12), pt(15, -6), lw)
        pygame.draw.line(surf, color, pt(15, -6), pt(19, 0), lw)
        # Bacaklar öne kıvrık, dizler iki yana açık
        pygame.draw.line(surf, color, pt(0, 2), pt(-11, 8), lw)
        pygame.draw.line(surf, color, pt(-11, 8), pt(-13, 16), lw)
        pygame.draw.line(surf, color, pt(0, 2), pt(11, 8), lw)
        pygame.draw.line(surf, color, pt(11, 8), pt(13, 16), lw)

    def _pack_view(self, pid):
        """Paketin gosterilecek bilgisi (ilk sinif + yetenekleri)."""
        pack = next(p for p in CLASS_PACKS if p["id"] == pid)
        first = None
        if pack["chars"]:
            cid = savegame.cid_of(pack["chars"][0])
            first = CLASS_BY_ID.get(cid)
        name = pack["name"]
        story = pack["story"]
        ab = []
        if first is not None:
            name = first["name"]
            story = first["story"]
            for sid in first["abilities"]:
                sk = SKILLS.get(sid, {})
                ab.append("%s: %s" % (sk.get("name", "-"), sk.get("desc", "")))
            sk = SKILLS.get(first["ult"], {})
            ab.append("ULTİ %s: %s" % (sk.get("name", "-"), sk.get("desc", "")))
        return {"name": name, "story": story, "abilities": ab,
                "color": pack.get("color", (235, 215, 130)), "pack": pack["name"]}

    def _draw_buy_anim(self, surf):
        pid, prog, cam = self.buy_anim
        pack = self._pack_view(pid)
        TW, TH = 620, 540
        # Kamera tahta doğru yaklaşır
        e = prog * prog * (3 - 2 * prog)
        zoom = 0.45 + 0.75 * e
        tz = (max(1, int(TW * zoom)), max(1, int(TH * zoom)))
        stage = pygame.Surface((TW, TH), pygame.SRCALPHA)

        scx = TW // 2
        scy = 330
        color = pack.get("color", (235, 215, 130))

        # zemin
        pygame.draw.ellipse(stage, (34, 30, 44), pygame.Rect(scx - 190, scy, 380, 42))
        pygame.draw.ellipse(stage, (78, 68, 100), pygame.Rect(scx - 190, scy, 380, 42), 3)
        # tahta: arkalık + tepelik
        pygame.draw.rect(stage, (112, 82, 40), pygame.Rect(scx - 48, scy - 156, 96, 138))
        pygame.draw.polygon(stage, (112, 82, 40),
                            [(scx - 48, scy - 156), (scx + 48, scy - 156), (scx, scy - 204)])
        pygame.draw.rect(stage, (190, 150, 70), pygame.Rect(scx - 48, scy - 156, 96, 138), 3)
        pygame.draw.line(stage, (190, 150, 70), (scx - 32, scy - 136),
                         (scx + 32, scy - 136), 3)
        # oturak + kol destekleri
        pygame.draw.rect(stage, (160, 122, 58), pygame.Rect(scx - 76, scy - 20, 152, 14))
        pygame.draw.rect(stage, (90, 66, 28), pygame.Rect(scx - 76, scy - 6, 152, 4))
        for sgn in (-1, 1):
            arm = pygame.Rect(scx + sgn * 66 - (10 if sgn > 0 else 10),
                              scy - 108, 20, 90)
            pygame.draw.rect(stage, (130, 98, 50), arm)
            pygame.draw.rect(stage, (190, 150, 70), arm, 2)

        # karakter oturur -> ayağa kalkar
        stand = max(0.0, min(1.0, (prog - 0.40) / 0.42))
        stand = stand * stand * (3 - 2 * stand)
        sk = chars.blend_skel("sit", "idle", stand)
        base_y = int(scy - 20 + 20 * stand)
        chars.draw_stickman(stage, scx, base_y, 1.15, color, 1, "idle", self.t,
                            skel=sk, ground=False)
        # kalkınca altın halka
        if stand > 0.05:
            rr = int(34 * (1 - stand) + 12)
            ring = pygame.Surface((rr * 2 + 8, rr * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(ring, (255, 220, 110, int(120 * (1 - stand))),
                               (rr + 4, rr + 4), rr, 3)
            stage.blit(ring, (scx - rr - 4, base_y - rr * 2 - 4))

        # 3 saniye sonra: isim, hikaye ve ozellikler
        if self.revealed:
            pan = pygame.Rect(20, 372, TW - 40, 158)
            pygame.draw.rect(stage, (28, 28, 44), pan, border_radius=10)
            pygame.draw.rect(stage, GOLD, pan, 3, border_radius=10)
            draw_text(stage, str(pack.get("pack", "")), 13, (170, 180, 205),
                      (pan.centerx, pan.y + 14))
            draw_text(stage, str(pack.get("name", "???")), 25, GOLD,
                      (pan.centerx, pan.y + 38))
            story = str(pack.get("story", "")).strip()
            sy = pan.y + 60
            for ln in wrap_text(story, 74)[:2]:
                draw_text(stage, ln, 12, (196, 204, 222), (pan.centerx, sy))
                sy += 15
            sy = pan.y + 94
            for ab in pack.get("abilities", [])[:4]:
                for ln in wrap_text(str(ab), 78)[:1]:
                    draw_text(stage, ln, 12, (240, 240, 248), (pan.centerx, sy))
                    sy += 15
        else:
            left = max(0.0, SHOP_REVEAL_TIME - self.buy_t)
            draw_text(stage, "BİLGİ %d" % int(math.ceil(left)), 17, (205, 215, 230),
                      (scx, 400))

        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, int(195 * prog)))
        surf.blit(ov, (0, 0))

        scaled = pygame.transform.smoothscale(stage, tz)
        surf.blit(scaled, (SCREEN_W // 2 - tz[0] // 2,
                           SCREEN_H // 2 - tz[1] // 2 + 10))

        for i in range(18):
            a = i * 2.39996 + self.t * 1.4
            rr = 56 + (i % 6) * 20
            sx = SCREEN_W // 2 + math.cos(a) * rr * (1.3 - 0.35 * prog)
            sy = SCREEN_H // 2 + math.sin(a + 0.7) * rr * 0.55
            tw = 0.5 + 0.5 * math.sin(self.t * 6 + i * 1.7)
            pygame.draw.circle(surf, (255, 226, 120), (int(sx), int(sy)),
                               int(2 + 2 * tw))
        draw_text(surf, "KAPATMAK İÇİN BİR TUŞA BAS", 17, (170, 180, 200),
                  (SCREEN_W // 2, SCREEN_H - 34))

    def handle_event(self, e, game=None):
        if self.buy_anim is not None:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.buy_anim = None
                self.buy_show = False
                self.revealed = False
                self.buy_t = 0.0
            return True
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return "back"
            return True
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            for pack in CLASS_PACKS:
                pid = pack["id"]
                r = self.pack_rects[pid]["rect"]
                br = self.pack_rects[pid]["buy"]
                if br.collidepoint(mx, my):
                    ok, msg = savegame.buy_pack(pid)
                    self.notice = msg if ok else msg
                    self.notice_t = 2.5
                    if ok and pack["chars"]:
                        self.selected_pack = pid
                        self.buy_show = False
                        self.buy_t = 0.0
                        self.revealed = False
                        self.buy_anim = (pid, 0.0, (r.centerx, r.centery))
                    return True
                if r.collidepoint(mx, my):
                    self.selected_pack = pid
                    return True
            if self.back_rect.collidepoint(mx, my):
                return "back"
            return True
        return False
