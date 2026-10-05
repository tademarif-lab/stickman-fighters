# -*- coding: utf-8 -*-
"""Online mod istemcisi: lobiden 4 kisilik odaya, 1v1 online mac."""
import socket
import threading
import time

import pygame

import netproto as np
from netproto import (HOST_DEFAULT, PORT, MAX_PLAYERS,
                      C_HELLO, C_ROOMS, C_CREATE, C_JOIN, C_LEAVE, C_READY,
                      C_START, C_CHAT, C_IN, C_PING,
                      S_WELCOME, S_ROOMS, S_JOINED, S_START, S_STATE,
                      S_OVER, S_MSG, S_BACK, S_ERR, S_PONG, S_NEEDPASS,
                      pack, recv_msg, blank_input, pack_input, apply_input,
                      player_state, draw_state, local_ip)

import settings
from settings import (SCREEN_W, SCREEN_H, GOLD, draw_text, blend, get_font,
                      make_bg, ROSTER, ROSTER_TOTAL)


class NetClient:
    """Arka planda calisan soket istemcisi."""

    def __init__(self):
        self.sock = None
        self.buf = b""
        self.my_id = 0
        self.connected = False
        self.rooms = []
        self.room = None
        self.is_host = False
        self.slots = []
        self.match = None          # {"p1":id,"p2":id}
        self.over = None
        self.state = None
        self.msgs = []
        self.err = ""
        self.match_running = False
        self.need_pass_room = 0
        self.chars = {}
        self.round = 0
        self.wins = {}
        self.lock = threading.Lock()
        self.thread = None
        self.stop = False
        self.name = "Oyuncu"
        self.char = "human"
        self.color = (200, 60, 60)
        self.latency = 0

    # ------------------------------------------------------------ baglanti
    def connect(self, host=HOST_DEFAULT, port=PORT, name="Oyuncu",
                char="human", color=(200, 60, 60)):
        self.name = name[:14]
        self.char = char
        self.color = tuple(color)
        try:
            s = socket.create_connection((host, port), timeout=6)
        except OSError as e:
            self.err = "Baglanilamadi: %s" % e
            return False
        s.setblocking(False)
        self.sock = s
        self.connected = True
        self.err = ""
        self.send({"t": C_HELLO, "name": self.name, "char": self.char,
                   "color": list(self.color)})
        self.stop = False
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        return True

    def disconnect(self):
        self.stop = True
        self.connected = False
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass
        self.sock = None
        self.room = None
        self.match_running = False

    def send(self, obj):
        if not self.sock:
            return
        try:
            self.sock.sendall(pack(obj))
        except OSError:
            self.connected = False

    # ------------------------------------------------------------ dinleme
    def _loop(self):
        while not self.stop:
            try:
                msg, self.buf = recv_msg(self.sock, self.buf)
            except Exception:
                break
            if msg is None:
                time.sleep(0.005)
                continue
            if msg is False:
                self.connected = False
                break
            self._handle(msg)

    def _handle(self, m):
        t = m.get("t")
        with self.lock:
            if t == S_WELCOME:
                self.my_id = m.get("id", 0)
            elif t == S_ROOMS:
                self.rooms = m.get("rooms", [])
            elif t == S_JOINED:
                self.room = m.get("room")
                self.is_host = bool(m.get("host"))
                self.match_running = False
            elif t == S_START:
                self.match_running = True
                self.room = m.get("room")
                self.round = m.get("round", 1)
                self.match = {"p1": m.get("p1"), "p2": m.get("p2")}
                self.chars = m.get("chars", {})
                self.over = None
            elif t == S_STATE:
                self.state = m.get("s")
            elif t == S_OVER:
                self.over = m.get("winner")
                self.wins = m.get("wins", {})
            elif t == S_MSG:
                self.msgs.append((m.get("name", "?"), m.get("text", "")))
                self.msgs = self.msgs[-6:]
            elif t == S_BACK:
                self.match_running = False
                self.match = None
                if m.get("why"):
                    self.msgs.append(("SUNUCU", m["why"]))
                    self.msgs = self.msgs[-6:]
            elif t == S_NEEDPASS:
                self.need_pass_room = m.get("room", 0)
                self.err = "Bu oda kilitli - sifreyi gir"
            elif t == S_ERR:
                self.err = m.get("why", "Hata")
        if t == C_HELLO:
            pass

    # ------------------------------------------------------------ komutlar
    def refresh(self):
        self.send({"t": C_ROOMS})

    def create(self, name="Oda", password=""):
        self.send({"t": C_CREATE, "name": name, "pass": password})

    def join(self, rid, password=""):
        self.send({"t": C_JOIN, "room": rid, "pass": password})

    def leave(self):
        self.send({"t": C_LEAVE})
        self.room = None

    def ready(self, v=True):
        self.send({"t": C_READY, "v": v})

    def start(self):
        self.send({"t": C_START})

    def chat(self, text):
        self.send({"t": C_CHAT, "text": text})

    def send_input(self, inp):
        self.send({"t": C_IN, "i": pack_input(inp)})

    def slot_me(self, room):
        if not room:
            return None
        for p in room.get("players", []):
            if p.get("id") == self.my_id:
                return p
        return None

    def my_char(self):
        sl = None
        for r in self.rooms:
            if r.get("id") == self.room:
                for p in r.get("players", []):
                    if p.get("id") == self.my_id:
                        sl = p
        if sl:
            return sl.get("char", "human"), tuple(sl.get("color", (200, 60, 60)))
        return self.char, self.color


# ============================================================ ONLINE EKRAN
class OnlineScreen:
    def __init__(self, game, client):
        self.g = game
        self.net = client
        self.t = 0.0
        self.bg = make_bg(SCREEN_W, SCREEN_H, settings.BG_COLOR,
                          tuple(max(0, c - 40) for c in settings.BG_COLOR))
        self.host = HOST_DEFAULT
        self.port = PORT
        self.name = "Oyuncu"
        self.cursor = 0
        self.room_list = pygame.Rect(60, 210, 640, 420)
        self.slot_rects = []
        self.btn = {}
        self._build()
        self.focus = "host"
        self.edit = ""
        self.err_t = 0.0
        self.view = None
        self.password = ""
        self.need_room = 0

    def _build(self):
        self.host_box = pygame.Rect(40, 128, 250, 34)
        self.port_box = pygame.Rect(302, 128, 120, 34)
        self.name_box = pygame.Rect(434, 128, 200, 34)
        self.pass_box = pygame.Rect(646, 128, 170, 34)
        cx = 850
        self.btn["baglan"] = pygame.Rect(cx, 128, 140, 34)
        self.btn["yenile"] = pygame.Rect(cx + 150, 128, 120, 34)
        self.btn["kur"] = pygame.Rect(cx, 172, 250, 34)
        self.btn["baslat"] = pygame.Rect(cx, 216, 250, 40)
        self.btn["cikis"] = pygame.Rect(cx, 266, 250, 34)
        self.btn["geri"] = pygame.Rect(60, 648, 180, 40)
        self.chat_box = pygame.Rect(360, 648, 630, 40)

    # ------------------------------------------------------------ girdi
    def handle_event(self, e, game=None):
        if e.type == pygame.KEYDOWN:
            k = e.key
            if k == pygame.K_ESCAPE:
                if self.focus == "mesaj":
                    self.focus = "host"
                else:
                    game.to_menu()
                return True
            if k == pygame.K_TAB:
                order = ["host", "port", "isim", "sifre", "mesaj"]
                self.focus = order[(order.index(self.focus) + 1) % len(order)]
                self.edit = ""
                return True
            if k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.focus == "mesaj":
                    if self.edit.strip():
                        self.net.chat(self.edit.strip())
                    self.edit = ""
                    self.focus = "host"
                elif self.focus == "sifre":
                    self.send_password()
                else:
                    self.connect()
                return True
            if k == pygame.K_BACKSPACE:
                self.edit = self.edit[:-1]
                return True
            if self.focus == "host" and e.unicode.isprintable():
                self.edit += e.unicode
                return True
            if self.focus == "port" and e.unicode.isdigit():
                self.edit += e.unicode
                return True
            if self.focus == "isim" and e.unicode.isprintable():
                self.edit += e.unicode
                return True
            if self.focus in ("sifre", "mesaj") and e.unicode.isprintable():
                self.edit += e.unicode
                return True
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = e.pos
            for key, r in self.btn.items():
                if r.collidepoint(pos):
                    self.press(key)
                    return True
            if self.host_box.collidepoint(pos):
                self.focus, self.edit = "host", self.host
            elif self.port_box.collidepoint(pos):
                self.focus, self.edit = "port", str(self.port)
            elif self.name_box.collidepoint(pos):
                self.focus, self.edit = "isim", self.name
            elif self.pass_box.collidepoint(pos):
                self.focus, self.edit = "sifre", ""
            elif self.chat_box.collidepoint(pos):
                self.focus, self.edit = "mesaj", ""
            else:
                for i, r in enumerate(self.slot_rects):
                    if r.collidepoint(pos):
                        rid = self.room_at(i)
                        if rid is None or self.net.room is not None:
                            return True
                        if self.locked_at(i):
                            self.need_room = rid
                            self.focus, self.edit = "sifre", ""
                            self.err = "Kilitli oda - sifreyi gir ve ENTER"
                            self.err_t = 5.0
                        else:
                            self.net.join(rid)
                        return True
        return False

    def press(self, key):
        n = self.net
        if key == "baglan":
            self.connect()
        elif key == "yenile":
            n.refresh()
        elif key == "kur":
            n.create("Oda " + self.name[:8], self.password)
        elif key == "baslat":
            n.start()
        elif key == "cikis":
            n.leave()
        elif key == "geri":
            n.disconnect()
            self.g.to_menu()

    def connect(self):
        try:
            port = int(self.edit) if self.focus == "port" and self.edit else self.port
        except ValueError:
            port = self.port
        host = self.host if not (self.focus == "host" and self.edit) else self.edit
        nm = self.name if not (self.focus == "isim" and self.edit) else self.edit
        self.port = port
        if self.focus == "host":
            self.host = self.edit
            host = self.edit
        if self.focus == "isim":
            self.name = self.edit
            nm = self.edit
        if self.net.connect(host, port, nm, self.g.online_char,
                            self.g.online_color):
            self.edit = ""
            self.focus = "host"
        else:
            self.err_t = 4.0

    def locked_at(self, i):
        if i < len(self.net.rooms):
            return bool(self.net.rooms[i].get("locked"))
        return False

    def send_password(self):
        """Sifre alanindaki degeri ilgili islemde kullanir."""
        pw = self.edit.strip()
        self.edit = ""
        self.focus = "host"
        if self.need_room:
            self.net.join(self.need_room, pw)
            self.need_room = 0
            self.err = ""
            self.err_t = 0.0
        else:
            self.password = pw

    def room_at(self, i):
        if i < len(self.net.rooms):
            return self.net.rooms[i]["id"]
        return None

    def update(self, dt):
        self.t += dt
        self.err_t = max(0.0, self.err_t - dt)
        if self.net.connected and self.net.match_running and self.net.state:
            st = self.net.state
            p1 = draw_state(st["p1"])
            p2 = draw_state(st["p2"])
            i_am_p1 = (self.net.match and self.net.match.get("p1") == self.net.my_id)
            if i_am_p1:
                self.net.send_input(self.g.p1)
            else:
                self.net.send_input(self.g.p2)
            if self.view is None:
                self._make_view(p1, p2)
            else:
                self._apply(p1, p2)
        else:
            self.view = None

    def _make_view(self, p1, p2):
        from fight import Fight
        from classes import CLASS_BY_ID
        cid = self.net.chars.get(str(self.net.match["p2" if
                                      self.net.match["p1"] == self.net.my_id
                                      else "p1"]), "human")
        cls = CLASS_BY_ID.get(cid)
        if cls:
            from savegame import class_char
            other = class_char(cid)
        else:
            from settings import CHARACTERS
            other = dict(CHARACTERS[0])
        me_id, other_id = ("p1", "p2")
        if self.net.match["p1"] != self.net.my_id:
            me_id, other_id = "p2", "p1"
        self.view = Fight([dict(CHARACTERS[0]), other],
                          [(200, 60, 60), (90, 140, 220)], "grass", 500.0)
        self.view.online = True
        self.view.me_slot = me_id

    def _apply(self, p1, p2):
        f = self.view
        if f is None:
            return
        me = f.p1 if f.me_slot == "p1" else f.p2
        ot = f.p2 if f.me_slot == "p1" else f.p1
        for src, dst in ((p1, f.p1), (p2, f.p2)):
            dst.x, dst.y = src.x, src.y
            dst.hp, dst.max_hp = src.hp, src.max_hp
            dst.shield, dst.max_shield = src.shield, src.max_shield
            dst.facing = src.facing
            dst.on_ground = src.on_ground
            dst.crouching = src.crouching
            dst.cooldowns = list(src.cooldowns)
            dst.ult_pct = src.ult_pct
        f.winner = None
        f.eng.time = self.t
        f.cam.update(ot, me, 1 / 60)

    # ------------------------------------------------------------ cizim
    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        draw_text(surf, "ONLINE MOD", 38, GOLD, (SCREEN_W // 2, 34))
        draw_text(surf, "4 kişilik oda  •  aynı ağdaki oyuncular birbirine katılır",
                  15, (160, 165, 185), (SCREEN_W // 2, 66))

        st = "BAĞLI  id=%d  (%s:%d)" % (self.net.my_id, self.host, self.port) \
            if self.net.connected else "BAĞLI DEĞİL"
        draw_text(surf, st, 17, (130, 240, 160) if self.net.connected
                  else (230, 130, 130), (SCREEN_W // 2, 92))

        self._field(surf, self.host_box, "SUNUCU IP", self.host, self.focus == "host")
        self._field(surf, self.port_box, "PORT", str(self.port), self.focus == "port")
        self._field(surf, self.name_box, "İSİM", self.name, self.focus == "isim")
        pw = "*" * len(self.edit) if self.focus == "sifre" and self.edit \
            else self.password
        self._field(surf, self.pass_box, "ODA ŞİFRESİ (boş = açık)",
                    pw or "-", self.focus == "sifre")

        self._btn(surf, self.btn["baglan"], "BAĞLAN", self.net.connected)
        self._btn(surf, self.btn["yenile"], "YENİLE", self.net.connected)
        self._btn(surf, self.btn["kur"], "ODA KUR", self.net.connected)
        self._btn(surf, self.btn["baslat"], "MACI BAŞLAT",
                  self.net.connected and self.net.is_host, GOLD)
        self._btn(surf, self.btn["cikis"], "ODADAN ÇIK", self.net.room is not None)
        self._btn(surf, self.btn["geri"], "GERİ (ESC)")

        # oda listesi
        pygame.draw.rect(surf, (18, 22, 34), self.room_list, border_radius=10)
        pygame.draw.rect(surf, (70, 80, 110), self.room_list, 2, border_radius=10)
        draw_text(surf, "ODALAR", 20, GOLD, (self.room_list.x + 12,
                                             self.room_list.y + 18))
        self.slot_rects = []
        y = self.room_list.y + 44
        for i, r in enumerate(self.net.rooms):
            rr = pygame.Rect(self.room_list.x + 10, y,
                             self.room_list.w - 20, 76)
            self.slot_rects.append(rr)
            mine = (r.get("id") == self.net.room)
            pygame.draw.rect(surf, (34, 40, 60) if mine else (26, 30, 46), rr,
                             border_radius=8)
            pygame.draw.rect(surf, GOLD if mine else (80, 90, 120), rr, 2,
                             border_radius=8)
            nm = r.get("name", "?")
            tag = "  [KİLİTLİ]" if r.get("locked") else ""
            draw_text(surf, "#%d  %s%s" % (r.get("id", 0), nm, tag), 18,
                      (255, 210, 130) if r.get("locked") else (255, 255, 255),
                      (rr.x + 14, rr.y + 18))
            stx = "MAC SURUYOR" if r.get("running") else \
                ("%d/%d oyuncu" % (r.get("n", 0), r.get("max", MAX_PLAYERS)))
            draw_text(surf, stx, 14, (200, 210, 230), (rr.x + 14, rr.y + 40))
            draw_text(surf, "sahibi: %s" % r.get("host", "-"), 13,
                      (170, 178, 200), (rr.right - 14, rr.y + 18))
            for j, p in enumerate(r.get("players", [])):
                px = rr.x + 14 + j * 92
                c = tuple(p.get("color", (200, 200, 200)))
                pygame.draw.circle(surf, (14, 16, 24), (px, rr.y + 62), 8)
                pygame.draw.circle(surf, c, (px, rr.y + 62), 6)
                tag = "✓" if p.get("ready") else "…"
                draw_text(surf, "%s %s" % (p.get("name", "?"), tag), 11,
                          (220, 226, 240), (px + 12, rr.y + 62))
            if not mine and not r.get("running") and r.get("n", 0) < MAX_PLAYERS:
                draw_text(surf, "ŞİFRE GİR" if r.get("locked")
                          else "KATILMAK İÇİN TIKLA", 13,
                          GOLD if not r.get("locked") else (255, 210, 130),
                          (rr.right - 14, rr.y + 62))
            y += 82
        if not self.net.rooms:
            draw_text(surf, "Henüz oda yok. 'ODA KUR' ile bir oda aç.",
                      17, (140, 148, 170), (self.room_list.centerx, y + 30))
        draw_text(surf, "IP: sunucuyu açan bilgisayarın ağ adresi "
                        "(cmd: ipconfig) • Port 27015",
                  13, (130, 138, 160), (self.room_list.centerx,
                                        self.room_list.bottom - 14))

        # mesajlar + sohbet
        yy = 560
        for nm, tx in self.net.msgs[-3:]:
            draw_text(surf, "%s: %s" % (nm, tx), 13, (200, 208, 225),
                      (70, yy), align="left")
            yy += 17
        pygame.draw.rect(surf, (22, 26, 40), self.chat_box, border_radius=8)
        pygame.draw.rect(surf, GOLD if self.focus == "mesaj" else (80, 90, 120),
                         self.chat_box, 2, border_radius=8)
        txt = self.edit if self.focus == "mesaj" else "Tab ile alan değiştir, mesaj için yaz"
        draw_text(surf, txt, 15, (220, 226, 240),
                  (self.chat_box.x + 12, self.chat_box.centery), align="left")

        if self.err_t > 0 and self.net.err:
            draw_text(surf, self.net.err, 20, (255, 120, 120),
                      (SCREEN_W // 2, 104))

    # ------------------------------------------------------------ online mac
    def draw_match(self, surf):
        """Sunucudan gelen durumla maci cizer."""
        if self.view is None:
            return
        f = self.view
        f.draw(surf)
        me = f.p1 if f.me_slot == "p1" else f.p2
        ot = f.p2 if f.me_slot == "p1" else f.p1
        # isim etiketleri
        draw_text(surf, "ONLINE  ROUND %d" % self.net.round, 24, GOLD,
                  (SCREEN_W // 2, 22))
        draw_text(surf, "SEN", 15, (130, 240, 160), (SCREEN_W - 130, 60))
        draw_text(surf, "RAKİP", 15, (250, 150, 150), (SCREEN_W - 130, 84))
        if self.net.over is not None:
            win = (self.net.over == self.net.my_id)
            draw_text(surf, "KAZANDIN!" if win else "KAYBETTİN", 62,
                      (130, 240, 160) if win else (250, 130, 130),
                      (SCREEN_W // 2, 130))
            draw_text(surf, "Lobiye dönmek için ESC", 22, (220, 226, 240),
                      (SCREEN_W // 2, 190))
        elif self.net.connected:
            draw_text(surf, "bağlantı: %s:%d" % (self.host, self.port), 13,
                      (150, 158, 180), (SCREEN_W - 120, 108))

    def _field(self, surf, box, label, value, active):
        pygame.draw.rect(surf, (22, 26, 40), box, border_radius=8)
        pygame.draw.rect(surf, GOLD if active else (70, 80, 110), box, 2,
                         border_radius=8)
        draw_text(surf, label, 11, (150, 158, 180),
                  (box.centerx, box.y + 9))
        draw_text(surf, value, 17, (235, 240, 250),
                  (box.centerx, box.centery + 6))

    def _btn(self, surf, r, label, enabled=True, col=None):
        c = col or GOLD
        base = blend((40, 46, 66), c, 0.35) if enabled else (40, 42, 52)
        pygame.draw.rect(surf, base, r, border_radius=8)
        pygame.draw.rect(surf, c if enabled else (90, 95, 110), r, 2,
                         border_radius=8)
        draw_text(surf, label, 17, (255, 255, 255) if enabled else (120, 124, 140),
                  r.center)