"""Голосовой ввод/вывод: запись с микрофона, STT (faster-whisper), TTS.

Все тяжёлые зависимости импортируются лениво, чтобы текстовый режим
работал без установленного голосового стека (requirements-voice.txt).
"""
from __future__ import annotations

import os

SAMPLE_RATE = 16000


class ModelNotReady(RuntimeError):
    """Модель распознавания не скачана/недоступна."""


# Кэш загруженных моделей Vosk: загрузка тяжёлая, а wake-word и режим
# «фразы конца» используют ту же модель — держим один экземпляр на путь.
_VOSK_MODELS: dict[str, object] = {}


def _load_vosk_model(model_path: str):
    """Загружает (с кэшем) модель Vosk. Бросает ModelNotReady, если её нет."""
    import os as _os

    if not _os.path.isdir(_os.path.join(model_path, "am")):
        raise ModelNotReady(
            f"Нет модели Vosk: {model_path}. "
            "Скачай:  .venv\\Scripts\\python.exe download_wake_model.py"
        )
    if model_path not in _VOSK_MODELS:
        from vosk import Model, SetLogLevel

        SetLogLevel(-1)  # убрать шумные логи Vosk
        _VOSK_MODELS[model_path] = Model(model_path)
    return _VOSK_MODELS[model_path]


def fuzzy_contains(text: str, phrases: list[str], fuzzy: float) -> bool:
    """Есть ли в тексте одна из фраз (точно или с нечётким совпадением)."""
    from difflib import SequenceMatcher

    text = (text or "").lower().strip()
    if not text:
        return False
    words = text.split()
    for ph in phrases:
        if not ph:
            continue
        if ph in text:
            return True
        n = len(ph.split())
        for i in range(max(1, len(words) - n + 1)):
            window = " ".join(words[i:i + n])
            if SequenceMatcher(None, ph, window).ratio() >= fuzzy:
                return True
    return False


def end_phrases(cfg: dict) -> list[str]:
    """Фразы-завершители команды из config.yaml (trigger.end_phrases)."""
    tcfg = cfg.get("trigger", {})
    return [p.lower().strip() for p in (tcfg.get("end_phrases") or []) if p and p.strip()]


def strip_end_phrases(text: str, phrases: list[str]) -> str:
    """Срезает фразу-завершитель (и хвостовую пунктуацию) с конца распознанного текста."""
    import re

    s = (text or "").strip()
    for ph in sorted([p for p in phrases if p], key=len, reverse=True):
        pat = re.compile(r"[\s,.:!?\-—]*" + re.escape(ph) + r"[\s,.:!?\-—]*$", re.IGNORECASE)
        new = pat.sub("", s)
        if new != s:
            return new.strip()
    return s


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


def record_until_silence(cfg: dict, on_block=None):
    """Записывает аудио с микрофона, пока не наступит тишина. Возвращает np.ndarray float32 mono.

    on_block(mono) — необязательный колбэк на каждый блок (для VU-метра в UI).
    Устройство ввода и усиление берутся из cfg['audio'].
    """
    import numpy as np
    import sounddevice as sd

    from src.audio import apply_gain, get_audio_cfg

    in_dev, _out, in_gain, _og = get_audio_cfg(cfg)

    tcfg = cfg.get("trigger", {})
    silence_s = float(tcfg.get("silence_seconds", 1.2))
    max_s = float(tcfg.get("max_seconds", 15))
    block = int(SAMPLE_RATE * 0.1)  # блок 100мс

    frames, silent_blocks, started = [], 0, False
    threshold = 0.012  # порог энергии (простой VAD)
    silence_limit = int(silence_s / 0.1)
    max_blocks = int(max_s / 0.1)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=block, device=in_dev) as stream:
        for _ in range(max_blocks):
            data, _overflow = stream.read(block)
            mono = apply_gain(data[:, 0], in_gain)
            frames.append(mono)
            if on_block is not None:
                on_block(mono)
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


def record_until_phrase(cfg: dict, on_block=None, vosk_model=None):
    """Записывает аудио, пока не услышит фразу-завершитель (через Vosk), затем останавливается.

    Возвращает np.ndarray float32 mono — вместе с произнесённой фразой конца
    (её удалит strip_end_phrases уже из распознанного whisper-ом текста).

    on_block(mono) — колбэк уровня для VU-метра.
    vosk_model     — переиспользуемая модель (engine отдаёт ту, что уже грузит wake-word).
    Бросает ModelNotReady, если модель Vosk недоступна.
    """
    import json

    import numpy as np
    import sounddevice as sd

    from src.audio import apply_gain, get_audio_cfg

    in_dev, _out, in_gain, _og = get_audio_cfg(cfg)
    tcfg = cfg.get("trigger", {})
    wake = tcfg.get("wakeword") or {}
    max_s = float(tcfg.get("max_seconds", 15))
    block = int(SAMPLE_RATE * 0.1)  # блок 100мс
    max_blocks = int(max_s / 0.1)

    phrases = end_phrases(cfg)
    fuzzy = float(wake.get("fuzzy", 0.7))

    if vosk_model is None:
        vosk_model = _load_vosk_model(wake.get("model", "models/vosk-model-small-ru"))
    from vosk import KaldiRecognizer

    rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)

    frames = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=block, device=in_dev) as stream:
        for _ in range(max_blocks):
            data, _overflow = stream.read(block)
            mono = apply_gain(data[:, 0], in_gain)
            frames.append(mono)
            if on_block is not None:
                on_block(mono)
            pcm = (np.clip(mono, -1, 1) * 32767).astype(np.int16).tobytes()
            if rec.AcceptWaveform(pcm):
                if fuzzy_contains(json.loads(rec.Result()).get("text", ""), phrases, fuzzy):
                    break
            elif fuzzy_contains(json.loads(rec.PartialResult()).get("partial", ""), phrases, fuzzy):
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
        self.audio = cfg.get("audio", {})
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

    def say(self, text: str, on_level=None) -> None:
        if not text:
            return
        if self.engine_name == "edge":
            try:
                self._say_edge(text, on_level=on_level)
                return
            except Exception as e:  # noqa: BLE001 — нет интернета и т.п.
                print(f"[TTS] edge не сработал ({e}); падаю на системный голос.")
                if self._pyttsx is None:
                    self._init_pyttsx()
        if self._pyttsx is None:
            self._init_pyttsx()
        self._pyttsx.say(text)
        self._pyttsx.runAndWait()

    def _say_edge(self, text: str, on_level=None) -> None:
        import asyncio
        import os
        import tempfile

        import edge_tts
        import soundfile as sf

        from src.audio import play

        path = os.path.join(tempfile.gettempdir(), "assistant_tts.mp3")

        async def _gen() -> None:
            await edge_tts.Communicate(text, self.voice, rate=self.rate).save(path)

        asyncio.run(_gen())
        data, sr = sf.read(path, dtype="float32")
        out_dev = self.audio.get("output_device")
        out_gain = float(self.audio.get("output_gain", 1.0))
        play(data, sr, device=out_dev, gain=out_gain, on_level=on_level)


def beep(freq: int = 880, ms: int = 150) -> None:
    """Короткий сигнал «слушаю» (Windows)."""
    try:
        import winsound

        winsound.Beep(freq, ms)
    except Exception:  # noqa: BLE001
        pass


class PushToTalk:
    """Активация по нажатию Enter."""

    def __init__(self, cfg: dict):
        pass

    def wait(self) -> bool:
        try:
            input("\n[Enter — говорить, Ctrl+C — выход] ")
            return True
        except (EOFError, KeyboardInterrupt):
            return False


class WakeListener:
    """«Дежурное» прослушивание фразы активации через Vosk (всегда слушает).

    Использует нечёткое совпадение, т.к. редкая/иностранная фраза распознаётся
    нестабильно. Варианты фраз и порог — в config.yaml (trigger.wakeword).
    """

    def __init__(self, cfg: dict):
        from vosk import KaldiRecognizer

        self.cfg = cfg
        wc = cfg["trigger"]["wakeword"]
        model_path = wc["model"]
        self.phrases = [p.lower().strip() for p in wc.get("phrases", []) if p.strip()]
        # Доп. варианты из калибровки (wake_calibrate live их сам записывает).
        pf = wc.get("phrases_file", "wake_phrases.txt")
        if pf and os.path.isfile(pf):
            with open(pf, encoding="utf-8") as f:
                for line in f:
                    s = line.strip().lower()
                    if s and s not in self.phrases:
                        self.phrases.append(s)
        self.fuzzy = float(wc.get("fuzzy", 0.7))
        self.rate = 16000
        self._Rec = KaldiRecognizer
        self.model = _load_vosk_model(model_path)

    def _match(self, text: str) -> bool:
        return fuzzy_contains(text, self.phrases, self.fuzzy)

    def wait(self, on_block=None, should_stop=None, ptt=None) -> bool:
        """Слушает фразу активации.

        on_block(mono)  — колбэк уровня для VU-метра (UI слышит микрофон и в простое).
        should_stop()   — если вернёт True, выходим с False (движок остановлен).
        ptt             — threading.Event: если выставлен, считаем за активацию (ручной захват).
        Устройство ввода и усиление берутся из self.cfg['audio'].
        """
        import json

        import numpy as np
        import sounddevice as sd

        from src.audio import apply_gain, get_audio_cfg

        in_dev, _out, in_gain, _og = get_audio_cfg(self.cfg)
        rec = self._Rec(self.model, self.rate)
        block = int(self.rate * 0.1)
        with sd.InputStream(samplerate=self.rate, channels=1,
                            dtype="float32", blocksize=block, device=in_dev) as stream:
            while True:
                if should_stop is not None and should_stop():
                    return False
                if ptt is not None and ptt.is_set():
                    ptt.clear()
                    return True
                data, _ = stream.read(block)
                mono = apply_gain(data[:, 0], in_gain)
                if on_block is not None:
                    on_block(mono)
                pcm = (np.clip(mono, -1, 1) * 32767).astype(np.int16).tobytes()
                if rec.AcceptWaveform(pcm):
                    if self._match(json.loads(rec.Result()).get("text", "")):
                        return True
                else:
                    if self._match(json.loads(rec.PartialResult()).get("partial", "")):
                        return True


def make_trigger(cfg: dict):
    mode = cfg.get("trigger", {}).get("mode", "push_to_talk")
    if mode == "wakeword":
        return WakeListener(cfg)
    return PushToTalk(cfg)
