# -*- coding: utf-8 -*-
"""Готовит XTTS-v2: качает модель и создаёт дефолтный референс-клип голоса Никси.

Запуск:  .venv\\Scripts\\python.exe setup_xtts.py

Что делает:
  1. Скачивает модель Coqui XTTS-v2 (~1.8 ГБ) в кэш TTS (первый импорт/инстанс).
  2. Если нет voices/nixi_ref.wav — синтезирует его через edge-tts (наш «аниме»
     пресет Светланы) и кладёт как референс для клонирования. Это даёт рабочий
     голос сразу и без чужих/копирайтных записей.

Свой тембр: положи СВОЙ клип (6-20с, чистый голос, моно) в voices/nixi_ref.wav —
XTTS склонирует именно его. Путь меняется в config.yaml → tts.xtts.speaker_wav.
"""
import asyncio
import os
import tempfile

REF_PATH = os.path.join("voices", "nixi_ref.wav")

# Текст для референса: несколько живых фраз, ~15с — так клон стабильнее.
REF_TEXT = (
    "Привет! Меня зовут Никси, я твоя голосовая помощница. "
    "Я могу включать музыку, искать ответы и просто болтать с тобой. "
    "Давай сделаем сегодняшний день чуточку лучше, хорошо?"
)


def _make_reference() -> None:
    if os.path.isfile(REF_PATH):
        print(f"Референс уже есть: {REF_PATH}")
        return
    os.makedirs("voices", exist_ok=True)
    print("Создаю дефолтный референс через edge-tts (Светлана, аниме-пресет)...")

    import edge_tts

    mp3 = os.path.join(tempfile.gettempdir(), "nixi_ref_src.mp3")

    async def _gen() -> None:
        await edge_tts.Communicate(
            REF_TEXT, "ru-RU-SvetlanaNeural", rate="+8%", pitch="+30Hz"
        ).save(mp3)

    asyncio.run(_gen())

    # edge отдаёт mp3 — XTTS-референсу нужен wav; конвертируем через librosa.
    import librosa
    import soundfile as sf

    wav, sr = librosa.load(mp3, sr=22050, mono=True)
    sf.write(REF_PATH, wav, sr)
    os.remove(mp3)
    print(f"Референс готов: {REF_PATH} ({len(wav) / sr:.1f}с)")


def _download_model() -> None:
    os.environ.setdefault("COQUI_TOS_AGREED", "1")
    print("Качаю/проверяю модель XTTS-v2 (первый раз ~1.8 ГБ)...")
    from TTS.api import TTS as CoquiTTS

    # Инстанс без GPU — только чтобы скачать и закэшировать веса.
    CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    print("Модель XTTS-v2 на месте.")


def main() -> None:
    _make_reference()
    _download_model()
    print("\nГОТОВО. Включи в config.yaml:  tts.engine: xtts  — и перезапусти сервер.")


if __name__ == "__main__":
    main()
