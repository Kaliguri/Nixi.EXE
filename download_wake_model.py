# -*- coding: utf-8 -*-
"""Скачивает маленькую русскую модель Vosk (~45 МБ) для wake word в models/.

Запуск:  .venv\\Scripts\\python.exe download_wake_model.py
"""
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile

URL = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
EXTRACTED = "models/vosk-model-small-ru-0.22"
DEST = "models/vosk-model-small-ru"


def _progress(block: int, block_size: int, total: int) -> None:
    if total > 0:
        pct = min(100, block * block_size * 100 // total)
        sys.stdout.write(f"\r  {pct}%")
        sys.stdout.flush()


def main() -> None:
    if os.path.isdir(os.path.join(DEST, "am")) or os.path.isdir(os.path.join(DEST, "conf")):
        print("Модель уже на месте:", DEST)
        return

    os.makedirs("models", exist_ok=True)
    zpath = os.path.join(tempfile.gettempdir(), "vosk-model-small-ru.zip")

    print(f"Качаю {URL}")
    urllib.request.urlretrieve(URL, zpath, _progress)
    print("\nРаспаковка...")
    with zipfile.ZipFile(zpath) as z:
        z.extractall("models")

    if os.path.isdir(EXTRACTED):
        if os.path.isdir(DEST):
            shutil.rmtree(DEST)
        os.rename(EXTRACTED, DEST)
    os.remove(zpath)

    ok = os.path.isdir(os.path.join(DEST, "am"))
    print(f"{'ГОТОВО' if ok else 'ВНИМАНИЕ: структура модели не найдена'} — {DEST}")


if __name__ == "__main__":
    main()
