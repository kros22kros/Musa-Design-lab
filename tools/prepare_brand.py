"""
Prepara los activos de marca de MUSA a partir de los archivos originales.

Entrada : tools/source/musa-logotipo.jpeg  (MUSA + Design Lab sobre azul)
Salida  : public/media/brand/  -> lockups horizontales y apilados, favicons.

El JPEG original tiene tipografía negra sobre un azul plano, así que se
extrae el trazo por luminancia (canal rojo) y se recolorea a tinta o marfil.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "source" / "musa-logotipo.jpeg"
OUT = ROOT / "public" / "media" / "brand"

INK = (12, 11, 11)
IVORY = (235, 233, 221)
WINE = (128, 35, 30)
BLUE = (103, 118, 141)


def extract() -> Image.Image:
    img = Image.open(SRC).convert("RGB")
    arr = np.asarray(img).astype(np.float32)
    bg_r = 0x8A  # fondo azul del original
    alpha = np.clip((bg_r - arr[:, :, 0]) / bg_r, 0, 1)
    alpha[alpha < 0.06] = 0
    alpha = np.clip((alpha - 0.06) / 0.94, 0, 1)
    return Image.fromarray((alpha * 255).round().astype(np.uint8), "L")


def recolor(mask: Image.Image, rgb) -> Image.Image:
    solid = Image.new("RGBA", mask.size, rgb + (255,))
    solid.putalpha(mask)
    return solid


def trim(img: Image.Image) -> Image.Image:
    box = img.getbbox()
    return img.crop(box) if box else img


def bands(mask: Image.Image):
    a = np.asarray(mask)
    rows = (a.sum(axis=1) / 255) > 0
    out, start = [], None
    for i, filled in enumerate(rows):
        if filled and start is None:
            start = i
        elif not filled and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(rows)))
    return out


def hstack(parts, gap=0, align="baseline"):
    height = max(p.height for p in parts)
    width = sum(p.width for p in parts) + gap * (len(parts) - 1)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = 0
    for p in parts:
        y = height - p.height if align == "bottom" else 0
        canvas.alpha_composite(p, (x, y))
        x += p.width + gap
    return canvas


def pad(img: Image.Image, pad: int) -> Image.Image:
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mask = extract()

    spans = bands(mask)
    spans = [s for s in spans if np.asarray(mask.crop((0, s[0], mask.width, s[1]))).sum() > 255 * 400]
    if len(spans) < 2:
        raise RuntimeError(f"No se pudieron separar las dos líneas del logo: {spans}")

    top = spans[0]
    bottom = spans[-1]
    musa_mask = trim(mask.crop((0, top[0], mask.width, top[1])))
    script_mask = trim(mask.crop((0, bottom[0], mask.width, bottom[1])))

    for name, rgb in (("dark", INK), ("light", IVORY)):
        musa = recolor(musa_mask, rgb)
        script = recolor(script_mask, rgb)

        # Apilado: MUSA centrado sobre Design Lab.
        stacked = Image.new("RGBA", (musa.width, musa.height + script.height + 34), (0, 0, 0, 0))
        stacked.alpha_composite(musa, ((musa.width - musa.width) // 2, 0))
        stacked.alpha_composite(script, ((musa.width - script.width) // 2, musa.height + 34))
        pad(trim(stacked), 18).save(OUT / f"logo-stacked-{name}.png", optimize=True)

        # Horizontal: MUSA + Design Lab a la derecha, apoyado en la base.
        scale = 0.40
        script_small = script.resize(
            (max(1, int(script.width * scale)), max(1, int(script.height * scale))),
            Image.LANCZOS,
        )
        lockup = hstack([musa, script_small], gap=int(musa.height * 0.16), align="bottom")
        pad(trim(lockup), 14).save(OUT / f"logo-horizontal-{name}.png", optimize=True)
        pad(script, 10).save(OUT / f"logo-script-{name}.png", optimize=True)

    # Monograma para favicon: primera letra del lockup.
    letters = bands(musa_mask.transpose(Image.Transpose.TRANSPOSE))  # columnas -> letras
    m_span = letters[0]
    m_mask = trim(musa_mask.crop((m_span[0], 0, m_span[1], musa_mask.height)))
    m_mask = m_mask.resize((int(m_mask.width * 0.92), int(m_mask.height * 0.92)), Image.LANCZOS)

    size = 512
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=104, fill=IVORY + (255,))
    glyph = recolor(m_mask, WINE)
    glyph.thumbnail((int(size * 0.56), int(size * 0.56)), Image.LANCZOS)
    icon.alpha_composite(glyph, ((size - glyph.width) // 2, (size - glyph.height) // 2))
    icon.save(OUT / "favicon.png", optimize=True)

    # Marca de agua del pie: lockup horizontal en marfil, baja opacidad en CSS.
    Image.open(OUT / "logo-horizontal-light.png").save(OUT / "watermark.png", optimize=True)

    for f in sorted(OUT.glob("*.png")):
        im = Image.open(f)
        print(f"{f.name:34s} {im.width}x{im.height}  {f.stat().st_size / 1024:5.1f} KB")


if __name__ == "__main__":
    main()
