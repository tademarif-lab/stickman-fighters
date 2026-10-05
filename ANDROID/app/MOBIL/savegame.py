# -*- coding: utf-8 -*-
"""Kayıt sistemi: Ruby, açılan paketler/karakterler, ilerleme."""
import io
import json
import os

from classes import CLASSES, CLASS_BY_ID, PACKS, PACK_BY_ID, RUBY_PER_GAME

SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SAVE")
SAVE_PATH = os.path.join(SAVE_DIR, "oyun_kayit.json")

START_RUBY = 5.0        # yeni oyuncunun baslangic ruby'si

DEFAULT = {
    "ruby": START_RUBY,
    "money": 0.0,
    "packs": [],
    "unlocked": [],
    "levels": {},
    "stats": {"games": 0, "wins": 0, "kills": 0, "bosses": 0},
    "best": {},
}

DATA = dict(DEFAULT)


def load():
    global DATA
    try:
        with io.open(SAVE_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        d = dict(DEFAULT)
        d.update(raw)
        st = dict(DEFAULT["stats"])
        st.update(raw.get("stats", {}))
        d["stats"] = st
        DATA = d
    except Exception:
        DATA = json.loads(json.dumps(DEFAULT))
    return DATA


def save():
    global DATA
    try:
        if not os.path.isdir(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        with io.open(SAVE_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(DATA, ensure_ascii=False, indent=2))
        return True
    except Exception:
        return False


def reset():
    global DATA
    DATA = json.loads(json.dumps(DEFAULT))
    save()


# ------------------------------------------------------------------ ruby
def ruby():
    return float(DATA.get("ruby", 0.0))


def add_ruby(n):
    DATA["ruby"] = round(max(0.0, ruby() + n), 2)
    save()
    return DATA["ruby"]


def add_game_reward(boss=False):
    DATA["stats"]["games"] = DATA["stats"].get("games", 0) + 1
    return add_ruby(RUBY_PER_GAME)


# ------------------------------------------------------------------ paketler
def owns_pack(pid):
    return pid in DATA.get("packs", [])


def owns_char(cid):
    if cid == "human":
        return True
    if cid in DATA.get("unlocked", []):
        return True
    c = CLASS_BY_ID.get(cid)
    if c is None:
        return False
    return owns_pack(c.get("pack"))


def can_afford(price):
    return ruby() + 1e-6 >= float(price)


def buy_pack(pid):
    p = PACK_BY_ID.get(pid)
    if p is None:
        return False, "Paket yok"
    if owns_pack(pid):
        return False, "Zaten sahipsin"
    if not can_afford(p["price"]):
        return False, "Ruby yetersiz"
    add_ruby(-p["price"])
    DATA.setdefault("packs", []).append(pid)
    for no in p["chars"]:
        c = CLASS_BY_ID.get(cid_of(no))
        if c and c["id"] not in DATA["unlocked"]:
            DATA["unlocked"].append(c["id"])
    save()
    return True, "Alındı: " + p["name"]


def cid_of(no):
    for c in CLASSES:
        if c["no"] == no:
            return c["id"]
    return None


def pack_of(cid):
    c = CLASS_BY_ID.get(cid)
    return c.get("pack") if c else None


def pack_price(cid):
    p = PACK_BY_ID.get(pack_of(cid) or "")
    return p["price"] if p else None


# ------------------------------------------------------------------ seviye
def level_of(cid):
    return int(DATA.get("levels", {}).get(cid, 0))


def set_level(cid, n):
    DATA.setdefault("levels", {})[cid] = int(n)


# ------------------------------------------------------------------ roster
def class_char(cid):
    """Sinif tanimindan oyun icin karakter sozlugu uretir."""
    c = CLASS_BY_ID[cid]
    lv = level_of(cid)
    levels = c.get("levels") or []
    src = levels[lv] if levels and lv < len(levels) else c
    hp = src.get("hp", c["hp"])
    sh = src.get("shield", c["shield"])
    sk = src.get("abilities", c["abilities"])
    ult = src.get("ult", c["ult"])
    return {
        "id": cid,
        "name": src.get("name", c["name"]),
        "hp": hp,
        "shield": sh,
        "speed": c["speed"],
        "info": c["accessory"],
        "story": c["story"],
        "class_def": {
            "id": cid,
            "no": c["no"],
            "name": c["name"],
            "abilities": list(sk),
            "ult": ult,
            "levels": levels,
            "passive": c["passive"],
            "accessory": c["accessory"],
            "shield": sh,
            "hp": hp,
            "speed": c["speed"],
        },
        "abilities": list(sk),
        "color": c["color"],
    }


def roster():
    """Acik karakterlerden olusan oynanabilir liste (Insan + siniflar)."""
    from settings import CHARACTERS
    out = [dict(c) for c in CHARACTERS]
    for c in CLASSES:
        if owns_char(c["id"]):
            out.append(class_char(c["id"]))
    return out


def locked_roster():
    """Tum karakterler + kilit bilgisi (karakter secim ekrani icin)."""
    from settings import CHARACTERS
    out = []
    for c in CHARACTERS:
        d = dict(c)
        d["locked"] = False
        d["owned"] = True
        d["no"] = 1
        d["pack"] = None
        out.append(d)
    for c in CLASSES:
        owned = owns_char(c["id"])
        d = class_char(c["id"]) if owned else {
            "id": c["id"], "name": c["name"], "hp": c["hp"],
            "shield": c["shield"], "speed": c["speed"],
            "info": c["accessory"], "story": c["story"],
            "abilities": list(c["abilities"]),
            "color": (70, 70, 90),
        }
        d["locked"] = not owned
        d["owned"] = owned
        d["no"] = c["no"]
        d["pack"] = c.get("pack")
        d["price"] = pack_price(c["id"])
        d["class_def"] = class_char(c["id"])["class_def"]
        out.append(d)
    out.sort(key=lambda x: x.get("no", 0))
    return out


def skill_desc(cid, idx):
    """Karakterin i. yeteneğinin adi + aciklamasi."""
    from classes import SKILLS
    ch = class_char(cid) if cid in CLASS_BY_ID else None
    if not ch:
        return ("-", "")
    sid = ch["class_def"]["abilities"][idx]
    sk = SKILLS.get(sid, {})
    return (sk.get("name", "-"), sk.get("desc", ""))


def ult_desc(cid):
    from classes import SKILLS
    ch = class_char(cid) if cid in CLASS_BY_ID else None
    if not ch:
        return ("-", "")
    sid = ch["class_def"]["ult"]
    sk = SKILLS.get(sid, {})
    return (sk.get("name", "-"), sk.get("desc", ""))




load()
if not os.path.isfile(SAVE_PATH):
    save()
