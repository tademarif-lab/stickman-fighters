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
"""
import os

from pythonforandroid.recipes import python3 as _upstream
from pythonforandroid.recipes.python3 import Python3Recipe as _Upstream

# p4a'nin gomulu tarif dizini (yamalar burada)
_UPSTREAM_DIR = os.path.dirname(os.path.abspath(_upstream.__file__))


class Python3Recipe(_Upstream):
    version = '3.10.14'

    url = ('https://github.com/python/cpython/archive/'
           'refs/tags/v{version}.tar.gz')

    def get_recipe_dir(self):
        """p4a'nin kendi tarif dizinini dondur.

        `--local-recipes` verildiginde p4a once YEREL dizini arar; orada
        p4a'nin surume gore ekledigi yamalar (patches/py3.8.1.patch,
        patches/cpython-311-ctypes-find-library.patch) yok. Bu yuzden
        orijinal dizini gosteriyoruz.
        """
        return _UPSTREAM_DIR


recipe = Python3Recipe()
