# -*- coding: utf-8 -*-
"""Скачивает модель распознавания речи faster-whisper в папку models/.

Запуск (любая оболочка — cmd или PowerShell), из корня проекта:
    .venv\\Scripts\\python.exe download_model.py            # small (по умолчанию)
    .venv\\Scripts\\python.exe download_model.py medium     # другой размер

Размеры: tiny | base | small | medium | large-v3
Докачка прерванной загрузки поддерживается — просто запусти снова.
"""
import os
import sys

# hf_transfer ускоряет и стабилизирует загрузку на нестабильной сети — включаем, если установлен.
try:
    import hf_transfer  # noqa: F401
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
    print("hf_transfer: включён (быстрая загрузка)")
except ImportError:
    print("hf_transfer не установлен — обычная загрузка. Для скорости:")
    print('  .venv\\Scripts\\python.exe -m pip install -U "huggingface_hub[hf_transfer]"')

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

size = sys.argv[1] if len(sys.argv) > 1 else "small"
repo = f"Systran/faster-whisper-{size}"
dest = f"models/faster-whisper-{size}"

print(f"\nКачаю {repo}\n  -> {dest}\n(можно прервать Ctrl+C и запустить снова — докачает)\n")

from huggingface_hub import snapshot_download

snapshot_download(repo, local_dir=dest)

ok = os.path.isfile(os.path.join(dest, "model.bin"))
print(f"\n{'ГОТОВО' if ok else 'ВНИМАНИЕ: model.bin не найден'} — {dest}")
if ok and size != "small":
    print(f"Не забудь указать модель в config.yaml:  stt.model: {dest}")
