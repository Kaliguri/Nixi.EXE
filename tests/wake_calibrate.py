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

    print("Как Vosk слышит имя активации (СИНТЕЗ — прокси, не твой голос):\n")
    for ph in ["никси", "никси никси", "nixi", "ники"]:
        print(f"  сказано {ph!r:32} -> Vosk: {hear(ph)!r}")
    print("\nДля точной настройки запусти ЖИВОЙ режим:  ... wake_calibrate live")


def live_mode(model: Model) -> None:
    import numpy as np
    import sounddevice as sd

    rate = 16000
    block = int(rate * 0.25)
    rec = KaldiRecognizer(model, rate)
    seen: dict[str, int] = {}
    print("ЖИВАЯ калибровка. Скажи фразу активации 5–10 раз, чётко, близко к микрофону.")
    print("Полоска = уровень звука: при речи должна заметно расти.")
    print("Когда закончишь — Ctrl+C.\n")
    try:
        with sd.InputStream(samplerate=rate, channels=1, dtype="float32", blocksize=block) as st:
            while True:
                data, _ = st.read(block)
                mono = data[:, 0]
                peak = float(np.max(np.abs(mono))) if len(mono) else 0.0
                bar = "#" * min(40, int(peak * 80))
                print(f"\rуровень |{bar:<40}| {peak:.3f}", end="")
                pcm = (np.clip(mono, -1, 1) * 32767).astype(np.int16).tobytes()
                if rec.AcceptWaveform(pcm):
                    t = json.loads(rec.Result()).get("text", "")
                    if t:
                        seen[t] = seen.get(t, 0) + 1
                        print(f"\n  услышано: {t!r}")
    except KeyboardInterrupt:
        t = json.loads(rec.FinalResult()).get("text", "")
        if t:
            seen[t] = seen.get(t, 0) + 1
        print("\n\n--- ИТОГ: что Vosk слышал (по убыванию частоты) ---")
        ranked = sorted(seen.items(), key=lambda x: -x[1])
        for t, c in ranked:
            print(f"  {c}x  {t!r}")
        top = [t for t, c in ranked if c >= 2] or [t for t, _ in ranked[:3]]
        if top:
            with open("wake_phrases.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(top) + "\n")
            print(f"\nСохранил {len(top)} вариант(ов) в wake_phrases.txt — wake их уже использует.")
            print("Запускай:  .\\run.ps1 -voice")
        else:
            print("\nVosk ничего не распознал. Смотри на полоску уровня: если при речи она")
            print("почти не растёт — повысь громкость микрофона в Windows и говори ближе.")


def main() -> None:
    cfg = load_config()
    model = Model(cfg["trigger"]["wakeword"]["model"])
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        live_mode(model)
    else:
        synth_mode(cfg, model)


if __name__ == "__main__":
    main()
