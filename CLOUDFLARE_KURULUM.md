# 🔒 REPO PRIVATE KALACAKSA — CLOUDFLARE PAGES

**GitHub Pages private repoda çalışmaz** (bedava hesapta) → 404 verir.
Ama **Cloudflare Pages** private repoyu destekler. Ücretsiz, 7/24, HTTPS.

| | GitHub Pages | **Cloudflare Pages** |
|---|---|---|
| Private repo | ❌ 404 | ✅ **çalışır** |
| Ücret | ücretsiz | ücretsiz |
| 7/24 | ✅ | ✅ |
| Duraklama | yok | **yok** (Netlify'de var) |
| Özel alan adı | ❌ | ✅ |

---

## 📋 ADIMLAR (5 dakika)

### 1) GitHub'da erişim izni ver
Repo → **Settings** → **Collaborators** → **Add people**
→ **`cloudflare`** yaz → **Add** (ekran açılır)

Bu, Cloudflare bot'unun repoyu görmesi için gerekli.

### 2) Cloudflare hesabı aç
Tarayıcıda → **dash.cloudflare.com** → ücretsiz üye ol

### 3) Pages projesi oluştur
1. Sol menüden **Workers & Pages** → **Create application**
2. **Pages** → **Connect to Git**
3. GitHub'ı seç → GitHub hesabını bağla
4. **Authorize** → tüm repolara erişim ver (ya da sadece bu repoyu seç)
5. Repo listesinden **stickman-fighters**'ı seç → **Begin setup**

### 4) Ayarları gir
| Alan | Değer |
|---|---|
| Project name | `stickman-fighters` |
| Production branch | `main` (ya da `master`) |
| **Build command** | *(boş bırak)* |
| **Build output directory** | `SITE` |

> ⚠️ **Build output = `SITE`** — bu en önemli kısım.

**Save and Deploy** → 30 saniyede site yayında:
```
https://stickman-fighters.pages.dev
```

### 5) Siteye adresini yaz
Yayınlandıktan sonra:
```powershell
python SITE_HAZIRLA.py KULLANICIADIN stickman-fighters https://stickman-fighters.pages.dev
```
Sonra tekrar GitHub'a gönder → Cloudflare otomatik yeniler.

---

## 📁 Dosya yapısı ne olmalı

```
stickman-fighters/          ← GitHub reposu
├── SITE/                   ← Cloudflare bunu yayınlar
│   ├── index.html
│   ├── favicon.png
│   ├── APK_YAPIMI.md
│   ├── MOBIL_REHBERI.md
│   ├── ONLINE_REHBERI.md
│   └── indir/
│       └── STICKMAN-FIGHTERS-1.4.0-PC.zip   ← yedek indirme
└── .github/workflows/      ← APK derleme (private repo'da da çalışır)
    └── android-apk.yml
```

`python SITE_HAZIRLA.py` çalıştırınca zip hem `YAYIN/` klasörüne hem de
`SITE/indir/` klasörüne konur → **site üzerinden de PC sürümü indirilebilir.**

---

## 📱 APK Private Repoda Nasıl Dağıtılır?

Private repoda **Releases bağlantıları 404 verir** (ziyaretçi giriş yapamaz).
3 seçenek:

### Seçenek A — APK'yı siteye koy (en basit) ⚠️
APK ~80 MB. Cloudflare Pages dosya başına **25 MB** sınırı koyar.
APK 25 MB'ın altına sıkıştırılabilirse (`app bundle`/obfuscation) yöntem
Cloudflare **R2** kullanmak daha doğru:

1. Cloudflare Dashboard → **R2** → **Create bucket** (`apk`)
2. Bucket'e APK yükle
3. **Settings → Public access → Connect domain** veya
   **R2.dev subdomain** aç → `https://pub-xxx.r2.dev/STICKMAN-FIGHTERS-1.4.0.apk`
4. `SITE/index.html` içinde `APK_YEDEK` satırına bu adresi yaz

**R2 ücretsiz:** 10 GB depolama + aylık 10 milyon indirme.

### Seçenek B — Ayrı public indirme reposu (en kolay) ✅
1. GitHub'da yeni **public** repo: `stickman-fighters-downloads`
   (boş olsun, kod olmasın)
2. **Actions → android-apk.yml** çalıştır → APK otomatik oraya yüklenir
3. Site butonlarını o repoya yönlendir

Game kodu private kalır, sadece indirme linkleri public olur.

### Seçenek C — itch.io (en kolay, oyuncu odaklı) ✅
1. **itch.io**'da ücretsiz hesap aç
2. **Create new project** → `STICKMAN FIGHTERS`
3. **Upload files** → `main.py`, `ui.py`, ... hepsini yükle
   (itch.io oyuncu için "Play in browser" bile sunar)
4. Sayfana bağlantıyı siteye koy

itch.io reklamla desteklenir, oyuncular için en tanıdık yer.

---

## 🏆 TAVSİYEM

Repo'yu **public** yap. Nedenleri:
- GitHub Pages hemen çalışır (0 ayar)
- Releases bağlantıları çalışır → APK + ZIP tek yerden
- Actions aynı şekilde çalışır
- Oyun kaynağı public olması **hiçbir dezavantaj değil**
  (binlerce oyun açık kaynak; kimse bir şey kaybetmez)
- Yedek için ayrı **private** repo tutarsın

Private kalmak gerçekten şartsa → **Cloudflare Pages + Seçenek B** kombinasyonu
(ziyaretçiler public indirme reposundan indirir, oyun kodu private kalır).

---

## ⚡ Kontrol listesi

- [ ] Repo **public** (ya da Cloudflare kuruldu)
- [ ] `python SITE_HAZIRLA.py` çalıştırıldı
- [ ] `SITE/` klasörü repoda var
- [ ] `.github/` klasörü **gizli değil**
- [ ] Actions → **SITE** çalıştırıldı
- [ ] Actions → **ANDROID APK** çalıştırıldı
- [ ] Releases'a PC zip yüklendi
- [ ] Site açıldı, PC butonu çalışıyor
- [ ] Site açıldı, telefon butonu çalışıyor
- [ ] Telefonda APK kuruldu ve açıldı