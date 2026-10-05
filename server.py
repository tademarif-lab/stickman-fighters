# -*- coding: utf-8 -*-
"""STICKMAN FIGHTERS ONLINE SUNUCU (Ayni Wi-Fi / kablo agi icin).

Kullanim:
    python server.py            -> 27015 portundan dinler
    python server.py 28000      -> farkli port

Odada en fazla 4 oyuncu olur. Her mac 1v1; mac bitince kazanan yerde kalir,
kaybeden sıradaki oyuncuyla eslesir (turnuva sirasi). Oda sahibi
(FIRLATAN adam) maclari baslatir.
"""
import socket
import threading
import time

from netproto import (PORT, MAX_PLAYERS, TICK, TIMEOUT,
                      C_HELLO, C_ROOMS, C_CREATE, C_JOIN, C_LEAVE, C_READY,
                      C_START, C_CHAT, C_IN, C_PING,
                      S_WELCOME, S_ROOMS, S_JOINED, S_SLOTS, S_START,
                      S_STATE, S_OVER, S_MSG, S_BACK, S_ERR, S_PONG,
                      S_NEEDPASS, C_PASS,
                      pack, recv_msg, blank_input, pack_input, apply_input,
                      local_ip, player_state)

import settings


class Peer:
    def __init__(self, cid, sock, addr):
        self.id = cid
        self.sock = sock
        self.addr = addr
        self.buf = b""
        self.name = "Oyuncu"
        self.char = "human"
        self.color = (200, 60, 60)
        self.room = None
        self.ready = False
        self.alive = True
        self.last = time.time()
        self.inp = blank_input()
        self.inp_t = 0.0
        self.wins = 0

    def send(self, obj):
        try:
            self.sock.sendall(pack(obj))
            return True
        except OSError:
            self.alive = False
            return False


class Room:
    def __init__(self, rid, name, host, password=""):
        self.id = rid
        self.name = name
        self.host = host
        self.password = password or ""      # bos ise oda herkese acik
        self.locked = bool(self.password)
        self.peers = []
        self.running = False
        self.t = 0.0
        self.round = 0
        self.queue = []
        self.match = None          # (p1, p2)
        self.next_at = 0.0
        self.log = []

    def add(self, p):
        if len(self.peers) >= MAX_PLAYERS:
            return False
        self.peers.append(p)
        p.room = self
        return True

    def remove(self, p):
        if p in self.peers:
            self.peers.remove(p)
        p.room = None
        if self.host is p:
            self.host = self.peers[0] if self.peers else None
        if len(self.peers) < 2 and self.running:
            self.stop_match("ODA DAHA FAZLA OYUNCU GEREK")

    def start_match(self):
        if self.running or len(self.peers) < 2:
            return
        if self.match is None:
            self.queue = list(self.peers)
            self.round = 0
        if len(self.queue) < 2:
            self.queue = list(self.peers)
            self.round = 0
        self.match = (self.queue[0], self.queue[1])
        self.running = True
        self.t = 0.0
        self.round += 1
        self._build_fight()
        for p in self.peers:
            p.send({"t": S_START, "room": self.id, "round": self.round,
                    "p1": self.match[0].id, "p2": self.match[1].id,
                    "names": {str(self.match[0].id): self.match[0].name,
                              str(self.match[1].id): self.match[1].name},
                    "chars": self.chars,
                    "tags": [self.match[0].name, self.match[1].name]})

    def _build_fight(self):
        import savegame
        from settings import CHARACTERS
        from fight import Fight
        a, b = self.match

        def char_of(peer):
            if peer.char and peer.char != "human":
                try:
                    return savegame.class_char(peer.char)
                except Exception:
                    pass
            return dict(CHARACTERS[0])

        self.fight = Fight([char_of(a), char_of(b)], [a.color, b.color],
                           "grass", 500.0)
        self.fight.online = True
        self.fight.name_tag = (a.name, b.name)
        self.chars = {str(a.id): a.char, str(b.id): b.char}

    def stop_match(self, why=""):
        self.running = False
        self.match = None
        if why:
            self.log.append(why)
        for p in self.peers:
            p.send({"t": S_BACK, "why": why})
        self.fight = None

    def broadcast(self, obj):
        for p in self.peers:
            p.send(obj)


class Server:
    def __init__(self, port=PORT):
        self.port = port
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(("0.0.0.0", port))
        self.srv.listen(16)
        self.srv.settimeout(0.05)
        self.peers = []
        self.rooms = {}
        self.next_id = 1
        self.next_room = 1
        self.lock = threading.Lock()
        self.running = True

    def log(self, txt):
        print("[SUNUCU] " + txt, flush=True)

    # ------------------------------------------------------------ dis baglanti
    def serve_forever(self):
        self.log("STICKMAN FIGHTERS ONLINE SUNUCU")
        self.log("Bu bilgisayarin IP adresi: %s" % local_ip())
        self.log("Port: %d  |  En fazla %d oyuncu" % (self.port, MAX_PLAYERS))
        self.log("Durdurmak icin Ctrl+C")
        last = time.time()
        while self.running:
            now = time.time()
            try:
                sock, addr = self.srv.accept()
                sock.setblocking(False)
                p = Peer(self.next_id, sock, addr)
                self.next_id += 1
                self.peers.append(p)
                self.log("Yeni baglanti: %s (id=%d)" % (addr[0], p.id))
                p.send({"t": S_WELCOME, "id": p.id, "max": MAX_PLAYERS,
                        "port": self.port})
            except socket.timeout:
                pass
            except OSError:
                pass
            for p in list(self.peers):
                if not p.alive:
                    self.drop(p)
                    continue
                if now - p.last > TIMEOUT * 3:
                    self.drop(p)
                    continue
                self.read_peer(p)
            if now - last >= TICK:
                last = now
                self.tick(TICK)
            time.sleep(0.004)

    def drop(self, p):
        self.log("Baglanti kapandi: %s" % p.name)
        if p.room is not None:
            p.room.remove(p)
        if p in self.peers:
            self.peers.remove(p)
        try:
            p.sock.close()
        except OSError:
            pass

    def read_peer(self, p):
        while p.alive:
            msg, p.buf = recv_msg(p.sock, p.buf)
            if msg is None:
                break
            if msg is False:
                self.drop(p)
                break
            p.last = time.time()
            self.handle(p, msg)

    # ------------------------------------------------------------ komutlar
    def handle(self, p, m):
        t = m.get("t")
        if t == C_PING:
            p.send({"t": S_PONG})
        elif t == C_HELLO:
            p.name = str(m.get("name", "Oyuncu"))[:14]
            p.char = str(m.get("char", "human"))
            p.color = tuple(m.get("color", (200, 60, 60)))
            self.broadcast_rooms()
        elif t == C_ROOMS:
            self.send_rooms(p)
        elif t == C_CREATE:
            name = str(m.get("name", "Oda"))[:18] or "Oda"
            pw = str(m.get("pass", ""))[:12]
            rid = self.next_room
            self.next_room += 1
            r = Room(rid, name, p, pw)
            r.add(p)
            self.rooms[rid] = r
            p.send({"t": S_JOINED, "room": rid, "host": True})
            self.broadcast_rooms()
            self.log("Oda kuruldu #%d %s (host=%s)" % (rid, name, p.name))
        elif t == C_JOIN:
            rid = int(m.get("room", 0))
            r = self.rooms.get(rid)
            if r is None:
                p.send({"t": S_ERR, "why": "Oda yok"})
                return
            if r.running:
                p.send({"t": S_ERR, "why": "Odada mac suruyor"})
                return
            if r.locked:
                pw = str(m.get("pass", ""))
                if pw != r.password:
                    p.send({"t": S_NEEDPASS, "room": rid})
                    self.log("%s kilitli odaya giremedi (#%d)" % (p.name, rid))
                    return
            if not r.add(p):
                p.send({"t": S_ERR, "why": "Oda dolu (%d)" % MAX_PLAYERS})
                return
            p.send({"t": S_JOINED, "room": rid, "host": r.host is p})
            self.broadcast_rooms()
            self.log("%s odaya katildi #%d" % (p.name, rid))
        elif t == C_LEAVE:
            if p.room is not None:
                p.room.remove(p)
                self.broadcast_rooms()
            p.send({"t": S_BACK, "why": "Odadan ciktin"})
        elif t == C_READY:
            p.ready = bool(m.get("v"))
            self.broadcast_rooms()
        elif t == C_CHAT:
            txt = str(m.get("text", ""))[:120]
            if p.room is not None and txt:
                p.room.broadcast({"t": S_MSG, "name": p.name, "text": txt})
        elif t == C_START:
            if p.room is not None and p.room.host is p:
                p.room.start_match()
            elif p.room is not None:
                p.send({"t": S_ERR, "why": "Sadece oda sahibi baslatabilir"})
            else:
                p.send({"t": S_ERR, "why": "Odasin yok"})
        elif t == C_IN:
            if p.room is not None:
                apply_input(p.inp, m.get("i", {}))
                p.inp_t = time.time()

    # ------------------------------------------------------------ odalar
    def room_info(self, r):
        return {"id": r.id, "name": r.name,
                "locked": r.locked,
                "n": len(r.peers), "max": MAX_PLAYERS,
                "host": r.host.name if r.host else "-",
                "running": r.running,
                "round": r.round,
                "players": [{"id": p.id, "name": p.name, "ready": p.ready,
                             "wins": p.wins, "char": p.char,
                             "color": list(p.color)} for p in r.peers]}

    def send_rooms(self, p):
        p.send({"t": S_ROOMS, "rooms": [self.room_info(r)
                                        for r in self.rooms.values()]})

    def broadcast_rooms(self):
        for p in self.peers:
            self.send_rooms(p)

    # ------------------------------------------------------------ oyun dongusu
    def tick(self, dt):
        for r in list(self.rooms.values()):
            if not r.running:
                continue
            f = getattr(r, "fight", None)
            if f is None:
                r.stop_match("Mac baslatilamadi")
                continue
            r.t += dt
            p1, p2 = r.match
            i1 = blank_input()
            i2 = blank_input()
            apply_input(i1, p1.inp_dict or {})
            apply_input(i2, p2.inp_dict or {})
            f.update(dt, i1, i2)
            st = {"p1": player_state(f.p1), "p2": player_state(f.p2)}
            r.broadcast({"t": S_STATE, "s": st})
            if f.winner is not None:
                win = p1 if f.winner == 1 else p2
                lose = p2 if f.winner == 1 else p1
                win.wins += 1
                for p in r.peers:
                    p.send({"t": S_OVER, "winner": win.id,
                            "wins": {str(x.id): x.wins for x in r.peers}})
                q = [x for x in r.queue if x not in (win, lose)]
                q.insert(0, win)
                q.append(lose)
                r.queue = q
                r.match = None
                r.running = False
                r.t = 0.0
                r.broadcast({"t": S_BACK, "why": "Mac bitti: %s kazandi" % win.name})
                self.broadcast_rooms()


# Peer.inp_dict alanini ekle
def _peer_init(self, cid, sock, addr):
    self.id = cid
    self.sock = sock
    self.addr = addr
    self.buf = b""
    self.name = "Oyuncu"
    self.char = "human"
    self.color = (200, 60, 60)
    self.room = None
    self.ready = False
    self.alive = True
    self.last = time.time()
    self.inp = blank_input()
    self.inp_dict = {}
    self.inp_t = 0.0
    self.wins = 0


Peer.__init__ = _peer_init


if __name__ == "__main__":
    import sys
    port = PORT
    for a in sys.argv[1:]:
        if a.isdigit():
            port = int(a)
    srv = Server(port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.log("Sunucu kapatildi.")
        srv.running = False