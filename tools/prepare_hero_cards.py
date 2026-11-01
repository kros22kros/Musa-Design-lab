"""
Recorta las tarjetas flotantes del hero a partir de las piezas ya procesadas.

Entrada : public/media/work-07.jpg, work-01.jpg y estudio-musa.jpg
Salida  : public/media/hero-card-a|b|brand.jpg|webp (4:5, sin texto suelto)

Las tarjetas del hero muestran solo imagen (retrato o marca), por eso se
recortan a mano: asÃ­ no quedan titulares sueltos flotando en la entrada.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "media"

# (origen, caja de recorte, archivo de salida, ancho)
CARDS = [
    ("work-07.jpg", (35, 561, 865, 1598), "hero-card-a", 560),
    ("estudio-musa.jpg", (150, 250, 930, 1225), "hero-card-brand", 560),
    ("work-01.jpg", (0, 240, 380, 715), "hero-card-b", 480),
]


def main():
    for source, box, slug, width in CARDS:
        src = OUT / source
        if not src.exists():
            raise SystemExit(f"Falta la pieza: {src}")

        crop = Image.open(src).convert("RGB").crop(box)
        height = round(width * 5 / 4)
        crop = crop.resize((width, height), Image.LANCZOS)

        jpg = OUT / f"{slug}.jpg"
        webp = OUT / f"{slug}.webp"
        crop.save(jpg, quality=84, optimize=True)
        crop.save(webp, quality=78, method=6)
        print(
            f"{slug:16s} {crop.size[0]}Ã—{crop.size[1]}  "
            f"{jpg.stat().st_size / 1024:5.1f} KB / {webp.stat().st_size / 1024:5.1f} KB"
        )


if __name__ == "__main__":
    main()

