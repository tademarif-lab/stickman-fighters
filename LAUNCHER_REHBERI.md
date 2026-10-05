# STICKMAN FIGHTERS — Launcher Rehberi

Launcher, Minecraft'taki gibi çalışır: ** ikonu aç → sürüm seç → Oyna → oyun başlar**.

## 1. Launcher'ı açmak (en kolay yol)

Oyun klasöründeki **`OYUNU_BASLAT.bat`** dosyasına **çift tıklama**.

Alternatif: oyun klasöründe `py launcher.py` ya da `python launcher.py`.

## 2. Masaüstü kısayolu + ikon (SANA GEREKEN ADIM)

Windows'ta ikonlu bir masaüstü kısayolu şöyle yapılır:

1. `OYUNU_BASLAT.bat` dosyasına **sağ tık** → **Kısayol oluştur**.
2. Oluşan kısayolu **masaüstüne** sürükle.
3. Kısayola **sağ tık** → **Özellikler**.
4. **Kısayol** sekmesi → **Simge değiştir...**
5. **Gözlüğe git...** → Klasör: `C:\Users\aaa\OneDrive\Masaüstü\STİCKMAN.FIGHTERS`
   (Klasörü bulamazsa tam yolu yaz)
6. `oyun_ikon.png` (oyun ikonu) veya `launcher_ikon.png` (launcher ikonu) dosyasını seç → **Tamam**.
7. **Genel** sekmesinde **Pencere durumu: Simgeye küçült** seç.
8. **Uygula** → **Tamam**.

Artık masaüstündeki ikona tıklayınca launcher açılır, sürümü seçip **OYNA**'ya
basınca oyun başlar.

### Simge bulanık görünürse
`oyun_ikon.png` 512×512 üretildi. Windows küçük boyutta bulanık gösterebilir;
bu durumda `launcher_ikon.png` (256×256)'yi seçebilirsin.

## 3. İkinci bir sürüm eklemek

Launcher `versions` klasöründeki her klasörü ayrı sürüm sayar:

```
STİCKMAN.FIGHTERS/
├── launcher.py
├── main.py
└── versions/
    ├── 1.0.0/        ← eski sürümün tam kopyası
    └── 1.2.0/        ← yeni sürümün tam kopyası
```

Yeni sürüm yapmak için: oyun klasörünün tamamını `versions` içine kopyalayıp
klasörü sürüm numarasıyla adlandır. Launcher açılınca listede görünür, seçip
Oyna'ya basınca o sürüm başlar.

Liste her launcher açılışında otomatik taranır; `settings.py` içindeki
`CHANGELOG` listesindeki sürüme ait güncelleme notu sağ panelde gösterilir.

## 4. Oyunu .exe yapmak (isteğe bağlı)

Python kurulu olmadan çalışan tek dosya istersen:

```
pip install pyinstaller
pyinstaller --onefile --windowed --icon oyun_ikon.png --name StickmanFighters main.py
```

Oluşan `dist\StickmanFighters.exe` çift tıklanabilir olur.
Launcher için aynısını `launcher.py` üzerinde çalıştırman gerekir
(`--name StickmanLauncher launcher.py`).

## 5. Sorun giderme

| Sorun | Çözüm |
|---|---|
| Launcher açılmıyor, siyah ekran | Python 3.11 kurulu mu? `python --version` yazıp kontrol et. |
| "HATA: Python bulunamadi" | Python kurulu değil veya PATH'e eklenmemiş. python.org'dan kur. |
| Oyna'ya basınca oyun açılmıyor | `versions` klasöründeki bozuk klasörü kontrol et. |
| Oyun çok yavaş | `python main.py` yerine masaüstü kısayolu kullanmak başlangıcı hızlandırır. |