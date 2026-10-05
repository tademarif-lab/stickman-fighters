import pygame

pygame.font.init()

SCREEN_W = 1280
SCREEN_H = 720

# --- MOBIL (APK) MODU: Android/iPad build'inda main.py ile acilir
MOBILE = False            # otomatik: main.py True yapar
TOUCH_SHOW = True         # dokunmatik gosterge cizilsin mi
HIDE_KEY_BAR = False      # mobilde klavye cubugu gizlenir
MENU_COMPACT = False      # kucuk ekranda sik menu
MOBILE_CONF = {}          # MOBIL/mobil_config.json


def mobile_setup(win_w, win_h):
    """Kucuk ekrana gore cozunurlugu ve modu ayarlar."""
    global SCREEN_W, SCREEN_H, MENU_COMPACT, TOUCH_SHOW, MOBILE_CONF
    global HIDE_KEY_BAR
    try:
        import json
        import os
        cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "MOBIL", "mobil_config.json")
        with open(cfg, "r", encoding="utf-8") as f:
            MOBILE_CONF = json.load(f)
    except Exception:
        MOBILE_CONF = {}
    dev = int(MOBILE_CONF.get("device", 0))
    sizes = [(540, 960), (960, 540), (1280, 800)]
    tw, th = sizes[dev if dev < len(sizes) else 0]
    if win_w and win_h:
        # cihaz ekranini dikey/yatay uyumuna gore hedef cozunurluge cevir
        want_land = (win_w > win_h)
        have_land = (tw > th)
        if want_land != have_land:
            tw, th = th, tw
        tw = max(420, min(win_w, tw))
        th = max(320, min(win_h, th))
    SCREEN_W, SCREEN_H = tw, th
    MENU_COMPACT = SCREEN_W < 1000
    TOUCH_SHOW = bool(MOBILE_CONF.get("show_touch", True))
    HIDE_KEY_BAR = True   # dokunmatik var, klavye cubugu gereksiz
    return SCREEN_W, SCREEN_H
FPS = 60
TITLE = "STICKMAN FIGHTERS"
FONT_NAME = "segoeui,arial"

# Sürüm ve güncelleme kayıtları (ana menüden erişilir, aşağı kaydırılır)
VERSION = "1.4.0"
UPDATE_NOTE = "android apk + mobil dokunmatik mod"
CHANGELOG = [
    ("1.1.0", UPDATE_NOTE, [
        "ANDROID APK SÜRÜMÜ: telefonda kurulabilen gerçek APK hazırlandı. ANDROID klasörü: main_mobile.py (giriş noktası), prepare.py (dosya + ikon kopyalama), build_apk.sh / build_docker.sh / build.bat (derleme) ve .github/workflows/android-apk.yml (bulutta GitHub Actions ile tek tıkla APK derleme). Adım adım anlatım: ANDROID/BUILD_APK.md",
        "MOBİL OYUN MODU: oyun artık dokunmatıkla oynanabiliyor. Menülerde dokunma = tıklama, dövüşte solda sanal joystick + sağda 1/2/3/Ulti butonları ve zıpla/eğil. Küçük ekranda klavye kontrol çubuğu gizlenir, can barı küçülür, çözünürlük cihaza göre ayarlanır.",
        "COZUNURLUK DÜZELTMESİ: ekran ölçüsü artık cihaz ekranına göre otomatik ayarlanır (yatay/dikey uyumu dahil) ve dokunma konumu fare sürücüsünden bağımsız çalışır.",
        "ONLINE MOD EKLENDİ: ana menüye ONLINE girdisi. Sunucu bu bilgisayarda çalışır, "
        "herkes sunucu IP adresine bağlanır. Odada en fazla 4 oyuncu olur; maçlar 1v1 olup "
        "turnuva sırasıyla döner (kazanan yerde kalır, kaybeden sıradakiyle eşleşir). "
        "Sunucuyu SUNUCU_BASLAT.bat ile tek tıkla başlatırsın. Detaylar: ONLINE_REHBERI.md",
        "KİLİTLİ ODA (ŞİFRE): ODA ŞİFRE kutusuna şifre yazınca oda kilitlenir, listede KİLİTLİ "
        "görünür ve şifreyi bilmeyen giremez. Şifre boş bırakılırsa oda açık kalır. "
        "Şifre yanlış girilirse sunucu yeni şifre ister.",
        "MOBİL PORT HAZIRLIĞI: SETUP klasöründe TELEFON SÜRÜMÜ artık tıklanabilir; mobil kurulum "
        "ekranı açılır (cihaz, çözünürlük, kontrol düzeni, gösterge ayarı). Dokunmatik kontroller "
        "eklendi: sol altta sanal joystick, sağ altta 4 yetenek butonu + zıpla + eğil. "
        "Kayıtlar SAVE klasöründe ortak kullanılır. Detaylar: MOBIL_REHBERI.md",
        "SAÇMA PAKETİ düzeltildi (Hırsız, Spirit, The Machine, Suikastçi, Hazine Bağımlısı - 55 Ruby) "
        "ve Çelik Adam + Parazit yalnızca DARVEL CHARACTERS paketinde (40 Ruby).",
        "30 YENİ KARAKTER SINIFI eklendi (Vampir, Zombi, İskelet, Mutant, Zehir Kralı, Ateş Manyağı, Madenci, "
        "Su Kralı, Yıldırım Patronsu, Element Kralı, Hava Patronsu, Steve, Alex, Güçlendirilmiş Zombi/İskelet, "
        "Mutant 2.0, Geliştirilmiş Vampir, Hırsız, Şövalye, Okçu, Çelik Adam, Parazit, Spirit, The Machine, "
        "Cameraman, Speakerman, TV Man, Suikastçi, Hazine Bağımlısı). Her sınıfın 3 özelliği + ultisi + pasifi var.",
        "YENİ YETENEK MOTORU: mermi/ok/zerre fırlatma, takip eden füzeler, zemin alanları (zehir dalgası, elektrik, "
        "yangın, asit, su duvarı), ışın/lazer, ses dalgası, kanca ile çekme, haritanın other ucuna fırlatma, "
        "minyon çağırma, kovalayan tsunami, hızlı mermi yağmuru (minigun), şarjlanan vuruş, dirilme.",
        "DURUM EFEKTLERİ: zehir, yanma, çarpılma, sersemletme, kanama, yavaşlatma, zayıflatma, görünmezlik, "
        "uçuş, duvardan geçme, dokunulmazlık, Zombi I (kontrol yapay zekaya geçer) ve can barında rozetler.",
        "KALKAN SİSTEMİ: kalkanı olan karakterler (Şövalye 75, Çelik Adam 125, Alex 25, Element Kralı 25...) "
        "gelen hasarı soğurur; bazı pasifler kalkanı düşman hasarına yansıtır.",
        "RUBY PARA BİRİMİ: oyuna elmas biçimli Ruby eklendi. Arena dışındaki modlarda oyun başına 0.5 Ruby kazanılır. "
        "Ruby kayıt dosyasında saklanır (SAVE/oyun_kayit.json).",
        "8 PAKET + FİYATLAR: CANSIZ PAKET 5, ELEMENT KAOSU 15, FAN CHARACTERS 25, MİNESTİCK İNSANI 15.50, "
        "ORTA ÇAĞ SAVAŞÇILARI 5.50, DARVEL CHARACTERS 40, SAÇMA PAKET 55, SKİBİDİ TOİLET 100 Ruby. "
        "Paket satın alınca içindeki karakterlerin kilitleri açılır.",
        "KAYIT SİSTEMİ: ilerleme, açılan paketler/karakterler, seviyeler ve Ruby SAVE klasöründe JSON olarak saklanır.",
        "SEVİYE SİSTEMİ: Cameraman (6 seviye), Speakerman ve TV Man (3 seviye) ultileriyle bir üst forma geçiyor; "
        "her seviye can/kalkan/ölçek/yetenekleri değiştiriyor.",
        "CAN BARI: buçuklu değerler artık net görünüyor (örn. 140.0), kalkanın ayrı çubuğu ve durum rozetleri eklendi.",
        "PAKET ANİMASYONU: kamera tahta doğru yaklaşıyor, karakter ayağa kalkıyor ve 3 saniye sonra altında "
        "karakterin adı, hikâyesi ve özellikleri beliriyor. Sağdaki soru işareti kaldırıldı.",
        "ŞEHİR → EV GEÇİŞİ: şehirdeki bir binanın çatısında eğilip bekleyen oyuncu otomatik olarak EV'e girer.",
        "EV TEK KAT: ev tek kata düştü (bodrum ve merdivenler kaldırıldı); kapının yanındaki kırmızı bölgeye girince şehre dönülür.",
        "OYUNCU ÇARPIŞMASI: oyuncular artık birbirine çarpar; kafasına binilir, "
        "alttaki nereye giderse üstteki de onun kafasında aynı yere taşınır (zıplayınca da birlikte zıplar).",
        "ARABA FUTBOLU FUTBOL OLDU: araçlar kaldırıldı, artık karakterler topu 1. özellikle düz, 2. özellikle havaya vurur.",
        "LAZER RUN MODU: platform koşusu; sağdan gelen bloklardan zıplayıp/eğilip kaçın, lazerlere dokunma.",
        "KARAKTER YÖN RENDER: sağa/sola bakarken yan profili, zıplarken ön profili görünür.",
        "AYARLAR MENÜSİ: tuş yeniden atama (P1 klavye, P2 ok tuşları), arka plan rengi seçici (RGB).",
        "DÜKKAN SİSTEMİ: boss öldürdüğünde \$0.5 kazan; paketler satın al (deneme paketi ücretsiz, isim/yeteneği ???), "
        "kamera yavaşça karaktere yaklaşır, bilgi gösterir.",
        "ZOMBİ SURVIVAL: sınırsız dalga ve daima görünen dalga sayacı eklendi; dalgalar giderek zorlaşır, ikisi de ölene kadar sürer.",
        "BOSS FIGHTS: boss sayısı 15'ten 100'e çıkarıldı (20 tier x 5 tema); her tema için 20 ayrı boss ismi ve "
        "tier'a göre değişen renkler eklendi, can/hız/hasar kademeli artıyor. Boss'lara tema özel yetenekler de eklendi: "
        "zombi çamur topu fırlatır, örümcek zehirli ağ atar, taş dev (creeper) yerden dikit fışkırtır, enderman ışınlanır, blaze lav püskürtür.",
        "OYUNCU KARAKTERİ YENİDEN ÇİZİLDİ: oyuncu artık atılan görseldeki gibi sade, yuvarlak başlı ve kalın "
        "gövdeli klasik stickman silüeti; yürüme, koşma, zıplama, çömelme, yumruk, tekme, kombosu, "
        "hasar alma ve yere yatma animasyonları çalışıyor.",
        "LAUNCHER YENİDEN DÜZENLENDİ: yazılar düzeldi (sol hizalı). Sol tarafta SÜRÜMLER, sağ tarafta OYUNLAR "
        "(oyun ikonu ve STICK FIGHTERS adı), altta BİLGİ bölümü var: oyunun amacı, karakter, yaratıklar, "
        "boss'lar ve modlar anlatılıyor.",
        "SETUP EKLENDİ: SETUP klasöründeki KURULUMU_BASLAT.bat açılınca kurulum ekranı gelir; OYUNU İNDİR ve "
        "PC SÜRÜMÜ çalışır, TELEFON SÜRÜMÜ devre dışıdır ve üstü siyah çizgiyle çizilir. "
        "Kurulum ayrıca masaüstüne 'Stick Fighters' kısayolu ekler.",
        "PAKET ANİMASYONU GÜNCELLENDİ: kamera tahta doğru yaklaşıyor, tahtta oturan karakter ayağa kalkıyor "
        "(eklemler yumuşak geçişle düzeliyor, kalkınca altın halka çıkıyor) ve 3 saniye sonra altında karakterin "
        "adı, hikâyesi ve özellikleri beliriyor. Sağdaki soru işareti kaldırıldı.",
        "KARAKTER YÖNÜ DÜZGÜN GÖSTERİLİYOR: karakter artık hep bize bakmıyor; sola giderken sol yan profili, "
        "sağa giderken sağ yan profili (burun, göz ve öne bakan ayaklar ile), zıplarken ön yüzü görünüyor.",
        "LAUNCHER ÇOKLU PROJE: launcher KATİL5019 LAUNCHER olarak yeniden yazıldı. Oyun adının iki yanında ◀ ▶ "
        "okları var; yeni projeler launcher_projects.py dosyasına eklenerek listeye otomatik giriyor.",
        "versions klasörüne kopyalanan her klasör ayrı sürüm olarak listede görünür. "
        "OYUNU_BASLAT.bat ile çift tıklamayla açılır; ikonlar için make_icons.py çalıştırılır.",
        "MODELlemE YENİLENDİ: oyuncu, boss ve yaratık çizimleri baştan yazıldı (chars.py). Artık yüz, göz, saç, "
        "zırh, taç ve aileye özel siluetler var; zombi, creeper, örümcek, enderman, blaze, hayvan ve golem "
        "her biri kendi modeliyle çiziliyor.",
        "DALGALAR SINIRSIZ: zombi modunda dalga sayısı kaldırıldı; her tur biraz güçleniyor, yaratık sayısı artıyor "
        "ve havuzdan rastgele yeni yaratıklar ekleniyor.",
        "SEÇİM EKRANI: karakter listesinde şu an tek karakter (İNSAN) var ve sayaç '1 / 100' yazıyor; "
        "yeni karakterler CHARACTERS listesine eklenince ok tuşlarıyla gezilir.",
        "KARAKTER/YARATIK AYRIMI: karakter listesinde şu an sadece İNSAN var. Zombi, creeper, örümcek, enderman, "
        "blaze, ejderha, hayvan ve golem gibi 99 yaratık ayrı listeye (CREATURES) alındı ve ZOMBİ modunda "
        "8 dalgaya dağıtıldı; her yaratık kendi hikâyesi, canı, hızı, rengi ve ailesiyle geliyor.",
        "SEÇİM EKRANI: karakterin iki yanındaki ◀ ▶ oklarıyla (veya P1 A/D, P2 ok tuşlarıyla) karakter değiştirilir; "
        "altında karakterin adı, hikâyesi ve 3 yeteneği gösterilir.",
        "ANA MENÜ GELİŞTİRİLDİ: her menü öğesinin ikonu ve açıklaması eklendi, seçili buton vurgulanıp kayıyor, "
        "arkada uçuşan altın parçacıkları ve logoya altın parlama geldi.",
        "PARKUR MODU KALDIRILDI: PARKUR haritası oyun modlarından çıkarıldı.",
    ]),
    ("1.0.0", UPDATE_NOTE, [
        "GÜNCELLEME KAYITLARI EKLENDİ: sürüm (1.0.0) ve güncelleme notu artık ana menüde görünür; bu ekranda tüm yenilikler aşağı kaydırılarak okunur.",
        "ZOMBİ SURVIVAL MODU: oyun modlarına 'ZOMBİ' haritası eklendi. Dalga dalga zombi, örümcek ve creeper saldırır; hepsini öldürerek hayatta kal, en çok öldüren kazanır.",
        "FUTBOL MODU: karakterler stadyumda topu rakip kaleye sokmaya çalışır; topa ayağıyla çarpılıp sürülür, ilk 3 golü atan kazanır.",
        "BOSS FIGHTS MODU: sırayla 15 farklı boss ile orta zorlukta dövüş; hepsini yenen oyuncu kazanır.",
        "MİNECRAFT: artık her cevherden (kömür, demir, altın, elmas, obsidyen) 10 tane var.",
        "MİNECRAFT: 'ÇUBUK' eşyası eklendi (2 odun -> 4 çubuk). Kazmalar artık 3 malzeme + 2 çubuk ile yapılır; taş, demir ve elmas kazma da üretilebilir.",
        "MADEN GİRİŞİ DÜZELTİLDİ: rampa merdivenlerinden 4 kat aşağıya sorunsuz inilir, oyuncu artık yüzeye fırlamaz.",
        "CANAVARLAR YALNIZCA MADENDE: ormanda canavar çıkmaz ve canavarlar madenin dışına çıkamaz.",
        "KIRILMAZ ARAZİ: toprak basamaklar ve yeni 'MADEN TAŞI' türü kırılamaz; ormandaki taş kayalar kırılınca taş verir.",
        "TEK SU GÖLÜ + TEK LAV GÖLÜ: ormanda birer tane; lav gölünün yanında nether portalı yanar.",
        "DETERMİNİSTİK ORMAN: ağaçlar her oyunda aynı yerde çıkar (rastgele değil).",
        "3x3 ELLE CRAFT: çalışma masası gerekmez, imleçle de üretilebilir.",
        "DERİN MADEN 4 KAT: kömür, demir, altın, elmas, obsidyen derinlikle artan değerde.",
    ]),
]


def changelog_entries():
    for version, note, lines in CHANGELOG:
        yield version, note, lines

TILE = 40
WORLD_TILES = 25
WORLD_W = WORLD_TILES * TILE
WORLD_H = WORLD_TILES * TILE
GROUND_Y = WORLD_H - 4 * TILE

GRAVITY = 1700.0
JUMP_SPEED = 620.0
CLIMB_SPEED = 210.0
MAX_FALL = 1500.0
STAND_H = 74
CROUCH_H = 50
PLAYER_W = 36

ULT_FILL_RATE = 0.2
ULT_HIT_BONUS = 5.0
ULT_TIME = 6.0
ULT_MULT = 2.0

CITY_DEATH_Y = 1040.0
CITY_ZOOM = 0.55

TRUCK_W = 160
TRUCK_H = 100
TRUCK_SPEED = 150.0
TRUCK_GAP = 2.2
TRUCK_EXPLODE_DIST = 950.0
TRUCK_DRIVE_CROUCH = 3.0
TRUCK_DRIVE_TIME = 5.0

LASER_SPEED = 130.0
LASER_DPS = 40.0

# şehir çatısında eğilme → EV'e geçiş
HOUSE_CROUCH_TIME = 0.8

MINE_WORLD_W = 4240
MINE_END_RETURN_DELAY = 10.0
PORTAL_LAVA_DIST = 130.0
MOB_AGGRO_DIST = 240.0
MOB_CONTACT_CD = 1.0
MOB_CONTACT_DMG_MAP = {"zombi": 0.5, "örümcek": 5.0, "creeper": 0.0,
                       "enderman": 10.0, "blaze": 8.0}
MOB_CONTACT_DMG = 5.0
MOB_EXPLODE_DMG = 25.0
MOB_STATS = {"zombi": (20, 80.0), "örümcek": (12, 150.0), "creeper": (8, 58.0),
             "enderman": (38, 210.0), "blaze": (26, 95.0)}
MOB_DROPS = {"zombi": "et", "örümcek": "et", "creeper": None,
             "enderman": "ender_incisi", "blaze": "blaze_cubugu"}
BLAZE_BALL_SPEED = 300.0
BLAZE_BALL_DMG = 8.0
BLAZE_SHOOT_TIME = 2.0
END_WATER_DIST = 150.0

ITEM_NAMES = {"odun": "ODUN", "çubuk": "ÇUBUK", "kömür": "KÖMÜR", "demir": "DEMİR", "altın": "ALTIN",
              "elmas": "ELMAS", "obsidyen": "OBSİDYEN", "et": "ET", "tas": "TAŞ",
              "nether_tasi": "NETHER TAŞI", "netherite": "NETHERITE",
              "blaze_cubugu": "BLAZE ÇUBUĞU",
              "ender_incisi": "ENDER İNCİSİ", "ender_gozu": "ENDER GÖZÜ",
              "tahta_kazma": "TAHTA KAZMA", "tas_kazma": "TAŞ KAZMA",
              "demir_kazma": "DEMİR KAZMA", "elmas_kazma": "ELMAS KAZMA",
              "kova": "KOVA", "lav_kovası": "LAV KOVASI", "yatak": "YATAK",
              "crafting_table": "CRAFTING TABLE",
              "end_cerceve": "END ÇERÇEVE"
              }
ITEM_COLORS = {"odun": (160, 116, 64), "çubuk": (188, 148, 92), "kömür": (84, 84, 96), "demir": (200, 128, 74),
               "altın": (232, 200, 84), "elmas": (120, 220, 232), "obsidyen": (72, 52, 96),
               "et": (196, 74, 74), "tas": (150, 150, 158), "nether_tasi": (98, 48, 44),
               "netherite": (150, 148, 165),
               "blaze_cubugu": (240, 190, 60), "ender_incisi": (120, 200, 120),
               "ender_gozu": (120, 220, 160), "tahta_kazma": (176, 132, 76),
               "tas_kazma": (158, 158, 166), "demir_kazma": (214, 146, 84),
               "elmas_kazma": (120, 220, 232), "kova": (170, 190, 210),
               "lav_kovası": (255, 150, 60),
               "yatak": (200, 120, 150), "crafting_table": (170, 130, 90),
               "end_cerceve": (90, 150, 110)}

PICKAXE_TIER = {"tahta_kazma": 1, "tas_kazma": 2, "demir_kazma": 3, "elmas_kazma": 4}
ORE_MIN_TIER = {"kömür": 1, "demir": 2, "altın": 3, "elmas": 3, "obsidyen": 4}

# ---------- TUŞ BAĞLAMALARI (varsayılan) ----------
import pygame
DEFAULT_KEYS_P1 = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_w,
    "crouch": pygame.K_s,
    "ability1": pygame.K_e,
    "ability2": pygame.K_q,
    "ability3": pygame.K_z,
    "ult": pygame.K_g,
    "craft": pygame.K_t,
    "place": pygame.K_r,
}
DEFAULT_KEYS_P2 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_UP,
    "crouch": pygame.K_DOWN,
    "ability1": None,
    "ability2": None,
    "ability3": None,
    "ult": None,
    "craft": None,
    "place": None,
}

# ---------- ARKA PLAN RENK ----------
DEFAULT_BG_COLOR = (22, 34, 66)

# ---------- TUŞ BAĞLAMALARI (varsayılan, ayarlardan değiştirilebilir) ----------
import pygame
DEFAULT_KEYS_P1 = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_w,
    "crouch": pygame.K_s,
    "ability1": pygame.K_e,
    "ability2": pygame.K_q,
    "ability3": pygame.K_z,
    "ult": pygame.K_g,
    "craft": pygame.K_t,
    "place": pygame.K_r,
}
DEFAULT_KEYS_P2 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_UP,
    "crouch": pygame.K_DOWN,
    "ability1": None,
    "ability2": None,
    "ability3": None,
    "ult": None,
    "craft": None,
    "place": None,
}

# Mevcut aktif tuşlar (menüden değiştirilebilir, varsayılanla başlar)
KEYS_P1 = DEFAULT_KEYS_P1.copy()
KEYS_P2 = DEFAULT_KEYS_P2.copy()

# Tuş haritaları (oyun içinde kullanılır, ayarlar menüsünden güncellenir)
def _build_keymap(keys_p1, keys_p2):
    km = {}
    for action, key in keys_p1.items():
        if key is not None:
            km[key] = ("p1", action)
    for action, key in keys_p2.items():
        if key is not None:
            km[key] = ("p2", action)
    return km

MOVE_KEYS = _build_keymap(KEYS_P1, KEYS_P2)

P1_ABILITY_KEYS = {}
for action in ("ability1", "ability2", "ability3", "ult", "craft", "place"):
    k1 = KEYS_P1.get(action)
    if k1 is not None:
        P1_ABILITY_KEYS[k1] = action + "_pressed"

# Arka plan rengi (menüden değiştirilebilir)
BG_COLOR = DEFAULT_BG_COLOR

# ---------- PARA BİRİMİ VE DÜKKAN ----------
PLAYER_MONEY = 0.0
BOSS_KILL_REWARD = 0.5  # her boss öldürüldüğünde
SHOP_REVEAL_TIME = 3.0   # paket animasyonunda bilgi kartının açılma süresi

# Paket tanımları
PACKS = {
    "deneme": {
        "name": "???",
        "price": 0.0,
        "char_name": "???",
        "story": "???",
        "abilities": ["???", "???", "???"],
        "desc": "Deneme paketi - ücretsiz - karakter bilgisi gizli",
        "hidden": True,
    }
}

# ---------- 3x3 grid recipes (Minecraft tarzı; hep 3x3, çalışma masası gerekmez)
# Kazmalar: üstte 3 malzeme + sapta 2 çubuk (orta alt sütun: 4 ve 7)
CRAFT_3 = {
    "çubuk": (("çubuk", 4),
              (None, "odun", None, None, "odun", None, None, None, None)),
    "tahta_kazma": (("tahta_kazma", 1),
                    ("odun", "odun", "odun", None, "çubuk", None, None, "çubuk", None)),
    "tas_kazma": (("tas_kazma", 1),
                  ("tas", "tas", "tas", None, "çubuk", None, None, "çubuk", None)),
    "demir_kazma": (("demir_kazma", 1),
                    ("demir", "demir", "demir", None, "çubuk", None, None, "çubuk", None)),
    "elmas_kazma": (("elmas_kazma", 1),
                    ("elmas", "elmas", "elmas", None, "çubuk", None, None, "çubuk", None)),
    "kova": (("kova", 1),
             ("demir", None, "demir", None, "demir", None, None, None, None)),
    "ender_gozu": (("ender_gozu", 1),
                   ("blaze_cubugu", "ender_incisi", None, None, None, None,
                    None, None, None)),
    "yatak": (("yatak", 1),
              ("et", "et", "et", "odun", "odun", "odun", None, None, None)),
    "end_cerceve": (("end_cerceve", 1),
                    ("nether_tasi", "nether_tasi", "nether_tasi",
                     "nether_tasi", "ender_gozu", "nether_tasi",
                     "nether_tasi", "nether_tasi", "nether_tasi")),
}
BLOCK_ITEMS = {"crafting_table", "end_cerceve", "yatak"}

DROWN_TIME = 5.0
DROWN_DMG = 25.0
LAVA_DPS = 5.0
CHAIR_CROUCH_TIME = 5.0
MASA_CROUCH_TIME = 10.0
CHAIR_DMG = 6.0
MASA_DMG = 12.0
JOHNNY_WIN_COUNT = 10
JOHNNY_PUNISH_DMG = 10.0
DRAGON_HP = 150.0
DRAGON_SPEED = 70.0
DRAGON_FIRE_SPEED = 260.0
DRAGON_TARGET_TIME = 10.0
CRYSTAL_HP = 30.0
CRYSTAL_SWITCH_TIME = 5.0
CRYSTAL_REGEN = 5.5
CRYSTAL_RESPAWN = 4.0

SPLIT_DIST_ON = 540.0
SPLIT_DIST_OFF = 440.0

ABILITIES = {
    "punch": {"name": "Yumruk", "dmg": 5, "cd": 0.5, "dur": 0.30, "hit0": 0.08, "hit1": 0.20,
              "range": 46, "ytop": 66, "h": 14, "pose": "punch"},
    "kick": {"name": "Tekme", "dmg": 10, "cd": 1.0, "dur": 0.42, "hit0": 0.10, "hit1": 0.24,
             "range": 62, "ytop": 24, "h": 26, "pose": "kick"},
    "combo": {"name": "Tekme+Yumruk", "dmg": 15, "cd": 1.5, "dur": 0.55, "hit0": 0.10, "hit1": 0.30,
              "range": 72, "ytop": 52, "h": 46, "pose": "combo"},
    "villpunch": {"name": "Köylü Yumruğu", "dmg": 1, "cd": 1.2, "dur": 0.30, "hit0": 0.08, "hit1": 0.20,
                  "range": 50, "ytop": 60, "h": 20, "pose": "punch"},
    "bite": {"name": "Isırık", "dmg": 6, "cd": 0.45, "dur": 0.28, "hit0": 0.07, "hit1": 0.18,
             "range": 40, "ytop": 56, "h": 16, "pose": "punch"},
    "headbutt": {"name": "Kafa Vuruşu", "dmg": 8, "cd": 0.8, "dur": 0.34, "hit0": 0.09, "hit1": 0.22,
                 "range": 44, "ytop": 62, "h": 18, "pose": "punch"},
    "uppercut": {"name": "Dirsek", "dmg": 12, "cd": 1.1, "dur": 0.40, "hit0": 0.10, "hit1": 0.24,
                 "range": 56, "ytop": 40, "h": 34, "pose": "kick"},
    "stomp": {"name": "Ayak Tabancası", "dmg": 9, "cd": 0.9, "dur": 0.36, "hit0": 0.08, "hit1": 0.20,
              "range": 58, "ytop": 8, "h": 22, "pose": "kick"},
    "sweep": {"name": "Yere Sürükleme", "dmg": 7, "cd": 1.0, "dur": 0.38, "hit0": 0.10, "hit1": 0.26,
              "range": 66, "ytop": 6, "h": 20, "pose": "kick"},
    "spin": {"name": "Nöbet", "dmg": 11, "cd": 1.3, "dur": 0.50, "hit0": 0.10, "hit1": 0.32,
             "range": 70, "ytop": 34, "h": 40, "pose": "combo"},
    "tackle": {"name": "Çarpanlık", "dmg": 13, "cd": 1.4, "dur": 0.48, "hit0": 0.10, "hit1": 0.28,
               "range": 78, "ytop": 36, "h": 38, "pose": "combo"},
    "smash": {"name": "Ezici Darbe", "dmg": 16, "cd": 1.6, "dur": 0.56, "hit0": 0.12, "hit1": 0.32,
              "range": 70, "ytop": 48, "h": 44, "pose": "combo"},
}

HUMAN_ABILITY_ORDER = ["punch", "kick", "combo"]

CREATURES = [
    {"id": "human", "name": "İNSAN", "hp": 100, "speed": 270.0,
     "info": "Dengeli savaşçı",
     "story": "Kralın emriyle üç kardeşini yurt dışına uğratmadan önce, kendi kılıcını kınına koyup bir daha açmamayı söyledi.",
     "abilities": ["punch", "kick", "combo"]},
    {"id": "madenci", "name": "MADENCİ", "hp": 110, "speed": 250.0,
     "info": "Yeraltının ustası",
     "story": "Kömür, demir, eldemir; her şey onun kazmasından çıktı. Yalnız kazarken karanlıkta bir şey onu izliyordu.",
     "abilities": ["smash", "kick", "punch"]},
    {"id": "asker", "name": "ASKER", "hp": 120, "speed": 265.0,
     "info": "Disiplinli savaşçı",
     "story": "Ordunun en uzun eğitim alanıydı; kılıcını kuşanırken kimseden izin almazdı.",
     "abilities": ["kick", "uppercut", "combo"]},
    {"id": "muhafiz", "name": "MUHAFIZ", "hp": 140, "speed": 210.0,
     "info": "Köyün demir kapısı",
     "story": "Köy kapısında duran dev; yıllardır kimse onu geçemedi, kimse de geçmeyi denemedi.",
     "abilities": ["smash", "stomp", "tackle"]},
    {"id": "paladin", "name": "PALADİN", "hp": 125, "speed": 255.0,
     "info": "Işığın savaşçısı",
     "story": "Yıkılmış tapınağın gölgesinde bulduğu zırhla kendini yeniden yarattı.",
     "abilities": ["uppercut", "combo", "headbutt"]},
    {"id": "korsan", "name": "KORSAAN", "hp": 110, "speed": 275.0,
     "info": "Denizlerden gelen",
     "story": "Gemileri yağmaladı, gemileri onu yağmaladı; bir gün karaya vurdu ve denizden vazgeçti.",
     "abilities": ["kick", "tackle", "smash"]},
    {"id": "ninja", "name": "NİNJA", "hp": 95, "speed": 330.0,
     "info": "Gölgede doğan",
     "story": "Gece yüzünden nefret ediyordu ama kimse onu gündüz göremedi.",
     "abilities": ["headbutt", "spin", "kick"]},
    {"id": "avci", "name": "AVCI", "hp": 100, "speed": 300.0,
     "info": "Ormanın gözü",
     "story": "Oku gözünden önce fırlatırdı; avını çoğu zaman isminden önce bulurdu.",
     "abilities": ["punch", "kick", "bite"]},
    {"id": "buyucu", "name": "BÜYÜCÜ", "hp": 90, "speed": 245.0,
     "info": "Karanlık bilgin",
     "story": "Kitabında gördüğü her yaratığa bir sayfa ayırdı; o gece sayfaların hepsi canlandı.",
     "abilities": ["spin", "uppercut", "tackle"]},
    {"id": "kahin", "name": "KÂHİN", "hp": 95, "speed": 255.0,
     "info": "Yıldızları okuyan",
     "story": "Gökyüzünü bir kez okudu, sonra kimseye göstermedi.",
     "abilities": ["headbutt", "spin", "kick"]},
    {"id": "gezgin", "name": "GEZGİN", "hp": 105, "speed": 280.0,
     "info": "Sonsuz yolcu",
     "story": "On adım ileri gitti, otuz adım geri geldi; kimse nerede olduğunu bilmiyor.",
     "abilities": ["kick", "punch", "sweep"]},
    {"id": "sovalye", "name": "ŞÖVALYE", "hp": 125, "speed": 250.0,
     "info": "Demir yemin",
     "story": "Kılıcını bir çocuğa verdi ve onun için kılıçsız savaşmaya başladı.",
     "abilities": ["smash", "uppercut", "tackle"]},
    {"id": "okcu", "name": "OKÇU", "hp": 100, "speed": 290.0,
     "info": "Uzun menzil",
     "story": "Gözünü kısmadan hedefi bulurdu; ama yakından kimse onu göremezdi.",
     "abilities": ["punch", "kick", "headbutt"]},
    {"id": "dovuscu", "name": "DÖVÜŞÇÜ", "hp": 115, "speed": 290.0,
     "info": "Arena ustası",
     "story": "Hiç kaybetmedi; hiç kazandığı da olmadı.",
     "abilities": ["combo", "kick", "tackle"]},
    {"id": "kilic", "name": "KILIÇ USTASI", "hp": 110, "speed": 270.0,
     "info": "Çelik ustadı",
     "story": "Bin kılıç dövdü, dokuz yüz doksan dokuzu kırıldı.",
     "abilities": ["kick", "combo", "smash"]},
    {"id": "yeralti", "name": "YERALTI SAVAŞÇISI", "hp": 120, "speed": 250.0,
     "info": "Karanlık madenci",
     "story": "Derinlere indi; yukarıdakiler onu hiç aramadı.",
     "abilities": ["smash", "sweep", "uppercut"]},
    {"id": "tuccar", "name": "TÜCCAR", "hp": 95, "speed": 265.0,
     "info": "Kılıç satan",
     "story": "Zırhın ağırlığına bakıp fiyatını söylerdi; kılıç da kendi ağırlığındaydı.",
     "abilities": ["headbutt", "punch", "kick"]},
    {"id": "rehber", "name": "REHBER", "hp": 100, "speed": 275.0,
     "info": "Kaybolmaz iz",
     "story": "Onu takip eden hiç kimse yolunu şaşırmadı; şaşıran tek oydu.",
     "abilities": ["kick", "sweep", "punch"]},
    {"id": "kasif", "name": "KÂŞİF", "hp": 105, "speed": 285.0,
     "info": "Bilinenlerin ötesi",
     "story": "Haritanın kenarına çizgi çekti, sonra o çizginin ötesine geçti.",
     "abilities": ["kick", "combo", "spin"]},
    {"id": "kral", "name": "KRAL", "hp": 130, "speed": 245.0,
     "info": "Taçlı gölge",
     "story": "Taç ona değil, ona baş kesti; o da kabul etti.",
     "abilities": ["smash", "combo", "uppercut"]},

    {"id": "zombi", "name": "ZOMBİ", "hp": 100, "speed": 230.0,
     "info": "Sessiz yürüyüş",
     "story": "Toprağa düşen her şey onu hatırlar; o da hiçbirini affetmez.",
     "abilities": ["bite", "punch", "kick"]},
    {"id": "zefirzombi", "name": "ZEFİR ZOMBİ", "hp": 95, "speed": 235.0,
     "info": "Zehir damarı",
     "story": "Bir ısırık yeter; gerisi ışığın sönmesi.",
     "abilities": ["bite", "spin", "sweep"]},
    {"id": "isikzombi", "name": "IŞIK ZOMBİSİ", "hp": 105, "speed": 225.0,
     "info": "Karanlık kovucu",
     "story": "Işığı emdiği için gece onun için gündüz, gündüz onun için gece.",
     "abilities": ["headbutt", "smash", "uppercut"]},
    {"id": "suzombi", "name": "SU ZOMBİSİ", "hp": 100, "speed": 240.0,
     "info": "Boğulan savaşçı",
     "story": "Deniz onu sakladı, kıyıya geri bırakmadı.",
     "abilities": ["bite", "sweep", "kick"]},
    {"id": "kumzombi", "name": "KUM ZOMBİSİ", "hp": 95, "speed": 245.0,
     "info": "Çölün bekçisi",
     "story": "Kumdan çıktığı günden beri susuz değildi.",
     "abilities": ["uppercut", "kick", "headbutt"]},
    {"id": "buzzombi", "name": "BUZ ZOMBİSİ", "hp": 100, "speed": 215.0,
     "info": "Donmuş öfke",
     "story": "Bu onu yavaşlattı, öfkesini ikiye katladı.",
     "abilities": ["smash", "uppercut", "tackle"]},
    {"id": "kayazombi", "name": "KAYA ZOMBİSİ", "hp": 130, "speed": 200.0,
     "info": "Dağın öfkesi",
     "story": "Yıllarca yatakta bekledi; ayağa kalktığında dağ da zor kalktı.",
     "abilities": ["smash", "stomp", "combo"]},
    {"id": "obszombi", "name": "OBSİDYEN ZOMBİSİ", "hp": 140, "speed": 205.0,
     "info": "Sert yüzeyli ölü",
     "story": "Kılıç kırıldı, eldiven kırıldı; kendisi kırılmadı.",
     "abilities": ["smash", "stomp", "uppercut"]},
    {"id": "eldaszombi", "name": "ELMAS ZOMBİSİ", "hp": 145, "speed": 215.0,
     "info": "Parlayan ölü",
     "story": "Işığı yansıtır; bu yüzden onu gözden kaçırmak kolaydır.",
     "abilities": ["smash", "kick", "spin"]},
    {"id": "altinzombi", "name": "ALTIN ZOMBİSİ", "hp": 135, "speed": 210.0,
     "info": "Hırs",
     "story": "Altına yakınlaştı; sonra altın onu yaklaştırdı.",
     "abilities": ["smash", "tackle", "punch"]},
    {"id": "koyuzombi", "name": "KÖY ZOMBİSİ", "hp": 105, "speed": 225.0,
     "info": "Dönüşü olmayan",
     "story": "Eve gitmek istedi ama ev artık onun için başka bir yerdeydi.",
     "abilities": ["punch", "villpunch", "kick"]},
    {"id": "balikzombi", "name": "BALIKÇI ZOMBİSİ", "hp": 105, "speed": 245.0,
     "info": "Çengelli el",
     "story": "Ağını kurdu, bir daha da toplamadı.",
     "abilities": ["bite", "headbutt", "kick"]},
    {"id": "patronzombi", "name": "PATRON ZOMBİSİ", "hp": 135, "speed": 225.0,
     "info": "Kırık kılıç",
     "story": "Kılıcını düşürmedi; kılıcı düştü.",
     "abilities": ["smash", "uppercut", "combo"]},
    {"id": "kralice", "name": "KRALİÇE", "hp": 140, "speed": 235.0,
     "info": "Taçlı kül",
     "story": "Krallığı öldükten sonra da bırakmadı.",
     "abilities": ["smash", "combo", "spin"]},
    {"id": "kabuszombi", "name": "KÂBUS ZOMBİSİ", "hp": 120, "speed": 250.0,
     "info": "Uykunun düşmanı",
     "story": "Gözlerini kapattığın anda gelir; açtığında çoktan oradadır.",
     "abilities": ["spin", "smash", "uppercut"]},

    {"id": "creeper", "name": "CREEPER", "hp": 90, "speed": 250.0,
     "info": "Patlayıcı sessizlik",
     "story": "Onu görmediği için öldü, duyduğu için kaçtı.",
     "abilities": ["kick", "punch", "sweep"]},
    {"id": "yildirim", "name": "YILDIRIM CREEPER", "hp": 85, "speed": 290.0,
     "info": "Fırtına",
     "story": "Üzerine yağmur yağınca güçlendi; güçlüyken gülümsedi.",
     "abilities": ["tackle", "kick", "spin"]},
    {"id": "lavcreeper", "name": "LAV CREEPER", "hp": 95, "speed": 245.0,
     "info": "Kor gibi",
     "story": "Ateş onu yakmadı; ateş onu besledi.",
     "abilities": ["smash", "uppercut", "bite"]},
    {"id": "buzcreeper", "name": "BUZ CREEPER", "hp": 95, "speed": 235.0,
     "info": "Ayaz",
     "story": "Donduğunda patlaması daha güçlü, sıcaklığı da daha soğuk olurdu.",
     "abilities": ["kick", "smash", "sweep"]},
    {"id": "sucreeper", "name": "SU CREEPER", "hp": 90, "speed": 260.0,
     "info": "Islak fitil",
     "story": "Suyu seviyor; ıslak fitili de daha hızlı yanıyordu.",
     "abilities": ["tackle", "kick", "uppercut"]},
    {"id": "tntcreeper", "name": "TNT CREEPER", "hp": 80, "speed": 270.0,
     "info": "Patlayıcı yük",
     "story": "İçinde bir fitil var; fitilin de bir sürüsü.",
     "abilities": ["bite", "tackle", "kick"]},
    {"id": "kralcreeper", "name": "KRAL CREEPER", "hp": 120, "speed": 230.0,
     "info": "Patlama tacı",
     "story": "Taç takmak patlamayı büyüttü; fark edemeyecek kadar güzeldi.",
     "abilities": ["smash", "tackle", "combo"]},
    {"id": "kumcreeper", "name": "KÜMELİ CREEPER", "hp": 100, "speed": 240.0,
     "info": "Kürkü ısırır",
     "story": "Isırmadan önce kürkünü tutuştururdu.",
     "abilities": ["spin", "kick", "bite"]},
    {"id": "kizilcreeper", "name": "KIZIL CREEPER", "hp": 105, "speed": 255.0,
     "info": "Kırmızı ışık",
     "story": "Kızardı, sonra yandı.",
     "abilities": ["uppercut", "smash", "kick"]},
    {"id": "golgecreeper", "name": "GÖLGE CREEPER", "hp": 95, "speed": 300.0,
     "info": "Görünmez fitil",
     "story": "Gölgede doğdu, gölgede büyüdü, gölgede patladı.",
     "abilities": ["spin", "headbutt", "kick"]},

    {"id": "orumcek", "name": "ÖRÜMCEK", "hp": 85, "speed": 300.0,
     "info": "Ağ ustası",
     "story": "Ağı ördü, sonra ağın içinde bekledi.",
     "abilities": ["bite", "punch", "kick"]},
    {"id": "zehirli", "name": "ZEHİRLİ ÖRÜMCEK", "hp": 80, "speed": 290.0,
     "info": "Bir damla",
     "story": "Damlayı gördüğünde çoktan geçmiş olurdu.",
     "abilities": ["bite", "spin", "sweep"]},
    {"id": "devorumcek", "name": "DEV ÖRÜMCEK", "hp": 130, "speed": 250.0,
     "info": "Sekiz bacak, tek niyet",
     "story": "Ayağının altına bakmadan yürürdü; bakması da işe yaramazdı.",
     "abilities": ["smash", "stomp", "tackle"]},
    {"id": "golgeorumcek", "name": "GÖLGE ÖRÜMCEĞİ", "hp": 95, "speed": 285.0,
     "info": "Karanlık ağ",
     "story": "Ağı ışıkta değil, gölgede görünürdü.",
     "abilities": ["spin", "bite", "headbutt"]},
    {"id": "agustasi", "name": "AĞ USTASI", "hp": 105, "speed": 275.0,
     "info": "Mimar",
     "story": "Her ağ bir tuzak; her tuzak bir hikâye.",
     "abilities": ["bite", "sweep", "uppercut"]},
    {"id": "karorumcek", "name": "KAR ÖRÜMCEĞİ", "hp": 100, "speed": 255.0,
     "info": "Beyaz avcı",
     "story": "Karda iz bırakmaz; ama izini de silerdi.",
     "abilities": ["headbutt", "kick", "smash"]},
    {"id": "kizilorumcek", "name": "KIZIL ÖRÜMCEK", "hp": 105, "speed": 265.0,
     "info": "Kan rengi",
     "story": "Avını görünce kızarır; kızardığında daha hızlı koşar.",
     "abilities": ["bite", "spin", "kick"]},
    {"id": "tavanorumcek", "name": "TAVAN ÖRÜMCEĞİ", "hp": 95, "speed": 280.0,
     "info": "Ters döner",
     "story": "Tavandan inmezdi; tavana çıkardı.",
     "abilities": ["headbutt", "uppercut", "punch"]},
    {"id": "anaorumcek", "name": "ANA ÖRÜMCEK", "hp": 140, "speed": 260.0,
     "info": "Yuva hanımı",
     "story": "Yuvasındaki yüzlerce yavru ona tek bir kıvılcım yeterdi.",
     "abilities": ["smash", "bite", "combo"]},
    {"id": "ucanorumcek", "name": "UÇAN ÖRÜMCEK", "hp": 90, "speed": 320.0,
     "info": "Rüzgâr ağı",
     "story": "Yere inmeden avını ağına sarıyordu.",
     "abilities": ["spin", "bite", "kick"]},

    {"id": "enderman", "name": "ENDERMAN", "hp": 95, "speed": 330.0,
     "info": "Sessiz taşıyıcı",
     "story": "Blokları alır, bir yere bırakır; nedenini kimse anlamadı.",
     "abilities": ["headbutt", "kick", "tackle"]},
    {"id": "bassiz", "name": "BAŞSIZ", "hp": 100, "speed": 300.0,
     "info": "Gözsüz savaşçı",
     "story": "Gözleri olmayınca nişan almayı da bırakmış.",
     "abilities": ["smash", "spin", "uppercut"]},
    {"id": "golgesavas", "name": "GÖLGE SAVAŞÇI", "hp": 105, "speed": 290.0,
     "info": "Gece gelen",
     "story": "Gündüz hiç yoktu; gündüz de bir şeyi vardı.",
     "abilities": ["spin", "combo", "kick"]},
    {"id": "bosluk", "name": "BOŞLUK GÖLGE", "hp": 95, "speed": 320.0,
     "info": "Hiçliğin adımı",
     "story": "Geçtiği yer boşalıyordu.",
     "abilities": ["tackle", "headbutt", "spin"]},
    {"id": "morhayalet", "name": "MOR HAYALET", "hp": 85, "speed": 310.0,
     "info": "Işığı olmayan",
     "story": "Karanlıkta mor; ışıkta yok.",
     "abilities": ["spin", "bite", "uppercut"]},
    {"id": "golgekrali", "name": "GÖLGE KRALI", "hp": 135, "speed": 300.0,
     "info": "Mor taç",
     "story": "Taç mordu; gölgesi taçtan uzundu.",
     "abilities": ["smash", "combo", "spin"]},
    {"id": "gecegolge", "name": "GECE GÖLGE", "hp": 100, "speed": 295.0,
     "info": "Karanlık ustası",
     "story": "Gece onu çağırırdı; o da gitmeyi reddederdi.",
     "abilities": ["tackle", "smash", "kick"]},
    {"id": "izigolge", "name": "İKİZ GÖLGE", "hp": 105, "speed": 285.0,
     "info": "İki kalp",
     "story": "Biri ölünce diğeri de susardı.",
     "abilities": ["headbutt", "combo", "uppercut"]},
    {"id": "sessizgolge", "name": "SESSİZ GÖLGE", "hp": 95, "speed": 300.0,
     "info": "Konuşmaz",
     "story": "Onu duydum diyenler aslında kendi seslerini duydu.",
     "abilities": ["spin", "tackle", "headbutt"]},
    {"id": "karagolge", "name": "KARA GÖLGE", "hp": 120, "speed": 290.0,
     "info": "Karanlığın kendisi",
     "story": "Karanlık onu korurdu; karanlık olmadan da dururdu.",
     "abilities": ["smash", "spin", "uppercut"]},
    {"id": "obsgolge", "name": "OBSİDYEN GÖLGE", "hp": 145, "speed": 275.0,
     "info": "Sert gölge",
     "story": "Gölgeye taş karışmış; taş da gölgeye.",
     "abilities": ["smash", "stomp", "tackle"]},
    {"id": "eldasgolge", "name": "ELMAS GÖLGE", "hp": 140, "speed": 300.0,
     "info": "Parlayan boşluk",
     "story": "Işık ondan yansıyordu ama o ışığın kaynağı değildi.",
     "abilities": ["smash", "spin", "kick"]},

    {"id": "blaze", "name": "BLAZE", "hp": 90, "speed": 290.0,
     "info": "Ateş topu",
     "story": "Oyuncuyu değil gölgeyi hedef alırdı; gölge de yeterliydi.",
     "abilities": ["kick", "bite", "spin"]},
    {"id": "lavefendisi", "name": "LAV EFENDİSİ", "hp": 135, "speed": 265.0,
     "info": "Yanan taç",
     "story": "Taç eridi; taç yanan taç oldu.",
     "abilities": ["smash", "uppercut", "tackle"]},
    {"id": "atessovalye", "name": "ATEŞ ŞÖVALYESİ", "hp": 130, "speed": 255.0,
     "info": "Kül zırhı",
     "story": "Zırhı kül; külü zırh.",
     "abilities": ["smash", "combo", "uppercut"]},
    {"id": "ejderha", "name": "EJDERHA", "hp": 160, "speed": 280.0,
     "info": "Kanatlı gölge",
     "story": "Kanatları gölge; gölgesi kanatlı.",
     "abilities": ["smash", "tackle", "combo"]},
    {"id": "ateisizi", "name": "ATEŞ İKİZİ", "hp": 105, "speed": 300.0,
     "info": "İki alev",
     "story": "Biri hızlıydı, diğeri güçlü; ikisi asla ayrılmadı.",
     "abilities": ["spin", "uppercut", "kick"]},
    {"id": "kulruhu", "name": "KÜL RUHU", "hp": 95, "speed": 285.0,
     "info": "Sönmüş kalp",
     "story": "Ateşi sönünce içinde bir şey kalmıştı.",
     "abilities": ["spin", "headbutt", "bite"]},
    {"id": "gunessavas", "name": "GÜNEŞ SAVAŞÇISI", "hp": 135, "speed": 270.0,
     "info": "Gündüz savaşır",
     "story": "Güneş ona güç verir; ama gözlerini de yakar.",
     "abilities": ["uppercut", "combo", "smash"]},
    {"id": "mezarbekci", "name": "MEZAR BEKÇİSİ", "hp": 120, "speed": 260.0,
     "info": "Nöbet tutan",
     "story": "Mezarında yatmak yerine başkasının mezarında nöbet tutar.",
     "abilities": ["smash", "kick", "tackle"]},
    {"id": "alevustasi", "name": "ALEV USTASI", "hp": 130, "speed": 275.0,
     "info": "Ateşin ustası",
     "story": "Ateşi söndürmez; yön verirdi.",
     "abilities": ["uppercut", "spin", "smash"]},
    {"id": "obsejderha", "name": "OBSİDYEN EJDERHA", "hp": 175, "speed": 250.0,
     "info": "Dikenli taç",
     "story": "Kanatları obsidyen; en yaklaşanı önce hissederdi.",
     "abilities": ["smash", "stomp", "tackle"]},
    {"id": "eldasejderha", "name": "ELDAS EJDERHA", "hp": 170, "speed": 265.0,
     "info": "Işık sırtı",
     "story": "Sırtındaki ışık yüzünden uykusunda bile uyarılırdı.",
     "abilities": ["smash", "combo", "tackle"]},
    {"id": "cehennem", "name": "CEHENNEM KAPI", "hp": 150, "speed": 240.0,
     "info": "Kapının ağzı",
     "story": "Açanı içeri alır; içeri alınanı geri göndermez.",
     "abilities": ["smash", "tackle", "uppercut"]},

    {"id": "kurt", "name": "KURT", "hp": 95, "speed": 310.0,
     "info": "Sürünün başı",
     "story": "Sürüyü korurken kimse onun korktuğunu görmedi.",
     "abilities": ["bite", "kick", "tackle"]},
    {"id": "kartal", "name": "KARTAL", "hp": 90, "speed": 330.0,
     "info": "Yüksekten avcı",
     "story": "Yukarıdan bakınca herkes küçük görünürdü.",
     "abilities": ["spin", "bite", "smash"]},
    {"id": "kaplan", "name": "KAPLAN", "hp": 130, "speed": 300.0,
     "info": "Çizgili cesaret",
     "story": "Korktuğunu asla göstermedi; gösterdiği tek şey çizgileriydi.",
     "abilities": ["smash", "tackle", "bite"]},
    {"id": "ayi", "name": "AYI", "hp": 145, "speed": 235.0,
     "info": "Ağır ama hızlı",
     "story": "Yavaş başlar; koşmaya başlayınca durmazdı.",
     "abilities": ["smash", "uppercut", "stomp"]},
    {"id": "tilki", "name": "TILKI", "hp": 85, "speed": 325.0,
     "info": "Tuzakçı",
     "story": "Kurnazlığıyla avını yordu; sonra gözlerini indirdi.",
     "abilities": ["bite", "spin", "punch"]},
    {"id": "koyun", "name": "KOYUN", "hp": 120, "speed": 230.0,
     "info": "Kalın yün",
     "story": "Yünü kalın olduğu için tokat yemezdi; tokat yiyen yündü.",
     "abilities": ["headbutt", "kick", "stomp"]},
    {"id": "domuz", "name": "DOMUZ", "hp": 125, "speed": 265.0,
     "info": "Kör öfke",
     "story": "Görüşü zayıf; öfkesi görmüyordu, o da öfkeyi.",
     "abilities": ["smash", "tackle", "kick"]},
    {"id": "tavuk", "name": "TAVUK", "hp": 70, "speed": 320.0,
     "info": "Zayıf ama yılmaz",
     "story": "Korkmazdı; korkmayacak kadar güçsüzdü.",
     "abilities": ["kick", "bite", "stomp"]},
    {"id": "balik", "name": "BALIK", "hp": 75, "speed": 300.0,
     "info": "Suyun dışında savunmasız",
     "story": "Suyun dışında geçen tek bir saniye yeterdi.",
     "abilities": ["sweep", "bite", "punch"]},
    {"id": "kuraga", "name": "KURBAĞA", "hp": 90, "speed": 290.0,
     "info": "Zıplatıcı",
     "story": "Dilini bir anda uzatır; sonra yine düşerdi.",
     "abilities": ["bite", "sweep", "uppercut"]},
    {"id": "yilan", "name": "YILAN", "hp": 80, "speed": 295.0,
     "info": "Sarmalayıcı",
     "story": "Sarmaladıktan sonra kendisi de uyuya kalırdı.",
     "abilities": ["bite", "spin", "sweep"]},
    {"id": "kurkadam", "name": "KÜRKDAM", "hp": 145, "speed": 280.0,
     "info": "Gece sıçraması",
     "story": "Ay ışığında insan olurdu; güneşte kendi haline dönerdi.",
     "abilities": ["smash", "tackle", "uppercut"]},
    {"id": "geyik", "name": "GEYİK", "hp": 110, "speed": 300.0,
     "info": "Kaçıcı",
     "story": "Kovalamayı değil kaçmayı severdi; ama arada bir dönerdi.",
     "abilities": ["kick", "punch", "headbutt"]},
    {"id": "panda", "name": "PANDA", "hp": 140, "speed": 245.0,
     "info": "Yeşil güç",
     "story": "Bambu yiyerek yaşar; bir yumruğuyla duvar yıkardı.",
     "abilities": ["smash", "sweep", "uppercut"]},
    {"id": "aksolotl", "name": "AKSOLOTL", "hp": 95, "speed": 255.0,
     "info": "Su canavarı",
     "story": "Bastonu yüzünden tırmandı; o da kendi kırk bacağını gösterdi.",
     "abilities": ["bite", "spin", "kick"]},
    {"id": "kopek", "name": "KÖPEK", "hp": 105, "speed": 295.0,
     "info": "Sadık",
     "story": "Efendisini bir kez tanır; bir kez tanıyınca bırakmaz.",
     "abilities": ["bite", "kick", "tackle"]},

    {"id": "golem", "name": "GOLEM", "hp": 170, "speed": 210.0,
     "info": "Toprak ve taş",
     "story": "Onu yaptılar, bir amaç için; amaç hiç söylenmedi.",
     "abilities": ["smash", "smash", "stomp"]},
    {"id": "kargolem", "name": "KAR GOLEM", "hp": 150, "speed": 225.0,
     "info": "Kışın kalıntısı",
     "story": "Yılınca yavaşlar; yavaşladıkça daha çok dayanır.",
     "abilities": ["smash", "stomp", "kick"]},
    {"id": "slaim", "name": "SLAİME", "hp": 85, "speed": 290.0,
     "info": "Bölünen",
     "story": "Vurulunca ikiye ayrılır; bu yüzden vurmak işe yaramaz.",
     "abilities": ["spin", "sweep", "bite"]},
    {"id": "magmakup", "name": "MAGMA KÜP", "hp": 100, "speed": 270.0,
     "info": "Ateş yığını",
     "story": "Küçücüktür ama her çarpışmada büyür.",
     "abilities": ["smash", "uppercut", "spin"]},
    {"id": "bekci", "name": "BEKÇİ", "hp": 180, "speed": 260.0,
     "info": "Karanlığın bekçisi",
     "story": "Duymaz, görmez; yalnızca titreşimi bilir. Ve titreşen her şeyi tanır.",
     "abilities": ["smash", "combo", "tackle"]},
]

for _c in CREATURES:
    _c["adesc"] = ["%s: %d hasar" % (ABILITIES[a]["name"], ABILITIES[a]["dmg"])
                   for a in _c["abilities"]]

# ---------- KARAKTERLER (oyuncu seçimi) ----------
# Şu an sadece İNSAN. Yeni karakterler buraya eklenecek.
CHARACTERS = [CREATURES[0]]

CREATURES = CREATURES[1:]

# Seçim ekranı şu an tek karakter gösterir (İNSAN).
# Karakter sayacı ileriye dönük 100 olarak yazılır; yeni karakter eklendiğinde
# CHARACTERS listesine eklemen yeterli.
ROSTER_TOTAL = 100


def _build_roster():
    import savegame
    return savegame.locked_roster()


ROSTER = _build_roster()

# Yaratıklar görsel/aile grubuna göre sınıflanır; çizim ve davranış bu gruba bakar.
CREATURE_FAMILIES = {
    "insan": ["madenci", "asker", "muhafiz", "paladin", "korsan", "ninja", "avci",
              "buyucu", "kahin", "gezgin", "sovalye", "okcu", "dovuscu", "kilic",
              "yeralti", "tuccar", "rehber", "kasif", "kral"],
    "zombi": ["zombi", "zefirzombi", "isikzombi", "suzombi", "kumzombi", "buzzombi",
              "kayazombi", "obszombi", "eldaszombi", "altinzombi", "koyuzombi",
              "balikzombi", "patronzombi", "kralice", "kabuszombi"],
    "creeper": ["creeper", "yildirim", "lavcreeper", "buzcreeper", "sucreeper",
                "tntcreeper", "kralcreeper", "kumcreeper", "kizilcreeper",
                "golgecreeper"],
    "örümcek": ["orumcek", "zehirli", "devorumcek", "golgeorumcek", "agustasi",
                "karorumcek", "kizilorumcek", "tavanorumcek", "anaorumcek",
                "ucanorumcek"],
    "enderman": ["enderman", "bassiz", "golgesavas", "bosluk", "morhayalet",
                 "golgekrali", "gecegolge", "izigolge", "sessizgolge", "karagolge",
                 "obsgolge", "eldasgolge"],
    "blaze": ["blaze", "lavefendisi", "atessovalye", "ejderha", "ateisizi",
              "kulruhu", "gunessavas", "mezarbekci", "alevustasi", "obsejderha",
              "eldasejderha", "cehennem"],
    "özel": ["golem", "kargolem", "slaim", "magmakup", "bekci"],
}
CREATURE_BY_ID = {c["id"]: c for c in CREATURES}
for _fam, _ids in CREATURE_FAMILIES.items():
    for _cid in _ids:
        if _cid in CREATURE_BY_ID:
            CREATURE_BY_ID[_cid]["family"] = _fam
CREATURE_FAMILIES["hayvan"] = [c["id"] for c in CREATURES
                                if "family" not in c]
for _cid in CREATURE_FAMILIES["hayvan"]:
    CREATURE_BY_ID[_cid]["family"] = "hayvan"

CREATURE_COLORS = {
    "zombi": (96, 148, 74),
    "creeper": (120, 205, 90),
    "örümcek": (58, 38, 48),
    "enderman": (46, 36, 62),
    "blaze": (240, 150, 40),
    "hayvan": (150, 120, 80),
    "insan": (200, 190, 170),
    "özel": (140, 140, 155),
}

MOB_COLORS = CREATURE_COLORS

for _c in CREATURES:
    _c["color"] = CREATURE_COLORS[_c["family"]]
    _c["mscale"] = round(0.85 + (_c["hp"] - 60) / 260.0, 2)
    _c["mob_hp"] = max(6.0, _c["hp"] * 0.34)
    _c["mob_speed"] = max(40.0, _c["speed"] * 0.32)
    _c["mob_dmg"] = round(max(1.0, _c["hp"] * 0.09), 1)

MOB_CONTACT_DMG_MAP.update({c["id"]: c["mob_dmg"] for c in CREATURES})
MOB_STATS.update({c["id"]: (c["mob_hp"], c["mob_speed"]) for c in CREATURES})
MOB_DROPS.update({c["id"]: ("et" if c["family"] in ("zombi", "hayvan") else None)
                  for c in CREATURES})

MAPS = [
    {"id": "grass", "name": "GRASS", "disp": "ÇİM"},
    {"id": "village", "name": "VILLAGE", "disp": "KÖY"},
    {"id": "city", "name": "CITY", "disp": "ŞEHİR"},
    {"id": "trucks", "name": "TRUCKS", "disp": "KAMYON"},
    {"id": "minestick", "name": "MINESTICK", "disp": "MİNECRAFT"},
    {"id": "house", "name": "HOUSE", "disp": "EV"},
    {"id": "johnny", "name": "JOHNNY", "disp": "JOHNNY"},
    {"id": "zombi", "name": "ZOMBİ SURVIVAL", "disp": "ZOMBİ"},
    {"id": "football", "name": "FUTBOL", "disp": "FUTBOL"},
    {"id": "laserrun", "name": "LAZER RUN", "disp": "LAZER"},
    {"id": "boss", "name": "BOSS FIGHTS", "disp": "BOSS"},
]

# ---------- ZOMBİ SURVIVAL ----------
ZOMBIE_WAVES = 12
ZOMBIE_SPAWN_XS = (60, 940)
# Dalgalar sınırsızdır: ilk 8 dalga elle yazılmıştır, sonrası güçlenerek tekrarlar.
ZOMBIE_WAVE_PLAN = {
    1: [("zombi", 3)],
    2: [("zombi", 4), ("orumcek", 1)],
    3: [("zombi", 4), ("orumcek", 2), ("creeper", 1)],
    4: [("zombi", 3), ("orumcek", 2), ("creeper", 1), ("kurt", 1)],
    5: [("zombi", 3), ("orumcek", 2), ("creeper", 2), ("enderman", 1),
        ("kaplan", 1)],
    6: [("isikzombi", 2), ("zombi", 2), ("zehirli", 2), ("kizilcreeper", 1),
        ("devorumcek", 1)],
    7: [("eldaszombi", 1), ("zombi", 2), ("anaorumcek", 1), ("agustasi", 1),
        ("golgeorumcek", 1), ("kizilorumcek", 2), ("tntcreeper", 1)],
    8: [("blaze", 2), ("zombi", 2), ("orumcek", 2), ("creeper", 1),
        ("morhayalet", 1), ("karagolge", 1)],
    9: [("kayazombi", 1), ("obsgolge", 1), ("eldasgolge", 1),
        ("lavcreeper", 2), ("ucanorumcek", 2), ("slaim", 2), ("golem", 1)],
    10: [("ejderha", 1), ("magmakup", 2), ("bekci", 1), ("tavanorumcek", 2),
         ("golgecreeper", 2), ("kabuszombi", 2)],
    11: [("obsejderha", 1), ("eldasejderha", 1), ("cehennem", 1), ("kurkadam", 2),
         ("devorumcek", 2), ("anaorumcek", 1)],
    12: [("altinzombi", 2), ("obszombi", 2), ("kralcreeper", 2), ("kralice", 1),
         ("sessizgolge", 1), ("golgekrali", 1)],
}
# Sonsuz dalga için güç çarpanları (üstel tırmanış + yumuşak tavan)
ZOMBIE_CYCLE_COUNT = len(ZOMBIE_WAVE_PLAN)
ZOMBIE_HP_CAP = 6.0
ZOMBIE_SPEED_CAP = 2.2
ZOMBIE_COUNT_CAP = 4

# ---------- FUTBOL ----------
FOOT_GOAL_SCORE = 3
FOOT_BALL_R = 16
FOOT_KICK_SPEED = 520.0
FOOT_LOFT_SPEED = 660.0
FOOT_LOFT_FWD = 130.0
FOOT_GRAVITY = 1500.0
FOOT_BOUNCE = 0.55
FOOT_DRIBBLE = 150.0
FOOT_ARENA_LEFT = 40
FOOT_ARENA_RIGHT = 960
FOOT_ZOOM = 0.55

# ---------- LAZER RUN ----------
LR_BLOCK_W = 40
LR_BLOCK_H = 40
LR_BLOCK_SPEED = 180.0
LR_SPAWN_INTERVAL = 1.2
LR_BLOCK_DMG = 15.0
LR_LASER_DMG = 40.0
LR_PLATFORM_Y = None  # set at runtime
LR_ZOOM = 0.65

# ---------- BOSS FIGHTS (100 boss, 20 tier x 5 tema) ----------
# Her boss türünün kendi temasına özel gücü vardır:
#   zombi -> çamur topu fırlatır, örümcek -> zehirli ağ atar, creeper -> dikit,
#   enderman -> ışınlanır, blaze -> lav püskürtür
STALAGMITE_DMG = 10.0
BOSS_POWER_TIME = 3.5
STALAGMITE_GROW = 0.55
STALAGMITE_END = 1.6
STALAGMITE_LIFE = 2.0
BOSS_POWER_NAMES = {
    "zombi": "ÇAMUR TOPU!",
    "örümcek": "ZEHİRLİ AĞ!",
    "creeper": "DİKİT!",
    "enderman": "IŞINLANMA!",
    "blaze": "LAV PÜSKÜRTME!",
}
BOSS_MUD_SPEED = 380.0
BOSS_MUD_DMG = 12.0
BOSS_WEB_DMG = 6.0
BOSS_WEB_LIFE = 3.0
BOSS_TELE_DMG = 14.0
BOSS_LAVA_DMG = 18.0
BOSS_LAVA_RANGE = 130.0
# 5 tema türü; her biri 20 boss'luk isim havuzuna sahip (toplam 100 boss)
BOSS_KINDS = ["zombi", "örümcek", "creeper", "enderman", "blaze"]
BOSS_TIER_COUNT = 20

BOSS_STYLE_NAMES = {
    "zombi": ["ÇAMUR ZOMBİ", "CESUR ASKER", "KRİSTAL KORUYUCUSU", "GÖMÜK ZOMBİ",
              "ELMAS ZOMBİ", "ALTIN ZOMBİ", "KIZILTAŞ ZOMBİ", "BOĞUK ZOMBİ",
              "DERİ ZOMBİ", "KÜL ZOMBİ", "YOSUNLU ZOMBİ", "ZEYTİNLİK ZOMBİ",
              "OBSİDYEN ZOMBİ", "ZEHİR ZOMBİ", "KAHRAMAN ZOMBİ", "DEV ZOMBİ",
              "ÇÜRÜK KRAL", "KAOS ZOMBİSİ", "SON ZOMBİ", "KARA CUMHAYRI"],
    "örümcek": ["ÖRÜMCEK KRALİÇE", "DEMİR GÖLGE", "MADEN CASUSU", "KARA ÖRÜMCEK",
                "ZEHİRLİ ÖRÜMCEK", "BOĞAN ÖRÜMCEK", "AĞ USTASI", "TAŞ ÖRÜMCEK",
                "ALTIN ÖRÜMCEK", "ELMAS ÖRÜMCEK", "DEV ÖRÜMCEK", "KIZIL ÖRÜMCEK",
                "GÖLGE AĞI", "KUM ÖRÜMCEĞİ", "YANAN ÖRÜMCEK", "BUZ ÖRÜMCEĞİ",
                "TİPİ ÖRÜMCEK", "YOLKUZ ÖRÜMCEK", "ANA KUYU", "SON AĞ"],
    "creeper": ["TAS GOLİAT", "AĞ DEVİ", "CEHENNEM ŞEFİ", "PATLAYICI",
                "YOSUNLU GOLİAT", "TAVAN TAŞI", "BAZALTAŞ BEY", "KIZILTAŞ ŞAH",
                "GÖKTAŞ YAMAN", "AY TAŞI", "YOSUN TAŞI", "VOLKAN TAŞI",
                "BUZUL DİKİT", "MİNERAR ŞAHIN", "SAPAN TAŞI", "ANCIKAYA",
                "SON TAŞ", "DEVRİLEN TAŞ", "DÜNYANIN TAŞI", "KAHRAMAN DİKİT"],
    "enderman": ["GÖLGE AVCISI", "BLAZE EFENDİSİ", "HAYALET KRAL", "MOR GÖLGE",
                 "BOŞLUK GÖLGE", "İKİZ GÖLGE", "GECEYİN GÖLGE", "SESSİZ GÖLGE",
                 "KÖR GÖLGE", "ÇADIR GÖLGE", "DÖVÜŞÇÜ GÖLGE", "KAÇAK GÖLGE",
                 "ZÜMRÜD GÖLGE", "ELMAS GÖLGE", "OBSİDYEN GÖLGE", "KIZIL GÖLGE",
                 "SONSUZ GÖLGE", "HİÇLİK GÖLGE", "GÖLGE KRALLIĞI", "KARANLIK EFENDİSİ"],
    "blaze": ["LAV ÖFKEYİ", "ENDER SAVAŞÇISI", "EJDERHA LORDU", "ATEŞ TOPU",
              "KIZIL ATEŞ", "ALTIN ALEV", "ELMAS ALEV", "OBSİDYEN ALEV",
              "KÜL ATEŞİ", "GÜNEŞ ATEŞİ", "BİLİM ATEŞİ", "MEZAR ATEŞİ",
              "İKİ ALEV", "DEV ALEV", "EJDERHA YAVRUSU", "YANIK EJDERHA",
              "KIZGIN EJDERHA", "ATEŞ BULUTU", "VATAN ALEVİ", "EJDERHA KRALI"],
}

# tema başına temel renk; tier'a göre 5 kademede açılıp koyulaşır
BOSS_TINT = {
    "zombi": (96, 148, 74),
    "örümcek": (58, 38, 48),
    "creeper": (128, 122, 132),
    "enderman": (70, 54, 90),
    "blaze": (240, 150, 40),
}

BOSS_NAMES = [BOSS_STYLE_NAMES[k][i // 5] for i, k in enumerate(
    [BOSS_KINDS[i % 5] for i in range(100)])]
BOSS_COLORS = []
for _i in range(100):
    _k = BOSS_KINDS[_i % 5]
    _sh = ((((_i // 5) + 2) % 5) - 2) * 16
    BOSS_COLORS.append(tuple(max(0, min(255, c + _sh)) for c in BOSS_TINT[_k]))


def boss_hp(i):
    """İlk 15 boss eski dengede; sonrası kademeli artar."""
    if i <= 14:
        return 180.0 + i * 45.0
    return 810.0 + (i - 15) * 12.0


def boss_speed(i):
    if i <= 14:
        return 70.0 + i * 3.0
    return 112.0 + (i - 15) * 0.35


def boss_dmg(i):
    if i <= 14:
        return 8.0 + i * 0.4
    return 13.6 + (i - 15) * 0.05


def make_bosses():
    """100 boss = 20 tier x 5 tema. İlk 15 eski ayarda, sonrası kademeli."""
    out = []
    for i in range(100):
        kind = BOSS_KINDS[i % 5]
        tier = i // 5
        out.append({
            "i": i,
            "name": BOSS_STYLE_NAMES[kind][tier],
            "hp": boss_hp(i),                # 180 -> 1818
            "speed": boss_speed(i),          # 70 -> 141
            "dmg": boss_dmg(i),              # 8 -> 17.8
            "kind": kind,
            "color": BOSS_COLORS[i],
            "size": 1.2 + (i % 5) * 0.14,     # 1.20 -> 1.76
            "tier": tier,
        })
    return out


BOSSES = make_bosses()

VILLAGER_COLORS = [(124, 138, 62), (146, 108, 62), (198, 178, 132), (122, 128, 140),
                   (168, 96, 56)]

P1_COLOR = (25, 25, 25)
P2_COLOR = (170, 45, 45)
COLOR_PRESETS = [(25, 25, 25), (190, 40, 40), (40, 90, 200), (40, 170, 60),
                 (150, 70, 200), (230, 120, 30), (40, 180, 190), (230, 70, 150),
                 (90, 90, 100), (255, 40, 40), (90, 160, 255), (140, 230, 60),
                 (200, 120, 255), (255, 180, 30), (120, 240, 240), (255, 170, 220)]
GOLD = (255, 200, 40)

SKY = (135, 206, 235)
CLOUD = (255, 255, 255)
GRASS_TOP = (114, 196, 74)
GRASS_DARK = (96, 174, 62)
GRASS_BOTTOM = (84, 158, 56)

_fonts = {}


def get_font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(FONT_NAME, size, bold=bold)
    return _fonts[key]


def draw_text(surface, text, size, color, center, bold=True, align="center"):
    img = get_font(size, bold).render(text, True, color)
    if align == "left":
        rect = img.get_rect(midleft=center)
    elif align == "right":
        rect = img.get_rect(midright=center)
    else:
        rect = img.get_rect(center=center)
    surface.blit(img, rect)
    return rect


def blend(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


_TOUCH_POS = [0, 0]


def set_touch_pos(pos):
    """Dokunma noktasini hatirlar (mobilde fare surucusu yok)."""
    _TOUCH_POS[0] = int(pos[0])
    _TOUCH_POS[1] = int(pos[1])
    try:
        pygame.mouse.set_pos(pos)
    except Exception:
        pass


def clear_touch_pos():
    _TOUCH_POS[0] = _TOUCH_POS[1] = 0


LOGICAL_SURFACE = None


def set_logical_surface(surf):
    """Cizim yuzeyini sabitler (mobilde ekran olcegi degisebilir)."""
    global LOGICAL_SURFACE
    LOGICAL_SURFACE = surf


def logical_pos(pos=None):
    if pos is None:
        if MOBILE and _TOUCH_POS != [0, 0]:
            pos = (_TOUCH_POS[0], _TOUCH_POS[1])
        else:
            pos = pygame.mouse.get_pos()
    x, y = pos
    s = LOGICAL_SURFACE or pygame.display.get_surface()
    if s is None:
        return (int(x), int(y))
    sw, sh = s.get_size()
    k = min(sw / SCREEN_W, sh / SCREEN_H)
    w, h = SCREEN_W * k, SCREEN_H * k
    offx = (sw - w) / 2.0
    offy = (sh - h) / 2.0
    return (int((x - offx) / k), int((y - offy) / k))


def wrap_text(text, limit):
    """Metni verilen karakter sinirina gore satirlara boler."""
    words = str(text).split()
    lines = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = w if not cur else cur + " " + w
    if cur:
        lines.append(cur)
    return lines


def load_cover_from(img, w, h, top_bias=0.30):
    """Yuklenmis bir gorseli hedef cerceveye kirparak sigdirir."""
    import pygame
    iw, ih = img.get_width(), img.get_height()
    k = max(w / iw, h / ih)
    nw = max(w, int(iw * k + 0.5))
    nh = max(h, int(ih * k + 0.5))
    img = pygame.transform.smoothscale(img, (nw, nh))
    return img.subsurface(pygame.Rect((nw - w) // 2, int((nh - h) * top_bias),
                                      w, h)).copy()


def python_no_window():
    """Konsol penceresi acmayan Python yorumlayicisini verir (pythonw.exe).

    Terminal (siyah ekran) gorunmesin diye kullanilir.
    """
    import os
    import sys
    exe = sys.executable or "python"
    cand = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.isfile(cand):
        return cand
    return exe


def game_cover_path():
    """Oyun kapak/ikon gorselini bulur; en buyuk dosya secilir.

    Dosya adi onemli degildir: kapak.png, kapak.jpg, oyun_ikon.jpg vb.
    (Windows bazen uzantiyi iki kez ekler, o durum da yakalanir.)
    """
    import os
    names = ("kapak.png", "kapak.jpg", "kapak.jpeg", "oyun_ikon.jpg",
             "oyun_ikon.jpeg", "oyun_ikon.png", "oyun_ikon_512.png",
             "kapak.png.png")
    base = os.path.dirname(os.path.abspath(__file__))
    cands = []
    for nm in names:
        fp = os.path.join(base, nm)
        if os.path.isfile(fp):
            cands.append((os.path.getsize(fp), fp))
    if not cands:
        return None
    cands.sort(reverse=True)
    return cands[0][1]


_cover_cache = {}


def load_cover(w, h, square=False, top_bias=0.30):
    """Kapak gorselini hedef boyutta dondurur (kirparak, yaymaz)."""
    key = (w, h, square)
    if key in _cover_cache:
        return _cover_cache[key]
    out = None
    fp = game_cover_path()
    if fp:
        try:
            import pygame
            img = pygame.image.load(fp)
            iw, ih = img.get_width(), img.get_height()
            if square:
                side = min(iw, ih)
                img = img.subsurface(pygame.Rect((iw - side) // 2,
                                                 int((ih - side) * top_bias),
                                                 side, side))
                out = pygame.transform.smoothscale(img, (w, h))
            else:
                k = max(w / iw, h / ih)
                nw = max(w, int(iw * k + 0.5))
                nh = max(h, int(ih * k + 0.5))
                img = pygame.transform.smoothscale(img, (nw, nh))
                out = img.subsurface(pygame.Rect((nw - w) // 2,
                                                 int((nh - h) * top_bias),
                                                 w, h)).copy()
        except Exception:
            out = None
    _cover_cache[key] = out
    return out


def make_bg(w, h, top, bottom):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        pygame.draw.line(s, blend(top, bottom, t), (0, y), (w, y))
    return s