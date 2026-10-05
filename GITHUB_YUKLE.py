# -*- coding: utf-8 -*-
"""GITHUB'A OTOMATIK YUKLEME + SAYFA YAYINLAMA

Ne yapar:
  1) SITE/ klasorunu repoya yukler
  2) .github/workflows/site.yml ve android-apk.yml yukler
  3) GitHub Pages'i acar
  4) SITE is akisini tetikler
  5) PC zip'ini v1.4.0 Release'ine yukler
  6) Sayfa acildi mi diye bekler ve kontrol eder

Kullanim:
    python GITHUB_YUKLE.py
    (Token soracak - gizli degil, ekrana yazilir, disari gonderilmez)
"""
import base64
import io
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OWNER = "tademarif-lab"
REPO = "stickman-fighters"
BRANCH = "master"
TAG = "1.4.0"

CTX = ssl.create_default_context()
API = "https://api.github.com"
TOKEN = [None]


# ------------------------------------------------------------------ yardimci
def req(method, url, body=None, raw=None, ctype="application/json"):
    h = {"Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28",
         "User-Agent": "SF-Uploader"}
    if TOKEN[0]:
        h["Authorization"] = "Bearer " + TOKEN[0]
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h["Content-Type"] = "application/json"
    elif raw is not None:
        data = raw
        h["Content-Type"] = ctype
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=40, context=CTX) as resp:
            b = resp.read()
            try:
                return resp.status, json.loads(b.decode("utf-8", "replace"))
            except Exception:
                return resp.status, b
    except urllib.error.HTTPError as e:
        b = e.read()
        try:
            return e.code, json.loads(b.decode("utf-8", "replace"))
        except Exception:
            return e.code, {"_raw": b[:200].decode("utf-8", "replace")}
    except Exception as e:
        return None, {"_hata": "%s: %s" % (type(e).__name__, str(e)[:70])}


def ok(s):
    print("  [OK]   " + s)


def bad(s):
    print("  [!!]   " + s)


def info(s):
    print("         " + s)


# ------------------------------------------------------------------ adim 1
def upload_file(path_in_repo, local_path):
    full = "%s/%s" % (API, "repos/%s/%s/contents/%s"
                      % (OWNER, REPO, urllib.parse.quote(path_in_repo)))
    st, d = req("GET", full)
    sha = d.get("sha") if isinstance(d, dict) else None
    with io.open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    body = {
        "message": "site: " + path_in_repo,
        "content": content,
        "branch": BRANCH,
    }
    if sha:
        body["sha"] = sha
    st, d = req("PUT", full, body=body)
    if st in (200, 201):
        ok("%s  %s" % (path_in_repo,
                       "(guncellendi)" if sha else "(yeni)"))
        return True
    msg = d.get("message") if isinstance(d, dict) else str(d)
    bad("%s -> %s %s" % (path_in_repo, st, msg))
    return False


def upload_tree(src_dir, repo_prefix):
    n = 0
    for r, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            if f.endswith(".pyc"):
                continue
            p = os.path.join(r, f)
            rel = os.path.relpath(p, src_dir).replace("\\", "/")
            if upload_file("%s/%s" % (repo_prefix, rel) if repo_prefix else rel,
                           p):
                n += 1
    return n


# ------------------------------------------------------------------ adim 2
def enable_pages():
    url = "%s/repos/%s/%s/pages" % (API, OWNER, REPO)
    st, d = req("POST", url, body={"build_type": "workflow"})
    if st in (201, 200):
        ok("GitHub Pages acildi")
        return True
    msg = d.get("message") if isinstance(d, dict) else str(d)
    if "already" in str(msg).lower():
        ok("GitHub Pages zaten acik")
        return True
    info("Pages API ile acilamadi (%s: %s)" % (st, msg))
    info("-> Sayfa zaten acik olabilir, sonra dogrulanacak")
    return False


# ------------------------------------------------------------------ adim 3
def dispatch(wf):
    url = "%s/repos/%s/%s/actions/workflows/%s/dispatches" % (
        API, OWNER, REPO, wf)
    st, d = req("POST", url, body={"ref": BRANCH})
    if st == 204:
        ok("%s is akisi tetiklendi" % wf)
        return True
    msg = d.get("message") if isinstance(d, dict) else str(d)
    bad("%s tetiklenemedi -> %s %s" % (wf, st, msg))
    return False


# ------------------------------------------------------------------ adim 4
def make_release():
    url = "%s/repos/%s/%s/releases" % (API, OWNER, REPO)
    st, d = req("GET", url + "/tags/" + "v" + TAG)
    rel_id = None
    if st == 200 and isinstance(d, dict):
        rel_id = d.get("id")
    if not rel_id:
        st, d = req("POST", url, body={
            "tag_name": "v" + TAG,
            "name": "STICKMAN FIGHTERS " + TAG,
            "target_commitish": BRANCH,
            "draft": False,
            "prerelease": False,
            "body": ("## STICKMAN FIGHTERS %s\n\n"
                     "| Platform | Dosya |\n|---|---|\n"
                     "| PC (Windows) | `STICKMAN-FIGHTERS-%s-PC.zip` |\n"
                     "| Telefon (Android) | `STICKMAN-FIGHTERS-%s.apk` |\n"
                     % (TAG, TAG, TAG)),
        })
        if st in (200, 201):
            rel_id = d.get("id")
            ok("Release v%s olusturuldu" % TAG)
        else:
            info("Release olusturulamadi: %s %s"
                 % (st, d.get("message") if isinstance(d, dict) else d))
            return False
    else:
        ok("Release v%s zaten var" % TAG)

    # PC zip'i yukle
    zp = os.path.join(ROOT, "YAYIN", "STICKMAN-FIGHTERS-%s-PC.zip" % TAG)
    if not os.path.isfile(zp):
        bad("PC zip bulunamadi: %s (SITE_HAZIRLA.py calistir)" % zp)
        return False
    with io.open(zp, "rb") as f:
        data = f.read()
    up = ("https://uploads.github.com/repos/%s/%s/releases/%s/assets?name=%s"
          % (OWNER, REPO, rel_id,
             urllib.parse.quote("STICKMAN-FIGHTERS-%s-PC.zip" % TAG)))
    st, d = req("POST", up, raw=data, ctype="application/zip")
    if st == 201:
        ok("PC zip yuklendi (%.2f MB)" % (len(data) / 1048576.0))
    elif st == 422:
        info("PC zip zaten yuklu (422)")
    else:
        msg = d.get("message") if isinstance(d, dict) else str(d)
        bad("PC zip yuklenemedi: %s %s" % (st, msg))
    return True


# ------------------------------------------------------------------ adim 5
def check_site(wait=150):
    url = "https://%s.github.io/%s/" % (OWNER, REPO)
    print()
    print("  Site bekleniyor (%ds)..." % wait)
    for i in range(wait // 5):
        time.sleep(5)
        st, d = req("GET", url)
        if st == 200:
            ok("SITE YAYINDA: %s" % url)
            return url
        sys.stdout.write("\r         deneme %2d/%d  -> %s"
                         % (i + 1, wait // 5, st))
        sys.stdout.flush()
    print()
    bad("Site hala yuklenmedi. Actions -> SITE -> calistirmayi kontrol et.")
    print("         Elle ac:  %s" % url)
    return url


def check_token():
    url = "%s/repos/%s/%s" % (API, OWNER, REPO)
    st, d = req("GET", url)
    if st == 200:
        return d
    return None


if __name__ == "__main__":
    print()
    print("=" * 64)
    print("  GITHUB OTOMATIK YUKLEME  -  %s/%s" % (OWNER, REPO))
    print("=" * 64)
    print()

    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok:
        print("  GitHub Personal Access Token (PAT) gerekiyor.")
        print("  Alma adimi:")
        print("    1) https://github.com/settings/tokens/new")
        print("    2) Name: SF-YUKLEME   Expiration: 7 days")
        print("    3) Kutucuklari isaretle:")
        print("         repo (Contents: Read and write)")
        print("         workflow (Actions: Read and write)")
        print("         administration (Pages: Read and write)")
        print("    4) Generate token")
        print()
        print("  Token'i yapistir (gizlidir, sadece bu bilgisayarda kullanilir):")
        try:
            tok = input("  > ").strip()
        except EOFError:
            tok = ""
    TOKEN[0] = tok

    st, d = req("GET", "%s/repos/%s/%s" % (API, OWNER, REPO))
    if st != 200:
        print()
        bad("Baglanti hatasi / token gecersiz: %s %s"
            % (st, d.get("message") if isinstance(d, dict) else d))
        print("  Token'i kontrol et ve tekrar dene.")
        sys.exit(1)
    ok("Baglantii kuruldu  (repo: %s, private=%s)"
       % (d.get("full_name"), d.get("private")))
    br = d.get("default_branch") or "master"
    if br != BRANCH:
        BRANCH = br
        info("Varsayilan dal: %s" % BRANCH)

    print()
    print("  1) SITE yukleniyor")
    site = os.path.join(ROOT, "SITE")
    if not os.path.isdir(site):
        bad("SITE klasoru yok. python SITE_HAZIRLA.py calistir.")
        sys.exit(1)
    n = upload_tree(site, "SITE")
    ok("%d dosya yuklendi (SITE/)" % n)

    print()
    print("  2) Is akislari yukleniyor")
    wfdir = os.path.join(ROOT, ".github", "workflows")
    for f in ("site.yml", "android-apk.yml"):
        p = os.path.join(wfdir, f)
        if os.path.isfile(p):
            upload_file(".github/workflows/" + f, p)

    print()
    print("  3) GitHub Pages")
    enable_pages()

    print()
    print("  4) Release olusturuluyor + PC zip")
    make_release()

    print()
    print("  5) SITE is akisi tetikleniyor")
    dispatch("site.yml")

    print()
    print("=" * 64)
    url = check_site()
    print("=" * 64)
    print()
    print("  Site     : %s" % url)
    print("  PC ZIP   : https://github.com/%s/%s/releases/latest/download/"
          "STICKMAN-FIGHTERS-%s-PC.zip" % (OWNER, REPO, TAG))
    print("  APK      : https://github.com/%s/%s/releases/latest/download/"
          "STICKMAN-FIGHTERS-%s.apk" % (OWNER, REPO, TAG))
    print()
    print("  APK derlemek icin:  Actions -> ANDROID APK -> Run workflow")
    print("  (20-25 dk, bitince APK otomatik Releases'a yuklenir)")
    print()
    print("  Token'i silmek icin:")
    print("  https://github.com/settings/tokens  ->  token'a tikla  ->  Delete")