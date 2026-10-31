"""
Prepara los retratos reales del equipo para las tarjetas de la sección
«Equipo».

Entrada : las fotos originales en Documentos, una por integrante.
Salida  : public/media/team-{isabella,emilia,elizabeth}.jpg|webp
          recortadas a 4:5 (1000×1250), que es el formato de .team__media.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "media"
SRC = Path.home() / "Documents"

# (archivo, caja de recorte en la foto original)
PORTRAITS = [
    ("isabella.jpeg", (0, 116, 1066, 1449)),
    ("Emilia.jpeg", (0, 150, 1040, 1450)),
    ("Elizabeth.jpeg", (200, 0, 1124, 1155)),
]

TARGET = (1000, 1250)


def main():
    for filename, box in PORTRAITS:
        src = SRC / filename
        if not src.exists():
            raise SystemExit(f"No se encontró la foto: {src}")

        img = Image.open(src).convert("RGB")
        # La caja de recorte ya viene en 4:5; el resize fija el tamaño final.
        crop = img.crop(box).resize(TARGET, Image.LANCZOS)

        slug = filename.split(".")[0].lower()
        jpg = OUT / f"team-{slug}.jpg"
        webp = OUT / f"team-{slug}.webp"
        crop.save(jpg, quality=90, optimize=True)
        crop.save(webp, quality=84, method=6)
        print(f"{jpg.name:24s} {crop.size[0]}×{crop.size[1]}  {jpg.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
