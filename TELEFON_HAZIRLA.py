# -*- coding: utf-8 -*-
"""Telefona kopyalanacak TAM oyun klasorunu hazirlar.

Cikti:  TELEFON_OYUN/   (bunu telefona kopyala, Pydroid'de calistir)
"""
import io
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "TELEFON_OYUN")

FILES = [
    "main.py", "ui.py", "fight.py", "stickman.py", "chars.py", "hud.py",
    "maps.py", "settings.py", "classes.py", "skills.py", "savegame.py",
    "touch.py", "netproto.py", "online.py", "MOBIL_CALISTIR.py",
]
EXTRA = ["oyun_ikon.png", "kapak.png", "kapak.jpg"]


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    n = 0
    for f in FILES:
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(OUT, f))
            n += 1
    # kayit klasoru
    for d in ("SAVE", "MOBIL"):
        s = os.path.join(ROOT, d)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(OUT, d))
    for f in EXTRA:
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(OUT, f))
    readme = """STICKMAN FIGHTERS - TELEFON KURULUMU
====================================

1) Bu klasoru telefona kopyala:
     /sdcard/STIKMAN.FIGHTERS/

2) Play Store'dan "Pydroid 3" indir

3) Pydroid 3'te:
     Pip  ->  pygame  ->  Install

4) Dosya sec:
     /sdcard/STIKMAN.FIGHTERS/MOBIL_CALISTIR.py

5) Yesil OK'a bas.

------

Oyun acilmazsa:
  - Pip icinde "pygame" yoksa "pygame-ce" kur
  - Dosya sec ekranindan klasoru gorunuyorsa
    MOBIL_CALISTIR.py dosyasini sec

KONTROLLER
  Sol alt   :  joystick (sola / saga)
  Sag alt  :  1, 2, 3, U (ulti), ^ (zipla), v (egil)
  Menu     :  her yere dokun

KAYIT
  SAVE/oyun_kayit.json
  Bu klasoru bilgisayara kopyalarsan ilerlemen tasinir.
"""
    with io.open(os.path.join(OUT, "OKUBENI.txt"), "w",
                 encoding="utf-8") as f:
        f.write(readme)
    return n


if __name__ == "__main__":
    n = build()
    print("TELEFON_OYUN hazir: %d dosya" % n)
    for root, dirs, files in os.walk(OUT):
        rel = os.path.relpath(root, OUT)
        print(" ", (rel if rel != "." else "") + "/")
        for f in sorted(files):
            print("     ", f)
    print()
    print("Bu klasoru telefona kopyala (USB / Google Drive / WhatsApp).")
    print("Sonra: Pydroid 3 -> Pip -> pygame -> MOBIL_CALISTIR.py")