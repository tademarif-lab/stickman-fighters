# ⬆ GitHub'a YÜKLE

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
