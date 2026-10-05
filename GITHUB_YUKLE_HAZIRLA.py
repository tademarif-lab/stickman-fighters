# -*- coding: utf-8 -*-
"""GitHub'a yuklenecek dosyalari tek klasorde toplar.

Cikti:  GITHUB_YUKLE/
          SITE/                        (indirme sitesi)
          .github/workflows/site.yml   (siteyi yayinlayan is akisi)
          OKUBENI.md                   (ne yapacaksin)
"""
import io
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "GITHUB_YUKLE")

ITEMS = [
    ("SITE", os.path.join(ROOT, "SITE")),
    ("os.makedirs", None),
]


def copytree(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # 1) SITE klasoru
    copytree(os.path.join(ROOT, "SITE"), os.path.join(OUT, "SITE"))

    # 2) .github/workflows/site.yml
    wf = os.path.join(OUT, ".github", "workflows")
    os.makedirs(wf)
    shutil.copy2(os.path.join(ROOT, ".github", "workflows", "site.yml"),
                 os.path.join(wf, "site.yml"))

    # 3) p4a tabanli APK workflow (eski buildozer surumu yerine)
    shutil.copy2(os.path.join(ROOT, ".github", "workflows", "android-apk.yml"),
                 os.path.join(wf, "android-apk.yml"))

    # 4) APK_YAPIMI.md (Actions'ta gorunsun)
    shutil.copy2(os.path.join(ROOT, "APK_YAPIMI.md"),
                 os.path.join(OUT, "APK_YAPIMI.md"))

    # 5) kullanim
    with io.open(os.path.join(OUT, "OKUBENI.md"), "w", encoding="utf-8") as f:
        f.write(TEXT)

    # listele
    total = 0
    print("GITHUB_YUKLE hazir:")
    for r, d, fs in os.walk(OUT):
        rel = os.path.relpath(r, OUT)
        for x in sorted(fs):
            p = os.path.join(r, x)
            size = os.path.getsize(p)
            if size > 1024:
                size = "%.0f KB" % (size / 1024.0)
            else:
                size = "%d B" % size
            print("   %-46s %8s" % (os.path.join(rel, x).replace("\\", "/"),
                                    size))
            total += 1
    print("\n%d dosya" % total)


TEXT = """# ⬆ GitHub'a YÜKLE

Bu klasördeki **3 şey** repoya yüklenmeli.

## Adımlar (2 dakika)

1. GitHub'da şu repoyu aç:
   **https://github.com/tademarif-lab/stickman-fighters**

2. **Add file → Upload files** butonuna bas

3. Bu klasördeki her şeyi **sürükle bırak**:
   - `SITE/` klasörü
   - `.github/` klasörü
   - `APK_YAPIMI.md`

   > ⚠️ Tarayıcı **gizli dosyaları (. ile başlayan) atar**!
   > `.github` görünmüyorsa: sağ üstteki **"… / Upload files"** yerine
   > önce **"Add file" → "Create new file"** ile
   > `.github/workflows/site.yml` yolunu elle yaz, sonra
   > **"SITE/index.html"** için aynısını yap.
   >
   > **Kolay yol:** Bilgisayarında GitHub Desktop varsa, ya da
   > `git` kuruluysa aşağıdaki komutlar:
   > ```
   > cd GITHUB_YUKLE
   > git init
   > git add .
   > git commit -m "site + apk workflow"
   > git remote add origin https://github.com/tademarif-lab/stickman-fighters.git
   > git push -f origin HEAD:master
   > ```

4. Commit yeşil **Commit changes** → yüklendi

## Sonra

### A) Pages'ı aç
**Settings → Pages → Build and deployment → Source**
→ **GitHub Actions** seç → **Save**

### B) Siteyi yayınla
**Actions** sekmesi → **SITE** → **Run workflow** → 🟢
~1 dakika → site açılır:
```
https://tademarif-lab.github.io/stickman-fighters/
```

### C) APK derle
**Actions → ANDROID APK → Run workflow** → 🟢
20-25 dakika → APK **otomatik Releases'a yüklenir**,
site butonu kendiliğinden çalışır.

### D) PC zip'i Releases'a yükle
**Releases → New release**
- tag: `v1.4.0`
- dosya: `YAYIN/STICKMAN-FIGHTERS-1.4.0-PC.zip`

---

## Not

Bu repoda oyun dosyaları **`TELEFON_OYUN/`** klasöründe.
Bu site için sorun değil — site `SITE/` klasöründen yayınlanır.
"""

if __name__ == "__main__":
    main()