"""Masaustu kisayolu icin ikon uretir: en buyuk kapak gorselinden kare kirpar."""
import os
import pygame

pygame.init()
BASE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("kapak.png", "kapak.jpg", "kapak.jpeg", "oyun_ikon.jpg",
         "oyun_ikon.jpeg", "oyun_ikon.png")


def best_cover():
    cands = []
    for nm in NAMES:
        fp = os.path.join(BASE, nm)
        if os.path.isfile(fp):
            cands.append((os.path.getsize(fp), fp))
    cands.sort(reverse=True)
    for _sz, fp in cands:
        try:
            img = pygame.image.load(fp)
        except Exception:
            continue
        if img.get_width() >= 200 and img.get_height() >= 100:
            return img, fp
    return None, None


def square(img, size, top_bias=0.34):
    iw, ih = img.get_width(), img.get_height()
    side = min(iw, ih)
    x = (iw - side) // 2
    y = int((ih - side) * top_bias)
    sub = img.subsurface(pygame.Rect(x, y, side, side))
    return pygame.transform.smoothscale(sub, (size, size))


def rounded(img, radius_ratio=0.16):
    w, h = img.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(img, (0, 0))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=int(min(w, h) * radius_ratio))
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


if __name__ == "__main__":
    img, src = best_cover()
    if img is None:
        print("kapak gorseli bulunamadi, ikon uretilmedi")
    else:
        ic = square(img, 256)
        pygame.image.save(ic, os.path.join(BASE, "oyun_ikon.png"))
        ic512 = square(img, 512)
        pygame.image.save(ic512, os.path.join(BASE, "oyun_ikon_512.png"))
        print("ikon uretildi: oyun_ikon.png (256), oyun_ikon_512.png (512)")
        print("kaynak:", os.path.basename(src))