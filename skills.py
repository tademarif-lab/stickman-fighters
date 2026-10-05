# -*- coding: utf-8 -*-
"""Yetenek motoru: projilektil, alan, isin, dalga, minyon, cekme, firlatma.

Stickman bu motora baglanir; motor sahneyi (Fight) degil, oyunculari tanir.
"""
import math
import pygame
from classes import SKILLS, PX

# ---------------------------------------------------------------- durum etkileri
# status -> (etiket, renk, saniyede hasar, tip)
STATUS_INFO = {
    "poison": ("ZEHİR", (140, 220, 70), "dps"),
    "burn": ("YANMA", (255, 140, 40), "dps"),
    "shock": ("ÇARPILDI", (150, 210, 255), "dps"),
    "bleed": ("KANAMA", (220, 40, 40), "dps"),
    "fall": ("HAVADA", (220, 240, 255), "dps"),
    "stun": ("SERSEM", (255, 220, 90), "stun"),
    "slow": ("YAVAŞ", (150, 150, 170), "slow"),
    "weak": ("ZAYIF", (190, 170, 150), "weak"),
    "ai": ("ZOMBİ I", (90, 255, 120), "ai"),
    "fly": ("UÇUŞ", (200, 245, 255), "fly"),
    "invisible": ("GÖRÜNMEZ", (200, 200, 220), "buff"),
    "immune": ("DOKUNULMAZ", (255, 255, 255), "buff"),
    "liquid": ("SIVI", (40, 40, 55), "buff"),
    "phase": ("FANTOM", (190, 210, 255), "buff"),
}


class Projectile:
    __slots__ = ("o", "x", "y", "vx", "vy", "life", "max_life", "dmg", "hits",
                 "size", "color", "homing", "gravity", "spin", "ang", "st",
                 "lifesteal", "pickup", "ret", "owner_f", "burst", "dodge",
                 "half", "target", "dead", "spark", "glow", "arc", "glow_t")

    def __init__(self, owner, x, y, vx, vy, sk):
        self.o = owner
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.max_life = sk.get("life", 1.5)
        self.life = self.max_life
        self.dmg = sk.get("dmg", 0.0)
        self.hits = sk.get("hits", 1)
        self.size = sk.get("size", 8)
        self.color = sk.get("color", (230, 230, 230))
        self.homing = sk.get("homing", 0.0)
        self.gravity = sk.get("gravity", 0.0)
        self.spin = sk.get("spin", False)
        self.ang = 0.0
        self.st = sk.get("status")
        self.lifesteal = sk.get("lifesteal", 0.0)
        self.pickup = sk.get("pickup", False)
        self.ret = sk.get("return_home", False)
        self.owner_f = owner
        self.burst = None
        if sk.get("burst_zone"):
            self.burst = {"r": sk["burst_zone"] / 2.0,
                          "dmg": sk.get("burst_dmg", sk.get("dmg", 5.0)),
                          "life": sk.get("burst_life", 1.0)}
        self.dodge = None
        self.half = False
        self.target = None
        self.dead = False
        self.spark = sk.get("spark", False)
        self.glow = sk.get("glow", False)
        self.arc = sk.get("arc", False)
        self.glow_t = 0.0


class Zone:
    __slots__ = ("o", "x", "y", "w", "life", "max_life", "dmg", "color", "dodge",
                 "rep", "rep_t", "st", "follow", "seeker", "shake", "knock",
                 "push", "heal", "half", "shot", "count", "dead", "owner_f")

    def __init__(self, owner, x, y, sk):
        self.o = owner
        self.owner_f = owner
        self.x = float(x)
        self.y = float(y)
        self.w = float(sk.get("zw", PX * 5))
        self.max_life = sk.get("life", 1.0)
        self.life = self.max_life
        self.dmg = sk.get("dmg", 0.0)
        self.color = sk.get("color", (255, 255, 255))
        self.dodge = sk.get("dodge")
        self.half = sk.get("half_dodge")
        self.rep = sk.get("repeat", 0.0)
        self.rep_t = 0.0
        self.st = sk.get("status")
        self.follow = sk.get("follow", False)
        self.seeker = sk.get("seeker", False)
        self.shake = sk.get("shake", 0.0)
        self.knock = sk.get("knock", 0.0)
        self.push = sk.get("push", 0.0)
        self.heal = sk.get("heal", 0.0)
        self.count = sk.get("count", 1)
        self.shot = 0
        self.dead = False


class Beam:
    __slots__ = ("o", "x", "y", "f", "time", "max_time", "tick", "t", "dmg",
                 "ln", "color", "color2", "st", "no_limit", "left", "idx", "dead",
                 "mind", "zw", "limited")

    def __init__(self, owner, sk):
        self.o = owner
        self.x = owner.x
        self.y = owner.y - 40
        self.f = owner.facing
        self.max_time = sk.get("beam_time", 0.6)
        self.time = self.max_time
        self.tick = sk.get("beam_tick", 0.3)
        self.t = 0.0
        self.dmg = sk.get("dmg", 5.0)
        self.ln = sk.get("beam_len", PX * 6)
        self.zw = sk.get("zw", 0.0)
        self.color = sk.get("color", (255, 255, 255))
        self.color2 = sk.get("color2")
        self.st = sk.get("status")
        self.no_limit = sk.get("no_limit", False)
        self.limited = sk.get("limited", 0)
        self.mind = sk.get("mind_control", False)
        self.idx = 0
        self.dead = False


class Wall:
    __slots__ = ("o", "x", "y", "h", "w", "time", "max_time", "dmg", "color",
                 "wave", "spikes", "spike_dmg", "dead", "owner_f", "wave_dmg")

    def __init__(self, owner, sk):
        self.o = owner
        self.owner_f = owner
        self.x = owner.x + owner.facing * 70
        self.y = owner.y
        self.h = sk.get("wall_h", 80)
        self.w = sk.get("zw", PX * 3)
        self.max_time = sk.get("wall_time", 5.0)
        self.time = self.max_time
        self.dmg = sk.get("dmg", 5.0)
        self.wave_dmg = sk.get("wall_dmg", sk.get("dmg", 5.0))
        self.color = sk.get("color", (90, 150, 240))
        self.wave = sk.get("wave_speed", 500)
        self.spikes = sk.get("spikes", 0)
        self.spike_dmg = sk.get("spike_dmg", 5.0)
        self.dead = False


class Minion:
    __slots__ = ("o", "x", "y", "hp", "dmg", "speed", "f", "unit", "life",
                 "t", "target", "dead", "ranged")

    def __init__(self, owner, x, y, hp, dmg, speed, unit, ranged):
        self.o = owner
        self.x = float(x)
        self.y = float(y)
        self.hp = float(hp)
        self.dmg = dmg
        self.speed = speed
        self.f = 1
        self.unit = unit
        self.ranged = ranged
        self.life = 18.0
        self.t = 0.0
        self.target = None
        self.dead = False


class Chaser:
    __slots__ = ("o", "x", "y", "dmg", "life", "size", "color", "speed",
                 "target", "dead", "tick")

    def __init__(self, owner, sk):
        self.o = owner
        self.x = owner.x
        self.y = owner.y
        self.dmg = sk.get("dmg", 2.5)
        self.life = sk.get("chase_time", 12.0) + sk.get("tail_time", 0.0)
        self.size = sk.get("size", 50)
        self.color = sk.get("color", (80, 160, 255))
        self.speed = sk.get("speed", 180.0)
        self.target = None
        self.tick = 0.0
        self.dead = False


class Burst:
    __slots__ = ("o", "ammo", "rate", "sk", "t", "f", "dead", "half", "shot",
                 "dodge")

    def __init__(self, owner, sk):
        self.o = owner
        self.ammo = sk.get("ammo", 10)
        self.rate = sk.get("rate", 0.12)
        self.sk = sk
        self.t = 0.0
        self.f = owner.facing
        self.shot = 0
        self.half = sk.get("half_dodge")
        self.dodge = None
        self.dead = False


class SkillEngine:
    """Tum yetenek varliklarini tutar ve gunceller."""

    def __init__(self):
        self.fight = None
        self.projs = []
        self.zones = []
        self.beams = []
        self.walls = []
        self.minions = []
        self.chasers = []
        self.bursts = []
        self.fx = []            # gecici efekt listesi
        self.shake = 0.0
        self.time = 0.0

    # ------------------------------------------------------------ yardimcilar
    def bind(self, fight):
        self.fight = fight
        for p in (fight.p1, fight.p2):
            p.eng = self

    def targets(self):
        if self.fight is None:
            return []
        return [self.fight.p1, self.fight.p2]

    @staticmethod
    def _dodge_ok(target, mode):
        if not mode:
            return True
        if mode == "zıpla":
            return not target.on_ground
        if mode == "eğil":
            return not target.crouching
        return True

    def _facing(self, o):
        return o.facing

    # ------------------------------------------------------------ hasar
    def damage(self, target, amount, src=None, kind="hit"):
        """Hasar + kalkan + durum etkisi uygular."""
        if target is None or target.hp <= 0:
            return False
        if target.buff("immune"):
            return False
        amount *= target.dmg_taken_mult()
        if amount <= 0:
            return False
        used = target.absorb(amount)
        left = amount - used
        if left > 0:
            target.hp = max(0.0, target.hp - left)
        target.on_damaged(amount, src)
        self.fx.append({"t": 0.45, "x": target.x, "y": target.y - 46,
                        "txt": "%g" % round(amount, 1), "col": target.fx_col()})
        if left > 0 and src is not None and src.buff("reflect"):
            back = left * src.buff_val("reflect")
            if back > 0.5:
                self.damage(src, back, target, "reflect")
        if src is not None and target.buff("reflect") and amount > 0:
            back = amount * target.buff_val("reflect")
            if back > 0.5:
                self.damage(src, back, target, "reflect")
        if target.hp <= 0:
            target.on_death(src)
        return True

    def apply_status(self, target, st):
        if target is None or not st:
            return
        k = st.get("kind")
        if k in ("invisible", "immune", "phase", "liquid"):
            target.set_buff(k, 10.0, 0.0)
            return
        cur = target.st.get(k)
        dur = st.get("dur", 0.0)
        if cur is None or dur >= cur["t"]:
            target.st[k] = {"t": dur, "dps": st.get("dps", 0.0),
                            "power": st.get("power", 0.0)}
        else:
            cur["t"] = max(cur["t"], dur)

    # ------------------------------------------------------------ pasifler
    def cast_passive(self, owner, src):
        """Sinif pasifi: hasar alindiginda tetiklenir."""
        cid = owner.cls["id"] if owner.cls else ""
        if src is None:
            return
        if cid == "zehri_krali":
            self.apply_status(src, {"kind": "poison", "dur": 1.0, "dps": 1.0,
                                    "power": 0.0})
        elif cid == "ates_man":
            self.apply_status(src, {"kind": "burn", "dur": 3.0, "dps": 2.5,
                                    "power": 0.0})
        elif cid == "yildirim_patronu":
            self.damage(src, 2.5, owner)
            src.stunned_t = 0.5
            self.apply_status(src, {"kind": "stun", "dur": 0.5})
        elif cid == "madenci":
            self.minions.append(Minion(owner, src.x, src.y, 5.0, 5.0, 0.0,
                                       "elmas", False))
            m = self.minions[-1]
            m.life = 5.0
            m.target = src
            m.o = owner
        elif cid == "mutant20":
            self.apply_status(src, {"kind": "stun", "dur": 5.0})
            self.damage(src, 5.0, owner)
        elif cid == "speakerman":
            self.zones.append(Zone(owner, src.x, src.y,
                                   {"zw": 260, "dmg": 5.0, "life": 0.5,
                                    "dodge": "eğil", "color": (255, 220, 140)}))
        elif cid == "hirsiz":
            owner.limb_loss += 5.0
        elif cid == "suikasteci":
            lost = 100.0 - owner.hp
            owner.gain_shield(min(75.0 - owner.shield, lost * 0.5))

    # ------------------------------------------------------------ yetenek
    def cast(self, owner, sk, target, charge=0.0):
        kind = sk.get("kind", "melee")
        dmg = sk.get("dmg", 0.0) * owner.dmg_mult()
        if sk.get("chain"):
            dmg = sk["dmg"] * owner.dmg_mult()
        d = dict(sk)
        d["dmg"] = dmg
        if kind == "charge_melee":
            d["dmg"] = (sk.get("charge_dmg", dmg) if charge > 0 else dmg)
            kind = "melee"
        elif kind == "charge_proj":
            self._charge_proj(owner, sk, target, charge)
            return
        fn = getattr(self, "_c_" + kind, None)
        if fn is None:
            return
        fn(owner, d, target)

    # --- melee (animasyon Stickman'da; burada ek etkiler)
    def _c_melee(self, o, sk, t):
        if sk.get("heal"):
            o.heal(sk["heal"])
        if sk.get("self_slow"):
            o.set_buff("slow", sk.get("self_slow_time", 1.0), sk["self_slow"])
        if sk.get("launch"):
            t.vy = -sk["launch"]
            t.on_ground = False
        if sk.get("every"):
            o.ability_uses = getattr(o, "ability_uses", 0) + 1
            if o.ability_uses % sk["every"] == 0:
                self.zones.append(Zone(o, o.x + o.facing * sk.get("extra_zone", 100),
                                       o.y, {"zw": sk.get("extra_zone", 100),
                                             "dmg": sk.get("extra_dmg", 5.0),
                                             "life": 0.5, "color": sk.get("extra_color"),
                                             "dodge": sk.get("extra_dodge")}))

    def _c_buff(self, o, sk, t):
        mult = sk.get("buff_power", 1.0)
        for b in sk.get("buff", []):
            if b == "shield":
                o.gain_shield(sk.get("buff_shield", 0.0))
                o.set_buff("shield", sk.get("buff_time", 5.0), 0.5)
            elif b == "shield_half":
                o.shield = o.shield / 2.0
                o.max_shield = o.max_shield / 2.0
            elif b == "all5":
                o.set_buff("all5", sk.get("buff_time", 8.0), 5.0)
            elif b == "dmg":
                o.set_buff("dmg", sk.get("buff_time", 6.0), mult)
            elif b == "dmg_half":
                o.set_buff("dmg", sk.get("buff_time", 6.0), 0.5)
            elif b == "giant":
                o.set_buff("giant", sk.get("buff_time", 6.0), mult)
            elif b == "tier":
                o.level_up_tier(sk.get("buff_power", 2.5))
            elif b in ("speed", "invisible", "immune", "fly", "phase", "liquid",
                       "reflect", "sword", "horse", "form2", "vehicle", "akm",
                       "haste", "possess", "unpossess", "cd2"):
                o.set_buff(b, sk.get("buff_time", 5.0), mult)
        if sk.get("max_hp"):
            o.gain_max_hp(sk["max_hp"])

    def _c_proj(self, o, sk, t):
        n = sk.get("count", 1)
        spread = sk.get("spread", 0.0)
        base = sk.get("speed", 460)
        up = -60.0 if not sk.get("arc") else -220.0
        for i in range(n):
            f = base
            a = up
            if spread and n > 1:
                a += (i - (n - 1) / 2.0) * spread * 400.0
                f *= (0.92 + 0.04 * (i % 3))
            p = Projectile(o, o.x + o.facing * 26, o.y - 44,
                           o.facing * f, a, sk)
            if n > 1 and i % 2 == 0:
                p.y -= 10
            p.target = t
            self.projs.append(p)
        if sk.get("blink"):
            d = sk["blink"]
            if sk.get("blink_to_target") and t is not None:
                d = min(abs(t.x - o.x) - 30.0, d)
            o.teleport(d * o.facing)
        if sk.get("extra_proj"):
            for i in range(sk["extra_proj"]):
                self.projs.append(Projectile(o, o.x + o.facing * 26,
                                              o.y - 40 - i * 12,
                                              o.facing * 520, -40 - i * 20,
                                              dict(sk, dmg=sk.get("proj_dmg", 8.0),
                                                   life=1.2, color=sk.get("color"))))

    def _c_burst(self, o, sk, t):
        b = Burst(o, sk)
        self.bursts.append(b)

    def _c_zone(self, o, sk, t):
        n = sk.get("count", 1)
        for i in range(n):
            x = o.x + o.facing * sk.get("zw", PX * 5) * (0.35 + 0.65 * i / max(1, n - 1))
            z = Zone(o, x, o.y, sk)
            z.shot = i
            self.zones.append(z)
        if sk.get("extra_zones"):
            for i in range(sk["extra_zones"]):
                self.zones.append(Zone(o, o.x + o.facing * (120 + i * 45), o.y,
                                       dict(sk, dodge="eğil", zw=PX * 2.5)))
        if sk.get("shake"):
            self.shake = max(self.shake, sk["shake"])

    def _c_beam(self, o, sk, t):
        n = sk.get("beams", 1)
        alt = sk.get("alternates", 0)
        for i in range(n):
            b = Beam(o, sk)
            b.idx = i
            if alt:
                b.ln = PX * 4 if i % 2 == 0 else PX * 7
            elif n > 1:
                b.ln = PX * (4 + 3 * (i % 3))
            if sk.get("color2") and i % 2 == 1:
                b.color = sk["color2"]
            self.beams.append(b)

    def _c_wall(self, o, sk, t):
        self.walls.append(Wall(o, sk))
        if sk.get("proj_count"):
            for i in range(sk["proj_count"]):
                self.projs.append(Projectile(o, o.x + o.facing * 26,
                                              o.y - 44 - i * 10,
                                              o.facing * 470, -50,
                                              dict(sk, dmg=sk.get("proj_dmg", 10.0))))
        for i in range(sk.get("waves", 0)):
            self.zones.append(Zone(o, o.x + o.facing * (140 + i * 130), o.y,
                                   dict(sk, zw=PX * 3, life=1.2, dodge=None)))

    def _c_pull(self, o, sk, t):
        if t is None or t.hp <= 0:
            return
        dist = abs(t.x - o.x)
        if dist > sk.get("range", 340):
            self.fx.append({"t": 0.5, "x": t.x, "y": t.y - 60,
                            "txt": "ÇOK UZAK", "col": (200, 200, 210)})
            return
        self.damage(t, sk.get("dmg", 0.0), o)
        if sk.get("push_dmg"):
            t.vx = o.facing * 900
            t.vy = -260
            t.on_ground = False
            self.damage(t, sk["push_dmg"], o)
        else:
            t.vx = -o.facing * 780
            t.vy = -180
            t.on_ground = False
        for i in range(sk.get("pull_count", 1)):
            if t is not None and t.hp > 0:
                t.vx = -o.facing * 700
        o.fx_hook = 0.5

    def _c_throw(self, o, sk, t):
        if t is None or t.hp <= 0:
            return
        if abs(t.x - o.x) > 150:
            self.fx.append({"t": 0.5, "x": t.x, "y": t.y - 60,
                            "txt": "ÇOK UZAK", "col": (200, 200, 210)})
            return
        self.damage(t, sk.get("dmg", 20.0), o)
        w = self.fight.world_w if self.fight else 1000
        t.x = max(40.0, min(w - 40.0, t.x + o.facing * (w * 0.75)))
        t.vx = o.facing * 500
        t.vy = -700
        t.on_ground = False
        self.shake = max(self.shake, 16)

    def _c_grab(self, o, sk, t):
        if t is None or t.hp <= 0:
            return
        if abs(t.x - o.x) > sk.get("range", 200):
            self.fx.append({"t": 0.5, "x": t.x, "y": t.y - 60,
                            "txt": "ÇOK UZAK", "col": (200, 200, 210)})
            return
        t.grabbed = sk.get("grab_time", 3.0)
        t.grabbed_by = o
        if sk.get("chest"):
            t.in_chest = sk.get("grab_time", 5.0)
        if sk.get("dmg"):
            self.damage(t, sk["dmg"], o)

    def _c_summon(self, o, sk, t):
        n = sk.get("count", 3)
        unit = sk.get("unit", "toprak")
        for i in range(n):
            if unit == "iskelet_tank":
                hp, dmg, spd, rng = 200.0, 2.5, 70.0, False
            elif i % 5 == 4:
                hp, dmg, spd, rng = 30.0, 6.0, 90.0, True
            elif i % 2 == 0:
                hp, dmg, spd, rng = 15.0, 3.0, 80.0, True
            else:
                hp, dmg, spd, rng = 25.0, 5.0, 110.0, False
            m = Minion(o, o.x + o.facing * (40 + i * 26), o.y, hp, dmg, spd,
                       unit, rng)
            m.target = t
            self.minions.append(m)

    def _c_chase(self, o, sk, t):
        c = Chaser(o, sk)
        c.target = t
        self.chasers.append(c)

    def _c_revive(self, o, sk, t):
        o.arm_revive(sk.get("revive_hp", 50.0), sk.get("revive_time", 10.0))
        if sk.get("dmg_mult"):
            o.set_buff("dmg", 8.0, sk["dmg_mult"])
        if sk.get("speed_div"):
            o.set_buff("speed", 8.0, 1.0 / sk["speed_div"])

    def _c_steal_ability(self, o, sk, t):
        if t is None:
            return
        src = getattr(t, "skills", None)
        if not src:
            return
        new = list(src)[:3]
        o.stolen = new
        o.set_buff("dmg", 8.0, 0.5)

    def _charge_proj(self, o, sk, t, charge):
        d = dict(sk)
        tiers = sk.get("tiers")
        n = sk.get("count", 1)
        if tiers:
            i = min(len(tiers) - 1, int(charge))
            name, cnt, dm = tiers[i]
            n = cnt
            d["dmg"] = dm * o.dmg_mult()
            if sk.get("tier_range"):
                d["range"] = sk["tier_range"][i]
        else:
            step = sk.get("charge_step", 5.0)
            lvl = int(charge / step) if sk.get("unlimited_charge") else 0
            d["dmg"] = sk.get("dmg", 2.5) * o.dmg_mult() * (1.0 + 0.5 * lvl)
        d["count"] = n
        d.setdefault("spread", 0.10)
        d.setdefault("life", 1.4)
        self._c_proj(o, d, t)

    # ------------------------------------------------------------ guncelle
    def update(self, dt):
        self.time += dt
        self.shake = max(0.0, self.shake - dt * 40.0)
        for p in self.projs:
            if p.dead:
                continue
            p.life -= dt
            if p.life <= 0:
                p.dead = True
                continue
            if p.homing and p.target is not None and p.target.hp > 0:
                dx = p.target.x - p.x
                dy = (p.target.y - 44) - p.y
                L = math.hypot(dx, dy) or 1.0
                sp = math.hypot(p.vx, p.vy)
                p.vx += (dx / L) * p.homing * dt * 60
                p.vy += (dy / L) * p.homing * dt * 60
                L2 = math.hypot(p.vx, p.vy) or 1.0
                p.vx = p.vx / L2 * sp
                p.vy = p.vy / L2 * sp
            if p.gravity:
                p.vy += p.gravity * dt
            if p.ret:
                ox = p.owner_f.x
                dx = ox - p.x
                p.vx += (240 if dx > 0 else -240) * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.ang += dt * 9.0
            self._proj_hit(p)
        for z in self.zones:
            if z.dead:
                continue
            z.life -= dt
            if z.life <= 0:
                z.dead = True
                continue
            if z.follow and z.owner_f is not None:
                z.x = z.owner_f.x + z.owner_f.facing * 70
            if z.rep:
                z.rep_t -= dt
                if z.rep_t <= 0:
                    z.rep_t = z.rep
                    self._zone_hit(z)
            else:
                self._zone_hit(z)
        for b in self.beams:
            if b.dead:
                continue
            b.time -= dt
            b.t -= dt
            if b.time <= 0:
                b.dead = True
                continue
            if b.t <= 0:
                b.t = b.tick
                self._beam_hit(b)
        for w in self.walls:
            if w.dead:
                continue
            w.time -= dt
            if w.time <= 0:
                w.dead = True
                for i in range(max(1, w.spikes)):
                    self.projs.append(Projectile(
                        w.owner_f, w.x, w.y - 20,
                        (1 if w.owner_f.facing > 0 else -1) * w.wave,
                        -40 - i * 25,
                        {"dmg": w.spike_dmg, "life": 1.0, "size": 12,
                         "color": w.color, "speed": w.wave}))
                self.zones.append(Zone(w.owner_f, w.x + w.owner_f.facing * 60,
                                       w.y, {"zw": w.w * 2, "dmg": w.wave_dmg,
                                             "life": 0.9, "color": w.color}))
        for m in self.minions:
            if m.dead:
                continue
            m.life -= dt
            m.t += dt
            if m.life <= 0 or m.hp <= 0:
                m.dead = True
                continue
            tg = m.target if (m.target and m.target.hp > 0) else None
            if tg is None:
                continue
            dx = tg.x - m.x
            m.f = 1 if dx > 0 else -1
            want = 120 if m.ranged else 40
            if abs(dx) > want:
                m.x += m.f * m.speed * dt
            if abs(dx) < 260 and m.t > 0.8:
                m.t = 0.0
                self.damage(tg, m.dmg, m.o)
                if m.ranged:
                    self.projs.append(Projectile(m.o, m.x, m.y - 30,
                                                  m.f * 420, -20,
                                                  {"dmg": 0.0, "life": 0.5,
                                                   "size": 5, "color": (255, 230, 140)}))
        for c in self.chasers:
            if c.dead:
                continue
            c.life -= dt
            if c.life <= 0 or c.target is None or c.target.hp <= 0:
                c.dead = True
                continue
            dx = c.target.x - c.x
            c.x += (1 if dx > 0 else -1) * c.speed * dt
            c.tick -= dt
            if c.tick <= 0:
                c.tick = 0.35
                if abs(c.x - c.target.x) < c.size:
                    self.damage(c.target, c.dmg, c.o)
        for b in self.bursts:
            if b.dead:
                continue
            b.t += dt
            while b.t >= b.rate and b.ammo > 0:
                b.t -= b.rate
                b.ammo -= 1
                b.shot += 1
                sk = dict(b.sk)
                if b.half:
                    sk["dodge"] = "zıpla" if b.shot % 2 else "eğil"
                self.projs.append(Projectile(b.o, b.o.x + b.f * 26, b.o.y - 40,
                                              b.f * sk.get("speed", 700),
                                              -20, sk))
            if b.ammo <= 0:
                b.dead = True
        for f in self.fx:
            f["t"] -= dt
        self.fx = [f for f in self.fx if f["t"] > 0]
        self.projs = [p for p in self.projs if not p.dead]
        self.zones = [z for z in self.zones if not z.dead]
        self.beams = [b for b in self.beams if not b.dead]
        self.walls = [w for w in self.walls if not w.dead]
        self.minions = [m for m in self.minions if not m.dead]
        self.chasers = [c for c in self.chasers if not c.dead]
        self.bursts = [b for b in self.bursts if not b.dead]

    def _proj_hit(self, p):
        for t in self.targets():
            if t is p.owner_f or t.hp <= 0:
                continue
            if t.buff("phase") and not t.dead:
                continue
            if p.st and p.st.get("kind") == "phase":
                continue
            dx = t.x - p.x
            dy = (t.y - 40) - p.y
            hit_w = 26 + p.size
            hit_h = 74
            if abs(dx) < hit_w and -hit_h / 2 < dy < hit_h / 2:
                dodge = p.dodge
                if not self._dodge_ok(t, dodge):
                    p.dead = True
                    return
                if p.hits > 0 and p.dmg > 0:
                    self.damage(t, p.dmg, p.owner_f)
                    if p.lifesteal and p.owner_f is not None:
                        p.owner_f.heal(p.lifesteal)
                    if p.st:
                        self.apply_status(t, p.st)
                    p.hits -= 1
                if p.burst:
                    self._burst(p)
                p.dead = p.hits <= 0 and not p.pickup
                return
        if p.y > (self.fight.ground_y() if self.fight else 900) + 80:
            if p.burst:
                self._burst(p)
            p.dead = True

    def _burst(self, p):
        for t in self.targets():
            if t is p.owner_f or t.hp <= 0:
                continue
            if abs(t.x - p.x) < p.burst["r"]:
                self.damage(t, p.burst["dmg"], p.owner_f)
                if p.st:
                    self.apply_status(t, p.st)
        self.shake = max(self.shake, 10)

    def _zone_hit(self, z):
        for t in self.targets():
            if t is z.owner_f or t.hp <= 0:
                continue
            if abs(t.x - z.x) < z.w / 2.0 + 18:
                mode = z.dodge
                if z.half:
                    mode = z.half if z.shot % 2 == 0 else "zıpla"
                if not self._dodge_ok(t, mode):
                    continue
                if z.heal and t is z.owner_f:
                    t.heal(z.heal)
                    continue
                self.damage(t, z.dmg, z.owner_f)
                if z.st:
                    self.apply_status(t, z.st)
                if z.knock:
                    t.vx = z.owner_f.facing * z.knock
                    t.vy = -260
                    t.on_ground = False
                if z.push:
                    t.vx = z.owner_f.facing * z.push
                    t.vy = -140
                    t.on_ground = False

    def _beam_hit(self, b):
        o = b.o
        for t in self.targets():
            if t is o or t.hp <= 0:
                continue
            reach = b.ln if not b.no_limit else 1200.0
            if b.zw:
                reach = b.zw
            dx = (t.x - o.x) * o.facing
            if -20 < dx < reach:
                self.damage(t, b.dmg, o)
                if b.st:
                    self.apply_status(t, b.st)

    # ------------------------------------------------------------ cizim
    def draw(self, surf, cam):
        ox, oy, z = cam.x, cam.y, 1.0

        def tx(x):
            return int((x - ox) * z)

        def ty(y):
            return int((y - oy) * z)

        for z2 in self.zones:
            k = max(0.0, min(1.0, z2.life / max(0.01, z2.max_life)))
            r = pygame.Rect(tx(z2.x - z2.w / 2), ty(z2.y - 10),
                            max(2, int(z2.w * z)), max(3, int(16 * z)))
            layer = pygame.Surface((max(2, r.w), max(3, r.h)), pygame.SRCALPHA)
            a = int(90 * k)
            pygame.draw.ellipse(layer, (z2.color[0], z2.color[1], z2.color[2], a),
                                layer.get_rect())
            surf.blit(layer, r.topleft)
            pygame.draw.ellipse(surf, z2.color, r, 2)
        for w in self.walls:
            r = pygame.Rect(tx(w.x - w.w / 2), ty(w.y - w.h),
                            max(2, int(w.w * z)), max(3, int(w.h * z)))
            pygame.draw.rect(surf, w.color, r, border_radius=4)
            pygame.draw.rect(surf, (255, 255, 255), r, 2, border_radius=4)
        for p in self.projs:
            x, y = tx(p.x), ty(p.y)
            s = max(2, int(p.size * z))
            if p.spark:
                pygame.draw.circle(surf, p.color, (x, y), s)
                pygame.draw.line(surf, (255, 255, 255),
                                 (x - p.owner_f.facing * s * 3, y),
                                 (x, y), 2)
            elif p.glow:
                g = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
                pygame.draw.circle(g, (p.color[0], p.color[1], p.color[2], 90),
                                   (s * 2, s * 2), s * 2)
                surf.blit(g, (x - s * 2, y - s * 2))
                pygame.draw.circle(surf, p.color, (x, y), s)
            elif p.spin:
                pygame.draw.rect(surf, p.color,
                                 pygame.Rect(x - s, y - s, s * 2, s * 2), 2)
                pygame.draw.line(surf, p.color, (x - s, y), (x + s, y), 2)
            else:
                pygame.draw.circle(surf, p.color, (x, y), s)
                pygame.draw.circle(surf, (255, 255, 255), (x, y), max(1, s // 3))
        for b in self.beams:
            o = b.o
            x0, y0 = tx(o.x), ty(o.y - 44)
            L = int((1200.0 if b.no_limit else b.ln) * z)
            x1 = x0 + o.facing * L
            k = max(0.0, min(1.0, b.time / max(0.01, b.max_time)))
            lay = pygame.Surface((abs(x1 - x0) + 6, 16), pygame.SRCALPHA)
            col = b.color
            for i in range(4):
                a = int((200 - i * 45) * k)
                pygame.draw.line(lay, (col[0], col[1], col[2], a),
                                 (0, 8), (abs(x1 - x0), 8), 4 - i)
            sx = min(x0, x1)
            surf.blit(lay, (sx - 3, y0 - 8))
            pygame.draw.circle(surf, col, (x0, y0), max(3, int(7 * z)))
        for m in self.minions:
            x, y = tx(m.x), ty(m.y)
            s = max(3, int(14 * z))
            col = (120, 200, 90) if m.unit == "iskelet_tank" else (150, 110, 70)
            if m.unit == "iskelet_tank":
                col = (225, 225, 210)
            pygame.draw.rect(surf, col, (x - s // 2, y - s * 2, s, s * 2))
            pygame.draw.circle(surf, col, (x, y - s * 2 - s // 2), s // 2)
            pygame.draw.rect(surf, (255, 255, 255),
                             (x - s // 2, y - s * 6, s, 2))
        for c in self.chasers:
            x, y = tx(c.x), ty(c.y)
            s = max(4, int(c.size * z))
            layer = pygame.Surface((s * 2, s), pygame.SRCALPHA)
            pygame.draw.ellipse(layer, (c.color[0], c.color[1], c.color[2], 170),
                                layer.get_rect())
            surf.blit(layer, (x - s, y - s // 2))
            pygame.draw.ellipse(surf, c.color, (x - s, y - s // 2, s * 2, s), 2)
        for f in self.fx:
            a = max(0.0, min(1.0, f["t"] / 0.45))
            col = f["col"]
            surf.blit(pygame.font.SysFont("segoeui", 20, True).render(
                f["txt"], True, (col[0], col[1], col[2])), (tx(f["x"]) - 20,
                                                             ty(f["y"]) - 20))