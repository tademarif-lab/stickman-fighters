# 🌐 STICKMAN FIGHTERS — ONLINE MOD (4 Kişilik Oda)

## Nasıl oynanır?

### 1) Sunucuyu başlat (sunucu olmak istediğin bilgisayarda)
```
SUNUCU_BASLAT.bat
```
Ekranda **IP adresi** yazar (ör. `192.168.1.35`) ve **Port: 27015**.

### 2) Arkadaşların bağlansın
Oyun → **ONLINE** →
- **SUNUCU IP**: yazdığın IP (ör. `192.168.1.35`)
- **PORT**: `27015`
- **İSİM**: adın
- **BAĞLAN**

> Aynı Wi-Fi / aynı kablo ağı olması yeterli. İnternet ayarı gerekmez.

---

## 🔒 Kilitli (şifreli) Oda

1. **ODA ŞİFRE** kutusuna şifre yaz (ör. `1234`)
2. **ODA KUR** → oda listede **KİLİTLİ** olarak çıkar
3. Arkadaşın odaya tıklayınca **ŞİFRE GİR** yazar → şifreyi girip **ENTER**

Şifre boş bırakırsan oda herkese açık olur. Odadaki hiçbir oyuncu şifreyi göremez,
sadece doğru şifre giren girebilir.

---

## 👥 4 Kişi Nasıl Oynanır?

Oda **en fazla 4 kişi** alır. Maçlar **1v1** olur ve **turnuva sırası** işler:

```
Oda:  Ali | Veli | Ayşe | Kaan
1. maç:  Ali  vs  Veli     → Ali kazanır
2. maç:  Ali  vs  Kaan     (Veli sıra sonuna geçer)
3. maç:  Ali  vs  Veli     (Kaan sıra sonuna)
...
```
- Oda sahibi (**ODA KUR**'u basan kişi) **MACI BAŞLAT** der
- Kazanan yerde kalır, kaybeden sıradakiyle eşleşir
- Herkesin kazandığı maç sayısı odada görünür

---

## 📋 Komutlar

| Buton | Ne yapar |
|---|---|
| **BAĞLAN** | Sunucuya bağlanır |
| **YENİLE** | Oda listesini tazeler |
| **ODA KUR** | Yeni oda açar (şifre kutusu doluysa kilitli) |
| **MACI BAŞLAT** | Sadece oda sahibi → maçı başlatır |
| **ODADAN ÇIK** | Bulunduğun odadan ayrılır |
| **GERİ (ESC)** | Ana menü |

**Klavye:** `Tab` alan değiştirir, `Enter` uygular, `ESC` ana menü.
**Sohbet:** Alttaki mesaj kutusuna yazıp `Enter`.

---

## 📁 Dosyalar

| Dosya | Görevi |
|---|---|
| `server.py` | Sunucu (oda yönetimi, maç simülasyonu, 4 kişi limiti) |
| `netproto.py` | Ortak protokol (mesajlar, girdi paketi, durum özeti) |
| `online.py` | İstemci + online lobi ekranı |
| `SUNUCU_BASLAT.bat` | Sunucuyu tek tıkla başlatır |

Farklı port istersen: `python server.py 28000` ya da
`SUNUCU_BASLAT.bat 28000`