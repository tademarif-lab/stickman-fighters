"""Masaustu kisayolu icin gercek .ico dosyasi uretir (BMP/DIB tabanli).

PNG'nin ICO'ya gomulmesi Windows'ta calisir ama bazi cozuculerde bozulur;
bu yuzden klasik BMP (DIB) formatinda yazilir: her boyutta kesin calisir.
"""
import os
import struct

import pygame

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = ("oyun_ikon_512.png", "oyun_ikon.png", "kapak.png", "kapak.jpg",
       "oyun_ikon.jpg")
SIZES = (256, 128, 64, 48, 32, 16)


def pick_source():
    for nm in SRC:
        fp = os.path.join(BASE, nm)
        if os.path.isfile(fp):
            try:
                return pygame.image.load(fp), fp
            except Exception:
                continue
    return None, None


def square_image(size):
    img = pygame.Surface((size, size), pygame.SRCALPHA)
    src, _fp = pick_source()
    if src is None:
        img.fill((40, 48, 70, 255))
        return img
    iw, ih = src.get_width(), src.get_height()
    side = min(iw, ih)
    crop = src.subsurface(pygame.Rect((iw - side) // 2,
                                      int((ih - side) * 0.30), side, side))
    img.blit(pygame.transform.smoothscale(crop, (size, size)), (0, 0))
    return img


def dib_bytes(size):
    """Tek boyut icin BMP/DIB verisi (XOR + AND maskesi)."""
    img = square_image(size)
    w = h = size
    xor = bytearray()
    for y in range(h - 1, -1, -1):
        for x in range(w):
            r, g, b, a = img.get_at((x, y))
            xor += bytes((b, g, r, a))
    row_bytes = ((w + 31) // 32) * 4
    and_mask = bytes(row_bytes * h)
    header = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0,
                         len(xor) + len(and_mask), 0, 0, 0, 0)
    return header + bytes(xor) + and_mask


def build_ico(path):
    blobs = [(s, dib_bytes(s)) for s in SIZES]
    n = len(blobs)
    offset = 6 + 16 * n
    entries = b""
    data = b""
    for size, blob in blobs:
        w = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(blob), offset)
        data += blob
        offset += len(blob)
    with open(path, "wb") as f:
        f.write(struct.pack("<HHH", 0, 1, n) + entries + data)
    return path


if __name__ == "__main__":
    src, fp = pick_source()
    print("kaynak:", os.path.basename(fp) if fp else "-")
    p = build_ico(os.path.join(BASE, "oyun_ikon.ico"))
    print("uretildi:", os.path.basename(p), os.path.getsize(p), "bayt")
    print("boyutlar:", ", ".join(str(s) for s in SIZES), "(BMP/DIB)")