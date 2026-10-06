# -*- coding: utf-8 -*-
"""p4a icin yerel hostpython3 tarifi: surumu 3.10'a sabitler.

NEDEN GEREKIYOR?
----------------
p4a, hedef `python3` tarifi ile `hostpython3` tarifinin surumlerinin
AYNI olmasini zorunlu tutuyor:

    [ERROR] Build failed: python3 should have same version as
           hostpython3, 3.10.14 != 3.14.2

Yani python3'i 3.10'a cekince hostpython3 de 3.10 olmali.
Bunu yapmazsa derleme daha ilk adimda (1 dakika) hata verir.
"""
import os

from pythonforandroid.recipes import hostpython3 as _upstream
from pythonforandroid.recipes.hostpython3 import HostPython3Recipe as _Upstream


class HostPython3Recipe(_Upstream):
    version = '3.10.14'

    url = ('https://github.com/python/cpython/archive/'
           'refs/tags/v{version}.tar.gz')

    def apply_patches(self, arch, build_dir=None):
        # p4a'nin kendi yamalari (fix_ensurepip.patch) yerel tarif
        # dizininde yok; orijinal dizini kullan.
        yedek = self.recipe_dir
        self.recipe_dir = os.path.dirname(os.path.abspath(
            _upstream.__file__))
        try:
            super().apply_patches(arch, build_dir)
        finally:
            self.recipe_dir = yedek


recipe = HostPython3Recipe()
