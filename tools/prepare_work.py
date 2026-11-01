"""
Prepara las imágenes reales de MUSA para el sitio.

Entrada : Documentos/MUSA.jpeg y Documentos/1..7.jpeg (si siguen ahí)
Salida  : public/media/estudio-musa.jpg|webp      (sección 01, Estudio)
          public/media/work-01..07.jpg|webp       (portafolio Universo visual)

No recorta las piezas: conserva su proporción original para no cortar texto.
Si un original ya no está en Documentos, se conserva la versión procesada.
Las tarjetas flotantes de la entrada se generan aparte, con
prepare_hero_cards.py, a partir de estas piezas.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "media"
SRC = Path.home() / "Documents"


def save(img: Image.Image, slug: str, max_width: int, jpg_q: int, webp_q: int):
    if img.width > max_width:
        height = round(img.height * max_width / img.width)
        img = img.resize((max_width, height), Image.LANCZOS)

    jpg = OUT / f"{slug}.jpg"
    webp = OUT / f"{slug}.webp"
    img.save(jpg, quality=jpg_q, optimize=True)
    img.save(webp, quality=webp_q, method=6)
    print(
        f"{slug:14s} {img.width}×{img.height}  "
        f"{jpg.stat().st_size / 1024:6.1f} KB / {webp.stat().st_size / 1024:6.1f} KB"
    )


def main():
    estudio = SRC / "MUSA.jpeg"
    if estudio.exists():
        save(Image.open(estudio).convert("RGB"), "estudio-musa", 1080, 90, 84)
    else:
        print("· estudio-musa: sin original en Documentos, se conserva el actual")

    for number in range(1, 8):
        src = SRC / f"{number}.jpeg"
        if src.exists():
            piece = Image.open(src).convert("RGB")
            save(piece, f"work-0{number}", 900, 86, 80)
        else:
            print(f"· work-0{number}: sin original en Documentos, se conserva el actual")


if __name__ == "__main__":
    main()
