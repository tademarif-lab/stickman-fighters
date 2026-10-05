# -*- coding: utf-8 -*-
"""p4a icin Android projesini hazirlar.

python-for-android `p4a create` kaynak dosyalari calisma dizininin
KOKUNDE bekler. Bu yuzden oyun dosyalari ANDROID/app/ icine yazilir.
"""
import io
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AND = os.path.join(ROOT, "ANDROID")
APP = os.path.join(AND, "app")

GAME_FILES = [
    "main.py", "ui.py", "fight.py", "stickman.py", "chars.py", "hud.py",
    "maps.py", "settings.py", "classes.py", "skills.py", "savegame.py",
    "touch.py", "netproto.py", "online.py",
]

REQUIREMENTS = """python3
pygame2
setuptools
"""


def copy_game():
    if not os.path.isdir(APP):
        os.makedirs(APP)
    n = 0
    for f in GAME_FILES:
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(APP, f))
            n += 1
    # p4a giris noktasi (--launcher)
    shutil.copy2(os.path.join(AND, "main_mobile.py"),
                 os.path.join(APP, "main_mobile.py"))
    for d in ("SAVE", "MOBIL"):
        s = os.path.join(ROOT, d)
        t = os.path.join(APP, d)
        if os.path.isdir(s):
            if os.path.isdir(t):
                shutil.rmtree(t)
            shutil.copytree(s, t)
    for name in ("oyun_ikon.png", "kapak.png", "kapak.jpg"):
        src = os.path.join(ROOT, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(APP, name))
    with io.open(os.path.join(APP, "requirements.txt"), "w",
                 encoding="utf-8") as f:
        f.write(REQUIREMENTS)
    return n


if __name__ == "__main__":
    n = copy_game()
    print("ANDROID/app hazir: %d oyun dosyasi + main_mobile.py + requirements.txt"
          % n)
    print("Simdi derlemek icin:  bash ANDROID/build_apk.sh")
