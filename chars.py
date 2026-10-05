"""Ortak karakter ve yaratık çizim kütüphanesi.

Stickman oyuncular, boss'lar ve yaratıklar hep buradan çizilir; böylece
hepsi aynı kalitede, ortak bir görsel dile sahip olur.
"""
import math
import pygame


def mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def outline(c, f=0.55):
    return shade(c, f)


def _pt(p, f, s, ox, oy):
    return (int(ox + p[0] * f * s), int(oy + p[1] * s))


def _limb(surf, a, b, w, col, cap=True):
    pygame.draw.line(surf, col, a, b, max(2, int(w)))
    if cap:
        r = max(1, int(w / 2))
        pygame.draw.circle(surf, col, a, r)
        pygame.draw.circle(surf, col, b, r)


def _blob(surf, a, b, c, col):
    pygame.draw.polygon(surf, col, [a, b, c])


def _ellipse(surf, cx, cy, rx, ry, col, w=0):
    pygame.draw.ellipse(surf, col, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)), w)


# --------------------------------------------------------------- oyuncu

def draw_stickman(surf, ox, oy, s, color, facing, pose, phase,
                  flash=0.0, ult=False, ult_active=False, r=0.0, ground=True,
                  skel=None):
    """Klasik stickman silüeti: yuvarlak kafa, kalın gövde, düz kollar/bacaklar.

    Referans görseldeki gibi düz, yükseltisiz siluet; yön bakışa göre döner.
    """
    f = 1 if facing >= 0 else -1
    body = (255, 255, 255) if flash > 0 else color
    leg_w = max(3, int(7 * s))
    arm_w = max(3, int(6 * s))

    k = skel if skel is not None else _skel(pose, phase, r)
    by = k["bob"]
    P = lambda p: _pt(p, f, s, ox, oy + int(by * s))

    if ground and pose not in ("jump", "down"):
        _ellipse(surf, ox, oy, 13 * s, 4 * s, (20, 44, 28))

    if flash > 0:
        a = pygame.Surface((int(64 * s), int(64 * s)), pygame.SRCALPHA)
        pygame.draw.circle(a, (255, 140, 140, 48), (int(32 * s), int(32 * s)),
                           int(28 * s))
        surf.blit(a, (int(ox - 32 * s), int(oy - 62 * s)))
    if ult:
        pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1) / 2
        a = pygame.Surface((int(80 * s), int(80 * s)), pygame.SRCALPHA)
        pygame.draw.circle(a, (255, 210, 60, 30 + int(24 * pulse)),
                           (int(40 * s), int(40 * s)), int(33 * s),
                           max(1, int(2.5 * s)))
        surf.blit(a, (int(ox - 40 * s), int(oy - 74 * s)))
    if ult_active:
        a = pygame.Surface((int(84 * s), int(84 * s)), pygame.SRCALPHA)
        pygame.draw.circle(a, (255, 235, 120, 72), (int(42 * s), int(42 * s)),
                           int(36 * s), max(1, int(3 * s)))
        surf.blit(a, (int(ox - 42 * s), int(oy - 76 * s)))

    sho = k["chest"]
    hip = k["hip"]
    neck = (sho[0], sho[1] - 4)
    head = k["head"]

    _limb(surf, P(k["elbowB"]), P(k["handB"]), arm_w, body)
    _limb(surf, P(sho), P(k["elbowB"]), arm_w, body)
    _limb(surf, P(hip), P(k["kneeB"]), leg_w, body)
    _limb(surf, P(k["kneeB"]), P(k["footB"]), leg_w, body)

    _limb(surf, P(neck), P(hip), max(4, int(9 * s)), body)
    pygame.draw.circle(surf, body, P(neck), max(2, int(4 * s)))

    _limb(surf, P(sho), P(k["elbowF"]), arm_w, body)
    _limb(surf, P(k["elbowF"]), P(k["handF"]), arm_w, body)
    _limb(surf, P(hip), P(k["kneeF"]), leg_w, body)
    _limb(surf, P(k["kneeF"]), P(k["footF"]), leg_w, body)

    hr = int(11 * s)
    hc = P(head)
    pygame.draw.circle(surf, body, hc, hr)
    if not k["front"]:
        pygame.draw.polygon(surf, body, [
            (hc[0] + f * int(8 * s), hc[1] - int(2 * s)),
            (hc[0] + f * int(15 * s), hc[1] + int(2 * s)),
            (hc[0] + f * int(8 * s), hc[1] + int(5 * s))])
        pygame.draw.circle(surf, (255, 255, 255),
                           (hc[0] + f * int(4 * s), hc[1] - int(2 * s)),
                           max(1, int(1.6 * s)))
        _foot_fwd(surf, P(k["footF"]), f, s, body)
        _foot_fwd(surf, P(k["footB"]), f, s, body)

    if ult:
        hc = P(head)
        pygame.draw.circle(surf, (255, 200, 40), hc, hr + int(4 * s),
                           max(1, int(2 * s)))
    if pose == "down":
        pygame.draw.line(surf, (30, 26, 20), P(head), (int(ox + f * 12 * s),
                                                        int(oy - 4 * s)),
                         max(1, int(2 * s)))


def blend_skel(a, b, t, phase=0.0, r=0.0):
    """Iki pozi t oraninda karistirir (ayağa kalkma animasyonu icin)."""
    ka = _skel(a, phase, r)
    kb = _skel(b, phase, r)
    out = {}
    for key in ka:
        if key == "front":
            out[key] = ka[key] if t < 0.5 else kb[key]
        else:
            va, vb = ka[key], kb[key]
            if isinstance(va, tuple):
                out[key] = tuple(a + (b - a) * t for a, b in zip(va, vb))
            else:
                out[key] = va + (vb - va) * t
    return out


def _foot_fwd(surf, p, f, s, col):
    """Yandan görünüşte ayağın ucu baktığı yöne doğru uzanır."""
    pygame.draw.circle(surf, col, p, max(2, int(3.6 * s)))
    pygame.draw.line(surf, col, p, (int(p[0] + f * 6 * s), int(p[1])),
                     max(2, int(4 * s)))


# --------------------------------------------------------------- iskelet

def _skel(pose, phase, r=0.0):
    """Verilen poz için eklem noktaları (x ileri, y yukarı negatif)."""
    hip = (0, -34)
    chest = (0, -56)
    head = (0, -71)
    bob = 0.0
    kneeF, footF = (7, -19), (9, -2)
    kneeB, footB = (-7, -19), (-10, -2)
    elbowF, handF = (6, -44), (9, -30)
    elbowB, handB = (-6, -45), (-9, -31)
    front = False

    if pose == "walk":
        s = math.sin(phase)
        liftF = max(0.0, s)
        liftB = max(0.0, -s)
        footF = (10 + 9 * s, -2 - 7 * liftF)
        kneeF = (9 + 5 * s, -20 - 4 * liftF)
        footB = (-11 - 9 * s, -2 - 7 * liftB)
        kneeB = (-9 - 5 * s, -20 - 4 * liftB)
        handF = (9 - 11 * s, -30)
        elbowF = (5 - 5 * s, -44)
        handB = (-9 + 11 * s, -31)
        elbowB = (-5 + 5 * s, -45)
        bob = -abs(math.cos(phase)) * 2.5
    elif pose == "run":
        s = math.sin(phase)
        footF = (14 + 12 * s, -3 - 9 * max(0.0, s))
        kneeF = (13 + 7 * s, -20 - 6 * max(0.0, s))
        footB = (-13 - 12 * s, -3 - 9 * max(0.0, -s))
        kneeB = (-12 - 7 * s, -20 - 6 * max(0.0, -s))
        hip = (0, -35)
        chest = (3, -57)
        head = (5, -72)
        handF = (12 - 14 * s, -31)
        elbowF = (6 - 6 * s, -45)
        handB = (-11 + 14 * s, -32)
        elbowB = (-6 + 6 * s, -46)
        bob = -abs(math.cos(phase)) * 3.5
    elif pose == "jump":
        hip = (0, -33)
        chest = (0, -55)
        head = (1, -70)
        kneeF, footF = (11, -25), (14, -14)
        kneeB, footB = (-11, -25), (-14, -14)
        elbowF, handF = (9, -50), (6, -60)
        elbowB, handB = (-9, -50), (-6, -60)
        front = True
    elif pose == "sit":
        hip = (0, -22)
        chest = (0, -40)
        head = (0, -53)
        kneeF, footF = (13, -13), (16, -2)
        kneeB, footB = (-11, -13), (-14, -2)
        elbowF, handF = (11, -30), (16, -21)
        elbowB, handB = (-11, -31), (-16, -22)
        front = True
    elif pose == "crouch":
        hip = (0, -25)
        chest = (3, -45)
        head = (6, -59)
        kneeF, footF = (14, -15), (13, -2)
        kneeB, footB = (-6, -14), (-13, -2)
        elbowF, handF = (10, -36), (16, -28)
        elbowB, handB = (-9, -37), (-13, -27)
    elif pose == "punch":
        lean = r * 5
        hip = (0, -34)
        chest = (lean, -56)
        head = (lean + 2, -71)
        handF = (18 + r * 30, -53)
        elbowF = (9 + r * 10, -52)
        handB = (-9 - r * 3, -33)
        elbowB = (-6 - r * 2, -46)
        footF = (12 + r * 5, -2)
        kneeF = (11 + r * 3, -19)
    elif pose == "kick":
        back = r
        hip = (-back * 4, -34)
        chest = (-back * 7, -56)
        head = (-back * 9, -71)
        footF = (13 + back * 38, -14 - back * 28)
        kneeF = (12 + back * 19, -20 - back * 14)
        kneeB, footB = (-8 - back * 3, -19), (-13, -2)
        handF = (12 - back * 4, -38)
        elbowF = (7 - back * 3, -48)
        handB = (-14, -37)
        elbowB = (-8, -48)
    elif pose == "combo":
        lean = r * 4
        hip = (0, -34)
        chest = (lean, -56)
        head = (lean + 2, -71)
        footF = (13 + r * 30, -16 - r * 20)
        kneeF = (12 + r * 15, -20 - back_r(r, 10))
        handF = (18 + r * 28, -52)
        elbowF = (9 + r * 9, -51)
        handB = (-12, -37)
        elbowB = (-7, -48)
    elif pose == "hurt":
        hip = (-2, -33)
        chest = (-6, -55)
        head = (-11, -69)
        kneeF, footF = (11, -19), (13, -2)
        kneeB, footB = (-9, -20), (-13, -2)
        elbowF, handF = (-4, -50), (4, -58)
        elbowB, handB = (-9, -49), (-13, -57)
    elif pose == "down":
        hip = (-4, -12)
        chest = (-14, -16)
        head = (-24, -14)
        kneeF, footF = (12, -8), (18, -2)
        kneeB, footB = (2, -6), (10, -2)
        elbowF, handF = (-15, -25), (-7, -28)
        elbowB, handB = (-19, -9), (-25, -5)

    return {
        "hip": hip, "chest": chest, "head": head, "bob": bob, "front": front,
        "kneeF": kneeF, "footF": footF, "kneeB": kneeB, "footB": footB,
        "elbowF": elbowF, "handF": handF, "elbowB": elbowB, "handB": handB,
    }


def back_r(r, v):
    return r * v


# --------------------------------------------------------------- oyuncu

def draw_fighter(surf, ox, oy, s, color, facing, pose, phase,
                 hit=False, ult=False, flash=0.0, r=0.0, ground=True,
                 ult_active=False):
    """Detaylı insan figürü. ox/oy ayak zeminidir."""
    f = 1 if facing >= 0 else -1
    k = _skel(pose, phase, r)
    body = (255, 255, 255) if flash > 0 else color
    dark = shade(body, 0.68)
    skin = mix(body, (255, 255, 255), 0.12)
    line = max(2, int(5 * s))

    P = lambda p: _pt(p, f, s, ox, oy + int(k["bob"] * s))

    if ground and pose not in ("jump", "down"):
        _ellipse(surf, ox, oy, 15 * s, 5 * s, (18, 40, 24))
    if flash > 0:
        aura = pygame.Surface((int(70 * s), int(70 * s)), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 130, 130, 46), (35, 35), int(30 * s))
        surf.blit(aura, (int(ox - 35 * s), int(oy - 70 * s)))
    if ult:
        pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1) / 2
        aura = pygame.Surface((int(76 * s), int(76 * s)), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 210, 60, 30 + int(26 * pulse)),
                           (int(38 * s), int(38 * s)), int(32 * s), max(1, int(2.5 * s)))
        surf.blit(aura, (int(ox - 38 * s), int(oy - 72 * s)))
    if ult_active:
        glow = pygame.Surface((int(84 * s), int(84 * s)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 235, 120, 70), (int(42 * s), int(42 * s)),
                           int(36 * s), max(1, int(3 * s)))
        surf.blit(glow, (int(ox - 42 * s), int(oy - 76 * s)))

    # arka kol / arka bacak (koyu)
    _limb(surf, P(k["chest"]), P(k["elbowB"]), line, dark)
    _limb(surf, P(k["elbowB"]), P(k["handB"]), line - 1, dark)
    _limb(surf, P(k["hip"]), P(k["kneeB"]), line, dark)
    _limb(surf, P(k["kneeB"]), P(k["footB"]), line - 1, dark)
    pygame.draw.circle(surf, shade(body, 0.6), P(k["handB"]), int(3.4 * s))

    # gövde
    sh_top = (k["chest"][0], k["chest"][1] - 2)
    sh_bot = (k["hip"][0], k["hip"][1])
    w_sh = 6.5
    w_hip = 5.0
    torso = [P((sh_top[0] - w_sh, sh_top[1] - 1)), P((sh_top[0] + w_sh, sh_top[1] - 1)),
             P((sh_top[0] + w_hip + 0.5, sh_bot[1])), P((sh_top[0] - w_hip - 0.5, sh_bot[1]))]
    pygame.draw.polygon(surf, body, torso)
    pygame.draw.polygon(surf, shade(body, 0.62), torso, max(1, int(1.6 * s)))
    pygame.draw.circle(surf, body, P((sh_top[0], sh_top[1] - 1)), int(w_sh * s))
    pygame.draw.circle(surf, body, P((sh_bot[0], sh_bot[1])), int(w_hip * s))
    # kemer
    belt = [P((sh_bot[0] - w_hip - 0.5, sh_bot[1] - 4)), P((sh_bot[0] + w_hip + 0.5, sh_bot[1] - 4)),
            P((sh_bot[0] + w_hip + 0.5, sh_bot[1] - 1.5)), P((sh_bot[0] - w_hip - 0.5, sh_bot[1] - 1.5))]
    pygame.draw.polygon(surf, shade(body, 0.5), belt)

    # ön bacak
    _limb(surf, P(k["hip"]), P(k["kneeF"]), line, body)
    _limb(surf, P(k["kneeF"]), P(k["footF"]), line - 1, mix(body, (255, 255, 255), 0.15))
    _foot(surf, P(k["footF"]), f, s, shade(body, 0.45), 1)
    _foot(surf, P(k["footB"]), f, s, shade(body, 0.4), 0)

    # ön kol
    _limb(surf, P(k["chest"]), P(k["elbowF"]), line, body)
    _limb(surf, P(k["elbowF"]), P(k["handF"]), line - 1, skin)
    pygame.draw.circle(surf, shade(skin, 0.85), P(k["handF"]), max(2, int(4 * s)))

    # kafa
    _head(surf, P(k["head"]), f, s, skin, body, pose, flash)
    if ult:
        hc = P(k["head"])
        pygame.draw.circle(surf, (255, 200, 40), hc, int(14 * s), max(1, int(2 * s)))
        pygame.draw.circle(surf, (255, 245, 190),
                           (int(hc[0] + 4 * s), int(hc[1] - 4 * s)), max(1, int(2 * s)))


def _foot(surf, p, f, s, col, front):
    w = (7 if front else 6) * s
    rect = pygame.Rect(int(p[0] - (0 if front else 3) * s), int(p[1] - 1.5 * s),
                       int(w), int(4 * s))
    pygame.draw.rect(surf, col, rect, border_radius=int(2 * s))


def _head(surf, p, f, s, skin, body, pose, flash):
    r = int(9 * s)
    pygame.draw.circle(surf, shade(skin, 0.72), p, r)
    pygame.draw.circle(surf, skin, p, r)
    pygame.draw.circle(surf, shade(skin, 0.88), (p[0] - f * int(2 * s), p[1]),
                       int(r * 0.68))
    ex = f * int(2.2 * s)
    ey = -int(1.2 * s)
    angry = pose in ("punch", "kick", "combo")
    for sgn in (-1, 1):
        cxp = p[0] + ex + sgn * int(3.1 * s)
        cyp = p[1] + ey
        pygame.draw.circle(surf, (250, 250, 250), (cxp, cyp), max(2, int(2.3 * s)))
        pygame.draw.circle(surf, (25, 22, 30), (cxp + f * int(0.8 * s), cyp),
                           max(1, int(1.3 * s)))
        if angry:
            pygame.draw.line(surf, (30, 25, 25),
                             (cxp - int(2.6 * s), cyp - int(4.2 * s)),
                             (cxp + int(2.2 * s), cyp - int(2.4 * s)), max(1, int(1.4 * s)))
    my = p[1] + int(3.6 * s)
    if pose in ("punch", "kick", "combo"):
        pygame.draw.ellipse(surf, (95, 55, 60),
                            (int(p[0] - 2.2 * s), int(my - 1.2 * s), int(4.6 * s), int(3.0 * s)))
    else:
        pygame.draw.line(surf, shade(skin, 0.5), (p[0] - int(2.2 * s), my),
                         (p[0] + int(2.2 * s), my), max(1, int(1.4 * s)))
    hair = shade(body, 0.5)
    pygame.draw.arc(surf, hair, (int(p[0] - r), int(p[1] - r - 1), int(r * 2), int(r * 2)),
                    math.radians(195), math.radians(345), max(1, int(2.2 * s)))
    pygame.draw.line(surf, shade(skin, 0.75), (p[0] + f * int(6 * s), p[1] + int(1 * s)),
                     (p[0] + f * int(9 * s), p[1] + int(2.6 * s)), max(1, int(1.5 * s)))


# --------------------------------------------------------------- yaratık

def draw_creature(surf, ox, oy, s, color, family, cid, phase, state=None):
    st = state or {}
    f = 1 if st.get("dir", 1) >= 0 else -1
    dark = shade(color, 0.62)
    if family == "insan":
        draw_stickman(surf, ox, oy, s, color, f, "walk", phase)
        return
    if family == "zombi":
        _c_zombie(surf, ox, oy, s, color, dark, f, phase, st)
    elif family == "creeper":
        _c_creeper(surf, ox, oy, s, color, dark, f, phase, st)
    elif family == "örümcek":
        _c_spider(surf, ox, oy, s, color, dark, f, phase, st)
    elif family == "enderman":
        _c_enderman(surf, ox, oy, s, color, dark, f, phase, st)
    elif family == "blaze":
        _c_blaze(surf, ox, oy, s, color, dark, f, phase, st)
    elif family == "hayvan":
        _c_animal(surf, ox, oy, s, color, dark, f, phase, st, cid)
    else:
        _c_special(surf, ox, oy, s, color, dark, f, phase, st, cid)


def _eyes(surf, cx, cy, s, gap, col=(255, 255, 255), pupil=(20, 20, 25), r=2.4):
    for sgn in (-1, 1):
        p = (int(cx + sgn * gap), int(cy))
        pygame.draw.circle(surf, col, p, int(r * s))
        pygame.draw.circle(surf, pupil, (p[0], p[1]), max(1, int(r * 0.55 * s)))


def _c_zombie(surf, ox, oy, s, color, dark, f, phase, st):
    sw = math.sin(phase)
    _ellipse(surf, ox, oy, 15 * s, 5 * s, (18, 40, 24))
    lean = 6 * s
    hip = (ox, oy - 26 * s)
    chest = (ox + f * lean, oy - 44 * s)
    head = (ox + f * (lean + 5 * s), oy - 58 * s)
    _limb(surf, hip, (chest[0] - f * 2 * s, chest[1] + 4 * s), int(9 * s), color)
    _limb(surf, chest, (head[0] - f * 2 * s, head[1] + 6 * s), int(8 * s), color)
    for sgn, sp in ((-1, sw), (1, -sw)):
        kx = hip[0] + sgn * f * 4 * s
        ky = oy - 14 * s
        fx = hip[0] + sgn * f * (5 + 4 * sp) * s
        _limb(surf, hip, (kx, ky), int(5 * s), dark)
        _limb(surf, (kx, ky), (fx, oy - 2 * s), int(4 * s), dark)
    # kollar öne doğru
    for sgn, off in ((-1, 0), (1, 3)):
        ex = chest[0] + f * (12 + off) * s
        ey = chest[1] + 4 * s
        hx = chest[0] + f * (24 + off) * s
        hy = chest[1] + 2 * s + sgn * sw * 2 * s
        _limb(surf, chest, (ex, ey), int(5 * s), color if sgn > 0 else dark)
        _limb(surf, (ex, ey), (hx, hy), int(4 * s), color if sgn > 0 else dark)
    r = int(8 * s)
    pygame.draw.circle(surf, shade(color, 1.05), head, r)
    _eyes(surf, head[0] + f * 2 * s, head[1] - int(1 * s), s, 3.0 * s,
          (250, 250, 240), (40, 20, 20), 2.2)
    pygame.draw.line(surf, (60, 30, 30),
                     (head[0] - 3 * s, head[1] + 4 * s),
                     (head[0] + 4 * s, head[1] + 3 * s), max(1, int(1.6 * s)))
    # yırtık kıyafet
    pygame.draw.polygon(surf, dark, [(chest[0] - 8 * s, chest[1] + 2 * s),
                                     (chest[0] + 8 * s, chest[1] + 2 * s),
                                     (chest[0] + 4 * s, oy - 24 * s),
                                     (chest[0] - 5 * s, oy - 26 * s)])


def _c_creeper(surf, ox, oy, s, color, dark, f, phase, st):
    sw = math.sin(phase)
    siz = st.get("sizzle", 0.0)
    if siz > 0:
        k = min(1.0, siz / 0.9)
        aura = pygame.Surface((int(56 * s), int(56 * s)), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 245, 190, int(24 + 90 * k)),
                           (int(28 * s), int(28 * s)), int(24 * s))
        surf.blit(aura, (int(ox - 28 * s), int(oy - 44 * s)))
    _ellipse(surf, ox, oy, 15 * s, 5 * s, (18, 40, 24))
    # 4 kısa bacak
    for i, sgn in enumerate((-1, 1)):
        swing = sw if i == 0 else -sw
        _limb(surf, (ox + sgn * 8 * s, oy - 16 * s),
              (ox + sgn * (11 + 3 * swing) * s, oy - 2 * s), int(5 * s), dark)
    # gövde (kutu)
    bw, bh = 13 * s, 30 * s
    body = pygame.Rect(int(ox - bw), int(oy - 16 * s - bh), int(bw * 2), int(bh))
    pygame.draw.rect(surf, color, body, border_radius=int(5 * s))
    pygame.draw.rect(surf, dark, body, max(1, int(1.8 * s)), border_radius=int(5 * s))
    # baş
    hw, hh = 9 * s, 18 * s
    head = pygame.Rect(int(ox - hw), int(oy - 16 * s - bh - hh), int(hw * 2), int(hh))
    pygame.draw.rect(surf, color, head, border_radius=int(4 * s))
    pygame.draw.rect(surf, dark, head, max(1, int(1.8 * s)), border_radius=int(4 * s))
    # gözler
    ey = head.y + int(5 * s)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, (18, 18, 20), (int(ox + sgn * 3.6 * s), ey),
                           max(1, int(2.3 * s)))
        pygame.draw.circle(surf, (255, 255, 255), (int(ox + sgn * 3.6 * s), ey),
                           max(1, int(1.0 * s)))
    # ağız dokusu
    for i in range(4):
        y = ey + int((4 + i * 3.2) * s)
        wdt = int((5 - abs(i - 1.5)) * s)
        pygame.draw.rect(surf, shade(color, 0.45),
                         (int(ox - wdt), y, wdt * 2, max(1, int(2.4 * s))))
    if siz > 0:
        k = min(1.0, siz / 0.9)
        flashcol = (255, 255, 255) if k > 0.6 else (255, 236, 130)
        pygame.draw.rect(surf, flashcol, head.inflate(int(4 * k), int(4 * k)),
                         max(1, int((2 + 3 * k) * s)), border_radius=int(4 * s))
        pygame.draw.rect(surf, flashcol, body.inflate(int(3 * k), int(3 * k)),
                         max(1, int((2 + 3 * k) * s)), border_radius=int(5 * s))


def _c_spider(surf, ox, oy, s, color, dark, f, phase, st):
    sw = math.sin(phase)
    _ellipse(surf, ox, oy, 20 * s, 5 * s, (18, 40, 24))
    abd = (ox - f * 6 * s, oy - 24 * s)
    _ellipse(surf, abd[0], abd[1], 15 * s, 13 * s, color)
    _ellipse(surf, abd[0], abd[1], 15 * s, 13 * s, dark, max(1, int(2 * s)))
    _ellipse(surf, abd[0] - f * 3 * s, abd[1] - 4 * s, 8 * s, 6 * s, shade(color, 0.8))
    for i in range(3, -1, -1):
        for sgn in (-1, 1):
            a = 0.7 + i * 0.42
            kx = abd[0] - f * 2 * s + sgn * math.cos(a) * 8 * s
            ky = abd[1] + math.sin(a) * 7 * s
            ex = abd[0] + sgn * 18 * s + sw * 4 * s * sgn
            ey = abd[1] + (6 + i * 5) * s
            lx = abd[0] + sgn * 30 * s + sw * 6 * s * sgn
            ly = oy - 2 * s - i * 4 * s
            _limb(surf, (kx, ky), (ex, ey), int(3.4 * s), dark)
            _limb(surf, (ex, ey), (lx, ly), int(2.6 * s), dark)
    hd = (ox + f * 14 * s, oy - 28 * s)
    pygame.draw.circle(surf, shade(color, 0.92), hd, int(9 * s))
    pygame.draw.circle(surf, dark, hd, int(9 * s), max(1, int(1.6 * s)))
    _eyes(surf, hd[0] + f * 1 * s, hd[1] - int(3 * s), s, 3.0 * s,
          (235, 70, 70), (20, 10, 10), 2.0)
    for sgn in (-1, 1):
        pygame.draw.line(surf, shade(color, 0.6),
                         (hd[0], hd[1] + int(2 * s)),
                         (hd[0] + sgn * int(3 * s), hd[1] + int(6 * s)),
                         max(1, int(1.8 * s)))


def _c_enderman(surf, ox, oy, s, color, dark, f, phase, st):
    sw = math.sin(phase)
    _ellipse(surf, ox, oy, 14 * s, 5 * s, (18, 30, 44))
    hip = (ox, oy - 34 * s)
    chest = (ox, oy - 60 * s)
    head = (ox, oy - 74 * s)
    _limb(surf, hip, chest, int(8 * s), color)
    _limb(surf, chest, head, int(6 * s), color)
    for sgn, sp in ((-1, sw), (1, -sw)):
        _limb(surf, hip, (hip[0] + sgn * 4 * s, oy - 17 * s), int(5 * s), dark)
        _limb(surf, (hip[0] + sgn * 4 * s, oy - 17 * s),
              (hip[0] + sgn * (7 + 5 * sp) * s, oy - 1 * s), int(4 * s), dark)
    for sgn, sp in ((-1, -sw), (1, sw)):
        ex = chest[0] + sgn * 9 * s
        ey = chest[1] + 7 * s
        hx = chest[0] + sgn * (17 + 4 * sp) * s
        hy = chest[1] + 34 * s
        _limb(surf, chest, (ex, ey), int(5 * s), color if sgn > 0 else dark)
        _limb(surf, (ex, ey), (hx, hy), int(4 * s), color if sgn > 0 else dark)
        pygame.draw.circle(surf, shade(color, 1.15), (int(hx), int(hy)),
                           max(1, int(2.4 * s)))
    hw, hh = int(7 * s), int(9 * s)
    hd = pygame.Rect(int(head[0] - hw), int(head[1] - hh), hw * 2, hh * 2)
    pygame.draw.rect(surf, shade(color, 0.85), hd, border_radius=int(2 * s))
    pygame.draw.rect(surf, (10, 8, 16), hd, max(1, int(1.8 * s)), border_radius=int(2 * s))
    for sgn in (-1, 1):
        for dy in (-3, 3):
            pygame.draw.rect(surf, (205, 165, 255),
                             (int(head[0] + sgn * 3.6 * s - 1.5 * s),
                              int(head[1] + dy * s - 1 * s),
                              int(3 * s), int(2 * s)))


def _c_blaze(surf, ox, oy, s, color, dark, f, phase, st):
    bob = math.sin(phase * 0.9) * 3 * s
    cy = oy - 34 * s + bob
    aura = pygame.Surface((int(64 * s), int(64 * s)), pygame.SRCALPHA)
    pygame.draw.circle(aura, (255, 150, 40, 52), (int(32 * s), int(32 * s)),
                       int(28 * s))
    surf.blit(aura, (int(ox - 32 * s), int(cy - 32 * s)))
    for i in range(7):
        a = i / 7.0 * 6.283 + phase
        px = ox + math.cos(a) * 17 * s
        py = cy + math.sin(a) * 13 * s
        pygame.draw.circle(surf, (255, 190, 70), (int(px), int(py)), max(2, int(4 * s)))
        pygame.draw.circle(surf, (255, 245, 170), (int(px), int(py)), max(1, int(2 * s)))
    for i in range(9):
        t2 = phase * 2 + i
        fx = ox + math.sin(t2 * 0.7) * 14 * s
        fy = cy - 16 * s - abs(math.cos(t2)) * 16 * s
        pygame.draw.circle(surf, (255, 170, 50), (int(fx), int(fy)), max(1, int(2.6 * s)))
    pygame.draw.rect(surf, color, (int(ox - 9 * s), int(cy - 9 * s), int(18 * s), int(18 * s)),
                     border_radius=int(4 * s))
    pygame.draw.rect(surf, (255, 235, 150), (int(ox - 6 * s), int(cy - 6 * s), int(12 * s), int(12 * s)),
                     border_radius=int(3 * s))
    pygame.draw.rect(surf, dark, (int(ox - 9 * s), int(cy - 9 * s), int(18 * s), int(18 * s)),
                     max(1, int(2 * s)), border_radius=int(4 * s))
    _eyes(surf, ox, cy - 1 * s, s, 3.4 * s, (60, 30, 10), (20, 10, 5), 2.0)


ANIMAL_TINT = {
    "kurt": (150, 140, 130), "kartal": (170, 140, 90), "kaplan": (215, 160, 60),
    "ayi": (135, 95, 55), "tilki": (215, 130, 60), "koyun": (235, 235, 230),
    "domuz": (225, 175, 180), "tavuk": (245, 245, 240), "balik": (90, 160, 220),
    "kuraga": (110, 190, 110), "yilan": (90, 170, 80), "kurkadam": (140, 110, 80),
    "geyik": (160, 120, 80), "panda": (245, 245, 245), "aksolotl": (240, 160, 200),
    "kopek": (190, 150, 95),
}


def _c_animal(surf, ox, oy, s, color, dark, f, phase, st, cid):
    sw = math.sin(phase)
    col = ANIMAL_TINT.get(cid, color)
    light = shade(col, 1.12)
    _ellipse(surf, ox, oy, 20 * s, 5 * s, (18, 40, 24))
    body = (ox, oy - 26 * s)
    _ellipse(surf, body[0], body[1], 16 * s, 11 * s, col)
    _ellipse(surf, body[0] - f * 2 * s, body[1] - 3 * s, 12 * s, 6 * s, light)
    for i, sgn in enumerate((-1, 1)):
        lx = body[0] + sgn * (10 - i * 4) * s
        ky = oy - 15 * s
        fx = lx + sgn * 2 * s + sw * 5 * s * sgn
        _limb(surf, (lx, body[1] + 4 * s), (lx + sgn * 1 * s, ky), int(6 * s), dark)
        _limb(surf, (lx + sgn * 1 * s, ky), (fx, oy - 2 * s), int(5 * s), dark)
    hd = (body[0] + f * 16 * s, oy - 36 * s)
    pygame.draw.circle(surf, col, hd, int(9 * s))
    pygame.draw.circle(surf, dark, hd, int(9 * s), max(1, int(1.5 * s)))
    if cid in ("kaplan", "kurt", "kurkadam", "kopek", "tilki"):
        for sgn in (-1, 1):
            pygame.draw.polygon(surf, col, [
                (int(hd[0] - 5 * s + sgn * 4 * s), int(hd[1] - 6 * s)),
                (int(hd[0] + 1 * s + sgn * 4 * s), int(hd[1] - 6 * s)),
                (int(hd[0] + 1 * s + sgn * 1.5 * s), int(hd[1] - 14 * s))])
        pygame.draw.polygon(surf, shade(col, 1.25), [
            (int(hd[0] + 2 * s), int(hd[1])),
            (int(hd[0] + 12 * s), int(hd[1] + 3 * s)),
            (int(hd[0] + 2 * s), int(hd[1] + 6 * s))])
    elif cid in ("tavuk", "panda", "koyun"):
        pygame.draw.circle(surf, light, (int(hd[0] - 4 * s), int(hd[1] - 7 * s)),
                           int(6 * s))
    if cid == "panda":
        pygame.draw.circle(surf, (40, 40, 45), (int(hd[0] - f * 4 * s), int(hd[1] - 3 * s)),
                           int(4 * s))
    _eyes(surf, hd[0] + f * 2 * s, hd[1] - int(1 * s), s, 2.8 * s, (250, 250, 250),
          (25, 22, 22), 2.0)
    if cid not in ("balik", "kuraga", "yilan"):
        _limb(surf, (body[0] - f * 14 * s, body[1] - 2 * s),
              (body[0] - f * 23 * s, body[1] - 10 * s - sw * 4 * s), int(4 * s), dark)
    if cid == "balik":
        _blob(surf, (int(ox - 13 * s), int(oy - 27 * s)), (int(ox + 13 * s), int(oy - 27 * s)),
              (int(ox - 2 * s), int(oy - 37 * s)), col)
        pygame.draw.polygon(surf, light, [
            (int(ox - 12 * s), int(oy - 27 * s)), (int(ox - 24 * s), int(oy - 34 * s)),
            (int(ox - 24 * s), int(oy - 20 * s))])
    if cid == "yilan":
        for i in range(5):
            _ellipse(surf, ox - f * i * 10 * s,
                     oy - 5 * s - abs(math.sin(phase + i)) * 4 * s, 7 * s, 5 * s, col)


def _c_special(surf, ox, oy, s, color, dark, f, phase, st, cid):
    if cid == "slaim":
        b = math.sin(phase * 2) * 0.12 + 1.0
        h = int(30 * s * b)
        _ellipse(surf, ox, oy - 1, 14 * s, 5 * s, (18, 40, 24))
        pygame.draw.rect(surf, (110, 200, 150), (int(ox - 14 * s), int(oy - h),
                                                   int(28 * s), h), border_radius=int(12 * s))
        pygame.draw.rect(surf, (70, 160, 120), (int(ox - 14 * s), int(oy - h),
                                                 int(28 * s), h), max(1, int(2 * s)),
                         border_radius=int(12 * s))
        _eyes(surf, ox, oy - h * 0.65, s, 5 * s, (240, 255, 250), (30, 60, 50), 3.0)
    elif cid == "magmakup":
        b = 1.0 + math.sin(phase * 3) * 0.08
        _ellipse(surf, ox, oy - 1, 13 * s, 4 * s, (60, 30, 10))
        r = int(13 * s * b)
        pygame.draw.rect(surf, (200, 90, 30), (int(ox - r), int(oy - r * 2), r * 2, r * 2),
                         border_radius=int(4 * s))
        pygame.draw.rect(surf, (255, 200, 90), (int(ox - r), int(oy - r * 2), r * 2, r * 2),
                         max(1, int(2 * s)), border_radius=int(4 * s))
        for i in range(4):
            a = phase * 2 + i / 4.0 * 6.283
            pygame.draw.circle(surf, (255, 240, 160),
                               (int(ox + math.cos(a) * r), int(oy - r + math.sin(a) * r)),
                               max(1, int(2.6 * s)))
        _eyes(surf, ox, oy - r * 0.6, s, 4.4 * s, (60, 30, 10), (20, 10, 5), 2.4)
    else:
        _ellipse(surf, ox, oy, 20 * s, 6 * s, (18, 40, 24))
        bw = int(15 * s)
        for sgn in (-1, 1):
            _limb(surf, (ox + sgn * bw * 0.6, oy - 44 * s),
                  (ox + sgn * (bw + 5 * s), oy - 26 * s), int(8 * s),
                  color if sgn > 0 else dark)
            _limb(surf, (ox + sgn * (bw + 5 * s), oy - 26 * s),
                  (ox + sgn * (bw + 2 * s), oy - 12 * s), int(7 * s),
                  color if sgn > 0 else dark)
            _limb(surf, (ox + sgn * bw * 0.5, oy - 8 * s),
                  (ox + sgn * (bw + 3 * s), oy - 2 * s), int(8 * s),
                  color if sgn > 0 else dark)
        torso = pygame.Rect(int(ox - bw), int(oy - 56 * s), bw * 2, int(40 * s))
        pygame.draw.rect(surf, color, torso, border_radius=int(4 * s))
        pygame.draw.rect(surf, dark, torso, max(1, int(2.4 * s)), border_radius=int(4 * s))
        for i in range(2):
            y = int(oy - (46 - i * 14) * s)
            pygame.draw.line(surf, shade(color, 0.6), (torso.left, y), (torso.right, y),
                             max(1, int(1.6 * s)))
        head = pygame.Rect(int(ox - 8 * s), int(oy - 68 * s), int(16 * s), int(14 * s))
        pygame.draw.rect(surf, shade(color, 1.12), head, border_radius=int(3 * s))
        pygame.draw.rect(surf, dark, head, max(1, int(2 * s)), border_radius=int(3 * s))
        for sgn in (-1, 1):
            pygame.draw.circle(surf, (20, 20, 24),
                               (int(ox + sgn * 4.2 * s), int(oy - 61 * s)), int(2.6 * s))
            pygame.draw.circle(surf, (255, 235, 120),
                               (int(ox + sgn * 4.2 * s), int(oy - 61 * s)), int(1.2 * s))


# --------------------------------------------------------------- boss

def draw_boss(surf, ox, oy, size, color, family, hp_frac, phase, state=None):
    st = state or {}
    f = 1 if st.get("dir", 1) >= 0 else -1
    s = max(0.8, size)
    dark = shade(color, 0.6)
    hurt = st.get("flash", 0.0)
    body = (255, 240, 240) if hurt > 0 else color
    angry = hp_frac < 0.35
    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2

    if angry:
        aura = pygame.Surface((int(110 * s), int(110 * s)), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 70, 60, 26 + int(18 * pulse)),
                           (int(55 * s), int(55 * s)), int(48 * s))
        surf.blit(aura, (int(ox - 55 * s), int(oy - 64 * s)))

    _ellipse(surf, ox, oy, 34 * s, 9 * s, (16, 14, 26))
    if family == "creeper":
        _c_creeper(surf, ox, oy, s * 1.75, body, dark, f, phase, st)
        _boss_crown(surf, ox, oy - 118 * s, s, angry)
        return
    if family == "örümcek":
        _c_spider(surf, ox, oy, s * 1.9, body, dark, f, phase, st)
        _boss_eyes_glow(surf, ox + 20 * s, oy - 58 * s, s * 1.6)
        return
    if family == "enderman":
        _c_enderman(surf, ox, oy, s * 1.5, body, dark, f, phase, st)
        _boss_crown(surf, ox, oy - 122 * s, s, angry)
        return
    if family == "blaze":
        _c_blaze(surf, ox, oy, s * 1.6, body, dark, f, phase, st)
        _boss_crown(surf, ox, oy - 92 * s, s, angry)
        return

    # varsayılan: iri insan biçimli boss (zombi ailesi)
    draw_fighter(surf, ox, oy, s * 1.5, body, f, "idle", phase, ult=angry)
    hip = (ox, oy - 51 * s)
    chest = (ox, oy - 84 * s)
    head = (ox, oy - 107 * s)
    # zırh plakası
    pygame.draw.polygon(surf, shade(body, 0.8), [
        (int(chest[0] - 14 * s), int(chest[1] - 2 * s)),
        (int(chest[0] + 14 * s), int(chest[1] - 2 * s)),
        (int(chest[0] + 10 * s), int(chest[1] + 20 * s)),
        (int(chest[0] - 10 * s), int(chest[1] + 20 * s))])
    pygame.draw.polygon(surf, shade(body, 0.55), [
        (int(chest[0] - 14 * s), int(chest[1] - 2 * s)),
        (int(chest[0] + 14 * s), int(chest[1] - 2 * s)),
        (int(chest[0] + 10 * s), int(chest[1] + 20 * s)),
        (int(chest[0] - 10 * s), int(chest[1] + 20 * s))], max(1, int(2 * s)))
    # omuz zırhları
    for sgn in (-1, 1):
        pygame.draw.circle(surf, shade(body, 0.7),
                           (int(chest[0] + sgn * 13 * s), int(chest[1] + 1 * s)),
                           int(7 * s))
        _limb(surf, (chest[0] + sgn * 13 * s, chest[1] + 2 * s),
              (chest[0] + sgn * (24 + 4 * math.sin(phase)) * s, chest[1] + 22 * s),
              int(6 * s), shade(body, 0.9 if sgn > 0 else 0.65))
    _boss_crown(surf, ox, oy - 122 * s, s, angry)


def _boss_crown(surf, ox, oy, s, angry):
    col = (255, 200, 60) if angry else (210, 180, 110)
    pts = [(ox - 11 * s, oy + 5 * s), (ox - 9 * s, oy - 7 * s), (ox - 4 * s, oy + 1 * s),
           (ox, oy - 10 * s), (ox + 4 * s, oy + 1 * s), (ox + 9 * s, oy - 7 * s),
           (ox + 11 * s, oy + 5 * s)]
    pygame.draw.polygon(surf, col, [(int(p[0]), int(p[1])) for p in pts])
    pygame.draw.polygon(surf, shade(col, 0.6), [(int(p[0]), int(p[1])) for p in pts],
                        max(1, int(1.6 * s)))


def _boss_eyes_glow(surf, ox, oy, s):
    for sgn in (-1, 1):
        pygame.draw.circle(surf, (255, 70, 70), (int(ox + sgn * 4 * s), int(oy)), int(2.6 * s))