"""
Descarga de videotutorías a Google Drive desde GitHub Actions.
Recibe la lista de grabaciones desde el snippet del campus (variable VIDEOS)
y solo descarga las que no estén ya en Drive (registro: Videotutorias/descargados.txt).
"""
import json
import os
import re
import subprocess
import sys

ZOOM_PASS = os.environ.get("ZOOM_PASS") or "ILERNA"
DRIVE = "gdrive:Videotutorias"
ARCHIVO = "descargados.txt"


def carpeta(nombre):
    if nombre.lower().startswith("tutoría"):
        return "Tutoría"
    return re.sub(r"[^\w\s.-]", "_", nombre).strip()


def main():
    videos = json.loads(os.environ["VIDEOS"])
    print(f"📚 Recibidas {len(videos)} grabaciones del campus")

    # Traer el registro de lo ya descargado desde Drive
    subprocess.run(["rclone", "copyto", f"{DRIVE}/{ARCHIVO}", ARCHIVO], check=False)

    errores = 0
    for asig, n, url in videos:
        print(f"\n▶ {asig} – VT{n}")
        r = subprocess.run([
            "yt-dlp", "--video-password", ZOOM_PASS,
            "--download-archive", ARCHIVO,
            "-f", "bv*+ba/b", "--merge-output-format", "mp4",
            "-o", f"salida/{carpeta(asig)}/VT{int(n):02d}_%(title)s.%(ext)s",
            url,
        ])
        if r.returncode != 0:
            errores += 1
        if os.path.isdir("salida"):
            subprocess.run(["rclone", "move", "salida", DRIVE, "--delete-empty-src-dirs"], check=True)
        if os.path.exists(ARCHIVO):
            subprocess.run(["rclone", "copyto", ARCHIVO, f"{DRIVE}/{ARCHIVO}"], check=True)

    print(f"\n✅ Terminado. Errores: {errores}")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
