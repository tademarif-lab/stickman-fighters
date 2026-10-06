# -*- coding: utf-8 -*-
"""p4a icin yerel hostpython3 tarifi: surumu 3.10'a sabitler.

NEDEN GEREKIYOR?
----------------
p4a, hedef `python3` tarifi ile `hostpython3` tarifinin surumlerinin
AYNI olmasini zorunlu tutuyor:

    [ERROR] Build failed: python3 should have same version as
           hostpython3, 3.10.14 != 3.14.2

Yani python3'i 3.10'a cekince hostpython3 de 3.10 olmali.
"""
import os

from pythonforandroid.recipes import hostpython3 as _upstream
from pythonforandroid.recipes.hostpython3 import HostPython3Recipe as _Upstream

# p4a'nin gomulu tarif dizini (fix_ensurepip.patch burada)
_UPSTREAM_DIR = os.path.dirname(os.path.abspath(_upstream.__file__))


class HostPython3Recipe(_Upstream):
    version = '3.10.14'

    url = ('https://github.com/python/cpython/archive/'
           'refs/tags/v{version}.tar.gz')

    def get_recipe_dir(self):
        """p4a'nın kendi tarif dizinini dondur (fix_ensurepip.patch burada)."""
        return _UPSTREAM_DIR


recipe = HostPython3Recipe()
