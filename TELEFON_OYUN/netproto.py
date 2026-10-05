# -*- coding: utf-8 -*-
"""Online mod ortak protokolu ve veri tipleri (max 4 oyuncu)."""
import json
import socket

HOST_DEFAULT = "127.0.0.1"
PORT = 27015
MAX_PLAYERS = 4
TIMEOUT = 12.0
TICK = 1 / 30.0

# mesaj tipleri
C_HELLO = "hello"
C_ROOMS = "rooms"
C_CREATE = "create"
C_JOIN = "join"
C_LEAVE = "leave"
C_READY = "ready"
C_START = "start"
C_CHAT = "chat"
C_IN = "in"
C_PING = "ping"
C_PASS = "pass"

S_WELCOME = "welcome"
S_ROOMS = "rooms"
S_JOINED = "joined"
S_SLOTS = "slots"
S_START = "start"
S_STATE = "state"
S_OVER = "over"
S_MSG = "msg"
S_BACK = "back"
S_ERR = "err"
S_PONG = "pong"
S_NEEDPASS = "needpass"

INPUT_FIELDS = ("left", "right", "jump", "crouch",
                "ability1_pressed", "ability2_pressed", "ability3_pressed",
                "ult_pressed", "jump_pressed")


def pack(obj):
    return (json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8")


def unpack(line):
    try:
        return json.loads(line.decode("utf-8", "replace"))
    except Exception:
        return None


def pack_input(inp):
    d = {}
    for k in INPUT_FIELDS:
        d[k] = bool(getattr(inp, k, False))
    return d


def apply_input(inp, d):
    for k in INPUT_FIELDS:
        if k in d:
            setattr(inp, k, bool(d[k]))


def blank_input():
    class _I:
        left = False
        right = False
        jump = False
        crouch = False
        ability1_pressed = False
        ability2_pressed = False
        ability3_pressed = False
        ult_pressed = False
        jump_pressed = False
    return _I()


def recv_line(sock, buf):
    """Socket'ten tam satir okur. (data, buf) doner, veri yoksa (None, buf)."""
    while b"\n" not in buf:
        try:
            chunk = sock.recv(8192)
        except (socket.timeout, BlockingIOError):
            return None, buf
        except OSError:
            return False, buf
        if not chunk:
            return False, buf
        buf += chunk
    line, _, rest = buf.partition(b"\n")
    return line, rest


def recv_msg(sock, buf):
    line, buf = recv_line(sock, buf)
    if line is None:
        return None, buf
    if line is False:
        return False, buf
    return unpack(line), buf


def local_ip():
    """Yerel agdaki IP (sunucu icin ekrana basilir)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"


def player_state(p):
    """Oyuncu ozetini ag uzerine gondermek icin hazirlar."""
    return {
        "x": round(p.x, 1), "y": round(p.y, 1),
        "hp": round(p.hp, 1), "sh": round(getattr(p, "shield", 0.0), 1),
        "mx": round(p.max_hp, 1), "ms": round(getattr(p, "max_shield", 0.0), 1),
        "f": p.facing, "c": list(p.color),
        "og": p.on_ground, "cr": p.crouching,
        "w": p.defn.get("name", "?"),
        "cd": [round(c, 2) for c in p.cooldowns],
        "ult": round(p.ult_pct, 1),
        "at": (p.attack["def"].get("pose", "idle")
               if p.attack else "idle"),
    }


def draw_state(st):
    """Gelen ozeti Stickman benzeri hafif nesneye cevirir."""
    class _P:
        pass
    p = _P()
    p.x = st["x"]
    p.y = st["y"]
    p.hp = st["hp"]
    p.shield = st.get("sh", 0.0)
    p.max_hp = st.get("mx", 100.0)
    p.max_shield = st.get("ms", 0.0)
    p.facing = st.get("f", 1)
    p.color = tuple(st.get("c", (200, 200, 200)))
    p.on_ground = st.get("og", True)
    p.crouching = st.get("cr", False)
    p.defn = {"name": st.get("w", "?")}
    p.cooldowns = list(st.get("cd", [0, 0, 0]))
    p.ult_pct = st.get("ult", 0.0)
    p.walk_phase = 0.0
    p.moving = False
    p.hit_timer = 0.0
    p.attack = None
    pose = st.get("at", "idle")
    if pose not in ("punch", "kick", "combo", "crouch", "run", "walk",
                    "jump", "hurt"):
        pose = "idle"
    p.attack = {"def": {"pose": pose}} if pose != "idle" else None
    return p