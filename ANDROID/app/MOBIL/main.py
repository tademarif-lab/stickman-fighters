import sys
import time
import pygame
import ui
import settings
import savegame
import savegame
from touch import TouchLayout, TouchInput
from settings import *
from fight import Fight


class PlayerInput:
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False
        self.crouch = False
        self.jump_pressed = False
        self.ability1_pressed = False
        self.ability2_pressed = False
        self.ability3_pressed = False
        self.ult_pressed = False
        self.craft_pressed = False
        self.place_pressed = False
        self.mouse_pos = (0, 0)
        self.left_click = False
        self.right_click = False

    def reset_edges(self):
        self.jump_pressed = False
        self.ability1_pressed = False
        self.ability2_pressed = False
        self.ability3_pressed = False
        self.ult_pressed = False
        self.craft_pressed = False
        self.place_pressed = False
        self.left_click = False
        self.right_click = False


class Game:
    def __init__(self, w=None, h=None, mobile=False):
        pygame.init()
        self.mobile = bool(mobile)
        if self.mobile:
            settings.MOBILE = True
            mw, mh = settings.mobile_setup(w or 0, h or 0)
            self._sync_screen(mw, mh)
            self.screen = pygame.display.set_mode((mw, mh), pygame.FULLSCREEN)
            self.W, self.H = mw, mh
            self.touch_layout = TouchLayout(mw, mh)
            self.touch = TouchInput(self.touch_layout)
        else:
            self.screen = pygame.display.set_mode((w or SCREEN_W,
                                                   h or SCREEN_H))
            self.W, self.H = SCREEN_W, SCREEN_H
            self.touch_layout = None
            self.touch = None
        self.frame = pygame.Surface((self.W, self.H))
        settings.set_logical_surface(self.frame)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.t = 0.0
        self.fullscreen = False
        self.p1 = PlayerInput()
        self.p2 = PlayerInput()
        self.mouse_held = {1: False, 2: False, 3: False}
        self.mouse_press_t = {1: 0.0, 3: 0.0}
        self.state = "menu"
        self.screens = {"menu": ui.MenuScreen()}
        self.map_id = "grass"
        self.fight = None

    def current(self):
        return self.screens.get(self.state)

    def start_select(self, map_id=None):
        self.screens["select"] = ui.SelectScreen()
        if map_id is not None:
            self.screens["select"].map_id = map_id
        self.state = "select"

    def open_changelog(self):
        self.screens["changelog"] = ui.ChangelogScreen()
        self.state = "changelog"

    def start_fight(self):
        import savegame
        sel = self.screens["select"]
        picks = [ROSTER[sel.p1["char"]], ROSTER[sel.p2["char"]]]
        for pk in picks:
            if pk.get("locked"):
                sel.notice = "%s kilitli - dükkan: %s" % (
                    pk["name"], savegame.PACK_BY_ID.get(pk.get("pack"), {})
                    .get("name", "?").title())
                sel.notice_t = 2.5
                self.open_shop()
                return
        chars = []
        for pk in picks:
            d = dict(pk)
            if pk.get("class_def"):
                d["class_def"] = dict(pk["class_def"])
                d["class_def"]["levels"] = (pk["class_def"].get("levels")
                                            or [])[:savegame.level_of(pk["id"]) + 1]
                d["abilities"] = list(pk["class_def"]["abilities"])
            chars.append(d)
        colors = [sel.p1["color"], sel.p2["color"]]
        self.map_id = sel.map_id
        settings.PLAYER_MONEY = savegame.ruby()
        self.fight = Fight(chars, colors, self.map_id, 990.0)
        self.state = "fight"
        self._rewarded = False
        self._reset_inputs()
        pygame.mouse.set_visible(False)

    def _reward(self):
        """Mac sonu odulu: arena disi modlarda 0.5 Ruby."""
        f = self.fight
        if f is None or self._rewarded:
            return
        if f.map_id == "grass":
            return
        self._rewarded = True
        savegame.DATA["stats"]["games"] = savegame.DATA["stats"].get("games", 0) + 1
        got = savegame.add_ruby(0.5)
        settings.PLAYER_MONEY = got
        self.ruby_msg = "+0.5 Ruby  (Toplam %.2f)" % got
        self.ruby_msg_t = 4.0

    def to_menu(self):
        self._reward()
        self.state = "menu"
        self.screens["menu"] = ui.MenuScreen()
        self.fight = None
        self._reset_inputs()
        pygame.mouse.set_visible(True)

    def open_settings(self):
        self.state = "settings"
        self.screens["settings"] = ui.SettingsScreen()
        pygame.mouse.set_visible(True)

    def open_shop(self):
        self.state = "shop"
        self.screens["shop"] = ui.ShopScreen()
        pygame.mouse.set_visible(True)

    def open_online(self):
        from online import NetClient, OnlineScreen
        if getattr(self, "net", None) is None:
            self.net = NetClient()
        self.online_char = "human"
        self.online_color = (200, 60, 60)
        sel = self.screens.get("select")
        if sel is not None and ROSTER:
            c = ROSTER[sel.p1["char"]]
            if not c.get("locked"):
                self.online_char = c.get("id", "human")
                self.online_color = sel.p1["color"]
        self.state = "online"
        self.screens["online"] = OnlineScreen(self, self.net)
        pygame.mouse.set_visible(True)

    def quit(self):
        self.running = False

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
            self.fullscreen = False
        else:
            try:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.fullscreen = True
            except pygame.error:
                self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    def _reset_inputs(self):
        self.p1 = PlayerInput()
        self.p2 = PlayerInput()
        self.mouse_held = {1: False, 2: False, 3: False}
        self.mouse_press_t = {1: 0.0, 3: 0.0}

    def _sync_screen(self, w, h):
        """'from settings import *' yapan modullere yeni olceyi yayar."""
        import chars
        import fight as _f
        import hud as _h
        import maps as _m
        for mod in (ui, chars, _f, _h, _m):
            if hasattr(mod, "SCREEN_W"):
                mod.SCREEN_W = w
            if hasattr(mod, "SCREEN_H"):
                mod.SCREEN_H = h
        try:
            import online
            if hasattr(online, "SCREEN_W"):
                online.SCREEN_W = w
                online.SCREEN_H = h
        except Exception:
            pass

    def _finger_to_click(self, e):
        """Menulerde dokunma = tiklama."""
        pos = (int(e.x * self.W), int(e.y * self.H))
        settings.set_touch_pos(pos)
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)

    def _touch_ui(self, e):
        """Dokunma olayini isler; True donerse olay tuketildi."""
        if self.state == "fight" and self.touch is not None:
            return self.touch.handle_event(e)
        if e.type == pygame.FINGERDOWN:
            self.dispatch(self._finger_to_click(e))
            return True
        if e.type == pygame.FINGERUP:
            self.dispatch(pygame.event.Event(
                pygame.MOUSEBUTTONUP, button=1,
                pos=(int(e.x * self.W), int(e.y * self.H))))
            return True
        return False

    def dispatch(self, e):
        """Tek bir olayi dogru ekrana yollar."""
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            self.toggle_fullscreen()
            return
        if self.state == "fight":
            self._fight_event(e)
            return
        scr = self.current()
        if scr is not None:
            result = scr.handle_event(e, self)
            if result == "back":
                self.to_menu()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type in (pygame.FINGERDOWN, pygame.FINGERUP,
                            pygame.FINGERMOTION):
                if self.mobile:
                    self._touch_ui(e)
                continue
            else:
                self.dispatch(e)

    def _fight_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.to_menu()
                return
            if self.fight.winner is not None:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e,
                             pygame.K_SPACE):
                    self.to_menu()
                return
            if e.key in MOVE_KEYS:
                who, act = MOVE_KEYS[e.key]
                p = self.p1 if who == "p1" else self.p2
                setattr(p, act, True)
                if act == "jump":
                    p.jump_pressed = True
            if e.key in P1_ABILITY_KEYS:
                setattr(self.p1, P1_ABILITY_KEYS[e.key], True)
            return
        elif e.type == pygame.KEYUP:
            if e.key in MOVE_KEYS:
                who, act = MOVE_KEYS[e.key]
                p = self.p1 if who == "p1" else self.p2
                setattr(p, act, False)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self.fight.winner is not None:
                return
            b = e.button
            now = time.time()
            if self.fight.craft_open and b in (1, 3):
                owner = self.p1 if self.fight.craft_owner == 1 else self.p2
                owner.mouse_pos = e.pos
                if b == 1:
                    owner.left_click = True
                else:
                    owner.right_click = True
                self.mouse_held[b] = True
                self.mouse_press_t[b] = now
                return
            if b in (1, 3):
                other = 3 if b == 1 else 1
                both = self.mouse_held[other] or (now - self.mouse_press_t[other] <= 0.15)
                if both:
                    self.p2.ult_pressed = True
                elif b == 1:
                    self.p2.ability1_pressed = True
                else:
                    self.p2.ability2_pressed = True
            elif b == 2:
                self.p2.ability3_pressed = True
            self.mouse_held[b] = True
            self.mouse_press_t[b] = now
        elif e.type == pygame.MOUSEBUTTONUP:
            self.mouse_held[e.button] = False

    def update(self, dt):
        self.t += dt
        if self.mobile and self.touch is not None and self.state == "fight":
            self.touch.apply(self.p1)
            self.touch.apply(self.p2, dead=0.5)
        scr = self.screens.get("online")
        if self.state == "online" and scr is not None and scr.view is not None:
            inp = self.p1
            scr.update(dt)
            self.p1.reset_edges()
            self.p2.reset_edges()
            return
        if self.state == "fight":
            self.fight.update(dt, self.p1, self.p2)
            self.p1.reset_edges()
            self.p2.reset_edges()
        else:
            scr = self.current()
            if scr is not None:
                scr.update(dt)

    def draw(self):
        osc = self.screens.get("online")
        if self.state == "online" and osc is not None and osc.view is not None:
            osc.draw_match(self.frame)
            return
        if self.state == "fight":
            self.fight.draw(self.frame)
        else:
            scr = self.current()
            if scr is not None:
                scr.draw(self.frame)
        sw, sh = self.screen.get_size()
        if sw == SCREEN_W and sh == SCREEN_H:
            self.screen.blit(self.frame, (0, 0))
        else:
            k = min(sw / SCREEN_W, sh / SCREEN_H)
            w, h = int(SCREEN_W * k), int(SCREEN_H * k)
            self.screen.fill((0, 0, 0))
            self.screen.blit(pygame.transform.scale(self.frame, (w, h)),
                             ((sw - w) // 2, (sh - h) // 2))
        if self.mobile and self.touch is not None and settings.TOUCH_SHOW \
                and self.state == "fight":
            self.touch.draw(self.frame)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            if dt > 0.05:
                dt = 0.05
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


def run_smoke():
    g = Game()

    def frames(n):
        for _ in range(n):
            g.handle_events()
            g.update(1 / 60)
            g.draw()

    frames(5)
    g.start_select()
    frames(5)
    sel = g.screens["select"]
    sel.p1["color"] = (255, 0, 120)
    sel.p2["color"] = (0, 180, 120)
    sel.p1["cursor"] = 0
    frames(3)
    g.start_fight()
    frames(60)
    f = g.fight
    f.p2.x = f.p1.x + 35
    for i in range(300):
        f.p2.x = f.p1.x + 35
        if i == 5:
            g.p1.ability1_pressed = True
        if i == 60:
            g.p1.ability2_pressed = True
        if i == 120:
            g.p1.ability3_pressed = True
        if i == 200:
            f.p1.ult_pct = 100.0
            g.p1.ult_pressed = True
        g.update(1 / 60)
        g.draw()
        if i == 202:
            print("p1_hp:", f.p1.hp, "p2_hp:", f.p2.hp, "p1ult:", f.p1.ult_timer > 0)
    f.p1.ult_pct = 100.0
    f.p1.try_ult(f.p2)
    f.p2.hp = 0
    f.update(1 / 60, g.p1, g.p2)
    g.draw()
    print("winner:", f.winner)
    g.to_menu()
    frames(5)
    pygame.quit()
    print("SMOKE OK")


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        run_smoke()
    else:
        Game().run()