# -*- coding: utf-8 -*-
"""p4a icin Android projesini hazirlar.

python-for-android `p4a create` kaynak dosyalari calisma dizininin
KOKUNDE bekler. Bu yuzden oyun dosyalari ANDROID/app/ icine yazilir.

Oyun dosyalari repoda birden fazla yerde durabilir (kok dizin,
TELEFON_OYUN/, OYUN/, game/). prepare.py hepsini sirayla arar.
"""
import io
import os
import sys
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AND = os.path.join(ROOT, "ANDROID")
APP = os.path.join(AND, "app")

GAME_FILES = [
    "main.py", "ui.py", "fight.py", "stickman.py", "chars.py", "hud.py",
    "maps.py", "settings.py", "classes.py", "skills.py", "savegame.py",
    "touch.py", "netproto.py", "online.py",
]

# Oyun dosyalarinin aranacagi klasorler (sirayla)
KAYNAK = ["", "TELEFON_OYUN", "OYUN", "game", "src", "oyun"]

# Oyunun karsilik gelmesi zorunlu dosyalar (eksikse hata ver)
ZORUNLU = ["main.py", "fight.py", "classes.py", "skills.py", "stickman.py",
           "settings.py", "savegame.py", "maps.py", "ui.py"]

REQUIREMENTS = """python3
pygame
setuptools
"""


def kaynak_bul():
    """Oyun dosyalarinin bulundugu dizini dondurur."""
    for d in KAYNAK:
        kok = os.path.join(ROOT, d) if d else ROOT
        if all(os.path.isfile(os.path.join(kok, f)) for f in ZORUNLU):
            return kok
    return None


def _temizle(yol):
    shutil.rmtree(yol, ignore_errors=True)
    if os.path.isdir(yol):
        shutil.rmtree(yol, ignore_errors=True)
    return not os.path.isdir(yol)


def copy_game():
    kaynak = kaynak_bul()
    if kaynak is None:
        print("HATA: oyun dosyalari bulunamadi.")
        print("Aranan dosyalar: %s" % ", ".join(ZORUNLU))
        print("Aranan klasorler: %s"
              % ", ".join(ROOT + "\\" + (d if d else "") for d in KAYNAK))
        return -1

    if os.path.abspath(kaynak) != os.path.abspath(APP):
        print("Kaynak klasor: %s" % os.path.relpath(kaynak, ROOT))

    if not os.path.isdir(APP):
        os.makedirs(APP)
    # eski .pyc dosyalari APK'ya girmesin
    shutil.rmtree(os.path.join(APP, "__pycache__"), ignore_errors=True)

    n = 0
    eksik = []
    for f in GAME_FILES:
        src = os.path.join(kaynak, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(APP, f))
            n += 1
        else:
            eksik.append(f)
    if eksik:
        print("UYARI: bulunamayan oyun dosyalari: %s" % ", ".join(eksik))

    # p4a giris noktasi (--launcher)
    giris = os.path.join(AND, "main_mobile.py")
    if not os.path.isfile(giris):
        print("HATA: %s yok" % giris)
        return -1
    shutil.copy2(giris, os.path.join(APP, "main_mobile.py"))

    # kayit klasoru yoksa bos olustur (oyun ilk acilista kendisi yaratir)
    for d in ("SAVE", "MOBIL"):
        s = os.path.join(kaynak, d)
        if not os.path.isdir(s):
            s = os.path.join(ROOT, d)
        t = os.path.join(APP, d)
        if os.path.isdir(s):
            if _temizle(t):
                shutil.copytree(s, t)
        else:
            os.makedirs(t, exist_ok=True)
    # oyunun ilk acilista okuyacagi kayit dosyasi
    kayit = os.path.join(APP, "SAVE", "oyun_kayit.json")
    if not os.path.isfile(kayit):
        with io.open(kayit, "w", encoding="utf-8") as f:
            f.write("{}")

    for name in ("oyun_ikon.png", "kapak.png", "kapak.jpg"):
        for base in (kaynak, ROOT):
            src = os.path.join(base, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(APP, name))
                break

    with io.open(os.path.join(APP, "requirements.txt"), "w",
                 encoding="utf-8") as f:
        f.write(REQUIREMENTS)
    return n


if __name__ == "__main__":
    n = copy_game()
    if n < 0:
        sys.exit(1)
    print("ANDROID/app hazir: %d oyun dosyasi + main_mobile.py + requirements.txt"
          % n)
    print("Gerekenler: %s" % REQUIREMENTS.split())
    print("Simdi derlemek icin:  bash ANDROID/build_apk_docker.sh")
