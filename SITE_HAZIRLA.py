# -*- coding: utf-8 -*-
"""SITE + LAUNCHER PAKETI HAZIRLAR.

1) Site ayarlarini doldurur (GitHub kullanici adi / repo / site adresi)
2) PC surumunu zip olarak paketler
3) Zip'i site klasorune de koyar (yedek indirme linki icin)
4) Sonunda yapilacaklari adim adim yazar

Kullanim:
    python SITE_HAZIRLA.py                       # interaktif
    python SITE_HAZIRLA.py KATIL5019             # sadece kullanici adi
    python SITE_HAZIRLA.py KATIL5019 x y         # + site adresi
"""
import io
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "SITE")
OUT = os.path.join(ROOT, "YAYIN")
DOWN = os.path.join(SITE, "indir")
TAG = "1.4.0"

PC_FILES = [
    "launcher.py", "launcher_projects.py", "main.py", "ui.py", "fight.py",
    "stickman.py", "chars.py", "hud.py", "maps.py", "settings.py",
    "classes.py", "skills.py", "savegame.py", "touch.py", "netproto.py",
    "online.py", "server.py",
    "OYUNU_BASLAT.bat", "SUNUCU_BASLAT.bat",
    "APK_YAPIMI.md", "MOBIL_REHBERI.md", "ONLINE_REHBERI.md", "README.md",
]
PC_DIRS = ["SETUP"]
PC_OPT = ["oyun_ikon.png", "oyun_ikon.ico", "kapak.png", "kapak.jpg",
          "MOBIL/mobil_config.json", "SAVE/oyun_kayit.json"]


def ask(prompt, default=""):
    try:
        v = input(prompt).strip()
    except EOFError:
        v = ""
    return v or default


def set_var(html, name, value):
    import re
    return re.sub(r'var %s\s*=\s*"[^"]*";' % name,
                  'var %s = "%s";' % (name, value), html, count=1)


def patch_site(owner, repo, site_url):
    p = os.path.join(SITE, "index.html")
    s = io.open(p, encoding="utf-8").read()
    s = set_var(s, "OWNER", owner)
    s = set_var(s, "REPO", repo)
    s = set_var(s, "TAG", TAG)
    s = set_var(s, "SITE_URL", site_url)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    for f in ("oyun_ikon.png", "kapak.png"):
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(SITE, "favicon.png"))
            break
    # rehberleri siteye kopyala
    for f in ("APK_YAPIMI.md", "MOBIL_REHBERI.md", "ONLINE_REHBERI.md",
              "README.md"):
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(SITE, os.path.basename(f)))
    if not os.path.isfile(os.path.join(SITE, ".nojekyll")):
        io.open(os.path.join(SITE, ".nojekyll"), "w").close()
    print("site ayarlandi")
    print("  OWNER    =", owner)
    print("  REPO     =", repo)
    print("  TAG      =", TAG)
    print("  SITE_URL =", site_url or "(otomatik: github.io)")


def build_pc_zip(owner, repo, site_url):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    if not os.path.isdir(DOWN):
        os.makedirs(DOWN)
    name = "STICKMAN-FIGHTERS-%s-PC.zip" % TAG
    path = os.path.join(OUT, name)
    if os.path.isfile(path):
        os.remove(path)
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in PC_FILES:
            src = os.path.join(ROOT, f)
            if os.path.isfile(src):
                z.write(src, "STICKMAN-FIGHTERS/" + f)
                n += 1
        for d in PC_DIRS:
            sd = os.path.join(ROOT, d)
            if not os.path.isdir(sd):
                continue
            for r, _, fs in os.walk(sd):
                for f in fs:
                    p = os.path.join(r, f)
                    rel = os.path.relpath(p, ROOT).replace("\\", "/")
                    z.write(p, "STICKMAN-FIGHTERS/" + rel)
                    n += 1
        for f in PC_OPT:
            p = os.path.join(ROOT, f)
            if os.path.isfile(p):
                z.write(p, "STICKMAN-FIGHTERS/" + f)
                n += 1
        z.writestr("STICKMAN-FIGHTERS/OKUBENI.txt", readme(owner, repo, site_url))
    # yedek: site klasorune de koy
    shutil.copy2(path, os.path.join(DOWN, name))
    return path, n


def readme(owner, repo, site_url):
    base = "https://github.com/" + owner + "/" + repo
    site = site_url or ("https://" + owner + ".github.io/" + repo)
    return (
        "STICKMAN FIGHTERS - " + TAG + "\n" + "=" * 32 + "\n\n"
        "KURULUM\n--------\n"
        "1) Bu klasoru masaustune ac (acikca).\n"
        '2) "SETUP" klasorune gir, "KURULUMU_BASLAT.bat" cift tikla.\n'
        '3) "PC SURUMU" butonuna bas -> kurulum + kisayol + launcher.\n'
        '4) Kurulum sonrasi "KATIL5019 LAUNCHER" acilir.\n\n'
        'LAUNCHER 2 HALI\n----------------\n'
        "  OYNA            -> oyunu baslatir\n"
        "  TELEFON SURUMU  -> indirme sitesini acar (GitHub)\n\n"
        "ONLINE (4 KISILIK ODA)\n----------------------\n"
        '1) "SUNUCU_BASLAT.bat" calistir -> ekranda IP yazar\n'
        "2) Arkadaslarina o IP'yi ver\n"
        "3) Oyun: ONLINE -> SUNUCU IP -> BAGLAN -> ODA KUR\n\n"
        "TELEFON SURUMU\n---------------\n"
        "Site:  " + site + "/\n"
        "Linke dokun -> TELEFON SURUMU -> APK indirilir.\n\n"
        "APK derleme:  " + base + "/actions/workflows/android-apk.yml\n"
        "Rehberler:    APK_YAPIMI.md, MOBIL_REHBERI.md, ONLINE_REHBERI.md\n\n"
        "KAYIT\n-----\n"
        "SAVE/oyun_kayit.json  (Ruby, paketler, karakterler, seviyeler)\n"
    )


if __name__ == "__main__":
    a = sys.argv[1:] if len(sys.argv) > 1 else []
    owner = a[0] if a else ask("GitHub kullanici adin (orn. KATIL5019): ")
    repo = a[1] if len(a) > 1 else "stickman-fighters"
    site = a[2] if len(a) > 2 else ask("Site adresi (bos = github.io tahmini): ")

    patch_site(owner, repo, site)
    path, n = build_pc_zip(owner, repo, site)
    size = os.path.getsize(path) / 1024.0 / 1024.0
    print()
    print("PC ZIP hazir : %s  (%d dosya, %.2f MB)" % (os.path.basename(path), n, size))
    print("Konum       : %s" % path)
    print("Yedek kopyasi: SITE%sindir (site uzerinden de indirilebilir)"
          % os.sep)
    print()
    print("=" * 64)
    print(" SIMDI YAPILACAKLAR")
    print("=" * 64)
    print("""
 1) Bu klasoru GitHub'a yukle (.github klasoru gizli OLMAMALI)

 2) REPO PUBLIC OLSUN
    Settings -> General -> Danger Zone -> Change visibility -> Public
    (GitHub Pages ve Releases indirme linkleri sadece public repoda calisir)

 3) Actions -> SITE            -> Run workflow  (site ~1 dk)
     Actions -> ANDROID APK    -> Run workflow  (APK 20-25 dk)

 4) Releases -> New release
       tag: v%s
       dosya: YAYIN/%s

 5) APK workflow bitince Releases'a otomatik yuklenir.
     (Site butonu kendiliginden calisir)

 6) Site adresin:  https://%s.github.io/%s/
""" % (TAG, os.path.basename(path), owner, repo))
    print("=" * 64)
    print()
    print("PRIVATE kalmak istersen:  CLOUDFLARE_KURULUM.md dosyasina bak")
    print("(Cloudflare Pages private repoyu destekler, 7/24 ucretsiz)")
