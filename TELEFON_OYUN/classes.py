# -*- coding: utf-8 -*-
"""Karakter siniflari (30) + yetenek tanimlari. Motor: skills.py"""

PX = 40


def ST(kind, dur=0.0, dps=0.0, power=0.0):
    return {"kind": kind, "dur": dur, "dps": dps, "power": power}


def S(name, cd, desc, kind="melee", dmg=0.0, **kw):
    d = {"name": name, "cd": float(cd), "desc": desc, "kind": kind, "dmg": float(dmg)}
    d.update(kw)
    return d


SKILLS = {}


def _add(*pairs):
    for key, val in pairs:
        SKILLS[key] = val


# ------------------------------------------------------- 2. VAMPİR
_add(
 ("v_kilic", S("Bıçak Saldırısı", 0.5, "Bıçak çıkarıp saldırır, 10 hasar verir ve kendisine 10 can yeniler.",
   dmg=10, heal=10, range=54, ytop=60, h=18, pose="punch", fx="knife")),
 ("v_gorunmez", S("Görünmezlik", 5.0, "10 saniyeliğine görünmez olur, süre bitince görünürlüğe geri döner.",
   kind="buff", buff=["invisible"], buff_time=10.0)),
 ("v_yarasa", S("Yarasa Fırlat", 12.5, "3 yarasa fırlatır. Yarasalar 2 kere saldırır, her vuruş 1.5 hasar verir ve hızı azaltır.",
   kind="proj", dmg=1.5, hits=2, count=3, speed=430, life=1.5, size=9,
   color=(70, 50, 80), status=ST("slow", 3.0, 0.0, 0.5), spread=0.16, fly=True)),
 ("v_ult", S("Kan Sırmanı", 15.0, "15 yarasa fırlatır. Değdiği yer 3 can çalar, 6 hasar verir ve hızı 3 kat artar.",
   kind="proj", dmg=6, hits=1, count=15, speed=520, life=1.8, size=11,
   color=(120, 20, 40), lifesteal=3.0, buff=["speed"], buff_time=6.0,
   buff_power=3.0, spread=0.42, fly=True, is_ult=True)),
)

# ------------------------------------------------------- 3. ZOMBİ
_add(
 ("z_yumruk", S("Zehirli Yumruk", 0.5, "Yumruk atar ve rakibi 3 saniyeliğine zehirler (zehir saniyede 0.5 hasar verir).",
   dmg=4, range=50, ytop=60, h=18, pose="punch", status=ST("poison", 3.0, 0.5))),
 ("z_isirik", S("Isırık", 2.5, "Oyuncuyu ısırır ve 10 saniyeliğine zehirler.",
   dmg=6, range=42, ytop=52, h=16, pose="punch", status=ST("poison", 10.0, 0.6))),
 ("z_diril", S("Ölüm Diriltme", 15.0, "10 saniye içinde oyuncu ölürse 50 canla tekrar dirilir.",
   kind="revive", revive_hp=50, revive_time=10.0, is_ult=True)),
)

# ------------------------------------------------------- 4. İSKELET
_add(
 ("i_yumruk", S("Kemik Yumruğu", 0.5, "Yumruk atar ancak kendi hızını azaltır.",
   dmg=6, range=48, ytop=58, h=18, pose="punch", self_slow=0.45, self_slow_time=1.2)),
 ("i_parca", S("Kemik Parçası", 6.0, "Kendinden bir parça fırlatır ve 2.5 hasar verir. Parça yere düşer; eğilip üstüne gelirsen geri alırsın.",
   kind="proj", dmg=2.5, count=1, speed=520, life=1.1, size=10,
   color=(230, 230, 210), pickup=True, spin=True)),
 ("i_kanca", S("Kanca Mekanizması", 15.0, "Vücut parçalarını kullanarak kanca oluşturur ve oyuncuyu yanına çeker.",
   kind="pull", dmg=8, range=340, is_ult=True)),
 ("i_ult", S("Yeniden Doğuş", 15.0, "Zombideki gibi öldüğünde tekrar dirilir ancak 25 canla başlar. Vuruş gücü 2 katına çıkar, hızı 4 kat düşer.",
   kind="revive", revive_hp=25, revive_time=999.0, dmg_mult=2.0, speed_div=4.0,
   is_ult=True)),
)

# ------------------------------------------------------- 5. MUTANT
_add(
 ("mu_yumruk", S("Dev Yumruk", 0.5, "Yumruk atar ancak kendi hızını 5 kat düşürür.",
   dmg=9, range=58, ytop=62, h=22, pose="punch", self_slow=0.2, self_slow_time=1.5)),
 ("mu_tok", S("Yere Vurma", 5.0, "Yere sert basar, etraf titrer ve ses dalgası yayılır. Rakip zıplarsa hasar almaz, zıplamazsa 10 hasar yer.",
   kind="zone", dmg=10, zw=PX * 5, life=0.55, dodge="zıpla", color=(150, 110, 70),
   shake=14, stun=1.0)),
 ("mu_firlat", S("Yakala ve Fırlat", 30.0, "Oyuncuyu tutar, haritanın diğer ucuna fırlatır ve 25 hasar verir.",
   kind="throw", dmg=25, is_ult=True)),
 ("mu_ult", S("Devleşme", 15.0, "Canı 300 olur ancak hasarı yarıya iner ve hızı 10 kat düşer.",
   kind="buff", buff=["dmg_half", "speed"], buff_time=8.0, buff_power=0.1,
   max_hp=300, is_ult=True)),
)

# ------------------------------------------------------- 6. ZEHRİ KRALI
_add(
 ("zk_yumruk", S("Zehirli Yumruk", 0.5, "Yumruk atar ve 3 saniyeliğine zehirler.",
   dmg=6, range=52, ytop=60, h=18, pose="punch", status=ST("poison", 3.0, 1.0))),
 ("zk_dalga", S("Zehir Dalgası", 3.0, "Zehir dalgası gönderir. Rakip eğilirse kurtulur, eğilmezse 5 saniye zehirlenir ve fazladan 5 hasar alır.",
   kind="zone", dmg=5, zw=PX * 5.5, life=0.7, dodge="eğil", color=(120, 200, 70),
   status=ST("poison", 5.0, 0.8))),
 ("zk_top", S("Zehir Topları", 45.0, "Düşmanı takip eden 15 adet zehir topu fırlatır (değenler 10 saniye zehirlenir + 10 hasar alır).",
   kind="proj", dmg=10, count=15, speed=300, life=3.0, size=10,
   color=(140, 220, 80), homing=6.0, status=ST("poison", 10.0, 0.6), is_ult=True)),
 ("zk_ult", S("Zehir Kraliçesi", 18.0, "30 adet takip eden zehir topu ve 15 adet zehir dalgası fırlatır.",
   kind="proj", dmg=10, count=30, speed=320, life=3.2, size=11,
   color=(170, 240, 90), homing=7.0, status=ST("poison", 12.0, 0.8),
   extra_zones=15, is_ult=True)),
)

# ------------------------------------------------------- 7. ATEŞ MANYAĞI
_add(
 ("am_yumruk", S("Yanan Yumruk", 0.5, "Normal yumruk atar ancak rakibi 5 saniyeliğine yakar.",
   dmg=6, range=50, ytop=60, h=18, pose="punch", status=ST("burn", 5.0, 1.2))),
 ("am_alani", S("Ateş Alanı", 10.0, "15 piksel ileriye kadar olan alanı yakar. Değen kişi 5 hasar alır ve 10 saniye yanma efekti kazanır.",
   kind="zone", dmg=5, zw=PX * 7.5, life=2.5, color=(230, 110, 30),
   status=ST("burn", 10.0, 1.0), forward=0.7, repeat=0.5)),
 ("am_petrol", S("Petrol Şişesi", 12.0, "Bir şişe petrol fırlatır ve 12 piksellik bir alan yakar. Alanın içine girenler 10 saniye yanma efekti alır.",
   kind="proj", dmg=4, count=1, speed=380, life=1.4, size=11,
   color=(60, 50, 40), gravity=900, burst_zone=PX * 6, burst_life=4.0,
   status=ST("burn", 10.0, 1.1), arc=True)),
 ("am_ult", S("Ateş Kasırgası", 18.0, "3. özelliğini aynı anda kullanır ve ateş hasarı 2 katına çıkar.",
   kind="zone", dmg=14, zw=PX * 12, life=4.0, color=(255, 140, 40),
   status=ST("burn", 14.0, 2.2), extra_proj=3, proj_dmg=8, is_ult=True)),
)

# ------------------------------------------------------- 8. MADENCİ
_add(
 ("md_kazma", S("Kazma Fırlat", 2.5, "1 kazma fırlatıp geri çeker.",
   kind="proj", dmg=6, count=1, speed=470, life=1.2, size=13,
   color=(180, 180, 190), spin=True, return_home=True)),
 ("md_meshale", S("Meşale", 10.0, "Eline meşale alır; yanındaki 5 piksellik alana girenler hasar alır.",
   kind="zone", dmg=3, zw=PX * 5, life=4.0, color=(255, 190, 70),
   follow=True, repeat=0.5)),
 ("md_kalkan", S("Kalkan", 15.0, "10 saniye süren bir kalkan açar. Alacağı hasarı yarıya indirir ve engellediği o yarı hasarı düşmana yansıtır.",
   kind="buff", buff=["shield", "reflect"], buff_time=10.0, buff_power=0.5)),
 ("md_ult", S("Kazma Fırtınası", 20.0, "6 kazma fırlatır, hepsi 3.5 hasar verir ve geri döner. Ayrıca hedefe Madenci Yorgunluğu efekti verir (hasarı yarıya indirir, hızı 2 kat azaltır).",
   kind="proj", dmg=3.5, count=6, speed=540, life=1.4, size=12,
   color=(200, 200, 210), spin=True, return_home=True, is_ult=True,
   status=ST("weak", 8.0, 0.0, 0.5))),
)

# ------------------------------------------------------- 9. SU KRALI
_add(
 ("sk_top", S("Su Topu", 1.5, "İleriye su topu fırlatır (22.5 hasar).",
   kind="proj", dmg=22.5, count=1, speed=440, life=1.6, size=16,
   color=(70, 150, 255), status=ST("slow", 2.0, 0.0, 0.4))),
 ("sk_duvar", S("Su Duvarı", 5.5, "Su duvarı oluşturur, 5 saniye sonra bu duvarı dalga olarak ileri fırlatır.",
   kind="wall", dmg=10, zw=PX * 4, wall_h=90, wall_time=5.0,
   wave_speed=520, color=(60, 130, 240), wall_dmg=14)),
 ("sk_hepsi", S("Sel", 15.5, "3 su topu, 2 su dalgası ve 1 su duvarı gönderir.",
   kind="wall", dmg=12, zw=PX * 4, wall_h=90, wall_time=4.0,
   wave_speed=560, color=(60, 130, 240), proj_count=3, proj_dmg=12, waves=2,
   is_ult=True)),
 ("sk_tsunami", S("Tsunami", 25.0, "Bir tsunamiye biner ve oyuncuyu kovalar. 15 saniye sonra iner ama tsunami 5 saniye daha kovalamaya devam eder (her vuruş 2.5 hasar).",
   kind="chase", dmg=2.5, chase_time=15.0, tail_time=5.0, size=60,
   color=(50, 140, 255), speed=190, is_ult=True)),
)

# ------------------------------------------------------- 10. YILDIRIM PATRONU
_add(
 ("yp_yumruk", S("Elektrik Yumruğu", 0.5, "Yumruk atar. 5 kişiye kadar seken çarpılma efekti uygular (yumruğun kendisi 5 hasar + 2.5 çarpılma hasarı).",
   dmg=5, range=52, ytop=60, h=18, pose="punch", chain=5, chain_dmg=2.5)),
 ("yp_alan", S("Elektrik Alanı", 15.5, "15 piksellik bir alan açar; oraya giren kişi 5 saniye boyunca çarpılır.",
   kind="zone", dmg=2, zw=PX * 7.5, life=5.0, color=(120, 200, 255),
   status=ST("shock", 5.0, 1.0, 0.4), repeat=0.6)),
 ("yp_zemin", S("Zemin Elektriği", 35.5, "35.5 piksellik alanın zeminine elektrik salar. Kaçmak için zıplamak gerekir; zıplanmazsa 10 saniye çarpılma efekti uygulanır.",
   kind="zone", dmg=8, zw=PX * 12, life=4.0, dodge="zıpla",
   color=(160, 220, 255), status=ST("shock", 10.0, 1.4, 0.6), is_ult=True)),
 ("yp_ult", S("Fırtına", 18.0, "3. özelliğin birleşimidir ancak tüm hasarları 2 katına çıkar.",
   kind="zone", dmg=16, zw=PX * 14, life=5.0, dodge="zıpla",
   color=(200, 240, 255), status=ST("shock", 12.0, 2.6, 0.7),
   extra_proj=3, proj_dmg=10, is_ult=True)),
)

# ------------------------------------------------------- 11. ELEMENT KRALI
_add(
 ("ek_toprak", S("Toprak Atma", 2.0, "5 piksel ileri toprak atar (5.5 hasar).",
   kind="proj", dmg=5.5, count=1, speed=400, life=1.2, size=13,
   color=(130, 95, 55), gravity=700, arc=True)),
 ("ek_duvar", S("Toprak Duvarı", 8.5, "5 saniye duran bir duvar yapar. Süre bitince ileriye doğru 5 adet sertleşmiş toprak dikeni fırlatır (tanesi 5 hasar verir).",
   kind="wall", dmg=5, zw=PX * 3.5, wall_h=80, wall_time=5.0,
   wave_speed=500, spikes=5, spike_dmg=5, color=(140, 100, 58))),
 ("ek_minyon", S("Toprak Minyonları", 15.9, "5 adet toprak minyon üretir. (2 Okçu: uzaktan saldırır, 15 can. 2 Savaşçı: yakından saldırır, 25 can. 1 Elit Savaşçı: hem uzak hem yakın, 30 can).",
   kind="summon", count=5, is_ult=True)),
 ("ek_ult", S("Element Fırtınası", 20.0, "3. özelliğin birleşimidir ancak üretilen minyonların sayısı 2 katına çıkar.",
   kind="summon", count=10, is_ult=True)),
)

# ------------------------------------------------------- 12. HAVA PATRONU
_add(
 ("hp_yumruk", S("Hava Yumruğu", 1.0, "Yumruk atar ve rakibi 3 saniyeliğine havaya uçurur. Rakip aşağı düştüğünde havada kaldığı saniyeye göre artan bir düşüş hasarı (saniyede +2.5) alır.",
   dmg=6, range=52, ytop=60, h=18, pose="punch", status=ST("fall", 3.0, 2.5),
   launch=430)),
 ("hp_dalga", S("Hava Dalgası", 15.0, "Hava dalgası gönderir. Değen kişiler 15 saniye uçar, kaçınmak için eğilmek gerekir.",
   kind="zone", dmg=10, zw=PX * 8, life=0.9, dodge="eğil", color=(200, 240, 255),
   status=ST("fly", 15.0), knock=520)),
 ("hp_ufleme", S("Hava Üfleme", 3.5, "6 piksellik bir alana hava üfler. Dostlara 2.5 can yeniler, düşmanlara 2.5 hasar verir.",
   kind="zone", dmg=2.5, zw=PX * 3, life=0.7, color=(210, 245, 255),
   heal=2.5, push=260)),
 ("hp_kasirga", S("Dev Kasırga", 35.0, "35 saniye boyunca rakiplere 15 hasar veren dev bir kasırga oluşturur, ayrıca 3 adet küçük kasırga fırlatır. Kendisini rüzgardan bir kalkanla korur (gelen hasarı %25 azaltır).",
   kind="zone", dmg=15, zw=PX * 9, life=35.0, color=(200, 235, 255),
   extra_proj=3, proj_dmg=10, buff=["shield"], buff_time=35.0, buff_power=0.25,
   is_ult=True)),
)

# ------------------------------------------------------- 13. STEVE
_add(
 ("st_yumruk", S("Minecraft Yumruğu", 2.0, "Yumruk atar.",
   dmg=6, range=48, ytop=60, h=18, pose="punch")),
 ("st_tnt", S("TNT ve Mızrak", 15.0, "TNT koyup ateşler ve 5 piksel ileri mızrak atar. TNT patladığında 10 piksellik alana 15 hasar verir.",
   kind="proj", dmg=10, count=1, speed=560, life=0.9, size=10,
   color=(200, 200, 210), burst_zone=PX * 5, burst_dmg=15, burst_life=1.0,
   spark=True)),
 ("st_olta", S("Olta ve Mızrak", 15.7, "Oltayla oyuncuyu kendine çeker (5 hasar), ardından mızrakla geri iter (15 hasar).",
   kind="pull", dmg=5, push_dmg=15, range=400, is_ult=True)),
 ("st_ult", S("Eşya Seviyesi", 20.0, "Tahta eşyalarla başlar ancak ulti her açıldığında eşyaları bir üst seviyeye geçer (Taş ➔ Demir ➔ Altın ➔ Elmas ➔ Netherite). Her seviye atladığında hasarı 2.5 artar.",
   kind="buff", buff=["tier"], buff_time=0.0, buff_power=2.5, is_ult=True)),
)

# ------------------------------------------------------- 14. ALEX
_add(
 ("al_vuru", S("Vuruş / Zıpkın", 1.0, "Normal vurur. Tuşa basılı tutulursa zıpkın fırlatır (15 hasar verir).",
   kind="charge_melee", dmg=6, charge_dmg=15, charge_time=0.55,
   range=50, ytop=60, h=18, pose="punch")),
 ("al_pearl", S("Ender Pearl", 5.0, "Ender Pearl atar ve 10 piksel öteye ışınlanır.",
   kind="proj", dmg=5, count=1, speed=480, life=1.2, size=10,
   color=(70, 200, 160), blink=PX * 10, blink_to_target=True)),
 ("al_yay", S("Yay ve Ok", 30.0, "Yay ve okla 5 hasar verir. Tuşa basılı tutma süresine göre silah değişir: kısa ➔ 3'lü arbalet, uzun ➔ yanan ve patlayan havai fişek okları, en uzun ➔ 45 hasar veren zıpkın.",
   kind="charge_proj", dmg=5, charge_time=1.1,
   tiers=(("3'lu Arbalet", 3, 8.0), ("Havai Fishek Oklari", 3, 14.0),
          ("Zipkin", 1, 45.0)), is_ult=True)),
 ("al_ult", S("Eşya Seviyesi", 20.0, "13. karakter ile aynı (seviye atlayan eşya sistemi).",
   kind="buff", buff=["tier"], buff_time=0.0, buff_power=2.5, is_ult=True)),
)

# ------------------------------------------------------- 15. GÜÇLENDİRİLMİŞ ZOMBİ
_add(
 ("gz_yumruk", S("Güçlü Yumruk", 1.5, "Yumruk atar.",
   dmg=8, range=52, ytop=60, h=18, pose="punch")),
 ("gz_isirik", S("Zombi I", 6.5, "5 piksel yakınındaki düşmanı ısırır ve 'Zombi I' efekti verir. Bu efekt 6.5 saniye boyunca oyuncunun kontrolünü yapay zekaya bırakır.",
   dmg=7, range=PX * 5, ytop=64, h=26, pose="punch", status=ST("ai", 6.5))),
 ("gz_enerji", S("Enerji Topu", 19.5, "Göğsünden bir enerji topu fırlatır ve 25 hasar verir.",
   kind="proj", dmg=25, count=1, speed=360, life=2.2, size=18,
   color=(90, 240, 90), glow=True)),
 ("gz_ult", S("Yeşil Işın", 20.0, "35 piksellik alana 35 saniye boyunca yeşil enerji ışını saçar. Işına değen rakipler 25 hasar alır ve 15 saniye Zombi I efekti kazanır.",
   kind="beam", dmg=25, zw=PX * 17, beam_time=35.0, beam_tick=1.0,
   color=(90, 255, 110), status=ST("ai", 15.0), is_ult=True)),
)

# ------------------------------------------------------- 16. GÜÇLENDİRİLMİŞ İSKELET
_add(
 ("gi_yumruk", S("Kemik Yumruğu", 0.5, "Yumruk atar.",
   dmg=7, range=50, ytop=60, h=18, pose="punch")),
 ("gi_yay", S("Gerdirilebilir Yay", 10.9, "Yayı 3 aşamalı gerdirebilir. 1. Aşama: 1 saniye gerer, 5 piksel ileri, 2.5 hasar. 2. Aşama: 5 saniye gerer, 10 piksel ileri, 5 hasar. 3. Aşama: 10 saniye gerer, 20 piksel ileri, 10.5 hasar.",
   kind="charge_proj", dmg=2.5, charge_time=1.0,
   tiers=(("1. Asama", 1, 2.5), ("2. Asama", 1, 5.0), ("3. Asama", 1, 10.5)),
   tier_range=(5, 10, 20))),
 ("gi_tank", S("Tank Minyonları", 15.1, "5 adet 'Tank' iskelet minyon çağırır (her birinin canı 200, vuruşu 2.5).",
   kind="summon", count=5, unit="iskelet_tank", is_ult=True)),
 ("gi_ult", S("Kılıç Modu", 20.0, "Göğüslüğünden 5 saniye boyunca 15 piksel ileri giden bir enerji ışını çıkar (15 hasar). Sonrasında o enerjiyi kılıç formuna dönüştürür; 10 saniye süren bu modda her vuruşu 25 hasar verir.",
   kind="beam", dmg=15, zw=PX * 7, beam_time=5.0, beam_tick=0.6,
   beam_len=PX * 7, color=(230, 240, 255), buff=["sword"], buff_time=10.0,
   buff_power=25.0, is_ult=True)),
)

# ------------------------------------------------------- 17. MUTANT 2.0
_add(
 ("m2_vuru", S("Normal Vuruş / Tut-Sallat", 2.5, "Normal vurur (15 hasar + pasifle beraber toplam 20). Eğer tuşa uzun basarsa oyuncuyu tutar, yerden yere 3 kez vurur (25 hasar + 5 pasif hasarı).",
   kind="charge_melee", dmg=15, charge_dmg=25, charge_time=0.8,
   range=56, ytop=62, h=22, pose="punch", grab_hits=3)),
 ("m2_kalkan", S("Mutant Zırhı", 35.0, "Sadece canı azaldığında etkinleşir; 10 saniye boyunca aldığı hasarı yarıya düşürür ve kalkanına +50 ekler.",
   kind="buff", buff=["shield", "reflect"], buff_time=10.0,
   buff_power=0.5, buff_shield=50.0, need_hp_pct=0.7)),
 ("m2_eze", S("Ezici Alan", 40.5, "5 piksellik alanı ezer. Altında oyuncu varsa 20 hasar alır ve 15 saniye sersemletme efekti yer.",
   kind="zone", dmg=20, zw=PX * 2.5, life=0.7, color=(150, 60, 90),
   status=ST("stun", 15.0), is_ult=True)),
 ("m2_ult", S("Dev Mutant", 20.0, "Boyutu ve hasarı 2 katına çıkar ancak hızı ve kalkanı yarıya düşer.",
   kind="buff", buff=["giant", "dmg", "speed", "shield_half"],
   buff_time=8.0, buff_power=2.0, is_ult=True)),
)

# ------------------------------------------------------- 18. GELİŞTİRİLMİŞ VAMPİR
_add(
 ("gv_kilic", S("Kan Bıçağı", 0.5, "Bıçak çıkarıp saldırır, 10 hasar verir ve kendisine 10 can yeniler.",
   dmg=10, heal=10, range=54, ytop=60, h=18, pose="punch", fx="knife")),
 ("gv_gorunmez", S("Görünmezlik", 5.0, "10 saniyeliğine görünmez olur, süre bitince görünürlüğe geri döner.",
   kind="buff", buff=["invisible"], buff_time=10.0)),
 ("gv_yarasa", S("Yarasa Fırlat", 12.5, "3 yarasa fırlatır. Yarasalar 2 kere saldırır, her vuruş 1.5 hasar verir ve hızı azaltır.",
   kind="proj", dmg=1.5, hits=2, count=3, speed=430, life=1.5, size=9,
   color=(90, 20, 40), status=ST("slow", 3.0, 0.0, 0.5), spread=0.16, fly=True)),
 ("gv_ult", S("Kan Sırmanı", 15.0, "15 yarasa fırlatır. Değdiği yer 3 can çalar, 6 hasar verir ve hızı 3.5 kattır.",
   kind="proj", dmg=6, hits=1, count=15, speed=540, life=1.9, size=12,
   color=(150, 10, 40), lifesteal=3.0, buff=["speed"], buff_time=6.0,
   buff_power=3.5, spread=0.42, fly=True, is_ult=True)),
)

# ------------------------------------------------------- 19. HIRSIZ
_add(
 ("hz_yumruk", S("Kemer Vuruşu", 1.5, "Yumruk atar.",
   dmg=7, range=50, ytop=60, h=18, pose="punch")),
 ("hz_uzuv", S("Uzuv Çalma", 7.5, "Eğer 2 uzvu koptuysa ve 2.5 piksel yakınında bir düşman varsa, düşmanın uzvunu çalar ve kendisine takar.",
   kind="grab", dmg=6, range=PX * 2.5)),
 ("hz_yansit", S("Yansıtma", 15.7, "Kullanıldıktan sonra 10 saniye içinde hasar alırsa, hasarın yarısını düşmana yansıtır.",
   kind="buff", buff=["reflect"], buff_time=10.0, buff_power=0.5)),
 ("hz_kopya", S("Yetenek Kopyalama", 5.5, "Hasar aldığı düşmanın özelliğini kopyalıp kullanır, ancak verdiği hasarı yarıya düşürür (rakip 10 vuruyorsa hırsız 5 vurur).",
   kind="steal_ability", is_ult=True)),
)

# ------------------------------------------------------- 20. ŞÖVALYE
_add(
 ("sv_kilic", S("Kılıç Darbesi", 1.9, "Kılıç darbesi atar; 10 hasar vurur ve kanama efekti verir (kanama 5 saniyede toplam 2.5 hasar vurur).",
   dmg=10, range=62, ytop=64, h=22, pose="punch", fx="sword",
   status=ST("bleed", 5.0, 0.5))),
 ("sv_at", S("Ata Bin", 5.1, "Ata biner; hasar alana kadar attan inmez ve hızı artar.",
   kind="buff", buff=["horse", "speed"], buff_time=8.0, buff_power=1.6,
   flag="horse")),
 ("sv_iki_kilic", S("Çift Kılıç", 5.5, "2 kılıç hasarı verir ve 10 saniye sürecek kanama efekti uygular.",
   dmg=16, range=70, ytop=64, h=26, pose="combo", fx="sword",
   status=ST("bleed", 10.0, 0.6), is_ult=True)),
 ("sv_ult", S("Şövalye Yükselişi", 20.0, "Hasarı, canı ve kalkanı 2 katına çıkar ancak hızı 4 kat azalır.",
   kind="buff", buff=["dmg", "shield", "speed"], buff_time=8.0,
   buff_power=2.0, is_ult=True)),
)

# ------------------------------------------------------- 21. OKÇU
_add(
 ("ok_ok", S("Şarj Edilebilir Ok", 5.0, "Normal ok atar. 3 saniye basılı tutulursa Seviye 2'ye geçer. Her şarj seviyesi atış süresine 5 saniye ekler. Şarjın sınırı yoktur.",
   kind="charge_proj", dmg=2.5, base_cd=2.5, charge_time=3.0, charge_step=5.0,
   range=5, speed=620, size=8, color=(200, 170, 90), unlimited_charge=True)),
 ("ok_hiz", S("Sprint", 7.5, "4.5 - 5 saniyeliğine hız ve bekleme süresi statlarını 2 kat artırır.",
   kind="buff", buff=["speed", "haste"], buff_time=4.5, buff_power=2.0,
   cd_mult=0.5)),
 ("ok_bes_ok", S("Beşli Ok", 15.5, "1. özellik ile aynı mekaniklere sahiptir ancak tek bir ok yerine 5 ok atar.",
   kind="charge_proj", dmg=2.5, base_cd=2.5, charge_time=3.0, charge_step=5.0,
   range=5, speed=640, size=8, color=(215, 185, 100), count=5, spread=0.10,
   unlimited_charge=True, is_ult=True)),
 ("ok_ult", S("2. Form - Keskin Nişancı", 20.0, "Karakter 2. formuna geçer ve 'keskin nişancı tüfeği' kuşanır. Rakip ne kadar uzaktaysa hasarı o kadar artar (her mesafe birimi hasarı 2 kat artırır). 2. formdayken 1. ve 3. özellikleri şarjlanırsa 1 yerine 2 mermi atar ama mermi hasarları yarı yarıya bölünür.",
   kind="buff", buff=["form2"], buff_time=0.0, is_ult=True)),
)

# ------------------------------------------------------- 22. ÇELİK ADAM
_add(
 ("ca_lazer", S("Kırmızı Lazer", 10.5, "1. formunda 15 piksel uzağa giden ve 25 hasar veren kırmızı lazer atar. 2. formunda ise beyaz lazer atar ve sayılan değerlerin yarısı kadar etkili olur.",
   kind="beam", dmg=25, zw=PX * 7.5, beam_len=PX * 7.5, beam_time=0.5,
   beam_tick=0.25, color=(255, 70, 70), color2=(255, 255, 255))),
 ("ca_fuze", S("Takip Eden Füzeler", 6.9, "Düşmanı takip eden füze ateşler; patladığında 15 piksellik alana 25 hasar verir. Toplamda sadece 12 adet füze vardır. 2. formunda sol elindeki tabancayla 25 piksele kadar giden 3 el ateş eder (15 hasar).",
   kind="proj", dmg=25, count=3, ammo=12, speed=340, life=3.0, size=10,
   color=(255, 120, 60), homing=5.0, burst_zone=PX * 7.5, burst_dmg=25)),
 ("ca_uc_lazer", S("Üçlü Lazer", 10.3, "3 farklı yerinden piksel sınırı olmayan lazer fırlatır (her bir lazer 15.5 hasar verir).",
   kind="beam", dmg=15.5, beams=3, beam_time=0.7, beam_tick=0.3,
   no_limit=True, color=(255, 90, 90))),
 ("ca_ult", S("Uçuş Modu", 20.0, "Eğer zırhındaki füzeler bittiyse yenilenir, lazer statları 2 katına çıkar ve karakter uçabilir hale gelir. 2. formunda ulti açarsa; sadece 1. formundaki zırhı geri gelir ve dirilme pasifi tekrar aktifleşir.",
   kind="buff", buff=["fly", "dmg"], buff_time=10.0, buff_power=2.0,
   refill_ammo=True, is_ult=True)),
)

# ------------------------------------------------------- 23. PARAZİT
_add(
 ("pa_yumruk", S("Sıvı Yumruğu", 2.5, "Yumruk atar (5.5 hasar). Sıvı formundayken 5 piksel ileri uzanan parçasıyla vurur ancak hasarın yarısını verir.",
   dmg=5.5, range=52, ytop=60, h=18, pose="punch", liquid_range=PX * 2.5)),
 ("pa_ayril", S("Sıvı Formuna Gir", 15.0, "1. formundayken oyuncu bedeninden ayrılır ve sıvı formuna girer (bedeni ölmediği sürece geri içine girerek 1. forma dönebilir).",
   kind="buff", buff=["liquid", "phase"], buff_time=6.0)),
 ("pa_venom", S("VENOM YÜZÜ", 15.6, "Oyuncuyu tutar, rakibin ekranını Venom yüzü kaplar ve 'WE ARE PARAZITE' yazar. 5 saniye sonra düşman 35 hasar alır.",
   kind="grab", dmg=35, grab_time=5.0, face=True, is_ult=True)),
 ("pa_ult", S("Simbiyot", 22.0, "1. formunda kendi bedeninden ayrılıp rakibin bedenine girer. Ondan bir özellik ve bir aksesuar çalıp asıl bedenine kopyalar (çalınan özellik/statlar yarı gücündedir). 2. formunda açılırsa, içinde bulunduğu bedenin can, hız ve hasar statlarını 3.5 kat artırır ve o beden ölene kadar ona bağlı kalır.",
   kind="buff", buff=["possess"], buff_time=0.0, buff_power=3.5, is_ult=True)),
)

# ------------------------------------------------------- 24. SPIRIT
_add(
 ("sp_ele_gecir", S("Ele Geçir", 10.0, "Bir canlıyı veya aracı ele geçirip kontrol eder. Ele geçirdiği şey ölene kadar içinde kalır.",
   kind="buff", buff=["possess"], buff_time=10.0, buff_power=1.0)),
 ("sp_duvar", S("Duvardan Geç", 10.0, "10 saniye boyunca duvarların içinden geçebilir.",
   kind="buff", buff=["phase"], buff_time=10.0)),
 ("sp_ucus", S("Uçuş", 10.0, "10 saniye uçmasını sağlar.",
   kind="buff", buff=["fly"], buff_time=10.0)),
 ("sp_ult", S("Kendi Bedenine Dön", 15.0, "2. formundan çıkarak 1. formuna (asıl bedenine) geri döner.",
   kind="buff", buff=["unpossess"], buff_time=0.0, is_ult=True)),
)

# ------------------------------------------------------- 25. THE MACHINE
_add(
 ("mc_sok", S("Şok Dalgası", 9.5, "Yere ayağını sertçe vurup şok dalgası yaratır. Rakip zıplamazsa 15 hasar yer ve sersemletilir.",
   kind="zone", dmg=15, zw=PX * 6, life=0.7, dodge="zıpla",
   color=(140, 160, 190), status=ST("stun", 1.5), shake=18)),
 ("mc_minigun", S("Minigun", 25.9, "Sol elindeki minigun'ı kullanarak 150 mermi ateşler (mermi başı 1.5 hasar). Rakipler eğilerek veya zıplayarak bunlardan kaçınabilir.",
   kind="burst", dmg=1.5, ammo=150, rate=0.035, speed=760, life=1.1, size=5,
   color=(255, 220, 90), spread=0.07)),
 ("mc_lazer", S("Dev Lazer", 45.3, "Sırtından dev lazer silahı çıkarır. Ateşlediğinde 45 piksellik alana 45.3 hasar verir. Bu silahın maç boyu 3 kez kullanım hakkı vardır.",
   kind="beam", dmg=45.3, zw=PX * 22, beam_time=0.9, beam_tick=0.45,
   color=(255, 60, 200), limited=3)),
 ("mc_ult", S("ARABA MODU", 22.0, "1. formdayken (robot içindeyken) ulti açılırsa robot arabaya dönüşür. Araba formunda tepede minigun (300 mermi), önde ise lazer (6 kullanım) bulunur.",
   kind="buff", buff=["vehicle"], buff_time=0.0, is_ult=True)),
)

# ------------------------------------------------------- 26. CAMERAMAN
_add(
 ("cm_sev1_ates", S("Ateş", 5.6, "Ateş eder (15 hasar).",
   kind="proj", dmg=15, count=1, speed=620, life=1.0, size=7,
   color=(255, 240, 120), spark=True)),
 ("cm_sev2_jet", S("Jetpack", 5.0, "Jetpack ile 10 saniye uçar.",
   kind="buff", buff=["fly"], buff_time=10.0)),
 ("cm_sev2_raf", S("Tuvalet Şofonu", 6.0, "Tuvalet şifonu bulursa eline alıp 5 saniye yakın dövüşte kullanır, sonunda fırlatarak 10 piksel öteye 5 hasar verir.",
   kind="proj", dmg=5, count=1, speed=520, life=1.2, size=14,
   color=(230, 230, 240), spin=True, pickup=True)),
 ("cm_sev3_yumruk", S("Titan Yumruğu", 5.5, "Yumruk atar.",
   dmg=9, range=64, ytop=70, h=26, pose="punch")),
 ("cm_sev3_kalkan", S("Dokunulmazlık", 15.5, "10 saniye boyunca hasar almayan kalkan açar.",
   kind="buff", buff=["immune"], buff_time=10.0)),
 ("cm_sev3_firlat", S("Titan Fırlatma", 30.0, "Oyuncuyu tutup haritanın diğer ucuna fırlatır (45 hasar).",
   kind="throw", dmg=45, is_ult=True)),
 ("cm_sev4_lazer", S("Kalkan Lazer", 10.5, "Lazer fırlatır (sınırsız piksel menzili, 15 hasar).",
   kind="beam", dmg=15, no_limit=True, beam_time=0.8, beam_tick=0.4,
   color=(255, 120, 255))),
 ("cm_sev4_miknats", S("Mıknatıs Kolu", 15.5, "Mıknatıs koluyla demir toplayıp düşmana fırlatır (55 hasar).",
   kind="proj", dmg=55, count=3, speed=560, life=1.3, size=12,
   color=(170, 170, 180), homing=7.0)),
 ("cm_sev4_kalkan2", S("30 sn Dokunulmazlık", 30.0, "30 saniye boyunca hasar almayan kalkan açar.",
   kind="buff", buff=["immune"], buff_time=30.0, is_ult=True)),
 ("cm_sev5_testere", S("Testere", 12.0, "Testereyi yere fırlatır ve testere 15 saniye boyunca düşman kovalar.",
   kind="zone", dmg=3, zw=PX * 2, life=15.0, color=(200, 200, 210),
   seeker=True, follow=False)),
 ("cm_sev6_asit", S("Asit Alanı", 14.0, "Yere asit bırakır; asit 30 saniye durur, içine girene 15 hasar verir.",
   kind="zone", dmg=15, zw=PX * 3, life=30.0, color=(150, 230, 60),
   repeat=1.0)),
)

# ------------------------------------------------------- 27. SPEAKERMAN
_add(
 ("spm_sev3_blaster", S("Blaster", 10.0, "Blaster ateşler (Sıra: Sol kol ➔ Sağ kol ➔ Her ikisi). Blaster'ın menzili sınırsızdır ve vuruş başı 15 hasar verir.",
   kind="beam", dmg=15, no_limit=True, beam_time=0.9, beam_tick=0.45,
   color=(255, 200, 60), alternates=3)),
 ("spm_sev1_dalga", S("Ağır Ses Dalgası", 15.0, "Zıplamazsanız 10 hasar yersiniz.",
   kind="zone", dmg=10, zw=PX * 9, life=0.8, dodge="zıpla",
   color=(255, 220, 140), shake=10)),
 ("spm_sev2_yumruk", S("Yumruk", 1.6, "Yumruk atar. Her 2. kullanımında (çift sayılarda) fazladan, ancak zıplayarak kaçılabilecek 5 hasarlık bir ses dalgası yollar.",
   dmg=8, range=54, ytop=62, h=20, pose="punch", every=2,
   extra_zone=PX * 4, extra_dmg=5, extra_dodge="zıpla",
   extra_color=(255, 220, 140))),
 ("spm_sev2_tekme", S("Tekme", 5.5, "Tekme atar (1. özellikle aynı mantıkla çalışır ancak dalgası 10 vurur).",
   dmg=12, range=66, ytop=26, h=28, pose="kick", every=2,
   extra_zone=PX * 5, extra_dmg=10, extra_dodge="zıpla",
   extra_color=(255, 220, 140))),
 ("spm_sev2_dalga3", S("Üçlü Ses Dalgası", 30.0, "3 adet ses dalgası gönderir (2'si zıplayarak, 1'i eğilerek kaçılır, her biri 15 vurur).",
   kind="zone", dmg=15, zw=PX * 7, life=0.9, dodge="zıpla", count=3,
   color=(255, 220, 140), shake=12, is_ult=True)),
 ("spm_sev3_dalga10", S("10 Ses Dalgası", 30.0, "10 adet ses dalgası atar (5 tanesi eğilerek, 5 tanesi zıplayarak atlatılır, hepsi 15 vurur).",
   kind="zone", dmg=15, zw=PX * 8, life=1.0, count=10,
   half_dodge="eğil", color=(255, 230, 160), shake=16)),
 ("spm_sev3_hepsi", S("FIRLATMA", 60.0, "1 ve 2 numaralı özelliklerin birleşimini atar.",
   kind="zone", dmg=15, zw=PX * 9, life=1.1, count=6,
   half_dodge="eğil", color=(255, 240, 180), beams=4, beam_dmg=15,
   shake=20, is_ult=True)),
)

# ------------------------------------------------------- 28. TV MAN
_add(
 ("tv_sev1_yumruk", S("Yumruk", 0.9, "Yumruk atar.",
   dmg=8, range=52, ytop=62, h=20, pose="punch")),
 ("tv_sev1_beyaz", S("Beyaz Işın", 10.6, "15 piksel ileriye kadar yayılan beyaz bir ışın atar ve düşmanı 10 saniye boyunca sersemletir.",
   kind="beam", dmg=8, beam_len=PX * 7.5, beam_time=0.6, beam_tick=0.3,
   color=(255, 255, 255), status=ST("stun", 10.0))),
 ("tv_sev1_mor", S("Mor Işık", 10.8, "15 piksel ileriye mor bir ışık atar. Bu ışığa maruz kalan NPC düşmanlardan birini 15 saniyeliğine kontrol eder. Ayrıca diğer düşmanlara 15 hasar vurur ve onları 15 saniye sersemletir.",
   kind="beam", dmg=15, beam_len=PX * 7.5, beam_time=0.7, beam_tick=0.35,
   color=(190, 90, 255), status=ST("stun", 15.0), mind_control=True)),
 ("tv_sev2_yumruk", S("Yumruk", 6.9, "Yumruk atar.",
   dmg=12, range=58, ytop=66, h=22, pose="punch")),
 ("tv_sev2_beyaz", S("Beyaz Işın x2", 15.1, "1. seviyedeki 2. özellikle (beyaz ışın) aynıdır ancak tüm statları 2 kat artar.",
   kind="beam", dmg=16, beam_len=PX * 15, beam_time=0.8, beam_tick=0.4,
   color=(255, 255, 255), status=ST("stun", 20.0))),
 ("tv_sev2_10_isin", S("10 Işın", 25.5, "10 saniye boyunca (5 saniyesi beyaz, 5 saniyesi mor olmak üzere) toplam 10 ışın atar. Bu ışınlar 30 piksel ileri gider ve hasar gibi statları 1. seviyeye kıyasla 2.5 kat fazladır.",
   kind="beam", dmg=20, beams=10, beam_len=PX * 15, beam_time=10.0,
   beam_tick=1.0, color=(255, 255, 255), color2=(190, 90, 255),
   status=ST("stun", 15.0), is_ult=True)),
 ("tv_sev3_kirmizi", S("KIRMIZI ISIN", 45.9, "45 piksellik alana kırmızı ışın atar. Bu ışın 45 saniye boyunca sersemletme verir ve düşmana her 5 saniyede bir 15 hasar uygular.",
   kind="beam", dmg=15, zw=PX * 22, beam_time=45.0, beam_tick=5.0,
   color=(255, 60, 60), status=ST("stun", 45.0))),
 ("tv_sev3_kanca", S("Kanca Kombosu", 15.0, "15 piksellik alana kanca atar. 3 düşmanı veya oyuncuyu yanına çeker, yere çarpıp ezer. Bu kombo toplam 35 hasar verir.",
   kind="pull", dmg=35, range=PX * 15, pull_count=3, is_ult=True)),
)

# ------------------------------------------------------- 29. SUIKASTÇİ
_add(
 ("su_bicak", S("Çift Bıçak", 25.9, "5 piksel yakınındaki oyuncunun kafasına standart bıçağı, kalbine ise kelebek bıçağı saplar ve tek seferde 55 hasar verir.",
   dmg=55, range=PX * 2.5, ytop=70, h=34, pose="punch", fx="knife", is_ult=True)),
 ("su_atis", S("10 El Ateş", 15.0, "Piksel sınırı olmayan 10 el ateş eder. Mermilerden 5 tanesinden zıplayarak, 5 tanesinden ise eğilerek kaçınılabilir. Her bir mermi 2.5 hasar verir.",
   kind="burst", dmg=2.5, ammo=10, rate=0.14, speed=820, life=1.2, size=5,
   color=(255, 230, 140), spread=0.03, half_dodge="eğil")),
 ("su_canta", S("YENİ ÇANTA", 60.0, "Gökten yeni bir çanta düşer. Karakter belindeki silahı, bıçağı ve kelebeği bu çantaya koyar. Karşılığında çantadan bir AKM tüfek ve 3 adet el bombası çıkarıp kuşanır.",
   kind="buff", buff=["akm"], buff_time=0.0, limited=True)),
 ("su_ult", S("AKM MODU", 20.0, "3. özellik kullanılıp yeni silahlar kuşanılarak ulti formuna geçildiğinde karakterin bekleme süreleri 2 katına çıkar ve yetenekleri değişir.",
   kind="buff", buff=["akm", "cd2"], buff_time=0.0, cd_mult=2.0, is_ult=True)),
)

# ------------------------------------------------------- 30. HAZİNE BAĞIMLISI
_add(
 ("ha_yumruk", S("Yumruk", 1.5, "Yumruk atar.",
   dmg=8, range=52, ytop=62, h=20, pose="punch")),
 ("ha_cek", S("Çek", 7.5, "Rakip oyuncuyu kendi yakınına çeker.",
   kind="pull", dmg=4, range=500)),
 ("ha_sandik", S("Hazine Sandığı", 15.0, "Rastgele bir düşmanı veya oyuncuyu çekip sırtındaki sandığın içine atar. Hedef 5 saniye boyunca sandığın içinde kalır ve sandıkta kaldığı her saniye başına 15 hasar alır (toplam 75 hasar). Süre bitiminde hedef dışarı atılır.",
   kind="grab", dmg=75, range=400, grab_time=5.0, chest=True, is_ult=True)),
 ("ha_ult", S("Hazine Patlaması", 20.0, "Karakterin tüm statları (hasar, hız vb.) tam 5 katına çıkar.",
   kind="buff", buff=["all5"], buff_time=10.0, buff_power=5.0, is_ult=True)),
)


CLASSES = [
    {"id": "vampir", "no": 2, "name": "VAMPİR", "hp": 100, "shield": 0, "speed": 285.0,
     "color": (170, 25, 45), "accessory": "Vampir pelerini", "pack": "cansiz",
     "story": "Gece yarısı avlanmak için kendi kanını içmeyi seçti; gün doğumunu hiç görmediği için artık karanlıktan korkmuyor.",
     "passive": {"name": "-", "text": "Özel pasifi yok; kanla güçlenen bir savaşçı."},
     "abilities": ["v_kilic", "v_gorunmez", "v_yarasa"], "ult": "v_ult"},

    {"id": "zombi", "no": 3, "name": "ZOMBİ", "hp": 120, "shield": 0, "speed": 220.0,
     "color": (110, 150, 90), "accessory": "Zombi kafası", "pack": "cansiz",
     "story": "Toprak altında bir yıl bekledi; çıkarken kalbi atmıyordu ama öfkesi her zamankinden fazlaydı.",
     "passive": {"name": "Zehir", "text": "Vuruşları 3 saniye zehir verir."},
     "abilities": ["z_yumruk", "z_isirik", "z_diril"], "ult": "z_diril"},

    {"id": "iskelet", "no": 4, "name": "İSKELET", "hp": 90, "shield": 0, "speed": 300.0,
     "color": (225, 225, 210), "accessory": "İskelet göğüslüğü", "pack": "cansiz",
     "story": "Bir kazıda kalan son kemiğiydi; kırık bir parçasını bile kendi toplayıp mermiye dönüştürdü.",
     "passive": {"name": "Kemik Kıtası", "text": "Kendi kemiğinden mermi üretir."},
     "abilities": ["i_yumruk", "i_parca", "i_kanca"], "ult": "i_ult"},

    {"id": "mutant", "no": 5, "name": "MUTANT", "hp": 200, "shield": 0, "speed": 200.0,
     "color": (140, 90, 160), "accessory": "Büyük kol", "pack": "cansiz",
     "story": "Laboratuvarda kaldığı son şey kendi iradesiydi; kapıyı sökerek dışarı çıktığında artık bir insan değildi.",
     "passive": {"name": "200 Can", "text": "Çok yavaş ama çok dayanıklı."},
     "abilities": ["mu_yumruk", "mu_tok", "mu_firlat"], "ult": "mu_ult"},

    {"id": "zehri_krali", "no": 6, "name": "ZEHRİ KRALI", "hp": 110, "shield": 20, "speed": 265.0,
     "color": (110, 190, 70), "accessory": "Kral tacı", "pack": "element",
     "story": "Zehirini bir kralın kadehinden öğrendi; tahtını zehirle kazandı.",
     "passive": {"name": "Zehir Yansıması", "text": "Hasar aldığında saldıran rakibi 1 saniye zehirler."},
     "abilities": ["zk_yumruk", "zk_dalga", "zk_top"], "ult": "zk_ult"},

    {"id": "ates_man", "no": 7, "name": "ATEŞ MANYAĞI", "hp": 115, "shield": 0, "speed": 270.0,
     "color": (225, 105, 35), "accessory": "Sırtında petrol varili", "pack": "element",
     "story": "Yangın söndürmeye gitti, ilk kıvılcımı o yaktı; artık alev onun dilinden konuşuyor.",
     "passive": {"name": "Yakıcı Karşı Harekets", "text": "Hasar aldığında saldıran düşmanı 3 saniye yakar."},
     "abilities": ["am_yumruk", "am_alani", "am_petrol"], "ult": "am_ult"},

    {"id": "madenci", "no": 8, "name": "MADENCİ", "hp": 130, "shield": 10, "speed": 255.0,
     "color": (175, 155, 95), "accessory": "Sırtında kazma, elinde meşale ve kalkan",
     "pack": "element",
     "story": "Yeraltının altında çalışırken kafasına bir elmas düştü; o gün artık kazdığı şeyin kendisi olmadığını anladı.",
     "passive": {"name": "Elmas Bloğu", "text": "Hasar yediğinde saldıranın kafası elmas olur ve 5 sn sonra patlar."},
     "abilities": ["md_kazma", "md_meshale", "md_kalkan"], "ult": "md_ult"},

    {"id": "su_krali", "no": 9, "name": "SU KRALI", "hp": 120, "shield": 0, "speed": 260.0,
     "color": (55, 130, 245), "accessory": "Kafasında cam fanus", "pack": "element",
     "story": "Denizden bir taht yükseldi; içindeki adam tahtı değil, suyu yönetmeyi seçti.",
     "passive": {"name": "Su Dirilişi", "text": "Öldüğünde 50 can ve 50 kalkanla dirilir ama hasarı yarıya iner."},
     "abilities": ["sk_top", "sk_duvar", "sk_hepsi"], "ult": "sk_tsunami"},

    {"id": "yildirim_patronu", "no": 10, "name": "YILDIRIM PATRONU", "hp": 115, "shield": 0,
     "speed": 260.0, "color": (110, 190, 255), "accessory": "Sırtında tesla bobini",
     "pack": "element",
     "story": "Bir kulede yıllarca yalnız kaldı; öfkesi o kadar büyüdü ki gökyüzü bile ona kaçtı.",
     "passive": {"name": "Statik", "text": "Hasar aldığında saldıran çarpılır ve 0.5 sn durur."},
     "abilities": ["yp_yumruk", "yp_alan", "yp_zemin"], "ult": "yp_ult"},

    {"id": "element_krali", "no": 11, "name": "ELEMENT KRALI", "hp": 140, "shield": 25, "speed": 250.0,
     "color": (135, 100, 60), "accessory": "Çamur kaplı kafa", "pack": "element",
     "story": "Toprağı, alevi, suyu ve havayı bir arada tutan tek taht sahibiydi.",
     "passive": {"name": "25 Kalkan", "text": "Kalkanla başlar."},
     "abilities": ["ek_toprak", "ek_duvar", "ek_minyon"], "ult": "ek_ult"},

    {"id": "hava_patronu", "no": 12, "name": "HAVA PATRONU", "hp": 115, "shield": 15, "speed": 290.0,
     "color": (200, 240, 255), "accessory": "Arkasında kanatlar", "pack": "element",
     "story": "Rüzgârın tahtına oturdu; yere inen her şeyi yukarı kaldırır.",
     "passive": {"name": "Uçuş", "text": "Zıplama tuşuna art arda basılırsa uçar."},
     "abilities": ["hp_yumruk", "hp_dalga", "hp_ufleme"], "ult": "hp_kasirga"},

    {"id": "steve", "no": 13, "name": "STEVE", "hp": 100, "shield": 0, "speed": 265.0,
     "color": (85, 140, 200), "accessory": "Kare bir vücut", "pack": "fan",
     "story": "Kare bir yüzle dünyaya geldi; elytrayı 500 kez kullandıktan sonra bile gülümsemeye devam etti.",
     "passive": {"name": "Havai Fişek + Elytra", "text": "Zıplama spamıyla uçar; her saniye ultisi %25 dolar."},
     "abilities": ["st_yumruk", "st_tnt", "st_olta"], "ult": "st_ult"},

    {"id": "alex", "no": 14, "name": "ALEX", "hp": 50, "shield": 25, "speed": 285.0,
     "color": (200, 160, 110), "accessory": "Kare Alex kafası", "pack": "fan",
     "story": "Ok atmayı seven, okuna güvenen ve kalkanını her savaşta ilk kullanan avcı.",
     "passive": {"name": "Dengesiz", "text": "50 can düşük başlar ama 25 kalkan eklenir."},
     "abilities": ["al_vuru", "al_pearl", "al_yay"], "ult": "al_ult"},

    {"id": "gzombi", "no": 15, "name": "GÜÇLENDİRİLMİŞ ZOMBİ", "hp": 140, "shield": 0, "speed": 225.0,
     "color": (85, 220, 105), "accessory": "Yeşil çekirdekli göğüs zırhı", "pack": "cansiz",
     "story": "Göğsündeki yeşil çekirdek onu ölümsüz sandı; kontrolü tamamen kaybettiğinde bile çekirdek yanıyordu.",
     "passive": {"name": "75 Can + 50 Kalkan", "text": "Öldüğünde 75 can ve 50 kalkanla yeniden dirilir."},
     "abilities": ["gz_yumruk", "gz_isirik", "gz_enerji"], "ult": "gz_ult"},

    {"id": "giskelet", "no": 16, "name": "GÜÇLENDİRİLMİŞ İSKELET", "hp": 100, "shield": 50,
     "speed": 300.0, "color": (240, 245, 255), "accessory": "Beyaz çekirdekli göğüslük 2.0",
     "pack": "cansiz",
     "story": "Göğsündeki beyaz çekirdek ona ikinci bir iskelet daha verdi.",
     "passive": {"name": "100 Can + 50 Kalkan", "text": "Dirildiğinde kalkanı ve göğüslüğü 2.0 kaybolur."},
     "abilities": ["gi_yumruk", "gi_yay", "gi_tank"], "ult": "gi_ult"},

    {"id": "mutant20", "no": 17, "name": "MUTANT 2.0", "hp": 100, "shield": 100, "speed": 240.0,
     "color": (200, 70, 110), "accessory": "Kaslı bir beden", "pack": "cansiz",
     "story": "Birincisi kaçmayı öğrenmemişti; ikincisi artık sadece vuruyor.",
     "passive": {"name": "Sersemletme", "text": "Her vuruşu 5 sn sersemletme + 5 hasar verir."},
     "abilities": ["m2_vuru", "m2_kalkan", "m2_eze"], "ult": "m2_ult"},

    {"id": "gvampir", "no": 18, "name": "GELİŞTİRİLMİŞ VAMPİR", "hp": 200, "shield": 50,
     "speed": 285.0, "color": (215, 20, 60), "accessory": "Vampir pelerini (kanlı)",
     "pack": "cansiz",
     "story": "Aynı hikâye, iki katı kan; ilk vampirin kendisine yaptığı şeyi yaptı.",
     "passive": {"name": "2 Kat Can + 50 Kalkan", "text": "Vampirle aynı yetenekler."},
     "abilities": ["gv_kilic", "gv_gorunmez", "gv_yarasa"], "ult": "gv_ult"},

    {"id": "sovalye", "no": 20, "name": "ŞÖVALYE", "hp": 100, "shield": 75, "speed": 245.0,
     "color": (185, 190, 205), "accessory": "Şövalye kaskı", "pack": "minestick",
     "story": "Kılıcını kuşanırken tek bir söz verdi: hiçbir dövüşte geri adım atmamak.",
     "passive": {"name": "Kalkan Zırhı", "text": "Aldığı hasarın %7.5'ini engeller."},
     "abilities": ["sv_kilic", "sv_at", "sv_iki_kilic"], "ult": "sv_ult"},

    {"id": "okcu", "no": 21, "name": "OKÇU", "hp": 95, "shield": 0, "speed": 275.0,
     "color": (120, 170, 110), "accessory": "Okçu çantası", "pack": "minestick",
     "story": "Oku ne kadar şarj edersen o kadar uzağa gider; bir saat basılı tutsa tek atışta haritayı yarıdan keserdi.",
     "passive": {"name": "Sınırsız Şarj", "text": "Tüm yetenekleri şarj edilebilir; her seviye +5 sn."},
     "abilities": ["ok_ok", "ok_hiz", "ok_bes_ok"], "ult": "ok_ult"},

    {"id": "celik_adam", "no": 22, "name": "ÇELİK ADAM", "hp": 130, "shield": 125, "speed": 260.0,
     "color": (200, 60, 60), "accessory": "Lazerli çelik zırh (1. form)", "pack": "orta_cag",
     "story": "Zırhı bir daha çıkarmadı; zırh gittiğinde kalan adam da gitti.",
     "passive": {"name": "Zırh Dirilişi", "text": "Öldüğünde dirilir ama zırhı kaybolur (2. forma düşer)."},
     "abilities": ["ca_lazer", "ca_fuze", "ca_uc_lazer"], "ult": "ca_ult"},

    {"id": "parazit", "no": 23, "name": "PARAZİT", "hp": 120, "shield": 0, "speed": 280.0,
     "color": (30, 30, 40), "accessory": "Simsiyah beden ve Venom maskesi", "pack": "orta_cag",
     "story": "Artık sıvı; düşmanının yüzünden bakıyor ve o yüzde konuşuyor.",
     "passive": {"name": "Sıvı Form", "text": "5 sn eğilirse sıvı formuna geçer."},
     "abilities": ["pa_yumruk", "pa_ayril", "pa_venom"], "ult": "pa_ult"},

    {"id": "hirsiz", "no": 19, "name": "HIRSIZ", "hp": 110, "shield": 0, "speed": 295.0,
     "color": (75, 75, 95), "accessory": "Hırsız maskesi", "pack": "darvel",
     "story": "Uzuvlarını kaybettikçe daha iyi hırsız oldu; sonunda düşmanının kendi yeteneğini çalmayı öğrendi.",
     "passive": {"name": "Uzuv Kopması", "text": "Her 5 hasarda bir kollarından/bacaklarından biri kopar."},
     "abilities": ["hz_yumruk", "hz_uzuv", "hz_yansit"], "ult": "hz_kopya"},

    {"id": "spirit", "no": 24, "name": "SPIRIT", "hp": 85, "shield": 0, "speed": 305.0,
     "color": (210, 235, 255), "accessory": "Saydam bir beden", "pack": "darvel",
     "story": "Ölümünden sonra bir beden bulamayınca 25 saniye kaldı; 24'üncü saniyede bir zombinin içine girdi.",
     "passive": {"name": "Saydam Form", "text": "Dirildiğinde 2. forma geçer; 25 sn içinde beden bulamazsa ölür."},
     "abilities": ["sp_ele_gecir", "sp_duvar", "sp_ucus"], "ult": "sp_ult"},

    {"id": "machine", "no": 25, "name": "THE MACHINE", "hp": 250, "shield": 50, "speed": 220.0,
     "color": (160, 175, 195), "accessory": "Üstüne bindiği robot", "pack": "darvel",
     "story": "İnsan bedeni 5 kat büyüdüğünde artık insan sayılmıyordu.",
     "passive": {"name": "Robot", "text": "250 can + 50 kalkan; robot patlarsa insana döner."},
     "abilities": ["mc_sok", "mc_minigun", "mc_lazer"], "ult": "mc_ult"},

    {"id": "suikasteci", "no": 29, "name": "SUIKASTÇİ", "hp": 75, "shield": 0, "speed": 300.0,
     "color": (55, 60, 70), "accessory": "Kapüşonlu mont ve kelebek bıçak", "pack": "darvel",
     "story": "Belindeki iki bıçağın biri gitti, diğeri hâlâ duruyordu.",
     "passive": {"name": "Kalkan Birikimi", "text": "Canı azalınca kalkan kazanır; ölünce 75 canla dirilir."},
     "abilities": ["su_bicak", "su_atis", "su_canta"], "ult": "su_ult"},

    {"id": "hazine", "no": 30, "name": "HAZİNE BAĞIMLISI", "hp": 110, "shield": 0, "speed": 265.0,
     "color": (190, 150, 70), "accessory": "Sırtında boş sandık", "pack": "darvel",
     "story": "Sandığı hiçbir zaman dolmadı; dolu sandığın peşinden koştuğu için hiçbir şeye yetişemedi.",
     "passive": {"name": "-", "text": "Hiçbir pasifi yok."},
     "abilities": ["ha_yumruk", "ha_cek", "ha_sandik"], "ult": "ha_ult"},

    {"id": "cameraman", "no": 26, "name": "CAMERAMAN", "hp": 100, "shield": 25, "speed": 265.0,
     "color": (120, 120, 140), "accessory": "Kameraman (6 seviye)", "pack": "skibidi",
     "story": "Kamerası her şeyi kaydetti; en son kaydettiği şey kendi yükselişiydi.",
     "passive": {"name": "6 Seviye", "text": "Ulti onu bir sonraki forma dönüştürür."},
     "abilities": ["st_yumruk", "st_tnt", "st_olta"], "ult": "cm_sev1_ates",
     "levels": [
         {"name": "SEVİYE 1 - İnsan", "hp": 100, "shield": 25, "scale": 1.0, "stat": 2.0,
          "abilities": ["st_yumruk", "st_tnt", "st_olta"], "ult": "cm_sev1_ates"},
         {"name": "SEVİYE 2 - Jetpackli", "hp": 120, "shield": 50, "scale": 1.5, "stat": 3.0,
          "abilities": ["cm_sev1_ates", "cm_sev2_jet", "cm_sev2_raf"], "ult": "cm_sev1_ates"},
         {"name": "SEVİYE 3 - Titan v1", "hp": 150, "shield": 75, "scale": 7.5, "stat": 4.0,
          "abilities": ["cm_sev3_yumruk", "cm_sev3_kalkan", "cm_sev3_firlat"],
          "ult": "cm_sev3_firlat"},
         {"name": "SEVİYE 4 - Titan v2", "hp": 180, "shield": 100, "scale": 7.5, "stat": 5.0,
          "abilities": ["cm_sev4_lazer", "cm_sev4_miknats", "cm_sev4_kalkan2"],
          "ult": "cm_sev4_kalkan2", "intro": True},
         {"name": "SEVİYE 5 - Testere Titan", "hp": 200, "shield": 100, "scale": 7.5, "stat": 6.0,
          "abilities": ["cm_sev4_lazer", "cm_sev5_testere", "cm_sev4_kalkan2"],
          "ult": "cm_sev4_kalkan2"},
         {"name": "SEVİYE 6 - Asit Titan", "hp": 240, "shield": 120, "scale": 7.5, "stat": 7.0,
          "abilities": ["cm_sev4_lazer", "cm_sev6_asit", "cm_sev4_kalkan2"], "ult": None},
     ]},

    {"id": "speakerman", "no": 27, "name": "SPEAKERMAN", "hp": 100, "shield": 25, "speed": 265.0,
     "color": (200, 190, 120), "accessory": "Kafada hoparlör (6 seviye)", "pack": "skibidi",
     "story": "Sesini duyuran herkes susmaya çalışır; o da susunca daha çok duyulduğunu fark etti.",
     "passive": {"name": "Ses Dalgası", "text": "Hasar alınca ses dalgası yayar; eğilerek kurtulunur."},
     "abilities": ["st_yumruk", "spm_sev1_dalga", "st_olta"], "ult": "spm_sev1_dalga",
     "levels": [
         {"name": "SEVİYE 1 - İnsan", "hp": 100, "shield": 25, "scale": 1.0, "stat": 4.5,
          "abilities": ["st_yumruk", "spm_sev2_yumruk", "spm_sev1_dalga"],
          "ult": "spm_sev1_dalga"},
         {"name": "SEVİYE 2", "hp": 130, "shield": 50, "scale": 1.5, "stat": 5.0,
          "abilities": ["spm_sev2_yumruk", "spm_sev2_tekme", "spm_sev2_dalga3"],
          "ult": "spm_sev2_dalga3"},
         {"name": "SEVİYE 3 - Titan", "hp": 180, "shield": 75, "scale": 7.5, "stat": 6.0,
          "abilities": ["spm_sev3_blaster", "spm_sev3_dalga10", "spm_sev3_hepsi"],
          "ult": "spm_sev3_hepsi"},
     ]},

    {"id": "tvman", "no": 28, "name": "TV MAN", "hp": 100, "shield": 25, "speed": 265.0,
     "color": (150, 130, 190), "accessory": "Kafada televizyon (3 seviye)", "pack": "skibidi",
     "story": "Ekranında gördüğü her şeyi yaptı; gördüğü ilk şey kendi yaklaşan dev haliydi.",
     "passive": {"name": "3 Seviye", "text": "Paket sistemiyle seviye atlar."},
     "abilities": ["tv_sev1_yumruk", "tv_sev1_beyaz", "tv_sev1_mor"], "ult": "tv_sev1_beyaz",
     "levels": [
         {"name": "SEVİYE 1", "hp": 100, "shield": 25, "scale": 1.0, "stat": 1.0,
          "abilities": ["tv_sev1_yumruk", "tv_sev1_beyaz", "tv_sev1_mor"], "ult": "tv_sev1_beyaz"},
         {"name": "SEVİYE 2", "hp": 130, "shield": 50, "scale": 2.5, "stat": 1.6,
          "abilities": ["tv_sev2_yumruk", "tv_sev2_beyaz", "tv_sev2_10_isin"],
          "ult": "tv_sev2_10_isin"},
         {"name": "SEVİYE 3 - Titan", "hp": 170, "shield": 75, "scale": 7.5, "stat": 2.2,
          "abilities": ["tv_sev3_kirmizi", "tv_sev3_kanca", "tv_sev3_kanca"],
          "ult": "tv_sev3_kanca"},
     ]},
]

CLASS_BY_ID = {c["id"]: c for c in CLASSES}


def class_no(no):
    for c in CLASSES:
        if c["no"] == no:
            return c
    return None


PACKS = [
    {"id": "cansiz", "name": "CANSIZ PAKET", "price": 5.0,
     "chars": [2, 3, 4, 5, 15, 16, 17, 18], "color": (120, 120, 140),
     "desc": "Savaş alanında karşısına çıkan ilk paket. İçinde ölümsüz olanlar var.",
     "story": "Ölmekten korkmayan sekiz savaşçı; hiçbiri emri almadı, hepsi kendi eliyle seçti."},
    {"id": "element", "name": "ELEMENT KAOSU", "price": 15.0,
     "chars": [6, 7, 8, 9, 10, 11, 12], "color": (120, 190, 90),
     "desc": "Zehir, ateş, su, toprak, elektrik, hava ve kazma.",
     "story": "Yedi element bir araya geldi; biri hâlâ hangisinin güçlü olduğunu bilmiyor."},
    {"id": "fan", "name": "FAN CHARACTERS", "price": 25.0,
     "chars": [13, 14], "color": (90, 150, 210),
     "desc": "Steve ve Alex. Klasiklerin tahtı.",
     "story": "İkisi de aynı dünyada büyüdü ama farklı silahları seçti."},
    {"id": "minestick", "name": "MİNESTİK İNSANI", "price": 15.5,
     "chars": [20, 21], "color": (185, 190, 205),
     "desc": "Şövalye ve Okçu. Yeraltından çıkan iki yalnız savaşçı.",
     "story": "Karanlıktan çıkan ikisi de artık karanlıktan korkmuyor."},
    {"id": "orta_cag", "name": "ORTA ÇAĞ SAVAŞÇILARI", "price": 5.5,
     "chars": [], "color": (200, 60, 60),
     "desc": "Bu pakete henüz karakter eklenmedi.",
     "story": "İçi şimdilik boş. Yakında dolacak."},
    {"id": "darvel", "name": "DARVEL CHARACTERS", "price": 40.0,
     "chars": [22, 23], "color": (200, 60, 60),
     "desc": "Çelik Adam ve Parazit. Zırh ve simbiyot.",
     "story": "Biri zırhını çıkarmadı, diğeri hiç zırh giymedi."},
    {"id": "sacma", "name": "SAÇMA PAKET", "price": 55.0,
     "chars": [19, 24, 25, 29, 30], "color": (75, 75, 95),
     "desc": "Hırsız, Spirit, The Machine, Suikastçi ve Hazine Bağımlısı.",
     "story": "Beşi de farklı bir yoldan aynı kapıya geldi."},
    {"id": "skibidi", "name": "SKİBİDİ TOİLET", "price": 100.0,
     "chars": [26, 27, 28], "color": (150, 130, 190),
     "desc": "Cameraman, Speakerman ve TV Man. Üçü de seviye sistemiyle gelir.",
     "story": "Bir kamerayı, bir hoparlörü ve bir televizyonu aynı pakete koydular."},
]

PACK_BY_ID = {p["id"]: p for p in PACKS}

RUBY_PER_GAME = 0.5
RUBY_BOSS_REWARD = 0.5
