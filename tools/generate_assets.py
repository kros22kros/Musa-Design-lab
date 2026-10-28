"""
MUSA - Generador de universo visual
====================================
Crea, sin bancos de imágenes ni licencias externas, todas las piezas
visuales del sitio: arte editorial, retratos abstractos del equipo,
texturas, imágenes Open Graph y loops de video.

Uso:
    python tools/generate_assets.py

Salida:
    public/media/*.jpg|webp|mp4
    public/og-image.jpg
    public/grain.png
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
MEDIA = OUT / "media"
FONTS = ROOT / "tools" / "fonts"

SERIF = str(FONTS / "CormorantGaramond.ttf")
SERIF_IT = str(FONTS / "CormorantGaramond-Italic.ttf")
SANS = str(FONTS / "Jost.ttf")

# ----------------------------------------------------------------------------
# Paleta
# ----------------------------------------------------------------------------
INK = (20, 16, 13)
WINE_DEEP = (26, 10, 13)
WINE = (59, 18, 24)
CLAY = (168, 85, 58)
CLAY_LIGHT = (196, 120, 92)
GOLD = (176, 138, 87)
GOLD_LIGHT = (214, 186, 146)
IVORY = (243, 236, 225)
CREAM = (250, 246, 239)
SAGE = (108, 120, 104)

RNG = np.random.default_rng(2026)


# ----------------------------------------------------------------------------
# Tipografía
# ----------------------------------------------------------------------------
_font_cache: dict[tuple[str, int, str | None], ImageFont.FreeTypeFont] = {}


def font(path: str, size: int, weight: str | None = None) -> ImageFont.FreeTypeFont:
    key = (path, size, weight)
    if key not in _font_cache:
        f = ImageFont.truetype(path, size)
        if weight:
            try:
                f.set_variation_by_name(weight.encode())
            except Exception:
                pass
        _font_cache[key] = f
    return _font_cache[key]


def text_width(draw: ImageDraw.ImageDraw, text: str, f, tracking: float = 0) -> float:
    return sum(draw.textlength(c, font=f) for c in text) + tracking * max(0, len(text) - 1)


def tracked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    f,
    fill,
    tracking: float = 0,
    align: str = "left",
    anchor: str = "ls",
) -> float:
    """Dibuja texto con letter-spacing. xy = baseline del primer carácter."""
    total = text_width(draw, text, f, tracking)
    x = xy[0]
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    for ch in text:
        draw.text((x, xy[1]), ch, font=f, fill=fill, anchor=anchor)
        x += draw.textlength(ch, font=f) + tracking
    return total


def paragraph(
    draw,
    xy,
    lines: list[str],
    f,
    fill,
    leading: float,
    tracking: float = 0,
    align: str = "left",
):
    x, y = xy
    for line in lines:
        tracked(draw, (x, y), line, f, fill, tracking, align)
        y += leading
    return y


# ----------------------------------------------------------------------------
# Texturas y utilidades
# ----------------------------------------------------------------------------
def smooth_noise(w: int, h: int, cells: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, h // cells + 2), max(2, w // cells + 2))).astype(np.float32)
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return (arr - arr.min()) / max(1e-6, float(np.ptp(arr)))


def paper(w: int, h: int, base=CREAM, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.empty((h, w, 3), np.float32)
    arr[:] = base
    blotch = smooth_noise(w, h, 96, seed) - 0.5
    arr += blotch[..., None] * 5.0
    arr += rng.normal(0, 1.7, (h, w, 1))
    return np.clip(arr, 0, 255)


def vignette(w: int, h: int, strength: float = 0.55, power: float = 2.2) -> np.ndarray:
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r = np.sqrt(nx * nx + ny * ny) / math.sqrt(2)
    v = 1.0 - strength * np.power(np.clip(r, 0, 1), power)
    return v[..., None]


def grain(arr: np.ndarray, amount: float = 4.0, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.clip(arr + rng.normal(0, amount, arr.shape), 0, 255)


def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_map(field: np.ndarray, stops: list[tuple[float, tuple[int, int, int]]]) -> np.ndarray:
    f = np.clip(field, 0, 1)
    out = np.zeros(f.shape + (3,), np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        mask = (f >= p0) & (f <= p1)
        t = (f[mask] - p0) / max(1e-6, p1 - p0)
        for ch in range(3):
            out[..., ch][mask] = c0[ch] + (c1[ch] - c0[ch]) * t
    out[f < stops[0][0]] = stops[0][1]
    out[f > stops[-1][0]] = stops[-1][1]
    return out


def to_image(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def silk_field(w: int, h: int, t: float, scale: float = 1.0) -> np.ndarray:
    """Campo orgánico tipo seda líquida, continuo y repetible."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u = x / w
    v = y / h
    a = np.sin((u * 3.6 * scale + v * 1.4 + t * 0.55) * math.pi)
    b = np.sin((v * 4.4 * scale - u * 2.1 - t * 0.33) * math.pi * 1.27)
    c = np.sin((u * 2.4 - v * 3.7 * scale + t * 0.21) * math.pi * 0.83)
    d = np.sin(np.hypot(u - 0.48, v - 0.42) * 9.5 * scale - t * 1.15)
    e = np.sin((u * 7.5 + v * 6.5 - t * 0.7) * math.pi) * 0.45
    f = a * 0.34 + b * 0.27 + c * 0.18 + d * 0.13 + e * 0.08
    f = (f + 1.0) / 2.0
    return np.clip(f, 0, 1)


def silk_art(w: int, h: int, t: float, dark: bool = True, seed: int = 0) -> np.ndarray:
    field = silk_field(w, h, t)
    fine = silk_field(w, h, t + 0.4, scale=2.1)
    field = np.clip(field * 0.82 + fine * 0.18, 0, 1)

    if dark:
        stops = [
            (0.00, (18, 7, 10)),
            (0.30, WINE),
            (0.52, (92, 34, 30)),
            (0.70, CLAY),
            (0.84, GOLD),
            (0.95, GOLD_LIGHT),
            (1.00, (250, 240, 222)),
        ]
    else:
        stops = [
            (0.00, (122, 54, 36)),
            (0.35, CLAY),
            (0.62, (206, 150, 112)),
            (0.82, GOLD_LIGHT),
            (1.00, IVORY),
        ]
    arr = gradient_map(field, stops)

    # Vetas luminosas
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x / w, y / h
    ribbons = np.zeros((h, w), np.float32)
    for k, (ph, amp, freq) in enumerate([(0.0, 1.0, 2.4), (2.1, 0.55, 3.6), (4.0, 0.3, 5.1)]):
        band = np.sin((v * freq + 0.42 * np.sin(u * 4.1 + t) + ph) * math.pi * 2)
        ribbons += np.exp(-(band ** 2) / 0.26) * amp
    ribbons = np.clip(ribbons / 1.85, 0, 1)
    glow = np.asarray(
        Image.fromarray((ribbons * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)),
        np.float32,
    ) / 255.0
    arr += (ribbons[..., None] * 26 + glow[..., None] * 22) * np.array([1.0, 0.78, 0.58])

    # Vetas finas tipo mármol para dar detalle y profundidad
    veins = np.exp(-((np.sin(field * 24.0 + t * 0.6) ** 2)) / 0.035)
    arr += veins[..., None] * 7 * np.array([1.0, 0.82, 0.62])

    arr *= vignette(w, h, 0.62)
    img = to_image(np.clip(arr, 0, 255))
    img = img.filter(ImageFilter.UnsharpMask(radius=2.2, percent=55, threshold=2))
    return np.asarray(img, np.float32)


def draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill, inner: float = 0.16):
    pts = [
        (cx, cy - r),
        (cx + inner * r, cy - inner * r),
        (cx + r, cy),
        (cx + inner * r, cy + inner * r),
        (cx, cy + r),
        (cx - inner * r, cy + inner * r),
        (cx - r, cy),
        (cx - inner * r, cy - inner * r),
    ]
    draw.polygon(pts, fill=fill)


def arch_mask(size: tuple[int, int], radius: int) -> Image.Image:
    w, h = size
    ss = 2
    m = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=radius * ss, fill=255)
    # base recta: sólo arco superior
    d.rectangle([0, min(h * ss - 1, radius * ss), w * ss, h * ss], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def paste_arch(canvas: Image.Image, art: Image.Image, box, radius: int, outline=None, width=2):
    x, y, w, h = box
    mask = arch_mask((w, h), radius)
    canvas.paste(art.resize((w, h), Image.LANCZOS), (x, y), mask)
    if outline:
        d = ImageDraw.Draw(canvas)
        d.arc([x, y, x + w, y + radius * 2], start=180, end=360, fill=outline, width=width)
        d.line([(x, y + radius), (x, y + h)], fill=outline, width=width)
        d.line([(x + w, y + radius), (x + w, y + h)], fill=outline, width=width)


def sphere(size: tuple[int, int], cx: float, cy: float, r: float, base=WINE, hi=IVORY) -> Image.Image:
    ss = 2
    W = size[0] * ss
    H = size[1] * ss
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    arr = np.zeros((H, W, 4), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - cx * ss) / (r * ss)
    ny = (yy - cy * ss) / (r * ss)
    d2 = nx * nx + ny * ny
    mask = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    lx, ly, lz = -0.45, -0.65, 0.62
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lam = np.clip((nx * lx + ny * ly + nz * lz) / ln, 0, 1)
    spec = np.clip((nx * -0.3 + ny * -0.5 + nz * 0.85) / 1.05, 0, 1) ** 26
    hgt = np.clip(lam, 0, 1) ** 1.55
    for ch in range(3):
        arr[..., ch][mask] = base[ch] + (hi[ch] - base[ch]) * hgt[mask]
        arr[..., ch][mask] += spec[mask] * 55
    arr[..., 3][mask] = 255
    # sombra suave
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    return out.resize((size[0], size[1]), Image.LANCZOS)


def add_grain(img: Image.Image, amount=3.4, seed=1) -> Image.Image:
    arr = np.asarray(img.convert("RGB"), np.float32)
    arr = grain(arr, amount, seed)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


# ----------------------------------------------------------------------------
# Piezas de portafolio
# ----------------------------------------------------------------------------
def poster_silk(w=1200, h=1500) -> Image.Image:
    arr = silk_art(w, h, t=1.35)
    img = to_image(arr)
    d = ImageDraw.Draw(img)

    micro = font(SANS, 22, "Medium")
    micro_s = font(SANS, 18, "Regular")
    tracked(d, (86, 112), "MUSA — UNIVERSO VISUAL", micro, IVORY + (230,), 8)
    tracked(d, (w - 86, 112), "01 / 06", micro, IVORY + (190,), 6, align="right")
    d.line([(86, 148), (w - 86, 148)], fill=IVORY + (70,), width=1)

    draw_star(d, w - 150, 300, 34, GOLD_LIGHT + (235,))

    big = font(SERIF, 118, "Light")
    ital = font(SERIF_IT, 118, "Light")
    tracked(d, (84, 1060), "Donde las ideas", big, IVORY, 1)
    tracked(d, (84, 1182), "encuentran su voz.", ital, (244, 214, 178), 1)

    d.line([(86, 1290), (w - 86, 1290)], fill=IVORY + (70,), width=1)
    tracked(d, (86, 1348), "CREATIVIDAD · ESTRATEGIA · COMUNICACIÓN", micro_s, IVORY + (200,), 5)
    tracked(d, (86, 1400), "Inspiración que convierte ideas en posibilidades.", font(SERIF_IT, 38), IVORY + (170,), 0.5)

    arr = np.asarray(img, np.float32) * vignette(w, h, 0.5)
    return add_grain(to_image(arr), 3.0, 11)


def poster_type(w=1200, h=1500) -> Image.Image:
    arr = paper(w, h, CREAM, 21)
    img = to_image(arr)
    d = ImageDraw.Draw(img)

    # retícula editorial
    for x in (86, 300, w - 86):
        d.line([(x, 300), (x, h - 86)], fill=(20, 16, 13, 22), width=1)
    for y in (86, 300, h - 380, h - 86):
        d.line([(86, y), (w - 86, y)], fill=(20, 16, 13, 22), width=1)

    # bloque terracota
    d.rectangle([820, 150, 1114, 560], fill=CLAY + (255,))
    star = ImageDraw.Draw(img)
    draw_star(star, 967, 300, 42, CREAM)
    tracked(d, (967, 470), "INSPIRACIÓN", font(SANS, 17, "Medium"), CREAM, 6, align="center")

    micro = font(SANS, 22, "Medium")
    tracked(d, (86, 112), "MUSA — ESTUDIO CREATIVO", micro, (30, 24, 20), 8)
    tracked(d, (w - 86, 112), "02 / 06", micro, (30, 24, 20, 160), 6, align="right")

    big = font(SERIF, 372, "Light")
    tracked(d, (72, 900), "MUSA", big, INK, 16)
    tracked(d, (86, 1000), "la musa es la chispa", font(SERIF_IT, 58), (70, 52, 44), 0.5)
    tracked(d, (86, 1072), "que hace posible la idea.", font(SERIF_IT, 58), (70, 52, 44), 0.5)

    d.line([(86, 1160), (1114, 1160)], fill=(20, 16, 13, 90), width=1)
    paragraph(
        d,
        (86, 1235),
        ["Una empresa puede tener un gran producto.", "Lo que a veces falta es la manera de contarlo."],
        font(SERIF, 40),
        (38, 30, 26),
        54,
    )
    tracked(d, (86, 1375), "MUSA = INSPIRACIÓN QUE CONVIERTE IDEAS EN POSIBILIDADES", font(SANS, 15, "Medium"), (90, 72, 60), 4)

    d.rectangle([0, 0, w - 1, h - 1], outline=(20, 16, 13, 40), width=1)
    return add_grain(img, 2.6, 22)


def poster_orb(w=1200, h=1500) -> Image.Image:
    arr = silk_art(w, h, t=3.1)
    arr = np.asarray(to_image(arr), np.float32)
    img = to_image(arr * 0.62)
    d = ImageDraw.Draw(img)

    # órbita
    d.ellipse([190, 470, 1010, 1010], outline=GOLD_LIGHT + (110,), width=2)
    # esfera
    orb = sphere((w, h), 600, 740, 296, base=WINE_DEEP, hi=(206, 166, 118))
    img.paste(orb, (0, 0), orb)
    # brillo
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([420, 560, 780, 920], fill=(214, 186, 146, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    micro = font(SANS, 22, "Medium")
    tracked(d, (86, 112), "MUSA — UNIVERSO VISUAL", micro, IVORY + (225,), 8)
    tracked(d, (w - 86, 112), "03 / 06", micro, IVORY + (170,), 6, align="right")
    d.line([(86, 148), (w - 86, 148)], fill=IVORY + (65,), width=1)

    tracked(d, (600, 205), "SER VISTA", font(SANS, 20, "Medium"), IVORY + (200,), 12, align="center")
    tracked(d, (600, 295), "Ser entendida.", font(SERIF, 92, "Light"), IVORY, 1, align="center")
    tracked(d, (600, 379), "Ser recordada.", font(SERIF_IT, 92, "Light"), (240, 208, 172), 1, align="center")

    draw_star(d, 600, 1140, 22, GOLD_LIGHT + (230,))
    tracked(d, (600, 1220), "Comunicar no es publicar.", font(SERIF, 58), IVORY, 0.5, align="center")
    tracked(d, (600, 1288), "Comunicar es conectar.", font(SERIF_IT, 64), (242, 212, 176), 0.5, align="center")
    tracked(d, (600, 1380), "MUSA — DÓNDE LAS IDEAS ENCUENTRAN SU VOZ", font(SANS, 16, "Medium"), IVORY + (170,), 4, align="center")

    return add_grain(img, 3.6, 33)


def poster_arch(w=1200, h=1500) -> Image.Image:
    arr = paper(w, h, (249, 244, 235), 41)
    img = to_image(arr)
    d = ImageDraw.Draw(img)

    # arco con arte interior
    art = to_image(silk_art(720, 810, t=0.8, dark=False))
    paste_arch(img, art, (240, 160, 720, 810), 360, outline=GOLD + (150,), width=2)

    # arco fino desplazado
    d.arc([200, 120, 1000, 920], start=180, end=360, fill=GOLD + (110,), width=2)
    d.line([(200, 520), (200, 920)], fill=GOLD + (110,), width=2)
    d.line([(1000, 520), (1000, 920)], fill=GOLD + (110,), width=2)

    micro = font(SANS, 22, "Medium")
    tracked(d, (86, 112), "MUSA — PROPÓSITO", micro, (30, 24, 20), 8)
    tracked(d, (w - 86, 112), "04 / 06", micro, (30, 24, 20, 160), 6, align="right")

    tracked(d, (86, 1110), "El puente entre", font(SERIF, 90), INK, 0.5)
    tracked(d, (86, 1200), "la idea y su voz.", font(SERIF_IT, 98), CLAY, 0.5)
    d.line([(86, 1252), (520, 1252)], fill=(20, 16, 13, 120), width=1)
    paragraph(
        d,
        (86, 1308),
        ["Claridad, coherencia y una identidad", "visual cuidada para cada empresa."],
        font(SERIF, 42),
        (52, 42, 36),
        54,
    )
    draw_star(d, 1060, 1330, 22, CLAY + (235,))
    tracked(d, (1114, 1440), "MUSA", font(SANS, 15, "Medium"), (60, 46, 38), 5, align="right")
    d.rectangle([0, 0, w - 1, h - 1], outline=(20, 16, 13, 36), width=1)
    return add_grain(img, 2.4, 44)


def poster_grid(w=1200, h=1500) -> Image.Image:
    arr = paper(w, h, (247, 241, 231), 55)
    img = to_image(arr)
    d = ImageDraw.Draw(img)

    # retícula
    for x in (86, 400, 800, w - 86):
        d.line([(x, 300), (x, h - 86)], fill=(20, 16, 13, 26), width=1)
    for y in (86, 400, 900, h - 86):
        d.line([(86, y), (w - 86, y)], fill=(20, 16, 13, 26), width=1)

    d.rectangle([400, 400, 800, 900], fill=WINE)
    draw_star(d, 600, 650, 62, GOLD_LIGHT)
    d.ellipse([840, 470, 1040, 670], outline=CLAY + (255,), width=3)
    d.ellipse([910, 540, 970, 600], fill=CLAY)

    micro = font(SANS, 22, "Medium")
    tracked(d, (86, 112), "MUSA — ESTRATEGIA", micro, (30, 24, 20), 8)
    tracked(d, (w - 86, 112), "05 / 06", micro, (30, 24, 20, 160), 6, align="right")

    tracked(d, (86, 1020), "Ideas que se vuelven", font(SERIF, 78), INK, 0.5)
    tracked(d, (86, 1100), "posibilidades.", font(SERIF_IT, 100), CLAY, 0.5)
    d.line([(86, 1160), (1114, 1160)], fill=(20, 16, 13, 110), width=1)
    tracked(d, (86, 1230), "CREATIVIDAD  +  ESTRATEGIA  +  COMUNICACIÓN  +  DISEÑO DIGITAL", font(SANS, 16, "Medium"), (60, 46, 38), 4)

    # etiqueta vertical
    vlabel = Image.new("RGBA", (420, 60), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vlabel)
    tracked(vd, (0, 42), "ESTRATEGIA DE CONTENIDO", font(SANS, 16, "Medium"), (60, 46, 38), 5)
    vlabel = vlabel.rotate(90, expand=True)
    img.paste(vlabel, (1046, 420), vlabel)

    d.rectangle([0, 0, w - 1, h - 1], outline=(20, 16, 13, 36), width=1)
    return add_grain(img, 2.6, 55)


def poster_ribbon(w=1200, h=1500) -> Image.Image:
    # fondo terracota profundo
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x / w, y / h
    field = 0.5 + 0.5 * np.sin((u * 2.2 + v * 1.4 + 0.4) * math.pi)
    stops = [(0.0, (72, 24, 22)), (0.45, (140, 62, 46)), (0.78, CLAY), (1.0, (202, 148, 116))]
    arr = gradient_map(field, stops).astype(np.float32)

    # cintas de seda claras
    ribbons = np.zeros((h, w), np.float32)
    for k, (ph, wd, fr) in enumerate([(0.0, 0.010, 2.2), (2.1, 0.014, 3.4), (4.3, 0.020, 1.7)]):
        band = np.sin((v * fr + 0.34 * np.sin(u * 3.2 + ph * 0.2)) * math.pi * 2 + ph)
        ribbons += np.exp(-(band ** 2) / wd) * (0.9 - k * 0.2)
    ribbons = np.clip(ribbons, 0, 1)
    glow = np.asarray(Image.fromarray((ribbons * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)), np.float32) / 255
    arr += (ribbons[..., None] * 70 + glow[..., None] * 45) * np.array([1.0, 0.92, 0.82])
    arr *= vignette(w, h, 0.5)
    img = to_image(arr)
    d = ImageDraw.Draw(img)

    micro = font(SANS, 22, "Medium")
    tracked(d, (86, 112), "MUSA — COMUNICACIÓN", micro, IVORY + (230,), 8)
    tracked(d, (w - 86, 112), "06 / 06", micro, IVORY + (180,), 6, align="right")

    tracked(d, (600, 660), "Comunicar", font(SERIF, 150, "Light"), IVORY, 1, align="center")
    tracked(d, (600, 810), "es conectar.", font(SERIF_IT, 150, "Light"), (250, 222, 186), 1, align="center")
    draw_star(d, 600, 900, 20, GOLD_LIGHT)
    tracked(d, (600, 1000), "Hacer que otra persona entienda, recuerde y confíe.", font(SERIF_IT, 42), IVORY + (215,), 0.5, align="center")
    d.line([(400, 1120), (800, 1120)], fill=IVORY + (90,), width=1)
    tracked(d, (600, 1200), "MUSA", font(SERIF, 72, "Medium"), IVORY, 18, align="center")
    tracked(d, (600, 1280), "DÓNDE LAS IDEAS ENCUENTRAN SU VOZ", font(SANS, 16, "Medium"), IVORY + (190,), 5, align="center")
    return add_grain(img, 3.2, 66)


def team_card(name: str, initials: str, accent, seed: int, file: Path):
    w, h = 1000, 1250
    arr = paper(w, h, (247, 241, 231), seed)
    img = to_image(arr)
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, w - 40, h - 40], outline=(20, 16, 13, 60), width=1)

    tracked(d, (500, 116), "EQUIPO FUNDADOR", font(SANS, 16, "Medium"), (60, 46, 38), 6, align="center")

    # arco con arte interior
    art = to_image(silk_art(560, 690, t=seed * 0.37, dark=False))
    tint = Image.new("RGB", art.size, accent)
    art = Image.blend(art, tint, 0.16)
    paste_arch(img, art, (220, 158, 560, 690), 280, outline=accent + (120,), width=2)

    d = ImageDraw.Draw(img)
    tracked(d, (500, 1010), initials, font(SERIF, 150, "Light"), accent, 8, align="center")
    tracked(d, (500, 1072), "MUSA", font(SANS, 14, "Medium"), (86, 66, 54), 7, align="center")
    d.line([(330, 1118), (670, 1118)], fill=(20, 16, 13, 70), width=1)
    tracked(d, (500, 1168), "CREATIVIDAD · ESTRATEGIA · COMUNICACIÓN", font(SANS, 12, "Medium"), (100, 80, 66), 3, align="center")
    return add_grain(img, 2.6, seed + 100).save(file, quality=92, optimize=True)


# ----------------------------------------------------------------------------
# Video
# ----------------------------------------------------------------------------
def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Instala imageio-ffmpeg: pip install imageio-ffmpeg") from exc


def encode(frames_dir: Path, out: Path, fps: int, crf: int = 25, pattern="f_%05d.jpg"):
    ff = ffmpeg_exe()
    cmd = [
        ff, "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(fps), "-i", str(frames_dir / pattern),
        "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True)


def hero_video(out: Path, poster: Path, seconds=10, fps=30, W=1600, H=900):
    tmp = Path(tempfile.mkdtemp(prefix="musa_hero_"))
    sw, sh = 960, 540
    n = seconds * fps
    try:
        for i in range(n):
            t = (i / n) * math.tau
            arr = silk_art(sw, sh, t=t, dark=True)
            # foco de luz cálido que respira
            y, x = np.mgrid[0:sh, 0:sw].astype(np.float32)
            cx = sw * (0.66 + 0.06 * math.sin(t * 0.8))
            cy = sh * (0.44 + 0.05 * math.cos(t * 0.6))
            r = np.hypot(x - cx, y - cy) / (sw * 0.55)
            glow = np.exp(-(r ** 2) * 2.3)[..., None]
            arr += glow * np.array([58, 30, 16])
            img = to_image(arr).resize((W, H), Image.LANCZOS)
            # polvo dorado
            d = ImageDraw.Draw(img)
            rng = np.random.default_rng(1000 + i // 12)
            for _ in range(34):
                px = rng.uniform(0, W)
                py = (rng.uniform(0, H) + i * rng.uniform(0.15, 0.5)) % H
                rr = rng.uniform(0.5, 2.1)
                a = int(40 + 90 * (0.5 + 0.5 * math.sin(t + px)))
                d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(220, 186, 140, a))
            arr = np.asarray(img, np.float32) * vignette(W, H, 0.55)
            img = add_grain(to_image(arr), 2.8, 1000 + i)
            img.save(tmp / f"f_{i:05d}.jpg", quality=90)
        encode(tmp, out, fps, crf=25)
        Image.open(tmp / "f_00000.jpg").save(poster, quality=88)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def reel_video(out: Path, poster: Path, seconds=8, fps=30, W=720, H=1280):
    tmp = Path(tempfile.mkdtemp(prefix="musa_reel_"))
    n = seconds * fps
    try:
        for i in range(n):
            t = (i / n) * math.tau
            arr = silk_art(W, H, t=t, dark=True)
            img = to_image(arr * 0.75)
            d = ImageDraw.Draw(img)
            prog = i / (n - 1)

            # marco editorial
            d.rectangle([34, 34, W - 34, H - 34], outline=IVORY + (60,), width=1)
            tracked(d, (56, 92), "MUSA", font(SANS, 18, "Medium"), IVORY + (210,), 7)
            tracked(d, (W - 56, 92), "REEL — 2026", font(SANS, 13, "Medium"), IVORY + (170,), 4, align="right")

            # escenas
            if prog < 0.34:
                a = min(1.0, prog / 0.08)
                col = IVORY
                tracked(d, (W / 2, 560), "Ideas que", font(SERIF, 92, "Light"), col, 1, align="center")
                tracked(d, (W / 2, 650), "encuentran", font(SERIF_IT, 88, "Light"), (244, 214, 178), 1, align="center")
                tracked(d, (W / 2, 740), "su voz.", font(SERIF, 96, "Light"), col, 1, align="center")
                draw_star(d, W / 2, 840, 22, GOLD_LIGHT)
            elif prog < 0.67:
                tracked(d, (W / 2, 520), "CREATIVIDAD", font(SANS, 30, "Medium"), IVORY, 12, align="center")
                tracked(d, (W / 2, 620), "ESTRATEGIA", font(SANS, 30, "Medium"), IVORY, 12, align="center")
                tracked(d, (W / 2, 720), "COMUNICACIÓN", font(SANS, 30, "Medium"), IVORY, 12, align="center")
                d.line([(200, 800), (520, 800)], fill=GOLD_LIGHT + (160,), width=1)
                tracked(d, (W / 2, 880), "Un aliado creativo", font(SERIF_IT, 46), IVORY + (220,), 0.5, align="center")
            else:
                tracked(d, (W / 2, 560), "Dónde las ideas", font(SERIF, 66, "Light"), IVORY, 0.5, align="center")
                tracked(d, (W / 2, 640), "encuentran su voz.", font(SERIF_IT, 70, "Light"), (246, 216, 180), 0.5, align="center")
                tracked(d, (W / 2, 760), "MUSA", font(SANS, 22, "Medium"), IVORY, 14, align="center")

            d.line([(56, H - 96), (W - 56, H - 96)], fill=IVORY + (50,), width=1)
            d.line([(56, H - 96), (56 + (W - 112) * prog, H - 96)], fill=GOLD_LIGHT + (220,), width=2)
            tracked(d, (56, H - 56), "INSPIRACIÓN · IDEA · CRECIMIENTO", font(SANS, 11, "Medium"), IVORY + (160,), 3)
            img = add_grain(img, 3.2, 2000 + i)
            img.save(tmp / f"f_{i:05d}.jpg", quality=91)
        encode(tmp, out, fps, crf=23)
        Image.open(tmp / "f_00030.jpg").save(poster, quality=88)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def showreel(out: Path, poster: Path, seconds=16, fps=24, W=1600, H=900):
    posters = sorted(MEDIA.glob("gallery-*.jpg"))
    if len(posters) < 6:
        raise RuntimeError("Genera primero las piezas gallery-*.jpg")
    imgs = [Image.open(p).convert("RGB") for p in posters]
    tmp = Path(tempfile.mkdtemp(prefix="musa_reel_show_"))
    n = seconds * fps
    per = seconds / (len(imgs) + 1)  # intro + piezas
    try:
        for i in range(n):
            tsec = i / fps
            if tsec < per:
                arr = silk_art(W, H, t=0.6)
                img = to_image(arr * 0.5)
                d = ImageDraw.Draw(img)
                tracked(d, (W / 2, H / 2 + 30), "MUSA", font(SERIF, 240, "Light"), IVORY, 40, align="center")
                draw_star(d, W / 2, H / 2 - 150, 26, GOLD_LIGHT)
                tracked(d, (W / 2, H / 2 + 130), "UNIVERSO VISUAL", font(SANS, 20, "Medium"), IVORY + (210,), 14, align="center")
            elif tsec > seconds - per:
                arr = silk_art(W, H, t=tsec * 0.7)
                img = to_image(arr * 0.62)
                d = ImageDraw.Draw(img)
                tracked(d, (W / 2, H / 2 - 20), "Dónde las ideas", font(SERIF, 110, "Light"), IVORY, 1, align="center")
                tracked(d, (W / 2, H / 2 + 90), "encuentran su voz.", font(SERIF_IT, 116, "Light"), (246, 216, 180), 1, align="center")
                draw_star(d, W / 2, H / 2 + 190, 18, GOLD_LIGHT)
            else:
                idx = min(len(imgs) - 1, int((tsec - per) / per))
                local = ((tsec - per) % per) / per
                base = imgs[idx]
                zoom = 1.03 + 0.07 * local
                cw, ch = int(W * zoom), int(H * zoom)
                crop_h = base.height
                crop_w = int(crop_h * W / H)
                left = int((base.width - crop_w) * (0.5 + 0.22 * math.sin(idx * 1.7)))
                big = base.crop((left, 0, left + crop_w, crop_h)).resize((cw, ch), Image.LANCZOS)
                ox = (cw - W) // 2
                oy = int((ch - H) * (0.5 + 0.1 * math.cos(idx)))
                img = big.crop((ox, oy, ox + W, oy + H))
                d = ImageDraw.Draw(img)
                d.rectangle([36, 36, W - 36, H - 36], outline=(255, 255, 255, 40), width=1)
                tracked(d, (64, 84), "MUSA — UNIVERSO VISUAL", font(SANS, 16, "Medium"), IVORY + (220,), 7)
                tracked(d, (W - 64, 84), f"{idx + 1:02d} / 06", font(SANS, 14, "Medium"), IVORY + (180,), 5, align="right")
                d.line([(64, H - 52), (W - 64, H - 52)], fill=(255, 255, 255, 45), width=1)
                d.line([(64, H - 52), (64 + (W - 128) * (i / n), H - 52)], fill=GOLD_LIGHT + (220,), width=2)
            img = add_grain(img, 3.0, 3000 + i)
            img.save(tmp / f"f_{i:05d}.jpg", quality=90)
        encode(tmp, out, fps, crf=26)
        Image.open(tmp / "f_00040.jpg").save(poster, quality=88)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ----------------------------------------------------------------------------
# Open Graph + textura
# ----------------------------------------------------------------------------
def og_image(path: Path):
    W, H = 1200, 630
    arr = silk_art(W, H, t=2.2)
    img = to_image(arr * 0.5)
    d = ImageDraw.Draw(img)
    tracked(d, (72, 118), "MUSA — ESTUDIO CREATIVO", font(SANS, 18, "Medium"), IVORY + (210,), 7)
    tracked(d, (W - 72, 118), "MUSA · 2026", font(SANS, 14, "Medium"), IVORY + (150,), 5, align="right")
    tracked(d, (W / 2, 360), "MUSA", font(SERIF, 230, "Light"), IVORY, 46, align="center")
    draw_star(d, W / 2, 424, 20, GOLD_LIGHT)
    tracked(d, (W / 2, 480), "Dónde las ideas encuentran su voz.", font(SERIF_IT, 52), (246, 216, 180), 0.5, align="center")
    tracked(d, (W / 2, 552), "CREATIVIDAD · ESTRATEGIA · COMUNICACIÓN", font(SANS, 15, "Medium"), IVORY + (200,), 6, align="center")
    add_grain(img, 3.0, 77).save(path, quality=90, optimize=True)


def grain_tile(path: Path):
    rng = np.random.default_rng(9)
    a = rng.normal(128, 26, (220, 220)).clip(0, 255).astype(np.uint8)
    arr = np.dstack([a, a, a, np.full_like(a, 22)])
    Image.fromarray(arr, "RGBA").save(path, optimize=True)


# ----------------------------------------------------------------------------
def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    print("→ Generando piezas editoriales...")
    pieces = [
        ("gallery-01.jpg", poster_silk),
        ("gallery-02.jpg", poster_type),
        ("gallery-03.jpg", poster_orb),
        ("gallery-04.jpg", poster_arch),
        ("gallery-05.jpg", poster_grid),
        ("gallery-06.jpg", poster_ribbon),
    ]
    for name, fn in pieces:
        img = fn()
        img.save(MEDIA / name, quality=90, optimize=True)
        img.save(MEDIA / name.replace(".jpg", ".webp"), quality=86, method=6)
        print("   ", name)

    print("→ Generando retratos abstractos del equipo...")
    team_card("Isabella Corredor", "IC", CLAY, 71, MEDIA / "team-isabella.jpg")
    team_card("Emilia Macias", "EM", GOLD, 72, MEDIA / "team-emilia.jpg")
    team_card("Elizabeth Román", "ER", WINE, 73, MEDIA / "team-elizabeth.jpg")
    print("    equipo listo")

    print("→ Generando imagen Open Graph y textura...")
    og_image(OUT / "og-image.jpg")
    grain_tile(OUT / "grain.png")

    print("→ Renderizando loop del hero (10s)...")
    hero_video(MEDIA / "hero.mp4", MEDIA / "hero-poster.jpg")
    print("→ Renderizando reel vertical (8s)...")
    reel_video(MEDIA / "reel.mp4", MEDIA / "reel-poster.jpg")
    print("→ Renderizando showreel (16s)...")
    showreel(MEDIA / "showreel.mp4", MEDIA / "showreel-poster.jpg")

    print("\n✓ Universo visual generado en public/")
    total = sum(f.stat().st_size for f in MEDIA.rglob("*") if f.is_file())
    print(f"  Peso total de media: {total / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
