# -*- coding: utf-8 -*-
"""p4a icin yerel python3 tarifi: surumu 3.10'a sabitler.

NEDEN GEREKIYOR?
----------------
p4a'nin varsayilan python3 tarifi Python 3.14.2 kuruyor.
Ancak p4a'daki pygame tarifi pygame 2.1.0 derliyor ve onun
C kodu Python 3.12+'da derlenemiyor:

    src_c/_sdl2/sdl2.c:211:12: fatal error: 'longintrepr.h' file not found

`longintrepr.h` basligi Python 3.12'de kaldirildi.

3.10.14 iki tarafi da kurtarir:
  - `longintrepr.h` mevcut  -> pygame 2.1.0 derlenir
  - pygame 2.1.0 Python 3.6-3.10 arasini resmen destekliyor

p4a'nin Python3Recipe'i kullanilir; sadece `version` degistirilir.
`apply_patches` surume gore yama ekledigi icim (3.8-3.10 -> py3.8.1.patch)
p4a'nin kendi yamalarini kullanabilmek adina recipe_dir orijinale
geri cevrilir.
"""
import os

from pythonforandroid.recipes import python3 as _upstream
from pythonforandroid.recipes.python3 import Python3Recipe as _Upstream


class Python3Recipe(_Upstream):
    version = '3.10.14'
    url = ('https://github.com/python/cpython/archive/'
           'refs/tags/v{version}.tar.gz')

    def apply_patches(self, arch, build_dir=None):
        # p4a'nin kendi yamalarini kullanabilmek icin recipe_dir'i
        # gomulu (yerel) dizinden orijinal tarif dizinine cevir.
        # aksi halde patches/ klasoru burada olmadigi icin hata verir.
        yedek = self.recipe_dir
        self.recipe_dir = os.path.dirname(os.path.abspath(
            _upstream.__file__))
        try:
            super().apply_patches(arch, build_dir)
        finally:
            self.recipe_dir = yedek


recipe = Python3Recipe()
