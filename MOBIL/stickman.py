import math
import pygame
import chars
from classes import SKILLS, CLASS_BY_ID
from settings import *


class Stickman:
    def __init__(self, char_def, color, x, y, facing):
        self.defn = char_def
        self.color = color
        self.base_speed = char_def["speed"]
        self.hp = float(char_def["hp"])
        self.max_hp = char_def["hp"]
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = facing
        self.on_ground = True
        self.crouching = False
        self.moving = False
        self.walk_phase = 0.0
        self.cooldowns = [0.0] * 3
        self.attack = None
        self.hit_timer = 0.0
        self.ult_pct = 0.0
        self.ult_timer = 0.0
        self.solids = []
        self.land_solids = []
        self.on_wall = False
        self._wall_top = None
        self._wall_side = None
        self.nose = False
        self.drown_t = 0.0
        self.chair = False
        self.chair_t = 0.0
        self.floor_y = float(GROUND_Y)
        self.inv = {}
        self.world_w = WORLD_W
        # --- sinif / yetenek sistemi
        self.cls = char_def.get("class_def")
        self.skills = list(self.cls["abilities"]) if self.cls else list(
            char_def.get("abilities", []))
        self.ult_skill = self.cls["ult"] if self.cls else None
        self.level = 0
        self.levels = self.cls.get("levels") if self.cls else None
        self.tier = 0
        self.st = {}
        self.buffs = {}
        self.eng = None
        self.opp = None
        self.ability_uses = 0
        self.use_count = [0, 0, 0]
        self.grabbed = 0.0
        self.grabbed_by = None
        self.in_chest = 0.0
        self.fx_hook = 0.0
        self.stolen = None
        self.shield = float(self.cls["shield"]) if self.cls else 0.0
        self.max_shield = self.shield
        self.revive = None
        self.dmg_loss = 0.0
        self.limb_loss = 0.0
        self.bob_extra = 0.0
        self.hit_src = None
        self.hit_src_t = 0.0
        self.stunned_t = 0.0

    @property
    def rect(self):
        h = CROUCH_H if self.crouching else STAND_H
        return pygame.Rect(int(self.x - 18), int(self.y - h), 36, int(h))

    def speed(self):
        m = ULT_MULT if self.ult_timer > 0 else 1.0
        if self.buff("speed"):
            m *= max(0.05, self.buff_val("speed"))
        if self.buff("slow"):
            m *= max(0.05, self.buff_val("slow"))
        if self.st.get("slow"):
            m *= max(0.05, 1.0 - self.st["slow"]["power"])
        if self.st.get("weak"):
            m *= max(0.05, 1.0 - self.st["weak"]["power"])
        if self.buff("all5"):
            m *= self.buff_val("all5")
        return self.base_speed * m

    def ult_info(self, opp):
        if self.ult_timer > 0:
            return ("active", 1.0)
        pct = min(100.0, self.ult_pct)
        return ("ready" if pct >= 100.0 else "charging", pct / 100.0)

    def ult_ready(self):
        return self.ult_pct >= 100.0

    def gain_ult(self, pct):
        self.ult_pct = min(100.0, self.ult_pct + pct)

    def try_ult(self, opp):
        if self.hit_timer > 0 or self.hp <= 0 or not self.ult_ready():
            return False
        self.ult_timer = ULT_TIME
        self.ult_pct = 0.0
        if self.eng is not None and self.ult_skill:
            sk = SKILLS.get(self.ult_skill)
            if sk is not None:
                self.eng.cast(self, sk, opp or self.opp, 0.0)
        if self.levels and self.level + 1 < len(self.levels):
            self.level += 1
            self._apply_level()
        elif not self.levels and self.ult_skill == "st_ult":
            self.level_up_tier(0)
        return True

    # ---------------------------------------------------- sinif yardimcilari
    def buff(self, key):
        return key in self.buffs and self.buffs[key]["t"] > 0

    def buff_val(self, key):
        b = self.buffs.get(key)
        return b["v"] if b and b["t"] > 0 else 0.0

    def set_buff(self, key, t, v=1.0):
        if t <= 0:
            self.buffs.pop(key, None)
            return
        b = self.buffs.get(key)
        if b is None:
            self.buffs[key] = {"t": t, "v": v}
        else:
            b["t"] = max(b["t"], t)
            if v:
                b["v"] = v

    def dmg_mult(self):
        m = 1.0
        if self.buff("dmg"):
            m *= max(0.1, self.buff_val("dmg"))
        if self.buff("all5"):
            m *= self.buff_val("all5")
        if self.buff("sword"):
            m *= max(1.0, self.buff_val("sword") / 10.0)
        if self.buff("tier"):
            m *= 1.0 + 0.15 * self.tier
        return m * (ULT_MULT if self.ult_timer > 0 else 1.0)

    def dmg_taken_mult(self):
        m = 1.0
        if self.buff("shield"):
            m *= max(0.05, self.buff_val("shield"))
        if self.buff("dmg_half"):
            m *= 0.5
        return m

    def heal(self, n):
        if n <= 0 or self.hp <= 0:
            return
        self.hp = min(self.max_hp, self.hp + n)

    def gain_max_hp(self, n):
        self.max_hp += n
        self.hp += n

    def gain_shield(self, n):
        self.shield = min(self.max_shield, self.shield + n)

    def absorb(self, dmg):
        if self.shield <= 0:
            return 0.0
        used = min(self.shield, dmg)
        self.shield -= used
        if self.shield <= 0:
            self.buffs.pop("shield", None)
        return used

    def fx_col(self):
        return (255, 235, 160) if self.cls else (255, 220, 220)

    def teleport(self, d):
        if self.eng is not None and self.eng.fight is not None:
            w = self.eng.fight.world_w
        else:
            w = self.world_w
        self.x = max(40.0, min(w - 40.0, self.x + d))

    def arm_revive(self, hp, time):
        self.revive = {"hp": hp, "t": time}

    def level_up_tier(self, n):
        self.tier += 1

    def _level_def(self):
        if self.levels and self.level < len(self.levels):
            return self.levels[self.level]
        return self.cls

    def on_damaged(self, dmg, src):
        self.dmg_loss += dmg
        if src is not None:
            self.hit_src = src
            self.hit_src_t = 4.0
        if self.buff("reflect") and self.eng is not None:
            pass
        if self.cls and self.eng is not None:
            self.eng.cast_passive(self, src)

    def on_death(self, src):
        if self.revive is not None:
            self.hp = self.revive["hp"]
            self.max_hp = max(self.max_hp, self.revive["hp"])
            self.revive = None
            self.hit_timer = 0.0
            self.vx = 0.0
            self.vy = 0.0
            self.buffs.pop("shield", None)
            self.shield = 0.0
            return
        if self.levels and self.level + 1 < len(self.levels):
            self.level -= 1
            self._apply_level()
            return
        if self.levels and self.level >= 0:
            self.level = -1
        self.hp = 0.0

    def _apply_level(self):
        d = self._level_def()
        if not d:
            return
        self.max_hp = d.get("hp", self.max_hp)
        self.hp = self.max_hp
        self.max_shield = d.get("shield", 0.0)
        self.shield = self.max_shield
        self.skills = list(d["abilities"])
        self.ult_skill = d.get("ult")
        for i in range(3):
            self.cooldowns[i] = 0.0

    def _tick_class(self, dt):
        # kalkan azalması
        for key in list(self.buffs):
            b = self.buffs[key]
            b["t"] -= dt
            if b["t"] <= 0:
                del self.buffs[key]
        # durum etkileri
        for key in list(self.st):
            s = self.st[key]
            s["t"] -= dt
            if s["t"] <= 0:
                del self.st[key]
                continue
            if s["dps"] > 0:
                self.hp = max(0.0, self.hp - s["dps"] * dt)
                if self.eng is not None:
                    self.eng.damage(self, 0.0, None)
        if self.grabbed > 0:
            self.grabbed = max(0.0, self.grabbed - dt)
            self.vx = 0.0
        if self.in_chest > 0:
            self.in_chest = max(0.0, self.in_chest - dt)
            if self.eng is not None:
                self.eng.damage(self, 15.0 * dt, self.grabbed_by)
        if self.fx_hook > 0:
            self.fx_hook = max(0.0, self.fx_hook - dt)
        if self.hit_src_t > 0:
            self.hit_src_t = max(0.0, self.hit_src_t - dt)
        if self.stunned_t > 0:
            self.stunned_t = max(0.0, self.stunned_t - dt)
            self.set_buff("stun", self.stunned_t)
        if self.revive is not None:
            self.revive["t"] -= dt
            if self.revive["t"] <= 0:
                self.revive = None

    def take_hit(self, dmg, direction):
        if self.hp <= 0 or self.buff("immune"):
            return False
        if self.grabbed > 0:
            return False
        if self.eng is not None:
            self.eng.damage(self, dmg, self.hit_src)
        else:
            self.hp = max(0.0, self.hp - dmg)
            self.on_damaged(dmg, self.hit_src)
        self.hit_timer = 0.14
        self.vx = direction * 120.0
        self.vy = -90.0
        if self.hp <= 0:
            self.on_death(self.hit_src)
        return True

    def update(self, dt, inp, opp):
        if self.hp <= 0:
            return
        self.opp = opp
        self._tick_class(dt)
        self.ult_pct = min(100.0, self.ult_pct + ULT_FILL_RATE * dt)
        self._tick_timers(dt)
        stunned = self.buff("stun") or bool(self.st.get("stun"))
        if self.st.get("ai"):
            inp = self._ai_input(dt)
        if self.grabbed > 0 or self.in_chest > 0:
            inp = self._neutral_input()
        if stunned:
            inp = self._neutral_input()
        if self.attack is None:
            if inp.left and not inp.right:
                self.facing = -1
            elif inp.right and not inp.left:
                self.facing = 1
        abilities = self.defn["abilities"]
        if inp.ability1_pressed:
            self._press(abilities[0], 0)
        if inp.ability2_pressed:
            self._press(abilities[1], 1)
        if inp.ability3_pressed:
            self._press(abilities[2], 2)
        if inp.ult_pressed:
            self.try_ult(opp)
        if self.attack is not None:
            self._update_attack(dt, opp)
        if self.hit_timer > 0:
            self.vx *= 0.8
        else:
            self.vx = 0.0
            if self.attack is None and not self.on_wall:
                if inp.left and not inp.crouch:
                    self.vx = -self.speed()
                elif inp.right and not inp.crouch:
                    self.vx = self.speed()
                if inp.jump_pressed and self.on_ground and not inp.crouch:
                    self.vy = -JUMP_SPEED
                    self.on_ground = False
        self.crouching = bool(inp.crouch and self.on_ground and self.attack is None)
        self._physics(dt, inp)
        self.x = max(20.0, min(self.world_w - 20.0, self.x))
        self.moving = self.on_ground and abs(self.vx) > 1
        if self.moving:
            self.walk_phase += abs(self.vx) * dt * 0.05

    def _physics(self, dt, inp):
        was_wall = self.on_wall
        was_side = self._wall_side
        self.x += self.vx * dt
        self._clip_walls()
        self.on_wall = False
        self._wall_top = None
        self._wall_side = None
        skip_fall = False
        near = None
        if was_wall and inp.jump_pressed and self.hit_timer <= 0:
            away = 1 if was_side == "right" else -1
            self.vx = away * self.speed()
            self.vy = -JUMP_SPEED
        else:
            near = self._near_wall()
            if near is not None and not self.on_ground and self.hit_timer <= 0:
                side, top = near
                toward = (side == "right" and inp.left) or (side == "left" and inp.right)
                if toward and not self.crouching:
                    self.on_wall = True
                    self._wall_top = top
                    self._wall_side = side
                    self.vx = 0.0
                    if inp.jump:
                        if self.y <= top + 2:
                            self.y = float(top)
                            self.vy = 0.0
                            self.on_wall = False
                            self.on_ground = True
                            skip_fall = True
                        else:
                            self.vy = -CLIMB_SPEED
                            self.y += self.vy * dt
                    else:
                        self.vy = 0.0
        if not self.on_wall and not skip_fall:
            self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
            prev = self.y
            self.y += self.vy * dt
            self._land(prev)

    def _neutral_input(self):
        class _N:
            left = right = False
            jump = crouch = False
            ability1_pressed = ability2_pressed = ability3_pressed = False
            ult_pressed = False
            ability1_held = ability2_held = ability3_held = False
            drop = False
            use = False
            jump_pressed = False
            jump_held = False
            attack_pressed = False
        return _N()

    def _ai_input(self, dt=0.0):
        o = self.opp
        if o is None:
            return self._neutral_input()
        d = o.x - self.x
        f = 1 if d > 0 else -1
        near = abs(d) < 90

        class _I:
            jump = False
            crouch = False
            ability1_pressed = ability2_pressed = ability3_pressed = False
            ult_pressed = False
            ability1_held = ability2_held = ability3_held = False
            drop = False
            use = False
            jump_pressed = False
            jump_held = False
            attack_pressed = False

        i = _I()
        if near:
            i.left = d < -30
            i.right = d > 30
            i.ability1_pressed = True
        else:
            i.right = d > 0
            i.left = d < 0
            i.ability2_pressed = True
        return i

    def _body(self):
        h = CROUCH_H if self.crouching else STAND_H
        return pygame.Rect(int(self.x - 18), int(self.y - h), 36, h)

    def _clip_walls(self):
        body = self._body()
        for s in self.solids:
            if not (body.top < s.bottom - 4 and body.bottom > s.top + 4):
                continue
            if body.right > s.left and body.left < s.right:
                if body.centerx <= s.centerx:
                    self.x = s.left - 18.0
                else:
                    self.x = s.right + 18.0

    def _near_wall(self):
        body = self._body()
        for s in self.solids:
            if not (body.top < s.bottom - 4 and body.bottom > s.top + 8):
                continue
            if abs(body.right - s.left) <= 4 and body.right - 2 <= s.left:
                return ("left", s.top)
            if abs(body.left - s.right) <= 4 and body.left + 2 >= s.right:
                return ("right", s.top)
        return None

    def _land(self, prev):
        self.on_ground = False
        if self.vy >= 0:
            best = None
            for s in list(self.solids) + list(self.land_solids):
                body = self._body()
                if body.right > s.left + 3 and body.left < s.right - 3 and \
                        self.y >= s.top and prev <= s.top + 1:
                    if best is None or s.top > best:
                        best = s.top
            if best is not None:
                self.y = float(best)
                self.vy = 0.0
                self.on_ground = True
                self.on_wall = False
                return
        if self.floor_y is not None and self.y >= self.floor_y:
            self.y = float(self.floor_y)
            self.vy = 0.0
            self.on_ground = True
            self.on_wall = False

    def _press(self, key, idx):
        if self.hit_timer > 0 or self.buff("stun") or self.st.get("stun"):
            return
        if self.grabbed > 0:
            return
        sk = self.skills[idx] if idx < len(self.skills) else None
        if sk and sk in SKILLS:
            if self.cooldowns[idx] > 0 or self.attack is not None:
                return
            d = SKILLS[sk]
            self.cooldowns[idx] = self.skill_cd(d)
            self.use_count[idx] += 1
            if self.eng is None:
                return
            self.eng.cast(self, d, self.opp, 0.0)
            if d.get("kind") in ("melee", "charge_melee"):
                m = dict(d)
                m.setdefault("hit0", 0.08)
                m.setdefault("hit1", 0.20)
                m.setdefault("dur", 0.32)
                self.attack = {"def": m, "timer": 0.0, "hit": False}
            return
        if self.attack is not None or self.crouching:
            return
        slot = ABILITIES.get(key)
        if slot is None or self.cooldowns[idx] > 0:
            return
        self.cooldowns[idx] = slot["cd"]
        self.attack = {"def": slot, "timer": 0.0, "hit": False}

    def skill_cd(self, d):
        cd = d.get("cd", 1.0)
        if d.get("base_cd"):
            cd = d["base_cd"]
        if self.buff("cd2"):
            cd *= 2.0
        if self.buff("haste"):
            cd *= 1.0 / max(0.1, self.buff_val("haste"))
        return cd

    def _tick_timers(self, dt):
        for i in range(3):
            if self.cooldowns[i] > 0:
                self.cooldowns[i] = max(0.0, self.cooldowns[i] - dt)
        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)
        if self.ult_timer > 0:
            self.ult_timer = max(0.0, self.ult_timer - dt)

    def _update_attack(self, dt, opp):
        a = self.attack
        a["timer"] += dt
        d = a["def"]
        if not a["hit"] and d["hit0"] <= a["timer"] <= d["hit1"]:
            hb = self._hitbox(d)
            if hb.colliderect(opp.rect):
                dmg = d["dmg"] * (ULT_MULT if self.ult_timer > 0 else 1.0)
                if opp.take_hit(dmg, self.facing):
                    a["hit"] = True
                    self.gain_ult(ULT_HIT_BONUS)
        if a["timer"] >= d["dur"]:
            self.attack = None

    def _hitbox(self, d):
        x0 = self.x + self.facing * 8
        x1 = x0 + self.facing * d["range"]
        return pygame.Rect(int(min(x0, x1)), int(self.y - d["ytop"]), int(abs(x1 - x0)), d["h"])

    def _arm(self, shoulder, hand, off):
        sx, sy = shoulder
        hx, hy = hand
        dx, dy = hx - sx, hy - sy
        L = math.hypot(dx, dy) or 1.0
        px, py = -dy / L, dx / L
        ex = (sx + hx) / 2 + px * off
        ey = (sy + hy) / 2 + py * off
        return [((sx, sy), (ex, ey)), ((ex, ey), (hx, hy))]

    def _attack_progress(self, d, t):
        dur = max(0.001, d["dur"])
        p = t / dur
        if p < 0.22:
            r = 0.0
        elif p < 0.52:
            r = (p - 0.22) / 0.30
        elif p < 0.78:
            r = 1.0
        else:
            r = max(0.0, (1.0 - p) / 0.22)
        return r

    def _joints(self):
        segs = []
        fists = []
        crouch = self.crouching
        bob = 0.0
        hip_y = -16 if crouch else -30
        sho_y = hip_y - 24
        lean = 0.0
        hip = (0, hip_y)

        if crouch:
            sho = (0, sho_y)
            head = (0, sho_y - 9)
            segs.append((hip, sho))
            segs += [((-9, hip_y), (-6, -10)), ((-6, -10), (-12, 0)),
                     ((9, hip_y), (6, -10)), ((6, -10), (12, 0))]
            hf = (8, hip_y + 2)
            hb = (-9, hip_y)
            segs += self._arm(sho, hf, 5)
            segs += self._arm(sho, hb, 5)
            fists = [hf, hb]
        elif self.attack is not None:
            d = self.attack["def"]
            r = self._attack_progress(d, self.attack["timer"])
            pose = d["pose"]
            reach = int(16 + r * (d["range"] + 12))
            lean = r * 6
            sho = (int(lean), sho_y)
            head = (int(lean), sho_y - 9)
            segs.append((hip, sho))
            if pose == "kick":
                knee = (int(8 + r * d["range"] * 0.5), int(-16 - (1 - r) * 8))
                foot = (reach, -12)
                segs += [((0, hip_y), knee), (knee, foot), ((0, hip_y), (-11, 0))]
                hf = (7, -34)
                hb = (-9, -32)
                segs += self._arm(sho, hf, 7)
                segs += self._arm(sho, hb, 7)
                fists = [hf, hb]
            else:
                if pose == "combo":
                    knee = (int(9 + r * d["range"] * 0.5), int(-16 - (1 - r) * 8))
                    foot = (reach, -12)
                    leg_segs = [((0, hip_y), knee), (knee, foot), ((0, hip_y), (-9, 0))]
                else:
                    leg_segs = [((0, hip_y), (-8, 0)), ((0, hip_y), (int(4 + r * 8), 0))]
                segs += leg_segs
                hf = (int(lean) + 12 + int(r * (d["range"] + 14)), sho_y + 10)
                hb = (-11, -30)
                segs += self._arm(sho, hf, 12 * (1 - r) + 3)
                segs += self._arm(sho, hb, 6)
                fists = [hf, hb]
        elif not self.on_ground:
            sho = (0, sho_y)
            head = (0, sho_y - 9)
            segs.append((hip, sho))
            # Zıplama: ön görünüm - her iki bacak önde, kolları yukarı
            segs += [((0, hip_y), (-10, -10)), ((0, hip_y), (10, -10))]
            hf = (0, -40)
            hb = (0, -40)
            segs += self._arm(sho, hf, 8)
            segs += self._arm(sho, hb, 8)
            fists = [hf, hb]
        elif self.moving:
            s = math.sin(self.walk_phase)
            lift_a = max(0.0, s) * 13
            lift_b = max(0.0, -s) * 13
            sho = (0, sho_y)
            head = (0, sho_y - 9)
            bob = -abs(math.cos(self.walk_phase)) * 2
            segs.append((hip, sho))
            segs += [((0, hip_y), (-8 + 7 * s, -lift_a)), ((0, hip_y), (8 - 7 * s, -lift_b))]
            hf = (6 - 9 * s, -30)
            hb = (-6 + 9 * s, -30)
            segs += self._arm(sho, hf, 6)
            segs += self._arm(sho, hb, 6)
            fists = [hf, hb]
        else:
            sho = (0, sho_y)
            head = (0, sho_y - 9)
            segs.append((hip, sho))
            segs += [((0, hip_y), (-8, 0)), ((0, hip_y), (9, 0))]
            hf = (9, -28)
            hb = (-10, -28)
            segs += self._arm(sho, hf, 7)
            segs += self._arm(sho, hb, 7)
            fists = [hf, hb]
        return segs, fists, head, bob

    def draw(self, surf, cam_x, cam_y):
        if self.hp <= 0:
            self._draw_dead(surf, cam_x, cam_y)
            return
        cx = int(self.x - cam_x)
        cy = int(self.y - cam_y)
        f = self.facing
        flash = 0.22 if self.hit_timer > 0 else 0.0
        col = (255, 255, 255) if flash else self.color
        pose = "idle"
        r = 0.0
        if self.hit_timer > 0:
            pose = "hurt"
        elif self.attack is not None:
            pose = self.attack["def"]["pose"]
            r = self._attack_progress(self.attack["def"], self.attack["timer"])
        elif not self.on_ground:
            pose = "jump"
        elif self.crouching:
            pose = "crouch"
        elif self.moving:
            pose = "walk"
        chars.draw_stickman(surf, cx, cy, 1.0, col, f, pose, self.walk_phase,
                           flash=flash, ult=self.ult_ready(),
                           ult_active=self.ult_timer > 0, r=r,
                           ground=self.on_ground)

    def _s(self, cx, cy, f, p):
        return (cx + int(p[0] * f), cy + int(p[1]))

    def _draw_dead(self, surf, cam_x, cam_y):
        cx = int(self.x - cam_x)
        cy = int(self.y - cam_y)
        f = self.facing
        col = self.color
        pts = [((-6, -2), (10, 1)), ((-6, -2), (0, 10)), ((0, -12), (-18, -14)),
               ((0, -12), (8, -20)), ((0, -12), (-12, -6))]
        for p0, p1 in pts:
            pygame.draw.line(surf, col, self._s(cx, cy, f, p0), self._s(cx, cy, f, p1), 3)
        pygame.draw.circle(surf, col, self._s(cx, cy, f, (-24, -10)), 8)