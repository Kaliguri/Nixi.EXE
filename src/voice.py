"""Голосовой ввод/вывод: запись с микрофона, STT (faster-whisper), TTS.

Все тяжёлые зависимости импортируются лениво, чтобы текстовый режим
работал без установленного голосового стека (requirements-voice.txt).
"""
from __future__ import annotations

import os

SAMPLE_RATE = 16000


class ModelNotReady(RuntimeError):
    """Модель распознавания не скачана/недоступна."""


def _add_nvidia_dll_dirs() -> None:
    """Делает CUDA-DLL из pip-пакетов nvidia-* (cuBLAS/cuDNN) видимыми для CTranslate2 на Windows.

    Недостаточно добавить путь — CTranslate2 не находит DLL по имени, поэтому
    явно подгружаем их в процесс через WinDLL.
    """
    if os.name != "nt":
        return
    import ctypes
    import glob
    import sys

    base = os.path.join(sys.prefix, "Lib", "site-packages", "nvidia")
    bindirs = glob.glob(os.path.join(base, "*", "bin"))
    for bindir in bindirs:
        try:
            os.add_dll_directory(bindir)
        except OSError:
            pass
    # Принудительно грузим все CUDA-DLL (cuBLAS, cuDNN и зависимости).
    for bindir in bindirs:
        for dll in glob.glob(os.path.join(bindir, "*.dll")):
            try:
                ctypes.WinDLL(dll)
            except OSError:
                pass


def record_until_silence(cfg: dict):
    """Записывает аудио с микрофона, пока не наступит тишина. Возвращает np.ndarray float32 mono."""
    import numpy as np
    import sounddevice as sd

    tcfg = cfg.get("trigger", {})
    silence_s = float(tcfg.get("silence_seconds", 1.2))
    max_s = float(tcfg.get("max_seconds", 15))
    block = int(SAMPLE_RATE * 0.1)  # блок 100мс

    frames, silent_blocks, started = [], 0, False
    threshold = 0.012  # порог энергии (простой VAD)
    silence_limit = int(silence_s / 0.1)
    max_blocks = int(max_s / 0.1)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=block) as stream:
        for _ in range(max_blocks):
            data, _overflow = stream.read(block)
            mono = data[:, 0]
            frames.append(mono)
            energy = float(np.sqrt(np.mean(mono ** 2)))
            if energy > threshold:
                started, silent_blocks = True, 0
            elif started:
                silent_blocks += 1
                if silent_blocks >= silence_limit:
                    break
    if not frames:
        return np.zeros(0, dtype="float32")
    return np.concatenate(frames)


class STT:
    def __init__(self, cfg: dict):
        _add_nvidia_dll_dirs()
        from faster_whisper import WhisperModel

        scfg = cfg["stt"]
        self.language = scfg.get("language", "ru")
        name = scfg.get("model", "small")
        device = scfg.get("device", "cuda")
        compute = scfg.get("compute_type", "float16")

        # Если указан локальный путь, но нет model.bin — модель ещё не докачана.
        looks_like_path = ("/" in name) or ("\\" in name)
        if looks_like_path and not os.path.isfile(os.path.join(name, "model.bin")):
            raise ModelNotReady(
                f"Модель не готова (нет model.bin в {name}) — загрузка ещё идёт или не запущена.\n"
                f"Скачай модель командой:\n"
                f'  $env:HF_HUB_ENABLE_HF_TRANSFER = "1"\n'
                f"  .\\.venv\\Scripts\\python.exe -c \"from huggingface_hub import "
                f"snapshot_download; snapshot_download('Systran/faster-whisper-small', "
                f"local_dir='models/faster-whisper-small')\""
            )
        try:
            self.model = WhisperModel(name, device=device, compute_type=compute)
        except Exception as e:  # noqa: BLE001 — нет CUDA-библиотек и т.п.
            if device != "cpu":
                print(f"[STT] {device} недоступен ({e}); падаю на CPU/int8.")
                self.model = WhisperModel(name, device="cpu", compute_type="int8")
            else:
                raise

    def transcribe(self, audio) -> str:
        segments, _info = self.model.transcribe(audio, language=self.language)
        return " ".join(seg.text for seg in segments).strip()


class TTS:
    """Синтез речи. engine: 'edge' (нейро-голос Microsoft) или 'pyttsx3' (офлайн SAPI)."""

    def __init__(self, cfg: dict):
        self.cfg = cfg["tts"]
        self.engine_name = self.cfg.get("engine", "edge")
        self._pyttsx = None
        if self.engine_name == "pyttsx3":
            self._init_pyttsx()
        elif self.engine_name == "edge":
            import edge_tts  # noqa: F401  — проверяем, что установлен
            self.voice = self.cfg.get("edge_voice", "ru-RU-SvetlanaNeural")
            self.rate = self.cfg.get("edge_rate", "+0%")
        else:
            raise NotImplementedError(
                f"TTS '{self.engine_name}' не поддержан (есть edge, pyttsx3)."
            )

    def _init_pyttsx(self) -> None:
        import pyttsx3

        self._pyttsx = pyttsx3.init()
        self._pyttsx.setProperty("rate", int(self.cfg.get("rate", 180)))
        voice = self.cfg.get("voice")
        if voice:
            self._pyttsx.setProperty("voice", voice)

    def say(self, text: str) -> None:
        if not text:
            return
        if self.engine_name == "edge":
            try:
                self._say_edge(text)
                return
            except Exception as e:  # noqa: BLE001 — нет интернета и т.п.
                print(f"[TTS] edge не сработал ({e}); падаю на системный голос.")
                if self._pyttsx is None:
                    self._init_pyttsx()
        if self._pyttsx is None:
            self._init_pyttsx()
        self._pyttsx.say(text)
        self._pyttsx.runAndWait()

    def _say_edge(self, text: str) -> None:
        import asyncio
        import os
        import tempfile

        import edge_tts
        import soundfile as sf
        import sounddevice as sd

        path = os.path.join(tempfile.gettempdir(), "assistant_tts.mp3")

        async def _gen() -> None:
            await edge_tts.Communicate(text, self.voice, rate=self.rate).save(path)

        asyncio.run(_gen())
        data, sr = sf.read(path, dtype="float32")
        sd.play(data, sr)
        sd.wait()


class Trigger:
    """Активация записи. push_to_talk: жди Enter. (wakeword — TODO)"""

    def __init__(self, cfg: dict):
        self.mode = cfg.get("trigger", {}).get("mode", "push_to_talk")
        if self.mode != "push_to_talk":
            raise NotImplementedError(
                "Пока поддержан только trigger.mode=push_to_talk. "
                "Wake word (openWakeWord) добавим следующим шагом."
            )

    def wait(self) -> bool:
        try:
            input("\n[Enter — говорить, Ctrl+C — выход] ")
            return True
        except (EOFError, KeyboardInterrupt):
            return False
