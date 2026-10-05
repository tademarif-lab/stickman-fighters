import math
import random
import pygame
from types import SimpleNamespace
import maps
import chars
from settings import *
from skills import SkillEngine
import settings
from stickman import Stickman
from hud import HUD

JOHNNY_CMDS = ["EĞİL!", "ZIPLA!", "SAĞA KAÇ!", "SOLA KAÇ!", "DUR!", "VUR!"]


class Camera:
    def __init__(self, vpw, vph, world_w=WORLD_W, world_h=WORLD_H):
        self.vw = max(1, vpw)
        self.vh = max(1, vph)
        self.x = 0.0
        self.y = 0.0
        self.world_w = world_w
        self.world_h = world_h

    def _target(self, cx, cy):
        tx = cx - self.vw / 2
        ty = cy - self.vh / 2
        if self.vw >= self.world_w:
            tx = (self.world_w - self.vw) / 2
        else:
            tx = max(0.0, min(self.world_w - self.vw, tx))
        if self.vh >= self.world_h:
            ty = (self.world_h - self.vh) / 2
        else:
            ty = max(0.0, min(self.world_h - self.vh, ty))
        return tx, ty

    def center(self, x, y):
        self.x, self.y = self._target(x, y)

    def update(self, a, b, dt):
        tx, ty = self._target((a.x + b.x) / 2, (a.y + b.y) / 2)
        k = min(1.0, dt * 6.0)
        self.x += (tx - self.x) * k
        self.y += (ty - self.y) * k


class Villager(Stickman):
    def take_hit(self, dmg, direction):
        self.hit_timer = 0.14
        return True


class Fight:
    def __init__(self, chars, colors, map_id, cam_x, cam_y=None):
        self.map_id = map_id
        self.map = maps.MAP_OBJECTS[map_id]()
        self.zoom = CITY_ZOOM if map_id == "city" else FOOT_ZOOM if map_id == "football" else LR_ZOOM if map_id == "laserrun" else 1.0
        self.p1 = Stickman(chars[0], colors[0], 300, GROUND_Y, 1)
        self.p2 = Stickman(chars[1], colors[1], 700, GROUND_Y, -1)
        self._place_players()
        for p in (self.p1, self.p2):
            p.world_w = self.map.w
        self.p1.solids = self.map.solids
        self.p2.solids = self.map.solids
        self.villagers = []
        if map_id == "village":
            self._spawn_villagers()
        self.projectiles = []
        self.trucks = []
        self.truck_t = TRUCK_GAP * 0.5
        self.truck_n = 0
        self.house_crouch = 0.0
        self.stalagmites = []
        self.boss_splashes = []
        self.boss_webs = []
        self.boss_tele = []
        self.dragon = None
        self.dragon_fire_t = 0.0
        self.dragon_target = None
        self.dragon_target_t = 0.0
        self.crystal = None
        self.crystal_delay = 0.0
        self.mine_stage = "normal"
        self.mine_a1 = [False, False]
        self.mine_a2 = [False, False]
        self.mine_dead_delay = None
        self.mobs = []
        self.blaze_balls = []
        self.craft_open = False
        self.craft_owner = 1
        self.craft_sel = [0, 0]
        self.craft_inv_sel = 0
        self.craft_rep = 0.0
        self.craft_grid = [None] * 9
        self.craft_out = None
        self.craft_cursor = None
        self.craft_inv_scroll = 0
        self._craft_saved = None
        self._saved_portal = None
        self.portal_t = 0.0
        self._respawn_mine_mobs()
        self.johnny = {"next": 2.0, "win_end": None, "phase": "wait",
                       "counted": [False, False], "scores": [0, 0], "dead": False,
                       "cmd": 0}
        self.split = False
        self.cam = self._mk_cam(SCREEN_W, SCREEN_H)
        self.cam1 = self._mk_cam(SCREEN_W // 2, SCREEN_H)
        self.cam2 = self._mk_cam(SCREEN_W // 2, SCREEN_H)
        if cam_y is None:
            cam_y = GROUND_Y - SCREEN_H * 0.45
        self.cam.center(cam_x, cam_y)
        self.winner = None
        self.hud = HUD()
        self.t = 0.0
        self.fx = []
        self.inp1 = None
        self.inp2 = None
        # yeni oyun modları: zombi survival / football / boss fights
        self.zombie = {"wave": 0, "t": 2.0, "kills": [0, 0]}
        self.boss = None
        self.boss_id = 0
        self.boss_next_t = 1.0
        self.foot_state = None
        self.foot_kick = [False, False, False, False]
        self.lr_state = None
        self.coins = []
        self.notice = None
        self.world_w = self.map.w
        self.eng = SkillEngine()
        self.eng.bind(self)
        if map_id == "zombi":
            self._zombie_start_wave()
        if map_id == "boss":
            self._start_boss()
        if map_id == "football":
            self.foot_state = {
                "score": [0, 0],
                "ball": {"x": 500.0, "y": float(GROUND_Y - FOOT_BALL_R),
                         "vx": 0.0, "vy": 0.0},
                "cd": [0.0, 0.0],
            }
        if map_id == "laserrun":
            self.lr_state = {
                "blocks": [],
                "spawn_t": 0.0,
                "time": 0.0,
                "dead": [False, False],
            }

    def ground_y(self):
        return float(getattr(self.map, "ground_y", GROUND_Y))

    def _mk_cam(self, vpw, vph):
        return Camera(int(round(vpw / self.zoom)), int(round(vph / self.zoom)),
                      self.map.w, getattr(self.map, "world_h", WORLD_H))

    def _place_players(self):
        if self.map_id == "city":
            self.p1.x = float(self.map.buildings[2].centerx)
            self.p2.x = float(self.map.buildings[6].centerx)
            self.p1.y = float(self.map.buildings[2].top)
            self.p2.y = float(self.map.buildings[6].top)
            self.p1.floor_y = None
            self.p2.floor_y = None
        elif self.map_id == "village":
            self.p1.x = 500.0
            self.p2.x = 960.0
        elif self.map_id == "minestick":
            self.p1.x = 40.0
            self.p2.x = 175.0
            self.p1.floor_y = None
            self.p2.floor_y = None
        elif self.map_id == "house":
            self.p1.x = 260.0
            self.p2.x = 760.0
        elif self.map_id == "laserrun":
            self.p1.x = 150.0
            self.p2.x = 250.0
            self.p1.y = float(self.map.platform.top - STAND_H)
            self.p2.y = float(self.map.platform.top - STAND_H)
            self.p1.floor_y = self.map.platform.top
            self.p2.floor_y = self.map.platform.top
            self.p1.on_ground = True
            self.p2.on_ground = True

    def _spawn_villagers(self):
        vdef = {"id": "villager", "name": "KÖYLÜ", "hp": 1, "speed": 100.0,
                "info": "Köylü", "abilities": ["villpunch"],
                "adesc": ["Köylü Yumruğu: 1"]}
        for i, x in enumerate((470, 520, 620, 640, 930)):
            v = Villager(vdef, VILLAGER_COLORS[i], x, GROUND_Y, 1)
            v.solids = self.map.solids
            v.nose = True
            v.aggro = None
            v.aggro_t = 0.0
            v.attack_started = False
            v.roam_dir = 1 if i % 2 == 0 else -1
            v.roam_t = 1.2 + i
            self.villagers.append(v)

    def update(self, dt, inp1, inp2):
        self.t += dt
        self.inp1, self.inp2 = inp1, inp2
        if self.winner is not None:
            self._tick_fx(dt)
            self.eng.update(dt)
            self._move_projectiles(dt)
            return
        hp1, hp2 = self.p1.hp, self.p2.hp
        self._craft_intercept(inp1, inp2)
        self._chair_throw(dt)
        self.foot_kick = [False, False, False, False]
        if self.map_id == "football":
            self.foot_kick = [inp1.ability1_pressed, inp1.ability2_pressed,
                              inp2.ability1_pressed, inp2.ability2_pressed]
            inp1.ability1_pressed = inp1.ability2_pressed = inp1.ult_pressed = False
            inp2.ability1_pressed = inp2.ability2_pressed = inp2.ult_pressed = False
        pb1x, pb1body = self.p1.x, self.p1._body()
        pb2x, pb2body = self.p2.x, self.p2._body()
        self.p1.solids = self.map.solids
        self.p1.land_solids = [self.p2._body()]
        self.p1.update(dt, inp1, self.p2)
        self.p2.solids = self.map.solids
        self.p2.land_solids = [self.p1._body()]
        self.p2.update(dt, inp2, self.p1)
        self._ride(self.p1, self.p2, pb2x, pb2body, inp1)
        self._ride(self.p2, self.p1, pb1x, pb1body, inp2)
        self._craft_restore()
        if hp1 > self.p1.hp:
            self._add_fx(self.p1, hp1 - self.p1.hp, self.p2)
        if hp2 > self.p2.hp:
            self._add_fx(self.p2, hp2 - self.p2.hp, self.p1)
        self._separate()
        self.eng.update(dt)
        self._villager_phase(dt)
        self._map_specific(dt)
        self._move_projectiles(dt)
        self._split_update(dt)
        if self.winner is None:
            if self.map_id not in ("zombi", "football", "boss"):
                if self.p1.hp <= 0:
                    self.winner = 2
                elif self.p2.hp <= 0:
                    self.winner = 1
        self._tick_fx(dt)

    def _split_update(self, dt):
        dx = abs(self.p1.x - self.p2.x)
        if self.split and dx < SPLIT_DIST_OFF:
            self.split = False
        elif not self.split and dx > SPLIT_DIST_ON:
            self.split = True
        if self.split:
            self.cam1.update(self.p1, self.p1, dt)
            self.cam2.update(self.p2, self.p2, dt)
        else:
            self.cam.update(self.p1, self.p2, dt)

    def _add_fx(self, fighter, dmg, attacker=None):
        self.fx.append({
            "x": fighter.x, "y": fighter.y - STAND_H * 0.6,
            "txt": str(int(round(dmg)) if dmg == int(dmg) else round(dmg, 1)),
            "gold": attacker is not None and attacker.ult_timer > 0, "t": 0.0,
        })

    def _tick_fx(self, dt):
        for fx in self.fx:
            fx["t"] += dt
        self.fx = [fx for fx in self.fx if fx["t"] < 0.9]
        if self.notice is not None:
            self.notice["t"] += dt
            if self.notice["t"] >= self.notice["dur"]:
                self.notice = None
        for c in self.coins[:]:
            c["t"] += dt
            c["vy"] += 900 * dt
            c["x"] += c["vx"] * dt
            c["y"] += c["vy"] * dt
            if c["t"] >= 0.8:
                self.coins.remove(c)

    def _ride(self, a, b, b_x0, b_body0, inp_a):
        if a.hp <= 0 or a.hit_timer > 0 or not a.on_ground:
            return
        if inp_a is None or inp_a.left or inp_a.right:
            return
        if a.vy < 0:
            return
        ab = a._body()
        if not (ab.right > b_body0.left and ab.left < b_body0.right):
            return
        if abs(a.y - b_body0.top) > 3:
            return
        a.x += b.x - b_x0
        a.y = float(b._body().top)
        a.vx = 0.0
        a.vy = 0.0
        a.on_ground = True
        a.x = max(20.0, min(self.map.w - 20.0, a.x))

    def _separate(self):
        p1, p2 = self.p1, self.p2
        if not p1.on_ground or not p2.on_ground:
            return
        a1 = p1._body()
        a2 = p2._body()
        if a1.bottom <= a2.top + 1 or a2.bottom <= a1.top + 1:
            return
        dx = p1.x - p2.x
        min_d = 37.0
        if abs(dx) < min_d:
            push = (min_d - abs(dx)) / 2
            if dx >= 0:
                p1.x += push
                p2.x -= push
            else:
                p1.x -= push
                p2.x += push
            p1.x = max(20.0, min(self.map.w - 20.0, p1.x))
            p2.x = max(20.0, min(self.map.w - 20.0, p2.x))

    def _villager_phase(self, dt):
        if not self.villagers:
            return
        for p, tag in ((self.p1, 1), (self.p2, 2)):
            a = p.attack
            if a is None or a["hit"]:
                continue
            d = a["def"]
            if not (d["hit0"] <= a["timer"] <= d["hit1"]):
                continue
            hb = p._hitbox(d)
            hit = next((v for v in self.villagers if hb.colliderect(v.rect)), None)
            if hit is not None:
                hit.take_hit(1.0, p.facing)
                a["hit"] = True
                for v in self.villagers:
                    v.aggro = tag
                    v.aggro_t = 5.0
        for v in self.villagers:
            self._update_villager(v, dt)

    def _update_villager(self, v, dt):
        if v.aggro is not None:
            v.aggro_t -= dt
            if v.aggro_t <= 0:
                v.aggro = None
        if v.aggro is None:
            v.roam_t -= dt
            if v.roam_t <= 0 or v.on_wall:
                v.roam_dir *= -1
                v.roam_t = 1.6
            inp = SimpleNamespace(left=v.roam_dir < 0, right=v.roam_dir > 0, jump=False,
                                  crouch=False, jump_pressed=False, ability1_pressed=False,
                                  ability2_pressed=False, ability3_pressed=False, ult_pressed=False)
            opp = SimpleNamespace(x=v.x + v.roam_dir * 60)
        else:
            target = self.p1 if v.aggro == 1 else self.p2
            dx = target.x - v.x
            inp = SimpleNamespace(left=dx < 0, right=dx > 0, jump=False, crouch=False,
                                  jump_pressed=False,
                                  ability1_pressed=abs(dx) < 52 and v.attack is None,
                                  ability2_pressed=False, ability3_pressed=False, ult_pressed=False)
            opp = target
        v.update(dt, inp, opp)
        for pl in (self.p1, self.p2):
            dd = v.x - pl.x
            if abs(dd) < 30:
                v.x = pl.x + (30 if dd >= 0 else -30)
        if v.attack is not None:
            v.attack_started = True
        elif v.attack_started:
            v.attack_started = False
            if v.aggro is not None:
                v.aggro = None

    # ---------- map specific ----------

    def _map_specific(self, dt):
        if self.map_id == "city":
            self._city_house_crouch(dt)
            for p in (self.p1, self.p2):
                if p.hp > 0 and p.y > CITY_DEATH_Y:
                    p.hp = 0.0
        elif self.map_id == "trucks":
            self._truck_update(dt)
        elif self.map_id == "minestick":
            self._mine_update(dt)
        elif self.map_id == "house":
            self._house_redzone(dt)
        elif self.map_id == "johnny":
            self._johnny_update(dt)
        elif self.map_id == "zombi":
            self._zombie_update(dt)
        elif self.map_id == "football":
            self._football_update(dt)
        elif self.map_id == "laserrun":
            self._laserrun_update(dt)
        elif self.map_id == "boss":
            self._boss_update(dt)

    # ---------- şehir / ev geçişi ----------

    def _city_house_crouch(self, dt):
        on_roof = False
        for p in (self.p1, self.p2):
            if p.hp <= 0 or not p.crouching or not p.on_ground:
                continue
            if any(b.left - 2 <= p.x <= b.right + 2 and abs(p.y - b.top) <= 2
                   for b in self.map.buildings):
                on_roof = True
        self.house_crouch = self.house_crouch + dt if on_roof else 0.0
        if self.house_crouch >= HOUSE_CROUCH_TIME:
            self.house_crouch = 0.0
            self._swap_map("house")
            self._center_fx("EVE GİRDİN!")

    def _house_redzone(self, dt):
        for p in (self.p1, self.p2):
            if p.hp <= 0:
                continue
            if p.rect.colliderect(self.map.red_zone):
                self._swap_map("city")
                self._center_fx("ŞEHRE DÖNDÜN!")
                break

    def _center_fx(self, txt):
        self.fx.append({"x": 500, "y": GROUND_Y - 160, "txt": txt,
                        "gold": True, "t": 0.0})

    def _swap_map(self, new_id):
        self.map_id = new_id
        self.map = maps.MAP_OBJECTS[new_id]()
        self.zoom = CITY_ZOOM if new_id == "city" else FOOT_ZOOM if new_id == "football" else LR_ZOOM if new_id == "laserrun" else 1.0
        self.cam = self._mk_cam(SCREEN_W, SCREEN_H)
        self.cam1 = self._mk_cam(SCREEN_W // 2, SCREEN_H)
        self.cam2 = self._mk_cam(SCREEN_W // 2, SCREEN_H)
        self.split = False
        if new_id == "city":
            s1 = (self.map.buildings[2].centerx, self.map.buildings[2].top)
            s2 = (self.map.buildings[6].centerx, self.map.buildings[6].top)
        elif new_id == "house":
            s1 = (260.0, GROUND_Y)
            s2 = (760.0, GROUND_Y)
        else:
            s1 = (300.0, GROUND_Y)
            s2 = (700.0, GROUND_Y)
        for p, (x, y) in ((self.p1, s1), (self.p2, s2)):
            p.x = float(x)
            p.y = float(y)
            p.vx = 0.0
            p.vy = 0.0
            p.on_ground = True
            p.crouching = False
            p.attack = None
            p.drown_t = 0.0
            p.chair = False
            p.chair_t = 0.0
            p.world_w = self.map.w
            p.floor_y = GROUND_Y if new_id == "house" else None
        self.cam.center(float(s1[0] + s2[0]) / 2.0,
                        float(s1[1] + s2[1]) / 2.0 - 140)

    # ---------- trucks ----------

    def _truck_update(self, dt):
        self.truck_t -= dt
        if self.truck_t <= 0:
            self.truck_t = TRUCK_GAP
            self.truck_n += 1
            r = pygame.Rect(-TRUCK_W - 20, GROUND_Y - TRUCK_H, TRUCK_W, TRUCK_H)
            self.trucks.append({"rect": r, "fx": float(r.x), "vx": TRUCK_SPEED,
                                "dist": 0.0, "hit_p1": False, "hit_p2": False,
                                "drive": None, "drive_t": 0.0, "crouch_t": 0.0, "dir": 1})
        for tr in self.trucks[:]:
            r = tr["rect"]
            if tr["drive"] is not None:
                tr["drive_t"] += dt
                inp = self.inp1 if tr["drive"] == 1 else self.inp2
                if inp is not None and inp.right:
                    tr["vx"] = TRUCK_SPEED * 1.6
                elif inp is not None and inp.left:
                    tr["vx"] = -TRUCK_SPEED * 1.6
                else:
                    tr["vx"] = TRUCK_SPEED * tr["dir"] * 0.6
                if tr["drive_t"] >= TRUCK_DRIVE_TIME:
                    self._explode_truck(tr)
                    continue
            else:
                tr["vx"] = TRUCK_SPEED * tr["dir"]
            r.x += tr["vx"] * dt
            tr["fx"] += tr["vx"] * dt
            r.x = int(round(tr["fx"]))
            if tr["drive"] is not None:
                if r.x < 4 or r.x + r.w > WORLD_W - 4:
                    self._explode_truck(tr)
                    continue
            else:
                tr["dist"] += abs(tr["vx"] * dt)
                if tr["dist"] >= TRUCK_EXPLODE_DIST:
                    self._explode_truck(tr)
                    continue
            top = r.top
            for p, tag in ((self.p1, "p1"), (self.p2, "p2")):
                if p.hp <= 0:
                    continue
                horiz = p.rect.right > r.left and p.rect.left < r.right
                riding = horiz and abs(p.y - top) < 10
                if riding:
                    p.x += tr["vx"] * dt
                    p.y = float(top)
                    p.vy = 0.0
                    p.on_ground = True
                    if tr["drive"] is None:
                        inp = self.inp1 if tag == "p1" else self.inp2
                        if inp is not None and inp.crouch:
                            tr["crouch_t"] += dt
                            if tr["crouch_t"] >= TRUCK_DRIVE_CROUCH and tr["drive"] is None:
                                tr["drive"] = 1 if tag == "p1" else 2
                                tr["crouch_t"] = 0.0
                        else:
                            tr["crouch_t"] = max(0.0, tr["crouch_t"] - dt * 2)
                    continue
                if not p.on_ground and p.vy >= 0 and horiz and \
                        p.y >= top and p.y - p.vy * dt <= top + 2:
                    p.y = float(top)
                    p.vy = 0.0
                    p.on_ground = True
                    p.x += tr["vx"] * dt
                    continue
                if p.rect.colliderect(r) and not tr["hit_" + tag]:
                    if not p.crouching:
                        tr["hit_" + tag] = True
                        p.hp = max(0.0, p.hp - 50.0)
                        self._add_fx(p, 50)
        self.trucks = [tr for tr in self.trucks
                       if tr["drive"] is not None
                       or (tr["rect"].x < WORLD_W + 200 and tr["rect"].x > -TRUCK_W - 200)]

    def _driver(self):
        for tr in self.trucks:
            if tr["drive"] is not None:
                return tr["drive"]
        return None

    def _explode_truck(self, tr):
        r = tr["rect"]
        self.trucks.remove(tr)
        if tr["drive"] is not None:
            dp = self.p1 if tr["drive"] == 1 else self.p2
            if dp.hp > 0:
                dp.hp = max(0.0, dp.hp - 20.0)
                self._add_fx(dp, 20)
        self.fx.append({"x": r.centerx, "y": r.top - 30, "txt": "PAT!",
                        "gold": True, "t": 0.0})

    # ---------- zombie survival ----------

    def _zombie_start_wave(self):
        cols_default = (120, 120, 120)
        self.zombie["wave"] += 1
        wave = self.zombie["wave"]
        base = ZOMBIE_CYCLE_COUNT
        cycle = (wave - 1) // base
        idx = (wave - 1) % base
        plan = ZOMBIE_WAVE_PLAN[idx + 1]
        mult = min(ZOMBIE_HP_CAP, 1.0 + 0.45 * cycle)
        speed_mult = min(ZOMBIE_SPEED_CAP, 1.0 + 0.10 * cycle)
        extra = min(ZOMBIE_COUNT_CAP, cycle)
        pool = [cid for cid, cr in CREATURE_BY_ID.items()
                if cr["family"] in ("zombi", "creeper", "örümcek", "enderman",
                                    "blaze", "hayvan", "özel")]
        k = 0
        jobs = []
        for kind, n in plan:
            jobs.extend([kind] * (n + extra))
        if cycle > 0:
            for _ in range(min(6, cycle * 2)):
                jobs.append(pool[random.randrange(len(pool))])
        for kind in jobs:
            x = ZOMBIE_SPAWN_XS[k % 2]
            cr = CREATURE_BY_ID.get(kind)
            if cr is not None:
                base_hp, base_sp = cr["mob_hp"], cr["mob_speed"]
                fam = cr["family"]
                col = cr["color"]
                cname = cr["name"]
            else:
                base_hp, base_sp = MOB_STATS.get(kind, (20, 80.0))
                fam, col, cname = kind, cols_default, kind
            hp = base_hp * mult
            self.mobs.append({"kind": kind, "cid": kind, "family": fam,
                              "color": col, "cname": cname,
                              "mscale": cr["mscale"] if cr else 1.0,
                              "x": float(x), "y": float(GROUND_Y),
                              "hp": float(hp), "max_hp": hp, "speed": base_sp * speed_mult,
                              "dir": 1, "roam_t": 1.0 + k * 0.4, "touch_cd": 0.0,
                              "sizzle": 0.0, "wobbly": k * 0.4, "home_x": float(x),
                              "shoot_t": 1.5 + k * 0.3})
            k += 1
        self.fx.append({"x": 500, "y": GROUND_Y - 130,
                        "txt": "DALGA %d!" % wave, "gold": True, "t": 0.0})

    def _zombie_update(self, dt):
        self.map.stage = "normal"
        alive = [p for p in (self.p1, self.p2) if p.hp > 0]
        if not self.mobs:
            self.zombie["t"] -= dt
            if self.zombie["t"] <= 0:
                self.zombie["t"] = 2.2
                self._zombie_start_wave()
        for mob in self.mobs[:]:
            mob["touch_cd"] = max(0.0, mob["touch_cd"] - dt)
            target = None
            for p in alive:
                if abs(p.x - mob["x"]) <= MOB_AGGRO_DIST + 160:
                    target = p
                    break
            if target is not None:
                mob["dir"] = 1 if target.x >= mob["x"] else -1
                if mob["family"] == "creeper" and abs(target.x - mob["x"]) < 70 \
                        and abs(target.y - mob["y"]) < 120:
                    mob["sizzle"] += dt
                    if mob["sizzle"] >= 0.9:
                        self._explode_mob(mob)
                        continue
                elif mob["family"] == "blaze":
                    mob["shoot_t"] -= dt
                    if mob["shoot_t"] <= 0:
                        mob["shoot_t"] = BLAZE_SHOOT_TIME
                        self._spawn_blaze_ball(mob, target)
                elif mob["family"] == "enderman" and abs(target.x - mob["x"]) > 190:
                    mob["x"] += (target.x - mob["x"]) * 0.14
                mob["x"] += mob["dir"] * mob["speed"] * dt
            else:
                mob["sizzle"] = 0.0
                mob["roam_t"] -= dt
                if mob["roam_t"] <= 0:
                    mob["dir"] *= -1
                    mob["roam_t"] = 1.4
                mob["x"] += mob["dir"] * mob["speed"] * 0.4 * dt
            mob["x"] = max(50.0, min(self.map.w - 50.0, mob["x"]))
            dmg = MOB_CONTACT_DMG_MAP.get(mob["kind"], MOB_CONTACT_DMG)
            if dmg > 0:
                for p in alive:
                    if abs(p.x - mob["x"]) < 32 and abs(p.y - mob["y"]) < 60 \
                            and mob["touch_cd"] <= 0:
                        p.hp = max(0.0, p.hp - dmg)
                        self._add_fx(p, dmg)
                        mob["touch_cd"] = MOB_CONTACT_CD
                        break
        self.mobs = [m for m in self.mobs if m["hp"] > 0]
        self._check_mob_attacks()
        if self.winner is None and all(p.hp <= 0 for p in (self.p1, self.p2)):
            k1, k2 = self.zombie["kills"]
            self.winner = 1 if k1 >= k2 else 2

    # ---------- football (futbol) ----------

    def _football_update(self, dt):
        if self.winner is not None:
            return
        st = self.foot_state
        b = st["ball"]
        st["cd"][0] = max(0.0, st["cd"][0] - dt)
        st["cd"][1] = max(0.0, st["cd"][1] - dt)
        k = self.foot_kick
        if k[0] or k[1]:
            self._foot_kick(self.p1, k[0], k[1])
        if k[2] or k[3]:
            self._foot_kick(self.p2, k[2], k[3])
        b["vy"] = min(4200.0, b["vy"] + FOOT_GRAVITY * dt)
        b["vx"] *= max(0.0, 1.0 - 0.3 * dt)
        b["x"] += b["vx"] * dt
        b["y"] += b["vy"] * dt
        if b["x"] - FOOT_BALL_R < FOOT_ARENA_LEFT:
            b["x"] = FOOT_ARENA_LEFT + FOOT_BALL_R
            b["vx"] *= -0.65
        if b["x"] + FOOT_BALL_R > FOOT_ARENA_RIGHT:
            b["x"] = FOOT_ARENA_RIGHT - FOOT_BALL_R
            b["vx"] *= -0.65
        if b["y"] >= GROUND_Y - FOOT_BALL_R:
            if b["vy"] > 0:
                if b["vy"] > 60.0:
                    b["vy"] *= -FOOT_BOUNCE
                    b["vx"] *= 0.9
                else:
                    b["vy"] = 0.0
            b["y"] = GROUND_Y - FOOT_BALL_R
        self._foot_player(self.p1, b)
        self._foot_player(self.p2, b)
        if b["x"] < 72:
            self._foot_goal(1)      # sol kale (P1'in): P2 gol
        elif b["x"] > WORLD_W - 72:
            self._foot_goal(0)      # sağ kale (P2'nin): P1 gol

    def _foot_kick(self, p, flat, up):
        st = self.foot_state
        if p.hp <= 0:
            return
        idx = 0 if p is self.p1 else 1
        if st["cd"][idx] > 0:
            return
        b = st["ball"]
        bb = p._body()
        if abs(b["x"] - bb.centerx) > 92:
            return
        if b["y"] > bb.top + 150:
            return
        st["cd"][idx] = 0.22
        if up:
            b["vy"] = -FOOT_LOFT_SPEED
            b["vx"] = p.facing * FOOT_LOFT_FWD
            self.fx.append({"x": int(b["x"]), "y": int(b["y"]),
                            "txt": "HAVAYA!", "gold": False, "t": 0.0})
        else:
            b["vy"] = 0.0
            b["y"] = float(GROUND_Y - FOOT_BALL_R)
            b["vx"] = p.facing * FOOT_KICK_SPEED
            self.fx.append({"x": int(b["x"]), "y": int(b["y"]),
                            "txt": "VURUŞ!", "gold": False, "t": 0.0})

    def _foot_player(self, p, b):
        if p.hp <= 0:
            return
        bb = p._body()
        r = FOOT_BALL_R
        nx = max(bb.left, min(b["x"], bb.right))
        ny = max(bb.top, min(b["y"], bb.bottom))
        dx = b["x"] - nx
        dy = b["y"] - ny
        if dx * dx + dy * dy > r * r:
            return
        if -dy > abs(dx) and dx * dx + dy * dy > 1.0:
            b["y"] = bb.top - r - 1
            if b["vy"] > 0:
                b["vy"] = -abs(b["vy"]) * 0.75
                b["vx"] += p.facing * 30.0
            else:
                b["vy"] = -40.0
            return
        if b["x"] >= bb.centerx:
            b["x"] = float(bb.right + r + 1)
            if b["vx"] <= 0:
                b["vx"] = FOOT_DRIBBLE
            else:
                b["vx"] *= 1.2
        else:
            b["x"] = float(bb.left - r - 1)
            if b["vx"] >= 0:
                b["vx"] = -FOOT_DRIBBLE
            else:
                b["vx"] *= 1.2
        if b["y"] + FOOT_BALL_R >= GROUND_Y - 2:
            b["y"] = float(GROUND_Y - FOOT_BALL_R)

    def _foot_goal(self, scorer):
        st = self.foot_state
        st["score"][scorer] += 1
        self.fx.append({"x": 500, "y": GROUND_Y - 140, "txt": "GOL!",
                        "gold": True, "t": 0.0})
        b = st["ball"]
        b["x"] = 500.0
        b["y"] = float(GROUND_Y - FOOT_BALL_R)
        b["vx"] = 0.0
        b["vy"] = 0.0
        if st["score"][scorer] >= FOOT_GOAL_SCORE:
            self.winner = scorer + 1

    # ---------- lazer run ----------
    def _laserrun_update(self, dt):
        if self.winner is not None:
            return
        st = self.lr_state
        st["time"] += dt
        st["spawn_t"] += dt

        # blok spawn
        if st["spawn_t"] >= LR_SPAWN_INTERVAL:
            st["spawn_t"] = 0.0
            # rastgele yükseklik: platform üstü veya altı
            top_choices = [
                self.map.platform.top - LR_BLOCK_H,           # platform üstü
                self.map.platform.top - LR_BLOCK_H - 120,     # biraz üst
                self.map.platform.top - LR_BLOCK_H - 240,     # daha üst
            ]
            y = top_choices[int(st["time"] * 10) % len(top_choices)]
            st["blocks"].append({"x": float(self.map.w + 50), "y": float(y), "w": LR_BLOCK_W, "h": LR_BLOCK_H})

        # blokları hareket ettir
        for bl in st["blocks"][:]:
            bl["x"] -= LR_BLOCK_SPEED * dt
            if bl["x"] + bl["w"] < 0:
                st["blocks"].remove(bl)

        # oyuncu - blok çarpışması
        for i, p in enumerate((self.p1, self.p2)):
            if st["dead"][i] or p.hp <= 0:
                continue
            pr = p._body()
            for bl in st["blocks"]:
                br = pygame.Rect(int(bl["x"]), int(bl["y"]), bl["w"], bl["h"])
                if pr.colliderect(br):
                    # blok itiyor: oyuncuyu sola iter, hasar verir
                    p.x = max(40.0, p.x - LR_BLOCK_SPEED * dt * 1.5)
                    p.take_damage(LR_BLOCK_DMG * dt, -1)
                    if p.hp <= 0:
                        st["dead"][i] = True
                        self.fx.append({"x": p.x, "y": p.y - 40, "txt": "EZİLDİ!",
                                        "gold": False, "t": 0.0})

        # lazer hasarı (platformun sonunda)
        for i, p in enumerate((self.p1, self.p2)):
            if st["dead"][i] or p.hp <= 0:
                continue
            pr = p._body()
            for lr in self.map.lasers:
                if pr.colliderect(lr):
                    p.take_damage(LR_LASER_DMG * dt, 0)
                    if p.hp <= 0:
                        st["dead"][i] = True
                        self.fx.append({"x": p.x, "y": p.y - 40, "txt": "YANDI!",
                                        "gold": False, "t": 0.0})

        # platform dışına düşme
        for i, p in enumerate((self.p1, self.p2)):
            if st["dead"][i]:
                continue
            if p.x < self.map.platform.left - 20 or p.x > self.map.platform.right + 20:
                if p.y > self.map.platform.top + 50:
                    st["dead"][i] = True
                    p.hp = 0.0
                    self.fx.append({"x": p.x, "y": p.y - 40, "txt": "DÜŞTÜ!",
                                    "gold": False, "t": 0.0})

        # kazanan: en az biri hayatta ve süre 60sn geçti
        if st["time"] >= 60.0:
            alive = [i for i, d in enumerate(st["dead"]) if not d]
            if alive:
                self.winner = alive[0] + 1
            else:
                self.winner = 1
            return

        # her ikisi de ölü
        if all(st["dead"]):
            self.winner = 1

    # ---------- boss fights (100 boss = 20 tier x 5 tema) ----------

    def _start_boss(self):
        if self.boss_id >= len(BOSSES):
            if self.winner is None:
                hp1 = max(0.0, self.p1.hp)
                hp2 = max(0.0, self.p2.hp)
                self.winner = 1 if hp1 >= hp2 else 2
            return
        cfg = dict(BOSSES[self.boss_id])
        cfg["x"] = 500.0
        cfg["y"] = float(GROUND_Y)
        cfg["dir"] = 1
        cfg["touch_cd"] = 0.0
        cfg["sizzle"] = 0.0
        cfg["shoot_t"] = 2.0
        cfg["wobbly"] = 0.0
        cfg["power_t"] = BOSS_POWER_TIME
        cfg["max_hp"] = cfg["hp"]
        self.boss = cfg
        self.fx.append({"x": 500, "y": GROUND_Y - 150, "txt": cfg["name"] + "!",
                        "gold": True, "t": 0.0})

    def _boss_rect(self, cfg):
        body_w = int(30 * cfg["size"])
        body_h = int(52 * cfg["size"])
        return pygame.Rect(int(cfg["x"] - body_w // 2), int(cfg["y"] - body_h), body_w, body_h)

    def _boss_update(self, dt):
        if self.winner is not None:
            return
        for p in (self.p1, self.p2):
            if p.hp <= 0:
                p.hp = 25.0
                self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "DIRİLDİN!",
                                "gold": True, "t": 0.0})
        if self.boss is None:
            self.boss_next_t -= dt
            if self.boss_next_t <= 0:
                self._start_boss()
            return
        cfg = self.boss
        cfg["touch_cd"] = max(0.0, cfg["touch_cd"] - dt)
        cfg["wobbly"] = cfg.get("wobbly", 0.0) + dt
        alive = [p for p in (self.p1, self.p2) if p.hp > 0]
        target = alive[0] if alive else self.p1
        cfg["dir"] = 1 if target.x >= cfg["x"] else -1
        if cfg["kind"] == "blaze":
            cfg["shoot_t"] -= dt
            if cfg["shoot_t"] <= 0:
                cfg["shoot_t"] = BLAZE_SHOOT_TIME
                self._spawn_blaze_ball(cfg, target)
            cfg["y"] = float(GROUND_Y) - abs(math.sin(cfg["wobbly"] * 2.2) * 14)
        else:
            cfg["y"] = float(GROUND_Y)
            if cfg["kind"] == "enderman" and abs(target.x - cfg["x"]) > 220:
                cfg["x"] += (target.x - cfg["x"]) * 0.15
            elif cfg["kind"] == "creeper" and abs(target.x - cfg["x"]) < 110 \
                    and abs(target.y - cfg["y"]) < 150:
                cfg["sizzle"] += dt
                if cfg["sizzle"] >= 1.1:
                    self._boss_explode(cfg)
                    return
            else:
                cfg["x"] += cfg["dir"] * cfg["speed"] * dt
        cfg["x"] = max(60.0, min(self.map.w - 60.0, cfg["x"]))
        cfg["power_t"] = cfg.get("power_t", BOSS_POWER_TIME) - dt
        if cfg["power_t"] <= 0:
            cfg["power_t"] = BOSS_POWER_TIME
            self._boss_power(target)
        self._stalagmites_update(dt)
        self._boss_splashes_update(dt)
        self._boss_webs_update(dt)
        self._boss_tele_update(dt)
        br = self._boss_rect(cfg)
        if cfg["dmg"] > 0 and cfg["touch_cd"] <= 0:
            for p in alive:
                if br.inflate(10, 10).colliderect(p.rect):
                    p.hp = max(0.0, p.hp - cfg["dmg"])
                    self._add_fx(p, cfg["dmg"])
                    cfg["touch_cd"] = MOB_CONTACT_CD
                    break
        self._check_boss_attacks()
        self._blaze_balls_update(dt)

    def _boom_boss(self, cfg):
        cx = cfg["x"]
        self.fx.append({"x": cx, "y": cfg["y"] - 40, "txt": "MEGA PATLAMA!",
                        "gold": True, "t": 0.0})
        for p in (self.p1, self.p2):
            if p.hp > 0 and abs(p.x - cx) < 90 and abs(p.y - cfg["y"]) < 150:
                p.hp = max(0.0, p.hp - MOB_EXPLODE_DMG * 1.4)
                self._add_fx(p, MOB_EXPLODE_DMG * 1.4)

    def _boss_power(self, target):
        cfg = self.boss
        kind = cfg["kind"]
        if kind == "zombi":
            self._boss_mud(cfg, target)
        elif kind == "örümcek":
            self._boss_web(cfg, target)
        elif kind == "creeper":
            self._boss_dikit(cfg, target)
        elif kind == "enderman":
            self._boss_teleport(cfg, target)
        elif kind == "blaze":
            self._boss_lava(cfg, target)

    def _boss_mud(self, cfg, target):
        dx = target.x - cfg["x"]
        dy = (target.y - 30) - cfg["y"]
        d = math.hypot(dx, dy) or 1.0
        self.boss_splashes.append({"x": cfg["x"], "y": cfg["y"] - 60,
                                   "vx": dx / d * BOSS_MUD_SPEED,
                                   "vy": dy / d * BOSS_MUD_SPEED + 130.0,
                                   "t": 0.0, "fire": False})
        self.fx.append({"x": cfg["x"], "y": cfg["y"] - 80,
                        "txt": BOSS_POWER_NAMES["zombi"], "gold": True, "t": 0.0})

    def _boss_web(self, cfg, target):
        self.boss_webs.append({"x": float(target.x), "t": 0.0, "hit_t": {}})
        self.fx.append({"x": target.x, "y": GROUND_Y - 40,
                        "txt": BOSS_POWER_NAMES["örümcek"], "gold": True, "t": 0.0})

    def _boss_dikit(self, cfg, target):
        self.stalagmites.append({"x": float(target.x + target.facing * 20),
                                 "t": 0.0, "hit": False})
        self.fx.append({"x": self.stalagmites[-1]["x"], "y": GROUND_Y - 40,
                        "txt": "DİKİT!", "gold": True, "t": 0.0})

    def _boss_teleport(self, cfg, target):
        old_x = cfg["x"]
        nx = max(60.0, min(self.map.w - 60.0, target.x - target.facing * 30))
        self.boss_tele.append({"x": old_x, "y": cfg["y"], "t": 0.0})
        cfg["x"] = nx
        cfg["dir"] = 1 if target.x >= nx else -1
        self.boss_tele.append({"x": nx, "y": cfg["y"], "t": 0.0})
        for p in (self.p1, self.p2):
            if p.hp > 0 and abs(p.x - nx) < 90 and abs(p.y - GROUND_Y) < 160:
                p.hp = max(0.0, p.hp - BOSS_TELE_DMG)
                self._add_fx(p, BOSS_TELE_DMG)
        self.fx.append({"x": nx, "y": GROUND_Y - 90,
                        "txt": BOSS_POWER_NAMES["enderman"], "gold": True, "t": 0.0})

    def _boss_lava(self, cfg, target):
        cx, cy = cfg["x"], cfg["y"]
        for p in (self.p1, self.p2):
            if p.hp > 0 and abs(p.x - cx) < BOSS_LAVA_RANGE and abs(p.y - cy) < 180:
                p.hp = max(0.0, p.hp - BOSS_LAVA_DMG)
                self._add_fx(p, BOSS_LAVA_DMG)
        for i in range(8):
            a = i / 8.0 * 6.283 + 0.4
            self.boss_splashes.append({"x": cx + math.cos(a) * 18, "y": cy - 30,
                                       "vx": math.cos(a) * 280,
                                       "vy": math.sin(a) * 170 - 70,
                                       "t": 0.0, "fire": True})
        self.fx.append({"x": cx, "y": cy - 90,
                        "txt": BOSS_POWER_NAMES["blaze"], "gold": True, "t": 0.0})

    def _boss_splashes_update(self, dt):
        for sp in self.boss_splashes[:]:
            sp["t"] += dt
            sp["vy"] += 900 * dt
            sp["x"] += sp["vx"] * dt
            sp["y"] += sp["vy"] * dt
            hit = False
            r = pygame.Rect(int(sp["x"] - 9), int(sp["y"] - 9), 18, 18)
            for p in (self.p1, self.p2):
                if p.hp > 0 and r.colliderect(p.rect):
                    dmg = BOSS_MUD_DMG if not sp.get("fire") else BOSS_LAVA_DMG * 0.4
                    p.hp = max(0.0, p.hp - dmg)
                    self._add_fx(p, dmg)
                    hit = True
                    break
            if sp["y"] >= GROUND_Y - 8 or sp["t"] > 1.8:
                hit = True
            if hit:
                self.boss_splashes.remove(sp)

    def _boss_webs_update(self, dt):
        for wb in self.boss_webs[:]:
            wb["t"] += dt
            r = pygame.Rect(int(wb["x"] - 40), GROUND_Y - 12, 80, 12)
            for p in (self.p1, self.p2):
                key = "p1" if p is self.p1 else "p2"
                last = wb["hit_t"].get(key, -9.0)
                if p.hp > 0 and p.rect.colliderect(r) and wb["t"] - last >= 0.8:
                    p.hp = max(0.0, p.hp - BOSS_WEB_DMG)
                    self._add_fx(p, BOSS_WEB_DMG)
                    wb["hit_t"][key] = wb["t"]
            if wb["t"] > BOSS_WEB_LIFE:
                self.boss_webs.remove(wb)

    def _boss_tele_update(self, dt):
        for te in self.boss_tele[:]:
            te["t"] += dt
            if te["t"] > 0.5:
                self.boss_tele.remove(te)

    def _stalagmites_update(self, dt):
        for st in self.stalagmites[:]:
            st["t"] += dt
            if STALAGMITE_GROW <= st["t"] <= STALAGMITE_END and not st["hit"]:
                r = pygame.Rect(int(st["x"] - 12), GROUND_Y - 60, 24, 60)
                for p in (self.p1, self.p2):
                    if p.hp > 0 and r.colliderect(p.rect):
                        p.hp = max(0.0, p.hp - STALAGMITE_DMG)
                        self._add_fx(p, STALAGMITE_DMG)
                        st["hit"] = True
                        break
            if st["t"] > STALAGMITE_LIFE:
                self.stalagmites.remove(st)

    def _boss_explode(self, cfg):
        self._boom_boss(self.boss)
        self._boss_defeated()

    def _check_boss_attacks(self):
        cfg = self.boss
        if cfg is None:
            return
        for p in (self.p1, self.p2):
            a = p.attack
            if a is None or a["hit"]:
                continue
            dd = a["def"]
            if not (dd["hit0"] <= a["timer"] <= dd["hit1"]):
                continue
            hb = p._hitbox(dd)
            if self._boss_rect(cfg).inflate(8, 8).colliderect(hb):
                cfg["hp"] -= dd["dmg"]
                a["hit"] = True
                self.fx.append({"x": cfg["x"], "y": cfg["y"] - 44,
                                "txt": str(round(dd["dmg"], 1)), "gold": False, "t": 0.0})
                if cfg["hp"] <= 0:
                    self._boss_defeated()

    def _boss_defeated(self):
        if self.boss is None:
            return
        cfg = self.boss
        self.boss = None
        # Kutlama animasyonu: para parçacıkları + duyuru
        for _ in range(20):
            self.coins.append({
                "x": cfg["x"] + random.uniform(-50, 50),
                "y": cfg["y"] - 40 + random.uniform(-20, 20),
                "vx": random.uniform(-180, 180),
                "vy": random.uniform(-460, -160),
                "t": 0.0,
            })
        self.notice = {"title": cfg["name"] + " YENİLDİ!",
                       "sub": f"+${BOSS_KILL_REWARD:.2f} KAZANILDI!",
                       "t": 0.0, "dur": 1.6}
        self.fx.append({"x": cfg["x"], "y": cfg["y"] - 60, "txt": cfg["name"] + " YENİLDİ!",
                        "gold": True, "t": 0.0})
        drop = MOB_DROPS.get(cfg["kind"])
        if drop is not None:
            for p in (self.p1, self.p2):
                p.inv[drop] = p.inv.get(drop, 0) + 1
        # Para ödülü (merkezi settings modülünde tutulur)
        settings.PLAYER_MONEY += BOSS_KILL_REWARD
        self.boss_id += 1
        self.boss_next_t = 2.0
        if self.boss_id >= len(BOSSES):
            self._start_boss()

    # ---------- minestick ----------

    def _stage(self):
        if self.mine_dead_delay is not None:
            return "end"
        return self.mine_stage

    def _craft_intercept(self, inp1, inp2):
        self._craft_saved = None
        if self.map_id != "minestick" or not self.craft_open:
            return
        inp = inp1 if self.craft_owner == 1 else inp2
        if inp is None:
            return
        attrs = ("left", "right", "jump", "crouch", "jump_pressed",
                 "ability1_pressed", "ability2_pressed", "ability3_pressed", "ult_pressed")
        save = {a: getattr(inp, a) for a in attrs}
        for a in attrs:
            setattr(inp, a, False)
        self._craft_saved = (self.craft_owner, inp, save)

    def _craft_restore(self):
        if self._craft_saved is None:
            return
        owner, inp, save = self._craft_saved
        for a, v in save.items():
            setattr(inp, a, v)
        self._craft_saved = None

    def _mine_update(self, dt):
        if self.mine_dead_delay is not None:
            self.mine_dead_delay -= dt
            if self.mine_dead_delay <= 0:
                self.mine_dead_delay = None
                self.mine_stage = "normal"
                self.dragon = None
                self.crystal = None
                self.crystal_delay = 0.0
                self.dragon_target = None
                self.craft_open = False
                self._reset_mine_terrain()
                # nether'de dönüş portalı olmadığı için yüzey portalı geri yüklenir
                if self._saved_portal is not None:
                    sp = self._saved_portal
                    self.map.portal_blocks = list(sp["blocks"])
                    self.map.portal_lit = sp["lit"]
                    self.map.portal = sp["portal"]
                    self._saved_portal = None
                    self._sync_solids()
                for i, p in enumerate((self.p1, self.p2)):
                    p.x = (40.0, 175.0)[i]
                    p.y = float(GROUND_Y)
                    p.vx = 0.0
                    p.vy = 0.0
                    p.on_ground = True
                    p.crouching = False
                    p.attack = None
                    p.drown_t = 0.0
                    self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "NORMAL DÜNYA!",
                                    "gold": True, "t": 0.0})
            return
        self.map.stage = self.mine_stage
        # T: craft menüsünü aç/kapa (p1)
        if self.inp1 is not None and self.inp1.craft_pressed and self.mine_stage != "end":
            if self.craft_open:
                self._craft_flush(self.p1)
            self.craft_open = not self.craft_open
            self.craft_owner = 1
            if self.craft_open:
                self.craft_sel = [0, 0]
                self.craft_inv_sel = 0
                self.craft_inv_scroll = 0
                self.craft_cursor = None
                self.craft_rep = 0.0
                self._cf_state = None
                self.craft_out = self._craft_match()
        if self.craft_open:
            oinp = self.inp1 if self.craft_owner == 1 else self.inp2
            self._craft_update(dt, oinp)
        for i, (p, inp) in enumerate(((self.p1, self.inp1), (self.p2, self.inp2))):
            if inp is None or p.hp <= 0:
                continue
            if self.craft_open and self.craft_owner == i + 1:
                continue
            a1 = bool(inp.ability1_pressed and not inp.crouch)
            a2 = bool(inp.ability1_pressed and inp.crouch)
            if a1 and not self.mine_a1[i]:
                self._mine_break(p)
            if a2 and not self.mine_a1[i]:
                self._mine_place(p)
            if inp.ability2_pressed and not self.mine_a2[i]:
                self._use_bucket(p)
            self.mine_a1[i] = inp.ability1_pressed
            self.mine_a2[i] = inp.ability2_pressed
        if self.inp1 is not None and self.inp1.place_pressed and self.p1.hp > 0:
            self._place_block(self.p1)
        if self.mine_stage in ("normal", "nether"):
            self._check_mob_attacks()
            self._mine_mob_update(dt)
            self._blaze_balls_update(dt)
        if self.mine_stage == "normal":
            self._check_portal_ignite()
        if self.mine_stage == "nether" and not self.map.nether_end_active and not self.map.netherite:
            m = self.map
            m.nether_end_active = True
            fx_x = self.p1.x if self.p1.hp > 0 else 500.0
            self.fx.append({"x": fx_x, "y": self.p1.y - STAND_H, "txt": "3 NETHERITE KIRILDI!",
                            "gold": True, "t": 0.0})
            self.fx.append({"x": fx_x, "y": self.p1.y - STAND_H - 22, "txt": "END PORTALI AÇILDI!",
                            "gold": True, "t": 0.0})
        self.portal_t = max(0.0, self.portal_t - dt)
        advanced = False
        if self.mine_stage == "normal" and self.map.portal is not None and self.portal_t <= 0:
            for p in (self.p1, self.p2):
                if p.hp > 0 and p.rect.colliderect(self.map.portal):
                    self._advance_mine_stage("nether")
                    advanced = True
                    break
        if not advanced and self.mine_stage == "normal" and self.map.end_portal_active \
                and self.map.end_portal is not None:
            for p in (self.p1, self.p2):
                if p.hp > 0 and p.rect.colliderect(self.map.end_portal):
                    self._advance_mine_stage("end")
                    advanced = True
                    break
        if not advanced and self.mine_stage == "nether" and self.map.nether_end_active \
                and self.map.nether_end_portal is not None:
            for p in (self.p1, self.p2):
                if p.hp > 0 and p.rect.colliderect(self.map.nether_end_portal):
                    self._advance_mine_stage("end")
                    advanced = True
                    break
        for p in (self.p1, self.p2):
            if p.hp <= 0:
                continue
            zones = self.map.hazard_zones()
            in_water = any(k == "water" and p.rect.colliderect(r) for k, r in zones)
            in_lava = any(k == "lava" and p.rect.colliderect(r) for k, r in zones)
            if in_water:
                p.drown_t += dt
                if p.drown_t >= DROWN_TIME:
                    p.drown_t = 0.0
                    p.hp = max(0.0, p.hp - DROWN_DMG)
                    self._add_fx(p, DROWN_DMG)
            else:
                p.drown_t = 0.0
            if in_lava:
                p.hp = max(0.0, p.hp - LAVA_DPS * dt)
        if self.mine_stage == "end":
            self._dragon_update(dt)

    def _respawn_mine_mobs(self):
        self.mobs = []
        self.blaze_balls = []
        if self.mine_stage == "nether":
            # nether'de canavar yok; tek engel 3 netherite bloğu
            return
        if self.map_id != "minestick" or self.mine_stage != "normal":
            return
        # canavarlar SADECE madenin içinde doğar (katların üzerinde)
        specs = [("zombi", 3000, 1350), ("zombi", 3160, 1350),
                 ("zombi", 3320, 1430), ("creeper", 3480, 1430),
                 ("zombi", 3660, 1510), ("creeper", 3820, 1510),
                 ("creeper", 4000, 1590), ("zombi", 4160, 1590)]
        for kind, x, y in specs:
            hp, sp = MOB_STATS[kind]
            cr = CREATURE_BY_ID.get(kind)
            self.mobs.append({"kind": kind, "cid": kind,
                              "family": cr["family"] if cr else kind,
                              "color": cr["color"] if cr else None,
                              "mscale": cr["mscale"] if cr else 1.0,
                              "cname": cr["name"] if cr else kind,
                              "x": float(x), "y": float(y),
                              "hp": float(hp), "max_hp": hp, "speed": sp, "dir": 1,
                              "roam_t": 1.0 + (x % 3), "touch_cd": 0.0, "sizzle": 0.0,
                              "wobbly": (x % 7) * 0.5, "home_x": float(x)})

    def _mine_mob_update(self, dt):
        alive = [p for p in (self.p1, self.p2) if p.hp > 0]
        for mob in self.mobs[:]:
            mob["touch_cd"] = max(0.0, mob["touch_cd"] - dt)
            target = None
            for p in alive:
                if abs(p.x - mob["x"]) <= MOB_AGGRO_DIST and abs(p.y - mob["y"]) < 260:
                    target = p
                    break
            if mob.get("hover"):
                if target is not None:
                    mob["dir"] = 1 if target.x >= mob["x"] else -1
                    mob["x"] += mob["dir"] * mob["speed"] * dt
                    mob["shoot_t"] = mob.get("shoot_t", 1.0) - dt
                    if mob["shoot_t"] <= 0:
                        mob["shoot_t"] = BLAZE_SHOOT_TIME
                        self._spawn_blaze_ball(mob, target)
            else:
                if target is not None:
                    mob["dir"] = 1 if target.x >= mob["x"] else -1
                    if mob["family"] == "creeper" and abs(target.x - mob["x"]) < 70 \
                            and abs(target.y - mob["y"]) < 120:
                        mob["sizzle"] += dt
                        if mob["sizzle"] >= 0.9:
                            self._explode_mob(mob)
                            continue
                    mob["x"] += mob["dir"] * mob["speed"] * dt
                else:
                    mob["sizzle"] = 0.0
                    mob["roam_t"] -= dt
                    if mob["roam_t"] <= 0:
                        mob["dir"] *= -1
                        mob["roam_t"] = 1.4
                    mob["x"] += mob["dir"] * mob["speed"] * 0.4 * dt
            if mob["family"] == "enderman" and target is not None \
                    and abs(target.x - mob["x"]) > 240:
                mob["x"] += (target.x - mob["x"]) * 0.2
            mob["x"] = max(24.0, min(self.map.w - 24.0, mob["x"]))
            if self.mine_stage == "normal":
                # canavarlar madenin dışına çıkamaz (kenardan düşerlerse geri dönerler)
                if mob["x"] < 2760:
                    mob["x"] = 3000.0
                    mob["y"] = 1350.0
                elif mob["x"] > 4200:
                    mob["x"] = 4000.0
                    mob["y"] = 1590.0
            dmg = MOB_CONTACT_DMG_MAP.get(mob["kind"], MOB_CONTACT_DMG)
            if dmg > 0:
                for p in alive:
                    if abs(p.x - mob["x"]) < 32 and abs(p.y - mob["y"]) < 60 \
                            and mob["touch_cd"] <= 0:
                        p.hp = max(0.0, p.hp - dmg)
                        self._add_fx(p, dmg)
                        mob["touch_cd"] = MOB_CONTACT_CD
                        break
        self.mobs = [m for m in self.mobs if m["hp"] > 0]

    def _spawn_blaze_ball(self, mob, target):
        dx = target.x - mob["x"]
        dy = (target.y - 40) - mob["y"]
        d = math.hypot(dx, dy) or 1.0
        self.blaze_balls.append({"x": mob["x"], "y": mob["y"],
                                 "vx": dx / d * BLAZE_BALL_SPEED,
                                 "vy": dy / d * BLAZE_BALL_SPEED, "t": 0.0})

    def _blaze_balls_update(self, dt):
        for b in self.blaze_balls[:]:
            b["t"] += dt
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            hit = False
            for p in (self.p1, self.p2):
                if p.hp > 0 and p.rect.inflate(10, 10).colliderect(
                        pygame.Rect(int(b["x"] - 10), int(b["y"] - 10), 20, 20)):
                    p.hp = max(0.0, p.hp - BLAZE_BALL_DMG)
                    self._add_fx(p, BLAZE_BALL_DMG)
                    hit = True
                    break
            if hit or b["t"] > 2.6:
                self.blaze_balls.remove(b)

    def _explode_mob(self, mob):
        cx = mob["x"]
        self.fx.append({"x": cx, "y": mob["y"] - 30, "txt": "PATLAMA!", "gold": True, "t": 0.0})
        for p in (self.p1, self.p2):
            if p.hp > 0 and abs(p.x - cx) < 70 and abs(p.y - mob["y"]) < 120:
                p.hp = max(0.0, p.hp - MOB_EXPLODE_DMG)
                self._add_fx(p, MOB_EXPLODE_DMG)
        self.mobs.remove(mob)

    def _check_mob_attacks(self):
        for p in (self.p1, self.p2):
            a = p.attack
            if a is None or a["hit"]:
                continue
            dd = a["def"]
            if not (dd["hit0"] <= a["timer"] <= dd["hit1"]):
                continue
            hb = p._hitbox(dd)
            mob = next((m for m in self.mobs
                        if hb.colliderect(pygame.Rect(int(m["x"] - 16), int(m["y"] - 40), 32, 48))), None)
            if mob is None:
                continue
            mob["hp"] -= dd["dmg"]
            a["hit"] = True
            self.fx.append({"x": mob["x"], "y": mob["y"] - 40, "txt": str(round(dd["dmg"], 1)),
                            "gold": False, "t": 0.0})
            if mob["hp"] <= 0:
                self.fx.append({"x": mob["x"], "y": mob["y"] - 40, "txt": "CANAVAR YOK OLDU!",
                                "gold": True, "t": 0.0})
                drop = MOB_DROPS.get(mob["kind"])
                if drop is not None:
                    p.inv[drop] = p.inv.get(drop, 0) + 1
                if self.map_id == "zombi":
                    self.zombie["kills"][0 if p is self.p1 else 1] += 1

    # ---------- craft (T) ----------

    def _craft_owner_p(self):
        return self.p1 if self.craft_owner == 1 else self.p2

    def _craft_size(self):
        # her zaman 3x3: çalışma masası gerekmez
        return 3

    def _craft_inv_list(self, p):
        return [k for k in ITEM_NAMES if p.inv.get(k, 0) > 0]

    def _craft_match(self):
        for key, (out, pat) in CRAFT_3.items():
            if len(pat) != 9:
                continue
            ok = True
            for i, need in enumerate(pat):
                if need is None:
                    continue
                cell = self.craft_grid[i]
                if cell is None or cell[0] != need or cell[1] < 1:
                    ok = False
                    break
            if ok:
                return out[0]
        return None

    def _craft_layout(self):
        # ızgara 3x3 solda, envanter penceresi sağda, çıktı arada
        T = 40
        L = SCREEN_W // 2 - 360
        ty = SCREEN_H // 2 - 140
        cells = [pygame.Rect(L + 20 + c * T, ty + r * T, T, T) for r in range(3) for c in range(3)]
        grid = pygame.Rect(L + 16, ty - 4, 3 * T + 8, 3 * T + 8)
        out = pygame.Rect(L + 20 + 3 * T + 22, ty + T, T, T)
        invx = L + 20 + 3 * T + 22 + T + 46
        slots = [pygame.Rect(invx + 4 + c * T, ty + r * T, T - 8, T - 8)
                 for r in range(3) for c in range(2)]
        inv = pygame.Rect(invx, ty - 4, 2 * T + 8, 3 * T + 8)
        up = pygame.Rect(invx + 4, ty - 48, T - 8, 40)
        down = pygame.Rect(invx + 4 + T, ty - 48, T - 8, 40)
        return {"cells": cells, "grid": grid, "out": out, "slots": slots,
                "inv": inv, "up": up, "down": down}

    def _craft_hit(self, pos, layout):
        if pos is None:
            return None
        if layout["out"].collidepoint(pos):
            return ("out",)
        for i, r in enumerate(layout["cells"]):
            if r.collidepoint(pos):
                return ("cell", i)
        for i, r in enumerate(layout["slots"]):
            if r.collidepoint(pos):
                return ("slot", i)
        if layout["up"].collidepoint(pos):
            return ("up",)
        if layout["down"].collidepoint(pos):
            return ("down",)
        return None

    def _craft_window(self, p):
        items = self._craft_inv_list(p)
        n = max(0, len(items) - 6)
        self.craft_inv_scroll = max(0, min(self.craft_inv_scroll, n))
        return items[self.craft_inv_scroll:self.craft_inv_scroll + 6]

    def _craft_inc_cursor(self):
        self.craft_cursor[1] -= 1
        if self.craft_cursor[1] <= 0:
            self.craft_cursor = None

    def _craft_move(self, dr, dc, size):
        self.craft_sel[0] = max(0, min(size - 1, self.craft_sel[0] + dr))
        self.craft_sel[1] = max(0, min(size - 1, self.craft_sel[1] + dc))

    def _craft_update(self, dt, inp):
        p = self._craft_owner_p()
        size = self._craft_size()
        self.craft_out = self._craft_match()
        self.craft_rep = max(0.0, self.craft_rep - dt)
        dirs = []
        if inp and inp.left:
            dirs.append((0, -1))
        elif inp and inp.right:
            dirs.append((0, 1))
        if inp and inp.jump:
            dirs.append((-1, 0))
        elif inp and inp.crouch:
            dirs.append((1, 0))
        key = (bool(inp.left if inp else False),
               bool(inp.right if inp else False),
               bool(inp.jump if inp else False),
               bool(inp.crouch if inp else False))
        changed = key != getattr(self, "_cf_state", None)
        self._cf_state = key
        if dirs and (changed or self.craft_rep <= 0):
            self._craft_move(dirs[0][0], dirs[0][1], size)
            self.craft_rep = 0.26
        if inp is None:
            return
        if inp.ability1_pressed:
            self._craft_deposit(p, size)
        if inp.ability2_pressed:
            self._craft_return(p, size)
        if inp.ult_pressed:
            self._craft_take(p)
        if inp.left_click or inp.right_click:
            layout = self._craft_layout()
            hit = self._craft_hit(inp.mouse_pos, layout)
            if hit is not None:
                kind = hit[0]
                if kind == "out":
                    if inp.left_click:
                        self._craft_take(p)
                elif kind == "cell":
                    idx = hit[1]
                    if inp.right_click:
                        self._craft_cell_right(idx, p)
                    else:
                        self._craft_cell_left(idx, p)
                elif kind == "slot":
                    if inp.left_click:
                        self._craft_pick_slot(hit[1], p)
                elif kind == "up":
                    if inp.left_click:
                        self.craft_inv_scroll = max(0, self.craft_inv_scroll - 6)
                elif kind == "down":
                    if inp.left_click:
                        self.craft_inv_scroll += 6
            inp.left_click = False
            inp.right_click = False
            self.craft_out = self._craft_match()

    def _craft_cell_left(self, idx, p):
        cell = self.craft_grid[idx]
        if self.craft_cursor is None:
            if cell is None:
                return
            self.craft_cursor = [cell[0], 1]
            cell[1] -= 1
            if cell[1] <= 0:
                self.craft_grid[idx] = None
            return
        ckey, cq = self.craft_cursor
        if cell is None:
            self.craft_grid[idx] = [ckey, 1]
        elif cell[0] == ckey:
            cell[1] += 1
        else:
            p.inv[cell[0]] = p.inv.get(cell[0], 0) + cell[1]
            cell[0], cell[1] = ckey, cq
            self.craft_cursor = None
            return
        self._craft_inc_cursor()

    def _craft_cell_right(self, idx, p):
        cell = self.craft_grid[idx]
        if self.craft_cursor is not None:
            ckey, cq = self.craft_cursor
            if cell is None:
                self.craft_grid[idx] = [ckey, cq]
            elif cell[0] == ckey:
                cell[1] += cq
            else:
                return
            self.craft_cursor = None
            return
        if cell is None:
            return
        p.inv[cell[0]] = p.inv.get(cell[0], 0) + cell[1]
        self.craft_grid[idx] = None

    def _craft_pick_slot(self, si, p):
        items = self._craft_window(p)
        if si >= len(items):
            return
        key = items[si]
        amt = p.inv[key]
        if self.craft_cursor is None:
            self.craft_cursor = [key, amt]
        elif self.craft_cursor[0] == key:
            self.craft_cursor[1] += amt
        else:
            old = self.craft_cursor
            self.craft_cursor = [key, amt]
            p.inv[old[0]] = p.inv.get(old[0], 0) + old[1]
        p.inv.pop(key)

    def _craft_flush(self, p):
        if self.craft_cursor is not None:
            p.inv[self.craft_cursor[0]] = p.inv.get(self.craft_cursor[0], 0) + self.craft_cursor[1]
            self.craft_cursor = None

    def _craft_deposit(self, p, size):
        if self.craft_cursor is not None:
            idx = self.craft_sel[0] * size + self.craft_sel[1]
            self._craft_cell_right(idx, p)
            return
        items = self._craft_inv_list(p)
        if not items:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "ENVANTER BOŞ",
                            "gold": False, "t": 0.0})
            return
        if self.craft_inv_sel >= len(items):
            self.craft_inv_sel = 0
        key = items[self.craft_inv_sel]
        idx = self.craft_sel[0] * size + self.craft_sel[1]
        if self.craft_grid[idx] is not None and self.craft_grid[idx][0] != key:
            old = self.craft_grid[idx]
            p.inv[old[0]] = p.inv.get(old[0], 0) + old[1]
            self.craft_grid[idx] = None
        if self.craft_grid[idx] is None:
            self.craft_grid[idx] = [key, 0]
        self.craft_grid[idx][1] += 1
        p.inv[key] -= 1
        if p.inv[key] <= 0:
            p.inv.pop(key)
        self.craft_inv_sel = (self.craft_inv_sel + 1) % len(self._craft_inv_list(p) or [1])
        self.craft_out = self._craft_match()
        self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "→ " + ITEM_NAMES[key],
                        "gold": True, "t": 0.0})

    def _craft_return(self, p, size):
        if self.craft_cursor is not None:
            self._craft_flush(p)
            return
        idx = self.craft_sel[0] * size + self.craft_sel[1]
        cell = self.craft_grid[idx]
        if cell is None:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "boş",
                            "gold": False, "t": 0.0})
            return
        p.inv[cell[0]] = p.inv.get(cell[0], 0) + cell[1]
        self.craft_grid[idx] = None
        self.craft_out = self._craft_match()
        self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "← " + ITEM_NAMES[cell[0]],
                        "gold": False, "t": 0.0})

    def _craft_take(self, p):
        out_key = self.craft_out
        if out_key is None:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "TARİF YOK",
                            "gold": False, "t": 0.0})
            return
        (key, qty), pat = CRAFT_3[out_key]
        used = []
        for i, need in enumerate(pat):
            if need is None:
                continue
            c = self.craft_grid[i]
            if c is None or c[0] != need or c[1] < 1:
                return
            used.append(i)
        for i in used:
            c = self.craft_grid[i]
            c[1] -= 1
            if c[1] <= 0:
                self.craft_grid[i] = None
        p.inv[out_key] = p.inv.get(out_key, 0) + qty
        self.craft_out = self._craft_match()
        self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "+" + ITEM_NAMES[out_key],
                        "gold": True, "t": 0.0})

    def _check_portal_ignite(self):
        m = self.map
        if m.portal_lit or len(m.portal_blocks) < 3:
            return
        pr = m._portal_rect()
        sources = list(m.mine_lava) + list(m.poured_lava)
        near = any(pr.inflate(int(PORTAL_LAVA_DIST * 2), 0).colliderect(r) for r in sources)
        if not near:
            return
        m.portal_lit = True
        for r in m.portal_blocks:
            if r in m.blocks:
                m.blocks.remove(r)
        m.portal = pr
        self._sync_solids()
        self.fx.append({"x": pr.centerx, "y": pr.top - 10, "txt": "PORTAL YANDI!",
                        "gold": True, "t": 0.0})

    def _advance_mine_stage(self, nxt=None):
        prev = self.mine_stage
        if nxt is None:
            nxt = "nether" if prev == "normal" else ("normal" if prev == "nether" else "end")
        txt = {"nether": "NETHER!", "normal": "NORMAL DÜNYA!", "end": "END!"}[nxt]
        m = self.map
        preserve = (prev == "normal" and nxt == "nether") or (prev == "nether" and nxt == "normal")
        if prev == "normal" and nxt == "nether":
            self._saved_portal = {"blocks": list(m.portal_blocks), "lit": m.portal_lit,
                                  "portal": m.portal}
        self.mine_stage = nxt
        self.portal_t = 1.0
        self._reset_mine_terrain(preserve_frames=preserve)
        if nxt == "normal" and self._saved_portal is not None:
            sp = self._saved_portal
            m.portal_blocks = list(sp["blocks"])
            m.portal_lit = sp["lit"]
            m.portal = sp["portal"]
            self._saved_portal = None
            self._sync_solids()
        for i, p in enumerate((self.p1, self.p2)):
            p.x = (40.0, 175.0)[i]
            p.y = float(GROUND_Y)
            p.vx = 0.0
            p.vy = 0.0
            p.on_ground = True
            p.crouching = False
            p.attack = None
            p.drown_t = 0.0
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": txt, "gold": True, "t": 0.0})

    def _reset_mine_terrain(self, preserve_frames=False):
        m = self.map
        m.blocks = list(m._base_blocks) + [o["rect"] for o in m._base_ores]
        m.ores = [dict(o) for o in m._base_ores]
        m.portal_blocks = []
        m.portal_lit = False
        m.poured_lava = []
        m.portal = None
        if self.mine_stage == "nether":
            # nether'e her girişte 3 netherite yeniden dizilir, portal kapalı başlar
            m.netherite = list(m._netherite_base)
            m.nether_end_active = False
        m.stage = self.mine_stage
        if not preserve_frames:
            m.end_frames = []
            m.end_portal_active = False
            m.end_portal = None
            m.placements = []
            self._craft_flush(self.p1)
            self.craft_open = False
        self._sync_solids()
        self._respawn_mine_mobs()
        # normal katta yüzeye geri sıçrama yok; mağara katlarında gerçekten inilir
        if self.mine_stage == "normal":
            self.p1.floor_y = None
            self.p2.floor_y = None
        else:
            self.p1.floor_y = float(GROUND_Y)
            self.p2.floor_y = float(GROUND_Y)

    def _sync_solids(self):
        self.map.refresh_solids()
        self.p1.solids = self.map.solids
        self.p2.solids = self.map.solids
        for v in self.villagers:
            v.solids = self.map.solids

    def _pick_tier(self, p):
        best = 0
        for key, tier in PICKAXE_TIER.items():
            if p.inv.get(key, 0) > 0 and tier > best:
                best = tier
        return best

    def _mine_break(self, p):
        x0 = p.x + p.facing * 8
        x1 = p.x + p.facing * 58
        hb = pygame.Rect(int(min(x0, x1)), int(p.y - 30), int(abs(x1 - x0)), 40)
        if self.mine_stage == "nether":
            for r in list(self.map.netherite):
                if hb.colliderect(r):
                    if self._pick_tier(p) < 4:
                        self.fx.append({"x": r.centerx, "y": r.top - 10,
                                        "txt": "ELMAS KAZMA GEREK!", "gold": False, "t": 0.0})
                        return
                    self.map.netherite.remove(r)
                    p.inv["netherite"] = p.inv.get("netherite", 0) + 1
                    self._sync_solids()
                    self.fx.append({"x": r.centerx, "y": r.top - 10,
                                    "txt": "+NETHERITE", "gold": False, "t": 0.0})
                    return
            for r in list(self.map.nether_rocks):
                if hb.colliderect(r):
                    self.map.nether_rocks.remove(r)
                    p.inv["nether_tasi"] = p.inv.get("nether_tasi", 0) + 1
                    self._sync_solids()
                    self.fx.append({"x": r.centerx, "y": r.top - 10,
                                    "txt": "+NETHER TAŞI", "gold": False, "t": 0.0})
                    return
            self.fx.append({"x": p.x + p.facing * 30, "y": p.y - STAND_H, "txt": "boş",
                            "gold": False, "t": 0.0})
            return
        for ore in list(self.map.ores):
            b = ore["rect"]
            if not hb.colliderect(b):
                continue
            need = ORE_MIN_TIER.get(ore["type"], 0)
            if self._pick_tier(p) < need:
                self.fx.append({"x": b.centerx, "y": b.top - 10,
                                "txt": "KAZMA GEREK! (%s)" % ITEM_NAMES.get(ore["type"], ore["type"]),
                                "gold": False, "t": 0.0})
                return
            self.map.blocks.remove(b)
            self.map.ores.remove(ore)
            key = ore["type"]
            p.inv[key] = p.inv.get(key, 0) + 1
            self._sync_solids()
            self.fx.append({"x": b.centerx, "y": b.top - 10,
                            "txt": "+" + ITEM_NAMES.get(key, key),
                            "gold": False, "t": 0.0})
            return
        # toprak basamaklar ve maden taşı arazi kırılamaz
        for b in self.map._terrain_blocks:
            if hb.colliderect(b):
                self.fx.append({"x": p.x + p.facing * 30, "y": p.y - STAND_H,
                                "txt": "BURASI KIRILMAZ!", "gold": False, "t": 0.0})
                return
        for b in list(self.map.blocks):
                if not hb.colliderect(b):
                    continue
                self.map.blocks.remove(b)
                if b in self.map.portal_blocks:
                    self.map.portal_blocks.remove(b)
                    p.inv["obsidyen"] = p.inv.get("obsidyen", 0) + 1
                    txt = "OBSİDYEN ÇIKARILDI"
                else:
                    p.inv["tas"] = p.inv.get("tas", 0) + 1
                    txt = "BLOK KIRILDI! +TAŞ"
                self._sync_solids()
                self.fx.append({"x": b.centerx, "y": b.top - 10, "txt": txt,
                                "gold": False, "t": 0.0})
                return
        for t in list(self.map.trees):
            if hb.colliderect(t["trunk"]):
                self.map.trees.remove(t)
                p.inv["odun"] = p.inv.get("odun", 0) + 1
                self._sync_solids()
                self.fx.append({"x": t["trunk"].centerx, "y": t["trunk"].top - 10,
                                "txt": "AĞAÇ KIRILDI! +ODUN", "gold": False, "t": 0.0})
                return
        self.fx.append({"x": p.x + p.facing * 30, "y": p.y - STAND_H, "txt": "boş",
                        "gold": False, "t": 0.0})

    def _mine_place(self, p):
        m = self.map
        if self.mine_stage != "normal":
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "yapılamaz",
                            "gold": False, "t": 0.0})
            return
        if not m.portal_lit and p.inv.get("obsidyen", 0) > 0 and len(m.portal_blocks) < 14:
            g = TILE
            bx = int(math.floor((p.x + p.facing * (18 + g + 4)) / g) * g)
            n = len(m.portal_blocks)
            r = pygame.Rect(bx, GROUND_Y - (n + 1) * g, g, g)
            blockers = list(m.solids) + [self.p1.rect, self.p2.rect]
            if r.collidelist(blockers) != -1:
                self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "yapılamaz",
                                "gold": False, "t": 0.0})
                return
            m.portal_blocks.append(r)
            m.blocks.append(r)
            p.inv["obsidyen"] -= 1
            self._sync_solids()
            self.fx.append({"x": r.centerx, "y": r.top - 10, "txt": "PORTAL %d/3" % (n + 1),
                            "gold": True, "t": 0.0})
            return
        self.fx.append({"x": p.x + p.facing * 30, "y": p.y - STAND_H, "txt": "eşya yok",
                        "gold": False, "t": 0.0})

    def _place_block(self, p):
        m = self.map
        if self.mine_stage != "normal":
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "SADECE DÜNYADA!",
                            "gold": False, "t": 0.0})
            return
        item = next((k for k in ("end_cerceve", "crafting_table", "yatak")
                     if p.inv.get(k, 0) > 0), None)
        if item is None:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "BLOK EŞYASI YOK!",
                            "gold": False, "t": 0.0})
            return
        g = TILE
        bx = int(math.floor((p.x + p.facing * (18 + g + 4)) / g) * g)
        blockers = list(m.solids) + [self.p1.rect, self.p2.rect]
        if item == "end_cerceve" and not m.end_portal_active:
            n = len(m.end_frames)
            if n >= 3:
                self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "3 ÇERÇEVE TAMAM! SU (Q)",
                                "gold": False, "t": 0.0})
                return
            r = pygame.Rect(bx, GROUND_Y - (n + 1) * g, g, g)
            if r.collidelist(blockers) != -1:
                self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "yapılamaz",
                                "gold": False, "t": 0.0})
                return
            m.end_frames.append(r)
            m.placements.append({"rect": r, "item": item})
            p.inv[item] -= 1
            self._sync_solids()
            self.fx.append({"x": r.centerx, "y": r.top - 10, "txt": "END ÇERÇEVE %d/3" % (n + 1),
                            "gold": True, "t": 0.0})
            return
        for cy in (GROUND_Y - g, GROUND_Y - 2 * g, GROUND_Y - 3 * g):
            r = pygame.Rect(bx, cy, g, g)
            if r.collidelist(blockers) == -1:
                m.placements.append({"rect": r, "item": item})
                p.inv[item] -= 1
                self._sync_solids()
                self.fx.append({"x": r.centerx, "y": r.top - 10,
                                "txt": "%s KONULDU!" % ITEM_NAMES[item], "gold": True, "t": 0.0})
                return
        self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "yapılamaz",
                        "gold": False, "t": 0.0})

    def _use_bucket(self, p):
        m = self.map
        if self.mine_stage not in ("normal", "nether"):
            self._pour_water(p)
            return
        pools = list(m.mine_lava) + list(m.lava_pools) + list(m.poured_lava)
        if p.inv.get("lav_kovası", 0) > 0:
            g = TILE
            bx = math.floor((p.x + p.facing * (18 + g)) / g) * g
            r = pygame.Rect(bx, GROUND_Y - 14, g, 14)
            if r.collidelist(m.solids) == -1:
                m.poured_lava.append(r)
            p.inv["lav_kovası"] -= 1
            p.inv["kova"] = p.inv.get("kova", 0) + 1
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "LAV BIRAKILDI!",
                            "gold": False, "t": 0.0})
            return
        if p.inv.get("kova", 0) > 0:
            pr = p.rect.inflate(140, 0)
            near = any(pr.colliderect(r) for r in pools)
            if near:
                p.inv["kova"] -= 1
                p.inv["lav_kovası"] = p.inv.get("lav_kovası", 0) + 1
                self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "LAV ALINDI! +LAV KOVASI",
                                "gold": False, "t": 0.0})
                return
        self._pour_water(p)

    def _pour_water(self, p):
        m = self.map
        if self.mine_stage != "normal":
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "BURADA SU DÖKÜLMEZ",
                            "gold": False, "t": 0.0})
            return
        if not m.end_frames:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "ÖNCE ÇERÇEVE KOY (R)",
                            "gold": False, "t": 0.0})
            return
        pr = m._end_frame_rect()
        if abs(p.x - pr.centerx) > END_WATER_DIST:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "ÇERÇEVELERE ÇOK UZAK",
                            "gold": False, "t": 0.0})
            return
        if m.end_portal_active:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "PORTAL ZATEN AKTİF",
                            "gold": False, "t": 0.0})
            return
        if p.inv.get("kova", 0) <= 0:
            self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "KOVA GEREK!",
                            "gold": False, "t": 0.0})
            return
        p.inv["kova"] -= 1
        m.end_portal_active = True
        m.end_portal = pr
        self._sync_solids()
        self.fx.append({"x": pr.centerx, "y": pr.top - 14, "txt": "ENDER PORTALI AKTİF!",
                        "gold": True, "t": 0.0})

    def _dragon_update(self, dt):
        if self.dragon is None:
            self.dragon = {"hp": DRAGON_HP, "max": DRAGON_HP, "x": 430.0,
                           "y": 660.0, "dead": False}
        d = self.dragon
        if d["dead"]:
            return
        if self.crystal is None and self.crystal_delay > 0:
            self.crystal_delay -= dt
        if self.crystal is not None:
            own = self.p1 if self.crystal["owner"] == 1 else self.p2
            if own.hp <= 0:
                self.crystal["owner"] = 2 if self.crystal["owner"] == 1 else 1
                own = self.p2 if self.crystal["owner"] == 2 else self.p1
            self.crystal["x"] = own.x
            self.crystal["y"] = own.y - 165
            crect = pygame.Rect(int(self.crystal["x"] - 20), int(self.crystal["y"] - 26), 40, 52)
        else:
            crect = None
        for p, tag in ((self.p1, 1), (self.p2, 2)):
            a = p.attack
            if a is None or a["hit"]:
                continue
            dd = a["def"]
            if not (dd["hit0"] <= a["timer"] <= dd["hit1"]):
                continue
            hb = p._hitbox(dd)
            drect = pygame.Rect(int(d["x"] - 55), int(d["y"] - 28), 110, 56)
            dmg = dd["dmg"] * (ULT_MULT if p.ult_timer > 0 else 1.0)
            if hb.colliderect(drect):
                d["hp"] -= dmg
                a["hit"] = True
                self.fx.append({"x": d["x"], "y": d["y"] - 40, "txt": str(round(dmg, 1)),
                                "gold": p.ult_timer > 0, "t": 0.0})
            elif crect is not None and hb.colliderect(crect):
                self.crystal["hp"] -= dmg
                a["hit"] = True
                self.fx.append({"x": self.crystal["x"], "y": self.crystal["y"],
                                "txt": str(round(dmg, 1)), "gold": True, "t": 0.0})
                if self.crystal["hp"] <= 0:
                    self.fx.append({"x": self.crystal["x"], "y": self.crystal["y"],
                                    "txt": "KRİSTAL PATLADI!", "gold": True, "t": 0.0})
                    self.crystal = None
                    self.crystal_delay = CRYSTAL_RESPAWN
        if self.crystal is None and self.crystal_delay <= 0:
            alive = [p for p in (self.p1, self.p2) if p.hp > 0]
            if alive:
                target = min(alive, key=lambda p: abs(p.x - d["x"]))
                self.crystal = {"hp": CRYSTAL_HP, "owner": 1 if target is self.p1 else 2,
                                "t": 0.0, "x": target.x, "y": target.y - 165}
        if self.crystal is not None:
            self.crystal["t"] += dt
            d["hp"] = min(d["max"], d["hp"] + CRYSTAL_REGEN * dt)
            alive = [p for p in (self.p1, self.p2) if p.hp > 0]
            if self.crystal["t"] >= CRYSTAL_SWITCH_TIME:
                self.crystal["t"] = 0.0
                if len(alive) == 2:
                    self.crystal["owner"] = 2 if self.crystal["owner"] == 1 else 1
                    self.fx.append({"x": self.crystal["x"], "y": self.crystal["y"],
                                    "txt": "KRİSTAL GEÇTİ!", "gold": True, "t": 0.0})
        alive = [p for p in (self.p1, self.p2) if p.hp > 0]
        if self.dragon_target is None and alive:
            self.dragon_target = 1 if alive[0] is self.p1 else 2
            self.dragon_target_t = DRAGON_TARGET_TIME
        target = self.p1 if self.dragon_target == 1 else self.p2
        if target.hp <= 0:
            target = self.p2 if self.dragon_target == 1 else self.p1
            self.dragon_target = 2 if self.dragon_target == 1 else 1
        self.dragon_target_t -= dt
        if self.dragon_target_t <= 0:
            self.dragon_target_t = DRAGON_TARGET_TIME
            other = self.p1 if self.dragon_target == 2 else self.p2
            if other.hp > 0:
                self.dragon_target = 2 if self.dragon_target == 1 else 1
                target = other
                self.fx.append({"x": d["x"], "y": d["y"] - 40,
                                "txt": "EJDERHA HEDEF DEĞİŞTİ!", "gold": True, "t": 0.0})
        if target.hp > 0:
            dx = target.x - d["x"]
            step = DRAGON_SPEED * dt
            d["x"] = max(90.0, min(self.map.w - 90.0, d["x"] + max(-step, min(step, dx))))
        self.dragon_fire_t -= dt
        if self.dragon_fire_t <= 0:
            self.dragon_fire_t = 1.2
            if target.hp > 0:

                def _shot(x0):
                    sx, sy = x0, d["y"] + 20
                    vx, vy = target.x - sx, target.y - 40 - sy
                    L = math.hypot(vx, vy) or 1.0
                    s = DRAGON_FIRE_SPEED / L
                    return {"kind": "fire", "x": sx, "y": sy, "vx": vx * s, "vy": vy * s, "dmg": 5.0}

                self.projectiles.append(_shot(d["x"] - 20))
                self.projectiles.append(_shot(d["x"] + 20))
        if d["hp"] <= 0:
            d["dead"] = True
            self.crystal = None
            self.crystal_delay = 0.0
            self.mine_dead_delay = MINE_END_RETURN_DELAY
            self.p1.ult_pct = 100.0
            self.p2.ult_pct = 100.0
            self.fx.append({"x": d["x"], "y": d["y"], "txt": "EJDERHA YOK OLDU!",
                            "gold": True, "t": 0.0})

    # ---------- house ----------

    def _chair_throw(self, dt):
        if self.map_id != "house":
            return
        for p, inp in ((self.p1, self.inp1), (self.p2, self.inp2)):
            if p.hp <= 0:
                continue
            if p.crouching and p.on_ground:
                p.chair_t += dt
                if p.chair is False and p.chair_t >= CHAIR_CROUCH_TIME:
                    p.chair = "chair"
                    self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "SANDALYE!",
                                    "gold": False, "t": 0.0})
                if p.chair == "chair" and p.chair_t >= MASA_CROUCH_TIME:
                    p.chair = "masa"
                    self.fx.append({"x": p.x, "y": p.y - STAND_H, "txt": "MASA!",
                                    "gold": False, "t": 0.0})
            elif p.chair is False:
                p.chair_t = 0.0
            if p.chair is not False and inp and inp.ability1_pressed:
                inp.ability1_pressed = False
                kind = p.chair
                p.chair = False
                p.chair_t = 0.0
                dmg = MASA_DMG if kind == "masa" else CHAIR_DMG
                self.projectiles.append({"kind": kind, "x": p.x + p.facing * 28,
                                         "y": p.y - 34, "vx": p.facing * 520.0,
                                         "vy": 0.0, "dmg": dmg, "owner": p.facing,
                                         "grace": 0.2})

    # ---------- johnny ----------

    def _john_action(self, inp, p):
        if inp is None:
            return "DUR"
        if inp.crouch:
            return "EĞİL"
        if inp.jump or inp.jump_pressed:
            return "ZIPLA"
        if inp.right:
            return "SAĞA"
        if inp.left:
            return "SOLA"
        if p.attack is not None or inp.ability1_pressed or inp.ability2_pressed \
                or inp.ability3_pressed:
            return "VUR"
        return "DUR"

    def _johnny_update(self, dt):
        j = self.johnny
        if j["dead"]:
            return
        if j["phase"] == "wait" and self.t >= j["next"]:
            j["phase"] = "say"
            j["win_end"] = self.t + 1.1
            j["counted"] = [False, False]
            j["cmd"] = (j["cmd"] + 1) % len(JOHNNY_CMDS)
        if j["phase"] == "say":
            cmd = JOHNNY_CMDS[j["cmd"]].rstrip("!")
            for idx, (p, inp) in enumerate(((self.p1, self.inp1), (self.p2, self.inp2))):
                if p.hp > 0 and not j["counted"][idx] and self._john_action(inp, p) == cmd:
                    j["counted"][idx] = True
                    j["scores"][idx] += 1
            if self.t > j["win_end"]:
                j["phase"] = "wait"
                j["next"] = self.t + 1.4
                for idx, p in enumerate((self.p1, self.p2)):
                    if p.hp > 0 and not j["counted"][idx]:
                        p.hp = max(0.0, p.hp - JOHNNY_PUNISH_DMG)
                        self._add_fx(p, JOHNNY_PUNISH_DMG)
            for idx, p in enumerate((self.p1, self.p2)):
                if j["scores"][idx] >= JOHNNY_WIN_COUNT:
                    j["dead"] = True
                    p.ult_pct = 100.0
                    self.winner = idx + 1

    # ---------- projectiles ----------

    def _move_projectiles(self, dt):
        if not self.projectiles:
            return
        keep = []
        for pr in self.projectiles:
            pr["x"] += pr["vx"] * dt
            pr["y"] += pr["vy"] * dt
            alive = True
            rect = pygame.Rect(int(pr["x"] - 8), int(pr["y"] - 8), 16, 16)
            for p in (self.p1, self.p2):
                if p.hp > 0 and rect.colliderect(p.rect):
                    p.take_hit(pr["dmg"], pr.get("owner", 0))
                    self._add_fx(p, pr["dmg"])
                    alive = False
                    break
            if alive and pr.get("grace", 0) > 0:
                pr["grace"] -= dt
            elif alive and any(rect.colliderect(s) for s in self.map.solids):
                alive = False
            if alive and -100 < pr["x"] < self.map.w + 100 and pr["y"] < WORLD_H + 400:
                keep.append(pr)
        self.projectiles = keep

    # ---------- draw ----------

    def draw(self, surf):
        surf.fill(settings.BG_COLOR)
        if self.split:
            self._render_view(surf, pygame.Rect(0, 0, SCREEN_W // 2, SCREEN_H), self.cam1)
            self._render_view(surf, pygame.Rect(SCREEN_W // 2, 0, SCREEN_W - SCREEN_W // 2,
                                                SCREEN_H), self.cam2)
            pygame.draw.line(surf, (235, 235, 245), (SCREEN_W // 2, 0), (SCREEN_W // 2, SCREEN_H), 3)
        else:
            self._render_view(surf, pygame.Rect(0, 0, SCREEN_W, SCREEN_H), self.cam)
        self.hud.draw(surf, self.p1, self.p2, self.t)
        if self.map_id == "minestick":
            self._draw_minestick_bar(surf)
        if self.map_id == "johnny":
            self._draw_johnny_bar(surf)
        if self.map_id == "zombi":
            self._draw_zombie_bar(surf)
        if self.map_id == "football":
            self._draw_football_bar(surf)
        if self.map_id == "laserrun":
            self._draw_laserrun_bar(surf)
        if self.map_id == "boss":
            self._draw_boss_bar(surf)
        self._draw_notice(surf)
        if self.winner is not None:
            self._draw_result(surf)

    def _render_view(self, surf, rect, cam):
        vpw, vph = rect.w, rect.h
        direct = (self.zoom == 1.0 and vpw == SCREEN_W and vph == SCREEN_H)
        if direct:
            sub = surf
        else:
            tw = int(round(vpw / self.zoom))
            th = int(round(vph / self.zoom))
            sub = pygame.Surface((max(1, tw), max(1, th)))
        self.map.draw(sub, cam)
        objs = list(self.villagers) + [self.p1, self.p2]
        drv = self._driver()
        objs = [s for s in objs if not (drv == "p1" and s is self.p1)
                and not (drv == "p2" and s is self.p2)]
        for p in sorted(objs, key=lambda s: s.x):
            p.draw(sub, cam.x, cam.y)
        self._draw_props(sub, cam)
        self._draw_map_extra(sub, cam)
        self.eng.draw(sub, cam)
        self._draw_fx(sub, cam)
        self._draw_coins(sub, cam)
        if not direct:
            scaled = pygame.transform.smoothscale(sub, (vpw, vph))
            surf.blit(scaled, rect)

    def _draw_props(self, surf, cam):
        drv = self._driver()
        for p in (self.p1, self.p2):
            if getattr(p, "chair", False):
                if (drv == "p1" and p is self.p1) or (drv == "p2" and p is self.p2):
                    continue
                cx = int(p.x - cam.x) + p.facing * 16
                if p.chair == "masa":
                    cy = int(p.y - cam.y) - 36
                    pygame.draw.ellipse(surf, (150, 110, 70), (cx - 26, cy - 14, 56, 26))
                    pygame.draw.ellipse(surf, (110, 76, 44), (cx - 26, cy - 14, 56, 26), 3)
                    pygame.draw.line(surf, (110, 76, 44), (cx - 16, cy + 12), (cx - 16, cy + 22), 4)
                    pygame.draw.line(surf, (110, 76, 44), (cx + 16, cy + 12), (cx + 16, cy + 22), 4)
                    pygame.draw.line(surf, (110, 76, 44), (cx, cy + 12), (cx, cy + 22), 4)
                else:
                    cy = int(p.y - cam.y) - 36
                    pygame.draw.rect(surf, (150, 110, 70), (cx - 8, cy - 6, 28, 14))
                    pygame.draw.rect(surf, (110, 76, 44), (cx - 8, cy - 6, 28, 14), 2)
                    pygame.draw.line(surf, (110, 76, 44), (cx - 6, cy + 8), (cx - 6, cy + 14), 3)
                    pygame.draw.line(surf, (110, 76, 44), (cx + 18, cy + 8), (cx + 18, cy + 14), 3)
        for pr in self.projectiles:
            px = int(pr["x"] - cam.x)
            py = int(pr["y"] - cam.y)
            if pr["kind"] == "masa":
                pygame.draw.ellipse(surf, (150, 110, 70), (px - 22, py - 12, 48, 22))
                pygame.draw.ellipse(surf, (110, 76, 44), (px - 22, py - 12, 48, 22), 3)
                pygame.draw.line(surf, (110, 76, 44), (px - 12, py + 10), (px - 12, py + 18), 4)
                pygame.draw.line(surf, (110, 76, 44), (px + 12, py + 10), (px + 12, py + 18), 4)
            elif pr["kind"] == "chair":
                pygame.draw.rect(surf, (150, 110, 70), (px - 10, py - 6, 28, 14))
                pygame.draw.rect(surf, (110, 76, 44), (px - 10, py - 6, 28, 14), 2)
            else:
                pygame.draw.circle(surf, (180, 80, 255), (px, py), 8)
                pygame.draw.circle(surf, (230, 160, 255), (px, py), 3)

    def _draw_map_extra(self, surf, cam):
        if self.map_id == "trucks":
            for tr in self.trucks:
                r = pygame.Rect(int(tr["rect"].x - cam.x),
                                int(tr["rect"].y - cam.y), tr["rect"].w, tr["rect"].h)
                cab = (-1 if tr["dir"] > 0 else 1)
                body = pygame.Rect(r.x if tr["dir"] > 0 else r.x + 34, r.y + 30,
                                   r.w - 34 if tr["dir"] > 0 else r.w - 34, r.h - 30)
                pygame.draw.rect(surf, (70, 130, 170), body)
                pygame.draw.rect(surf, (40, 70, 100), body, 3)
                pane = (body.w - 28) // 3
                for i in range(2):
                    win = pygame.Rect(body.x + 10 + i * pane, body.y + 10, pane - 6, body.h - 30)
                    pygame.draw.rect(surf, (150, 205, 235), win)
                    pygame.draw.rect(surf, (30, 50, 72), win, 2)
                    pygame.draw.line(surf, (210, 240, 250), (win.x + 4, win.y + 3),
                                     (win.right - 4, win.y + 3), 2)
                cabr = pygame.Rect(body.x + body.w if tr["dir"] > 0 else body.x - 34,
                                   r.y - 8, 34, 40)
                pygame.draw.rect(surf, (54, 74, 112), cabr)
                pygame.draw.rect(surf, (26, 36, 54), cabr, 2)
                pygame.draw.rect(surf, (170, 212, 240), (cabr.x + 5, cabr.y + 8, 22, 18))
                pygame.draw.line(surf, (26, 36, 54), (cabr.x + 5, cabr.y + 17), (cabr.right - 5, cabr.y + 17), 2)
                if tr["dir"] > 0:
                    shield = pygame.Rect(cabr.right - 9, cabr.y + 4, 6, 28)
                else:
                    shield = pygame.Rect(cabr.x + 3, cabr.y + 4, 6, 28)
                pygame.draw.rect(surf, (150, 205, 235), shield)
                pygame.draw.rect(surf, (26, 36, 54), shield, 1)
                for wx in (body.x + 24, body.x + body.w - 32):
                    pygame.draw.circle(surf, (30, 30, 34), (wx, r.bottom), 14)
                    pygame.draw.circle(surf, (200, 120, 40), (wx, r.bottom), 5)
                if tr["drive"] is not None:
                    flash = (255, 240, 120) if int(self.t * 10) % 2 == 0 else (255, 200, 40)
                    pygame.draw.ellipse(surf, flash, (r.x + 30, r.y + 40, r.w - 60, r.h - 70), 3)
        elif self.map_id == "minestick":
            if self.mine_stage == "normal":
                self._draw_mine_mobs(surf, cam)
            if self.dragon is not None and not self.dragon["dead"]:
                d = self.dragon
                cx = int(d["x"] - cam.x)
                cy = int(d["y"] - cam.y)
                w_, h_ = d["wobbly"] = getattr(d, "wobbly", 0.0) + 0.06, None
                bob = int(math.sin(w_) * 6)
                pygame.draw.ellipse(surf, (70, 40, 70), (cx - 34, cy - 16 + bob, 68, 34))
                pygame.draw.polygon(surf, (110, 50, 90), [(cx - 20, cy - 10 + bob),
                                                          (cx - 28, cy - 44 + bob), (cx + 8, cy - 24 + bob)])
                pygame.draw.polygon(surf, (110, 50, 90), [(cx + 20, cy - 10 + bob),
                                                          (cx + 28, cy - 44 + bob), (cx - 8, cy - 24 + bob)])
                pygame.draw.circle(surf, (80, 160, 70), (cx + 30, cy - 8 + bob), 10)
                pygame.draw.circle(surf, (255, 240, 90), (cx + 34, cy - 10 + bob), 3)
                pygame.draw.line(surf, (90, 200, 80), (cx - 38, cy - 6 + bob), (cx - 56, cy + 4 + bob), 5)
                pygame.draw.line(surf, (90, 200, 80), (cx - 48, cy + 8 + bob), (cx - 62, cy + 12 + bob), 5)
                pygame.draw.line(surf, (60, 200, 120), (cx - 30, cy - 20 + bob),
                                 (cx - 30, cy - 34 + bob + math.sin(w_ * 1.3) * 5), 4)
                pygame.draw.line(surf, (60, 200, 120), (cx + 34, cy - 20 + bob),
                                 (cx + 34, cy - 34 + bob + math.sin(w_ * 1.1) * 5), 4)
            if self.crystal is not None:
                c = self.crystal
                cx = int(c["x"] - cam.x)
                cy = int(c["y"] - cam.y)
                bob2 = int(math.sin(self.t * 3.0) * 3)
                cy += bob2
                pygame.draw.circle(surf, (255, 230, 140), (cx, cy + 6), 30)
                pygame.draw.circle(surf, (255, 200, 60), (cx, cy + 6), 20)
                pygame.draw.polygon(surf, (120, 220, 120), [(cx, cy - 26), (cx + 18, cy),
                                                            (cx, cy + 26), (cx - 18, cy)])
                pygame.draw.polygon(surf, (160, 255, 160), [(cx, cy - 26), (cx + 11, cy),
                                                            (cx, cy + 12), (cx - 11, cy)])
                pygame.draw.line(surf, (255, 255, 255), (cx, cy - 34), (cx, cy - 46), 3)
                pygame.draw.circle(surf, (255, 255, 220), (cx, cy - 48), 4)
                own = self.p1 if c["owner"] == 1 else self.p2
                pygame.draw.line(surf, (255, 230, 140), (cx, cy - 26),
                                 (int(own.x - cam.x), int(own.y - 74 - cam.y)), 2)
        elif self.map_id == "johnny":
            if not self.johnny["dead"]:
                gx, gy = 500.0, float(GROUND_Y)
                col = (120, 60, 200)
                head = (int(gx - cam.x), int(gy - 400 - cam.y))
                sway = math.sin(self.t * 1.8) * 14
                pygame.draw.circle(surf, (255, 220, 120), head, 22)
                pygame.draw.circle(surf, col, head, 22, 3)
                pygame.draw.line(surf, col, (gx - cam.x, gy - 360 - cam.y),
                                 (gx - cam.x, gy - 160 - cam.y), 14)
                pygame.draw.line(surf, col, (gx - cam.x, gy - 300 - cam.y),
                                 (gx - 100 - cam.x, gy - 220 - cam.y + sway), 10)
                pygame.draw.line(surf, col, (gx - cam.x, gy - 300 - cam.y),
                                 (gx + 100 - cam.x, gy - 150 - cam.y - sway), 10)
                pygame.draw.line(surf, col, (gx - cam.x, gy - 160 - cam.y),
                                 (gx - 50 - cam.x, gy - cam.y), 12)
                pygame.draw.line(surf, col, (gx - cam.x, gy - 160 - cam.y),
                                 (gx + 50 - cam.x, gy - cam.y), 12)
                pygame.draw.circle(surf, (255, 240, 160), (gx - cam.x, gy - 250 - cam.y), 16)
        elif self.map_id == "zombi":
            self._draw_mine_mobs(surf, cam)
        elif self.map_id == "boss":
            if self.boss is not None:
                self._draw_boss(surf, cam)
            for b in self.blaze_balls:
                bx, by = int(b["x"] - cam.x), int(b["y"] - cam.y)
                pygame.draw.circle(surf, (255, 200, 60), (bx, by), 7)
                pygame.draw.circle(surf, (255, 120, 20), (bx, by), 7, 2)
                pygame.draw.circle(surf, (255, 240, 150), (bx + 2, by - 2), 3)
            gy = int(GROUND_Y - cam.y)
            for st in self.stalagmites:
                x = int(st["x"] - cam.x)
                t = st["t"]
                if t <= STALAGMITE_GROW:
                    hgt = int(60 * (t / STALAGMITE_GROW))
                elif t <= STALAGMITE_END:
                    hgt = 60
                else:
                    hgt = int(60 * max(0.0, 1.0 - (t - STALAGMITE_END) /
                                       max(0.01, STALAGMITE_LIFE - STALAGMITE_END)))
                if hgt > 2:
                    pygame.draw.polygon(surf, (144, 122, 104),
                                        [(x - 12, gy), (x, gy - hgt), (x + 12, gy)])
                    pygame.draw.polygon(surf, (112, 92, 76),
                                        [(x - 12, gy), (x, gy - hgt), (x + 12, gy)], 3)
            for wb in self.boss_webs:
                wx = int(wb["x"] - cam.x)
                gy2 = int(GROUND_Y - cam.y)
                pygame.draw.ellipse(surf, (190, 225, 235), (wx - 38, gy2 - 7, 76, 14))
                pygame.draw.ellipse(surf, (70, 95, 105), (wx - 38, gy2 - 7, 76, 14), 2)
                for k in (-22, 0, 22):
                    pygame.draw.line(surf, (215, 240, 245), (wx + k - 9, gy2 - 12),
                                     (wx + k + 9, gy2 - 4), 2)
                    pygame.draw.line(surf, (150, 200, 210), (wx + k - 9, gy2 - 4),
                                     (wx + k + 9, gy2 - 12), 2)
            for sp in self.boss_splashes:
                sx, sy = int(sp["x"] - cam.x), int(sp["y"] - cam.y)
                if sp.get("fire"):
                    pygame.draw.circle(surf, (255, 210, 80), (sx, sy), 7)
                    pygame.draw.circle(surf, (255, 120, 20), (sx, sy), 7, 2)
                    pygame.draw.circle(surf, (255, 240, 150), (sx + 2, sy - 2), 3)
                else:
                    pygame.draw.circle(surf, (150, 116, 70), (sx, sy), 8)
                    pygame.draw.circle(surf, (96, 70, 44), (sx, sy), 8, 2)
                    pygame.draw.circle(surf, (205, 175, 125), (sx - 3, sy - 2), 3)
            for te in self.boss_tele:
                f = te["t"] / 0.5
                if f >= 1.0:
                    continue
                r = max(1, int(6 + 26 * (1 - f)))
                px, py = int(te["x"] - cam.x), int(te["y"] - cam.y)
                pygame.draw.circle(surf, (150 + int(70 * f), 90 + int(50 * f),
                                          240 - int(120 * f)), (px, py), r)
                pygame.draw.circle(surf, (230, 180, 255), (px, py),
                                   max(2, r // 2), 2)
        elif self.map_id == "football":
            self._draw_football(surf, cam)
        elif self.map_id == "laserrun":
            self._draw_laserrun(surf, cam)

    def _draw_mine_mobs(self, surf, cam):
        for mob in self.mobs:
            cx = int(mob["x"] - cam.x)
            cy = int(mob["y"] - cam.y)
            if cx < -80 or cx > surf.get_width() + 80:
                continue
            fam = mob.get("family", mob["kind"])
            col = mob.get("color") or MOB_COLORS.get(fam, (120, 120, 120))
            s = mob.get("mscale", 1.0)
            chars.draw_creature(surf, cx, cy, s, col, fam, mob["kind"],
                                mob.get("wobbly", 0.0) + self.t,
                                {"dir": mob.get("dir", 1),
                                 "sizzle": mob.get("sizzle", 0.0)})
            fr = mob["hp"] / max(1.0, mob.get("max_hp", mob["hp"]))
            if fr < 0.999:
                bw = int(40 * s)
                bar = pygame.Rect(cx - bw // 2, cy - int(78 * s), bw, 4)
                pygame.draw.rect(surf, (30, 12, 16), bar.inflate(2, 2))
                pygame.draw.rect(surf, (220, 60, 70),
                                 (bar.x, bar.y, int(bw * max(0.0, fr)), 4))
        for b in self.blaze_balls:
            bx, by = int(b["x"] - cam.x), int(b["y"] - cam.y)
            pygame.draw.circle(surf, (255, 200, 60), (bx, by), 7)
            pygame.draw.circle(surf, (255, 245, 180), (bx, by), 3)

    def _draw_minestick_bar(self, surf):
        stage = self._stage()
        names = {"normal": "AÇIK MADEN", "nether": "NETHER", "end": "END"}
        col = (255, 255, 255) if stage != "nether" else (255, 160, 60)
        if stage == "end" and self.dragon is not None and not self.dragon["dead"]:
            draw_text(surf, names[stage], 20, col, (SCREEN_W // 2, 96))
        elif stage == "normal":
            m = self.map
            px = m._portal_rect()
            if m.portal_lit:
                draw_text(surf, "PORTAL YANDI  •  İÇİNE GİR", 20, (120, 255, 160),
                          (SCREEN_W // 2, 88))
            elif px is not None:
                n = len(m.portal_blocks)
                draw_text(surf, "PORTAL: %d/3  •  LAV GÖLÜ YANINDA YANAR" % n, 20,
                          (255, 220, 120), (SCREEN_W // 2, 88))
            else:
                draw_text(surf, "ORMANDAKİ AĞAÇLARI KIR (E)  •  T: CRAFT", 20, col,
                          (SCREEN_W // 2, 88))
            if m.end_portal_active:
                draw_text(surf, "ENDER PORTALI AKTİF  •  İÇİNE GİR", 20, (140, 255, 180),
                          (SCREEN_W // 2, 148))
            line = "E: KIR  •  S+E: OBSİDYEN(BLOK)  •  R: BLOK KOY  •  Q: SU DÖK"
            draw_text(surf, line, 15, (225, 225, 235), (SCREEN_W // 2, 118))
            self._draw_inventory(surf)
        elif stage == "nether":
            draw_text(surf, "NETHER  •  YAKLAŞAN PORTALA GİR: GERİ DÖN", 18, col,
                      (SCREEN_W // 2, 92))
            draw_text(surf, "KALEYE ÇIK: BLAZE  •  ADADAKİ ENDERMEN: ENDER İNCİSİ",
                      15, (240, 220, 180), (SCREEN_W // 2, 122))
            self._draw_inventory(surf)
        if stage == "end" and self.dragon is not None and not self.dragon["dead"]:
            d = self.dragon
            bx, by, bw = SCREEN_W // 2 - 260, 112, 520
            pygame.draw.rect(surf, (40, 20, 30), (bx, by, bw, 18))
            pygame.draw.rect(surf, (40, 20, 30), (bx, by, bw, 18), 2)
            fill = int(bw * max(0.0, d["hp"] / d["max"]))
            pygame.draw.rect(surf, (200, 30, 40), (bx, by, fill, 18))
            draw_text(surf, "EJDERHA", 15, (255, 220, 220), (SCREEN_W // 2, by + 9))
        self._draw_craft(surf)

    def _draw_inventory(self, surf):
        inv = self.p1.inv
        keys = [k for k in ITEM_NAMES if inv.get(k, 0) > 0]
        if not keys:
            draw_text(surf, "ENV: (boş)", 16, (200, 200, 220), (SCREEN_W // 2, 148))
            return
        parts = ["%s:%d" % (ITEM_NAMES.get(k, k), inv[k]) for k in keys]
        draw_text(surf, "ENV: " + "  ".join(parts), 16, (255, 255, 220),
                  (SCREEN_W // 2, 148))

    def _draw_craft(self, surf):
        if not self.craft_open:
            return
        p = self._craft_owner_p()
        lay = self._craft_layout()
        T = 40
        bg = pygame.Rect(lay["grid"].x - 20, lay["up"].y - 12,
                         lay["inv"].right - lay["grid"].x + 40,
                         lay["inv"].bottom - lay["up"].y + 24)
        overlay = pygame.Surface((bg.w, bg.h), pygame.SRCALPHA)
        overlay.fill((18, 12, 24, 225))
        surf.blit(overlay, (bg.x, bg.y))
        draw_text(surf, "CRAFT  •  ☞:ELLE KOY  ⇦:GERİ AL  ÇIKTIYA TIKLA:AL",
                  15, (255, 240, 180), (lay["grid"].centerx, lay["up"].y - 22))
        # 3x3 ızgara
        for idx, cr in enumerate(lay["cells"]):
            r, c = divmod(idx, 3)
            pygame.draw.rect(surf, (40, 34, 52), cr)
            pygame.draw.rect(surf, (120, 110, 150), cr, 2)
            if self.craft_sel == [r, c]:
                pygame.draw.rect(surf, (255, 220, 120), cr, 3)
            entry = self.craft_grid[idx]
            if entry is not None:
                key, qty = entry
                col = ITEM_COLORS.get(key, (200, 200, 200))
                pygame.draw.rect(surf, col, (cr.x + 6, cr.y + 6, T - 12, T - 12))
                pygame.draw.rect(surf, (20, 20, 30), (cr.x + 6, cr.y + 6, T - 12, T - 12), 2)
                draw_text(surf, str(qty), 16, (255, 255, 255), (cr.right - 10, cr.top + 10))
        # çıktı
        pygame.draw.rect(surf, (52, 60, 44), lay["out"])
        pygame.draw.rect(surf, (150, 255, 160), lay["out"], 2)
        if self.craft_out is not None:
            col = ITEM_COLORS.get(self.craft_out, (200, 200, 200))
            pygame.draw.rect(surf, col, (lay["out"].x + 6, lay["out"].y + 6, T - 12, T - 12))
            draw_text(surf, "ÇIKTI", 11, (180, 255, 190), (lay["out"].centerx, lay["out"].top - 6))
        else:
            draw_text(surf, "TARİF YOK", 11, (200, 200, 220), (lay["out"].centerx, lay["out"].bottom + 12))
        # envanter penceresi
        pygame.draw.rect(surf, (30, 26, 40), lay["inv"])
        pygame.draw.rect(surf, (120, 110, 150), lay["inv"], 2)
        for i, cr in enumerate(lay["slots"]):
            pygame.draw.rect(surf, (52, 44, 66), cr)
            pygame.draw.rect(surf, (120, 110, 150), cr, 1)
        items = self._craft_window(p)
        for i, key in enumerate(items):
            cr = lay["slots"][i]
            col = ITEM_COLORS.get(key, (200, 200, 200))
            pygame.draw.rect(surf, col, (cr.x + 4, cr.y + 4, cr.w - 8, cr.h - 8))
            pygame.draw.rect(surf, (20, 20, 30), (cr.x + 4, cr.y + 4, cr.w - 8, cr.h - 8), 2)
            draw_text(surf, str(p.inv[key]), 14, (255, 255, 255), (cr.right - 6, cr.bottom - 6))
        draw_text(surf, "▲", 20, (255, 255, 255), lay["up"].center)
        draw_text(surf, "▼", 20, (255, 255, 255), lay["down"].center)
        # imleçteki eşya
        if self.craft_cursor is not None:
            mp = pygame.mouse.get_pos()
            key, qty = self.craft_cursor
            col = ITEM_COLORS.get(key, (200, 200, 200))
            pygame.draw.rect(surf, col, (mp[0] - 14, mp[1] - 14, 28, 28))
            pygame.draw.rect(surf, (20, 20, 30), (mp[0] - 14, mp[1] - 14, 28, 28), 2)
            draw_text(surf, str(qty), 14, (255, 255, 255), (mp[0] + 14, mp[1] + 16))

    def _draw_johnny_bar(self, surf):
        j = self.johnny
        for i in range(2):
            bx, by = 120 + i * 270, 112
            draw_text(surf, f"OYUNCU {i + 1}", 14, (200, 200, 220), (bx + 60, by - 12))
            pygame.draw.rect(surf, (40, 30, 60), (bx, by, 120, 16))
            pygame.draw.rect(surf, (120, 60, 200), (bx, by, int(120 * min(1.0, j["scores"][i] / JOHNNY_WIN_COUNT)), 16))
            draw_text(surf, f"{j['scores'][i]}/{JOHNNY_WIN_COUNT}", 15, (255, 255, 255), (bx + 60, by + 8))
        if j["phase"] == "say":
            pygame.draw.circle(surf, (120, 60, 200), (SCREEN_W // 2, 200), 34)
            pygame.draw.circle(surf, (200, 160, 255), (SCREEN_W // 2, 200), 34, 3)
            draw_text(surf, JOHNNY_CMDS[j["cmd"]], 42, (255, 255, 255), (SCREEN_W // 2, 200))
        elif not j["dead"]:
            pygame.draw.circle(surf, (90, 46, 150), (SCREEN_W // 2, 170), 26)
            pygame.draw.circle(surf, (160, 120, 220), (SCREEN_W // 2, 170), 26, 3)

    def _draw_fx(self, surf, cam):
        for fx in self.fx:
            pr = fx["t"] / 0.9
            y = fx["y"] - cam.y - 40 * pr
            col = blend(GOLD, (255, 255, 255), 0.2) if fx["gold"] else (255, 255, 255)
            col = blend(col, (0, 0, 0), pr)
            draw_text(surf, fx["txt"], 24, col, (int(fx["x"] - cam.x), int(y)))

    def _draw_coins(self, surf, cam):
        for c in self.coins:
            pr = c["t"] / 0.8
            r = max(2, int(9 * (1 - pr)))
            col = blend((255, 224, 90), (255, 120, 40), pr)
            pygame.draw.circle(surf, col,
                               (int(c["x"] - cam.x), int(c["y"] - cam.y)), r)

    def _draw_notice(self, surf):
        if self.notice is None:
            return
        nt = self.notice
        pr = nt["t"] / nt["dur"]
        fade = min(1.0, pr * 4) * min(1.0, (1 - pr) * 4)
        # Arka plan şeridi
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        band = pygame.Rect(0, SCREEN_H // 2 - 95, SCREEN_W, 110)
        pygame.draw.rect(ov, (0, 0, 0, int(170 * fade)), band)
        surf.blit(ov, (0, 0))
        scale = 1.0 + 0.12 * math.sin(nt["t"] * 10)
        center = (SCREEN_W // 2, SCREEN_H // 2 - 45)
        sh = blend(GOLD, (40, 40, 55), pr)
        draw_text(surf, nt["title"], int(46 * scale), sh, center, bold=True)
        draw_text(surf, nt["sub"], 26, (130, 255, 150),
                  (center[0], center[1] + 46), bold=True)

    def _draw_zombie_bar(self, surf):
        dz = self.zombie
        done = dz["wave"]
        draw_text(surf, f"DALGA {done}", 22, (200, 220, 150),
                  (SCREEN_W // 2 - 170, 60))
        draw_text(surf, f"SAYI: P1 {dz['kills'][0]} - {dz['kills'][1]} P2",
                  20, (255, 240, 180), (SCREEN_W // 2 + 160, 60))
        draw_text(surf, f"KALAN: {len(self.mobs)}", 18, (255, 180, 120),
                  (SCREEN_W // 2, 96))
        draw_text(surf, "SINIRSIZ DALGA  •  İKİSİ DE ÖLÜNCE BİTER  •  EN ÇOK ÖLDÜREN KAZANIR",
                  15, (200, 205, 220), (SCREEN_W // 2, 120))

    def _draw_football_bar(self, surf):
        st = self.foot_state
        s = st["score"]
        draw_text(surf, "FUTBOL", 24, (255, 230, 120), (SCREEN_W // 2, 40))
        draw_text(surf, f"P1 {s[0]}  -  {s[1]} P2", 30, (255, 255, 255), (SCREEN_W // 2, 76))
        draw_text(surf, f"İLK {FOOT_GOAL_SCORE} GOL KAZANIR", 15, (200, 205, 220),
                  (SCREEN_W // 2, 108))
        draw_text(surf, "1. ÖZELLİK: DÜZ VURUŞ  •  2. ÖZELLİK: HAVAYA VURUŞ", 15,
                  (180, 200, 230), (SCREEN_W // 2, 134))

    def _draw_laserrun_bar(self, surf):
        st = self.lr_state
        draw_text(surf, "LAZER RUN", 24, (255, 100, 120), (SCREEN_W // 2, 40))
        t = max(0, 60 - int(st["time"]))
        draw_text(surf, f"SÜRE: {t}s", 28, (255, 255, 200), (SCREEN_W // 2, 76))
        draw_text(surf, "ZIPLA / EĞİL  •  BLOKLARDAN KAÇ  •  LAZERLERE DOKUNMA", 15,
                  (200, 220, 255), (SCREEN_W // 2, 108))
        # can göstergesi
        for i, p in enumerate((self.p1, self.p2)):
            x = 80 + i * (SCREEN_W - 160)
            c = p.color
            pygame.draw.rect(surf, (40, 20, 30), (x, 20, 200, 18))
            fill = int(200 * max(0.0, p.hp / 100.0))
            pygame.draw.rect(surf, c, (x, 20, fill, 18))
            draw_text(surf, f"P{i+1}: {int(p.hp)}", 14, (255, 255, 255), (x + 100, 29))

    def _draw_boss_bar(self, surf):
        bx, by, bw = SCREEN_W // 2 - 300, 20, 600
        draw_text(surf, "BOSS FIGHTS", 22, (220, 180, 255), (SCREEN_W // 2, 16))
        if self.boss is None:
            if self.winner is not None:
                return
            draw_text(surf, "SONRAKİ BOSS GELİYOR...", 20, (255, 240, 180),
                      (SCREEN_W // 2, 60))
            return
        cfg = self.boss
        draw_text(surf, f"BOSS {cfg['i'] + 1}/{len(BOSSES)}  •  {cfg['name']}", 20,
                  (255, 220, 255), (SCREEN_W // 2, 46))
        draw_text(surf, "ÖZEL GÜÇ: " + BOSS_POWER_NAMES.get(cfg["kind"], "?"),
                  15, (255, 235, 150), (SCREEN_W // 2, by + 92))
        pygame.draw.rect(surf, (40, 20, 30), (bx, by + 60, bw, 20))
        pygame.draw.rect(surf, (40, 20, 30), (bx, by + 60, bw, 20), 2)
        fill = int(bw * max(0.0, cfg["hp"] / cfg["max_hp"]))
        pygame.draw.rect(surf, (200, 40, 60), (bx, by + 60, fill, 20))
        draw_text(surf, "YENİLEN: %d/%d" % (self.boss_id, len(BOSSES)), 15,
                  (255, 235, 210), (SCREEN_W // 2, by + 70))

    def _draw_boss(self, surf, cam):
        cfg = self.boss
        cx = int(cfg["x"] - cam.x)
        cy = int(cfg["y"] - cam.y)
        frac = max(0.0, cfg["hp"] / max(1.0, cfg["max_hp"]))
        chars.draw_boss(surf, cx, cy, cfg["size"], cfg["color"], cfg["kind"], frac,
                        cfg.get("wobbly", 0.0),
                        {"dir": cfg.get("dir", 1), "flash": cfg.get("flash", 0.0)})

    def _draw_football(self, surf, cam):
        b = self.foot_state["ball"]
        bx = int(b["x"] - cam.x)
        by = int(b["y"] - cam.y)
        pygame.draw.circle(surf, (240, 240, 245), (bx, by), FOOT_BALL_R)
        pygame.draw.circle(surf, (60, 60, 80), (bx, by), FOOT_BALL_R, 3)
        pygame.draw.circle(surf, (120, 120, 140), (bx, by), 4)

    def _draw_laserrun(self, surf, cam):
        st = self.lr_state
        for bl in st["blocks"]:
            bx = int(bl["x"] - cam.x)
            by = int(bl["y"] - cam.y)
            r = pygame.Rect(bx, by, bl["w"], bl["h"])
            pygame.draw.rect(surf, (120, 80, 50), r)
            pygame.draw.rect(surf, (80, 50, 30), r, 2)
            # blok detay
            pygame.draw.line(surf, (160, 120, 80), (r.x + 4, r.y + 4), (r.right - 4, r.y + 4), 2)
            pygame.draw.line(surf, (60, 30, 10), (r.x + 4, r.bottom - 4), (r.right - 4, r.bottom - 4), 2)

    def _draw_result(self, surf):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surf.blit(ov, (0, 0))
        w = self.p1 if self.winner == 1 else self.p2
        lx = SCREEN_W // 2 - 230
        draw_text(surf, f"OYUNCU {self.winner} KAZANDI", 54, GOLD, (lx, 250))
        draw_text(surf, w.defn["name"], 32, (255, 255, 255), (lx, 322))
        draw_text(surf, f"CAN: {int(round(w.hp))}", 28, (130, 255, 150), (lx, 372))
        rx = SCREEN_W // 2 + 260
        draw_text(surf, f"OYUNCU {3 - self.winner} GAME OVER", 44, (255, 80, 80), (rx, 300))
        draw_text(surf, "ENTER: ANA MENÜ", 28, (255, 255, 255), (SCREEN_W // 2, 560))