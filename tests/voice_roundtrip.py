# -*- coding: utf-8 -*-
"""Проверка голосового тракта без микрофона: edge-TTS произносит фразу,
faster-whisper её распознаёт. Требует интернет (edge) и качает модель Whisper.
Запуск:  .\.venv\Scripts\python.exe -m tests.voice_roundtrip
"""
import asyncio
import os
import tempfile

import edge_tts

from src.config import load_config
from src.voice import _add_nvidia_dll_dirs

_add_nvidia_dll_dirs()
from faster_whisper import WhisperModel  # noqa: E402 — после добавления путей к CUDA-DLL

PHRASE = "Привет! Я Никси, голосовой ассистент. Включи музыку."


def main() -> None:
    cfg = load_config()
    path = os.path.join(tempfile.gettempdir(), "voice_roundtrip.mp3")

    asyncio.run(edge_tts.Communicate(PHRASE, cfg["tts"]["edge_voice"]).save(path))
    print("TTS ok:", os.path.getsize(path), "байт")

    scfg = cfg["stt"]
    dev, comp = scfg.get("device", "cuda"), scfg.get("compute_type", "float16")
    try:
        model = WhisperModel(scfg.get("model", "small"), device=dev, compute_type=comp)
    except Exception as e:  # noqa: BLE001
        print(f"{dev} недоступен ({e}); падаю на CPU/int8")
        dev = "cpu"
        model = WhisperModel(scfg.get("model", "small"), device="cpu", compute_type="int8")

    segments, info = model.transcribe(path, language="ru")
    text = " ".join(s.text for s in segments).strip()
    print(f"STT [{dev}] распознал: {text!r}")
    print(f"Язык: {info.language} | исходная фраза: {PHRASE!r}")


if __name__ == "__main__":
    main()
