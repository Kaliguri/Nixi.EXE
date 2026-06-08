# -*- coding: utf-8 -*-
"""Калибровка фразы активации под Vosk.

Два режима:
  .\\.venv\\Scripts\\python.exe -m tests.wake_calibrate        # синтез (прокси, быстро)
  .\\.venv\\Scripts\\python.exe -m tests.wake_calibrate live   # ЖИВОЙ голос в микрофон (точно)

Живой режим: говори фразу активации несколько раз, в конце (Ctrl+C) увидишь,
какие строки Vosk распознал чаще всего — их и впиши в config.yaml
(trigger.wakeword.phrases).
"""
import asyncio
import json
import os
import sys
import tempfile

import numpy as np
import soundfile as sf
from vosk import KaldiRecognizer, Model

from src.config import load_config


def to_pcm16k(data: np.ndarray, sr: int) -> bytes:
    if data.ndim > 1:
        data = data[:, 0]
    if sr != 16000:
        n = int(len(data) * 16000 / sr)
        data = np.interp(
            np.linspace(0, 1, n, endpoint=False),
            np.linspace(0, 1, len(data), endpoint=False),
            data,
        )
    return (np.clip(data, -1, 1) * 32767).astype(np.int16).tobytes()


def synth_mode(cfg: dict, model: Model) -> None:
    import edge_tts

    voice = cfg["tts"]["edge_voice"]

    def hear(phrase: str) -> str:
        path = os.path.join(tempfile.gettempdir(), "wake_cal.mp3")
        asyncio.run(edge_tts.Communicate(phrase, voice).save(path))
        data, sr = sf.read(path, dtype="float32")
        rec = KaldiRecognizer(model, 16000)
        rec.AcceptWaveform(to_pcm16k(data, sr))
        return json.loads(rec.FinalResult()).get("text", "")

    print("Как Vosk слышит фразу активации (СИНТЕЗ — прокси, не твой голос):\n")
    for ph in ["арс меджика", "арс меджика арс меджика", "ars magica", "арс магика"]:
        print(f"  сказано {ph!r:32} -> Vosk: {hear(ph)!r}")
    print("\nДля точной настройки запусти ЖИВОЙ режим:  ... wake_calibrate live")


def live_mode(model: Model) -> None:
    import sounddevice as sd

    rec = KaldiRecognizer(model, 16000)
    seen: dict[str, int] = {}
    print("ЖИВАЯ калибровка. Скажи фразу активации 5–10 раз, чётко.")
    print("Когда закончишь — Ctrl+C.\n")
    try:
        with sd.RawInputStream(samplerate=16000, blocksize=0, dtype="int16", channels=1) as st:
            while True:
                data, _ = st.read(4000)
                if rec.AcceptWaveform(bytes(data)):
                    t = json.loads(rec.Result()).get("text", "")
                    if t:
                        seen[t] = seen.get(t, 0) + 1
                        print("  услышано:", repr(t))
    except KeyboardInterrupt:
        print("\n--- ИТОГ: что Vosk слышал (по убыванию частоты) ---")
        for t, c in sorted(seen.items(), key=lambda x: -x[1]):
            print(f"  {c}x  {t!r}")
        print("\nВпиши подходящие строки в config.yaml -> trigger.wakeword.phrases")


def main() -> None:
    cfg = load_config()
    model = Model(cfg["trigger"]["wakeword"]["model"])
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        live_mode(model)
    else:
        synth_mode(cfg, model)


if __name__ == "__main__":
    main()
