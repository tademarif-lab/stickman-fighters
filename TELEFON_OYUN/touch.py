# -*- coding: utf-8 -*-
"""Dokunmatik kontroller (mobil port icin).

Sol altta sanal joystick, sag altta 4 yetenek butonu + zipla + egil.
Uretilen girdi, klavyeli oyundaki PlayerInput ile ayni alanlari doldurur;
bu yuzden mevcut oyun mantigi degismez.
"""
import math

import pygame

BTN_R = 34
JOY_OUT = 78
JOY_IN = 30


class TouchLayout:
    def __init__(self, w, h, mode="coarse", alt_serit=0):
        self.w = w
        self.h = h
        self.mode = mode
        # alt HUD bandinin ust kenari; kontroller bunun ALTINA giremez
        # (once can cubugunun uzerine ciziyorlardi)
        self.alt_serit = max(0, min(int(alt_serit), h))
        self.set_layout(mode)

    def set_layout(self, mode):
        """Kontrolleri ekrana SIGDIRAN sekilde yerlestirir.

        Once sabit boyutlardi: yetenek butonlari 80px ve diagonal olarak
        yukari dogru diziliyordu (4*80 + 3*46 = 458px). 360 yukseklikte
        en ustteki buton y=-122'ye duserek EKRAN DIŞINA cikiyordu
        (640x360 telefonlarda dokunma hic calismiyordu).

        Simdi: 4 yetenek 2x2 izgara, sag altta zipla + egilme, hepsi
        alt HUD bandinin ustunde kalir.
        """
        self.mode = mode
        w, h = self.w, self.h
        bot = self.alt_serit or h          # kullanilabilir alt sinir
        k = max(0.40, min(1.0, min(w / 1280.0, bot / 720.0)))
        m = max(10, int(24 * k))
        jr = max(28, int(JOY_OUT * k))    # joystick / zipla boyutu

        # yetenek butonlari icin sigacak en buyuk cap
        sz = max(22, min(int((BTN_R + 6) * 2 * k),
                         int((bot - 2 * m - jr) / 2.7),
                         int(w * 0.32)))
        gap = max(4, int(sz * 0.14))

        # sol alt: joystick
        self.joy_center = (m + jr - 10, bot - m - jr)

        # sag alt: zipla (en sag) + egilme (solunda)
        self.btn_jump = pygame.Rect(w - m - jr, bot - m - jr, jr, jr)
        self.btn_crouch = pygame.Rect(w - m - jr * 2 - m // 2, bot - m - jr,
                                      jr, jr)

        # yetenekler: 2x2 izgara, zipla/egilmenin SOLUNDA
        gx = self.btn_crouch.x - gap - (2 * sz + gap)
        gy = bot - m - (2 * sz + gap)
        self.btn_a1 = pygame.Rect(gx, gy + sz + gap, sz, sz)
        self.btn_a2 = pygame.Rect(gx + sz + gap, gy + sz + gap, sz, sz)
        self.btn_a3 = pygame.Rect(gx, gy, sz, sz)
        self.btn_ulti = pygame.Rect(gx + sz + gap, gy, sz, sz)

        self.btn_pause = pygame.Rect(m, m, max(48, int(74 * k)),
                                     max(32, int(44 * k)))
        self.pause = False


class TouchInput:
    """Dokunma -> girdi nesnesi."""

    def __init__(self, layout):
        self.L = layout
        self.joy_id = None
        self.joy_vec = (0.0, 0.0)
        self.btn_touch = {}          # finger_id -> buton adi
        self.btn_pressed = {"a1": False, "a2": False, "a3": False,
                            "ulti": False, "jump": False, "crouch": False}
        self._edge = {"a1": False, "a2": False, "a3": False,
                      "ulti": False, "jump": False}
        self._prev = dict(self.btn_pressed)

    # ------------------------------------------------------------ cizim
    def draw(self, surf, alpha=110):
        L = self.L
        jx, jy = L.joy_center
        vx, vy = self.joy_vec
        # joystick yaricaplari da yerlesime gore olceklenir
        joy_out = max(20, L.btn_jump.w // 2)
        joy_in = max(9, int(joy_out * (JOY_IN / float(JOY_OUT))))
        kx, ky = jx + vx * (joy_in - 18), jy + vy * (joy_in - 18)
        base = pygame.Surface((L.w, L.h), pygame.SRCALPHA)
        pygame.draw.circle(base, (255, 255, 255, alpha // 3), (jx, jy),
                           joy_out, 3)
        pygame.draw.circle(base, (255, 255, 255, alpha), (kx, ky), joy_in)
        specs = [(L.btn_a1, "1", (235, 215, 130)),
                 (L.btn_a2, "2", (140, 200, 255)),
                 (L.btn_a3, "3", (255, 160, 160)),
                 (L.btn_ulti, "U", (255, 120, 200)),
                 (L.btn_jump, "↑", (150, 240, 160)),
                 (L.btn_crouch, "↓", (200, 200, 210))]
        for r, txt, col in specs:
            on = self._is_on(txt)
            c = (col[0], col[1], col[2], alpha + 70) if on else \
                (col[0], col[1], col[2], alpha // 2)
            pygame.draw.ellipse(base, c, r)
            pygame.draw.ellipse(base, (255, 255, 255, alpha), r, 3)
            fs = max(11, int(r.h * 0.48))
            img = pygame.font.SysFont("segoeui", fs, True).render(
                txt, True, (255, 255, 255, alpha + 90))
            base.blit(img, img.get_rect(center=r.center))
        surf.blit(base, (0, 0))

    def _is_on(self, name):
        for k, v in self.btn_pressed.items():
            if v:
                return True
        return False

    # ------------------------------------------------------------ girdi
    def _hit(self, pos):
        L = self.L
        for r, txt, _ in ((L.btn_a1, "a1", None), (L.btn_a2, "a2", None),
                          (L.btn_a3, "a3", None), (L.btn_ulti, "ulti", None),
                          (L.btn_jump, "jump", None), (L.btn_crouch, "crouch", None)):
            if r.collidepoint(pos):
                return txt
        if L.btn_pause.collidepoint(pos):
            return "pause"
        return None

    def handle_event(self, e):
        L = self.L
        if e.type == pygame.FINGERDOWN:
            pos = (e.x * L.w, e.y * L.h)
            jx, jy = L.joy_center
            if math.hypot(pos[0] - jx, pos[1] - jy) <= JOY_OUT + 26:
                self.joy_id = e.finger_id
                self._set_joy(pos)
                return True
            b = self._hit(pos)
            if b:
                self.btn_touch[e.finger_id] = b
                self.btn_pressed[b] = True
                return True
        elif e.type == pygame.FINGERMOTION and e.finger_id == self.joy_id:
            self._set_joy((e.x * L.w, e.y * L.h))
            return True
        elif e.type == pygame.FINGERUP:
            if e.finger_id == self.joy_id:
                self.joy_id = None
                self.joy_vec = (0.0, 0.0)
                return True
            b = self.btn_touch.pop(e.finger_id, None)
            if b:
                self.btn_pressed[b] = False
                return True
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            b = self._hit(e.pos)
            if b:
                self.btn_pressed[b] = True
                return True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for k in list(self.btn_pressed):
                self.btn_pressed[k] = False
            return True
        return False

    def _set_joy(self, pos):
        jx, jy = self.L.joy_center
        dx = pos[0] - jx
        dy = pos[1] - jy
        L = math.hypot(dx, dy) or 1.0
        if L > JOY_IN - 18:
            dx = dx / L * (JOY_IN - 18)
            dy = dy / L * (JOY_IN - 18)
        self.joy_vec = (dx / (JOY_IN - 18), dy / (JOY_IN - 18))

    def apply(self, inp, dead=0.35):
        """Girdiyi PlayerInput benzeri nesneye yazar."""
        vx, vy = self.joy_vec
        inp.left = vx < -dead
        inp.right = vx > dead
        inp.crouch = self.btn_pressed["crouch"]
        b = self.btn_pressed
        inp.jump = b["jump"]
        inp.ability1_pressed = b["a1"] and not self._prev["a1"]
        inp.ability2_pressed = b["a2"] and not self._prev["a2"]
        inp.ability3_pressed = b["a3"] and not self._prev["a3"]
        inp.ult_pressed = b["ulti"] and not self._prev["ulti"]
        inp.jump_pressed = b["jump"] and not self._prev["jump"]
        self._prev = dict(b)
        return inp

    def reset(self):
        self.joy_id = None
        self.joy_vec = (0.0, 0.0)
        self.btn_touch.clear()
        for k in self.btn_pressed:
            self.btn_pressed[k] = False
        self._prev = dict(self.btn_pressed)