# -*- coding: utf-8 -*-
"""SITE KONTROL ARACI - 404'un sebebini bulur.

Kullanim:
    python SITE_KONTROL.py                                  # interaktif
    python SITE_KONTROL.py KULLANICIADIM                    # sadece kullanici adi
    python SITE_KONTROL.py KULLANICIADIM repo-adi
    python SITE_KONTROL.py KULLANICIADIM repo-adi https://x.pages.dev

Repo adresini bilmiyorsan:
    GitHub'da repo'ya gir -> sag ustteki "Code" butonu ->
    yeşil "HTTPS" kopyala butonu -> oradaki adresi yapistir
"""
import io
import json
import ssl
import sys
import urllib.error
import urllib.request

ROOT = __import__("os").path.dirname(__file__)
ctx = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (SF-SiteKontrol)"}


def head(url, timeout=12):
    """(durum, aciklama) doner."""
    try:
        req = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, "%d bayt" % len(r.read(4000))
    except urllib.error.HTTPError as e:
        return e.code, "HTTP %s" % e.code
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, str(e)[:60])


def ask(p, d=""):
    try:
        v = input(p).strip()
    except EOFError:
        v = ""
    return v or d


def repo_from_url(url):
    """https://github.com/KULLANICI/repo  ->  (KULLANICI, repo)"""
    try:
        p = url.rstrip("/").replace("https://github.com/", "")
        p = p.replace("http://github.com/", "").replace("git@github.com:", "")
        parts = [x for x in p.split("/") if x]
        if len(parts) >= 2:
            return parts[0], parts[1].replace(".git", "")
    except Exception:
        pass
    return None, None


def main():
    a = sys.argv[1:]
    if len(a) >= 2 and "/" in a[1]:
        owner, repo = repo_from_url(a[1] + "/" + a[2] if False else a[1])
        if not owner:
            owner, repo = a[0], a[1]
    elif len(a) >= 2:
        owner, repo = a[0], a[1]
    elif len(a) == 1:
        if "/" in a[0]:
            owner, repo = repo_from_url(a[0])
        else:
            owner, repo = a[0], None
    else:
        url = ask("GitHub repo adresi (yapistir): ")
        owner, repo = repo_from_url(url)

    if not owner:
        print("Kullanici adi alinamadi.")
        return
    if not repo:
        repo = "stickman-fighters"
    site = (a[2] if len(a) >= 3 else "") or ask("Site adresi (bos = github.io): ")

    tag = "1.4.0"
    pages = site or "https://%s.github.io/%s/" % (owner, repo)
    if not pages.endswith("/"):
        pages += "/"
    base = "https://github.com/%s/%s" % (owner, repo)

    print()
    print("=" * 66)
    print("  REPO   : %s" % base)
    print("  SAYFA  : %s" % pages)
    print("=" * 66)
    print()
    print("  1) Repo var mi / private mi?")
    st, msg = head(base)
    print("     %-46s %s  %s" % ("repo sayfasi", st or "HATA", msg))
    print()
    print("  2) Site yayinda mi?")
    st, msg = head(pages)
    print("     %-46s %s  %s" % ("ana sayfa", st or "HATA", msg))
    if st == 404:
        print("     -> 404: Pages YAYINLANMAMIS veya PRIVATE")
    print()
    print("  3) Actions calisti mi?")
    api = "https://api.github.com/repos/%s/%s/actions/workflows" % (owner, repo)
    st, msg = head(api)
    print("     %-46s %s" % ("workflows API", st or "HATA"))
    if st == 200:
        print("     -> API cevap verdi (workflow tanimli)")
    print()
    print("  4) Indirme baglantilari calisiyor mu?")
    rel = base + "/releases/latest/download/"
    for label, url in (
            ("PC zip (Releases)", rel + "STICKMAN-FIGHTERS-%s-PC.zip" % tag),
            ("APK  (Releases)", rel + "STICKMAN-FIGHTERS-%s.apk" % tag),
            ("PC zip (site yedek)", pages + "indir/STICKMAN-FIGHTERS-%s-PC.zip" % tag)):
        st, msg = head(url)
        mark = "OK " if st == 200 else ("404" if st == 404 else "hata")
        print("     [%s] %-46s %s" % (mark, label, st or "-"))
    print()

    # ---- site ayarini guncelle + PC zip'i paketle (hepsi tek komut)
    try:
        sys.path.insert(0, ROOT)
        import SITE_HAZIRLA as SH
        SH.patch_site(owner, repo, site)
        path, n = SH.build_pc_zip(owner, repo, site)
        print("  PC ZIP : %s (%d dosya, %.2f MB)"
              % (path.rsplit("\\", 1)[-1], n,
                 __import__("os").path.getsize(path) / 1048576.0))
        print("  Yedek  : SITE/indir/")
        print()
        print("  Simdi tek yapman gereken:")
        print("    1) Bu klasoru GitHub'a gonder (Site guncullendi)")
        print("    2) Actions -> SITE -> Run workflow")
        print("    3) %s adresini ac" % pages)
    except Exception as e:
        print("  Site guncellemesi yapilamadi: %s" % e)
    print()
    print("=" * 66)
    print("  COZUM (404 goruyorsan):")
    print("=" * 66)
    print("""
  A) REPO PRIVATE  ->  Settings > General > Danger Zone > Public YAP
                      (1 dakika, en kolay cozum)

  B) REPO PUBLIC AMA SAYFA 404
     Actions sekmesi -> "SITE" isimli is akisini bul -> Run workflow
     (SITE.yml sayfayi otomatik OWNER/REPO ile doldurup yayinlar)

  C) "Site not found" / Pages ayarli yok
     Settings -> Pages -> Source: "GitHub Actions" sec -> Save
     sonra Actions -> SITE -> Run workflow

  D) PRIVATE kalmak istiyorsan
     CLOUDFLARE_KURULUM.md dosyasina bak
     (Cloudflare Pages private repoyu destekler)
""")


if __name__ == "__main__":
    main()