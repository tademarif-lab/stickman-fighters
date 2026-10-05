"""KATIL5019 LAUNCHER — proje listesi

Bu dosyaya yeni proje eklemek icin listeye bir sozluk ekle.
    path  : klasor yolu ("" = launcher'in kendi klasoru)
    entry : calistirilacak python dosyasi
    cover : launcher'da gosterilecek kapak gorseli
    icon  : masaustu kisayolunda kullanilan .ico
    info  : (baslik, aciklama) listesi — ekranin altinda gorunur
"""

PROJECTS = [
    {
        "name": "STICKMAN FIGHTERS",
        "path": "",
        "entry": "main.py",
        "cover": "oyun_ikon.jpg",
        "icon": "oyun_ikon.ico",
        "info": [
            ("OYUNUN AMACI", "İki oyuncu arenada çarpışır; son hayatta kalan kazanır."),
            ("KARAKTER", "İNSAN: 100 can, hızlı koşar; yumruk, tekme ve kombosu vurur."),
            ("YARATIKLAR", "Zombi yavaş, örümcek çok hızlı, creeper patlar, enderman ışınlanır."),
            ("BOSS'LAR", "100 boss sırayla gelir; her biri kendi temasına özel gücünü kullanır."),
            ("MODLAR", "Arena, Zombi (sınırsız dalga), Futbol, Lazer Run ve Boss."),
        ],
    },
]