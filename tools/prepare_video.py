"""
Deriva los videos del sitio a partir de «VIDEO DE MUSA.mp4».

Entrada : C:/Users/USUARIO/Documents/VIDEO DE MUSA.mp4
Salida  : public/media/musa-showreel.mp4  (16:9, con audio)
          public/media/musa-reel.mp4      (9:16, silencioso, para el teléfono)
          posters .jpg/.webp de ambos.
"""
from pathlib import Path
import subprocess

import imageio_ffmpeg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "media"
SRC = Path.home() / "Documents" / "VIDEO DE MUSA.mp4"

IVORY = "0xECE9DC"


def ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    if not SRC.exists():
        raise SystemExit(f"No se encontró el video de origen: {SRC}")

    ff = ffmpeg()

    showreel = OUT / "musa-showreel.mp4"
    run([
        ff, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(SRC),
        "-vf", "scale=1280:720:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "23",
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(showreel),
    ])

    reel = OUT / "musa-reel.mp4"
    graph = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=720:1280:force_original_aspect_ratio=increase,"
        "crop=720:1280,gblur=sigma=46,eq=brightness=-0.32:saturation=0.55[bg2];"
        "[fg]scale=660:-2:flags=lanczos[fg2];"
        "[bg2][fg2]overlay=(W-w)/2:(H-h)/2:shortest=1,"
        f"drawbox=x=29:y=453:w=662:h=374:color={IVORY}@0.34:t=1[v]"
    )
    run([
        ff, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(SRC),
        "-filter_complex", graph,
        "-map", "[v]", "-an",
        "-c:v", "libx264", "-preset", "slow", "-crf", "24",
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-movflags", "+faststart",
        str(reel),
    ])

    for video, t, base, size in (
        (showreel, "00:00:04", "musa-showreel-poster", None),
        (reel, "00:00:04", "musa-reel-poster", None),
    ):
        jpg = OUT / f"{base}.jpg"
        webp = OUT / f"{base}.webp"
        run([
            ff, "-y", "-hide_banner", "-loglevel", "error",
            "-ss", t, "-i", str(video), "-frames:v", "1",
            "-q:v", "2", str(jpg),
        ])
        Image.open(jpg).save(webp, quality=84, method=6)
        print(f"{base}: {Image.open(jpg).size}")

    for f in (showreel, reel):
        print(f"{f.name:22s} {f.stat().st_size / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
