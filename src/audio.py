"""Аудио-устройства: перечисление, усиление, уровни, воспроизведение.

Тонкая обёртка над sounddevice. Даёт UI выбирать устройства ввода/вывода и
крутить громкость, а движку — считать уровень сигнала для VU-метра.
Все импорты sounddevice/numpy ленивые: текстовый режим работает без них.
"""
from __future__ import annotations

import math


def list_devices() -> dict:
    """Списки устройств ввода и вывода для UI.

    Возвращает {"input": [...], "output": [...]}, где каждый элемент —
    {id, name, channels, samplerate, default}.
    """
    import sounddevice as sd

    devices = sd.query_devices()
    try:
        default_in, default_out = sd.default.device
    except Exception:  # noqa: BLE001
        default_in, default_out = -1, -1

    inputs, outputs = [], []
    for idx, d in enumerate(devices):
        base = {
            "id": idx,
            "name": d["name"],
            "samplerate": int(d["default_samplerate"]),
        }
        if d["max_input_channels"] > 0:
            inputs.append({**base, "channels": d["max_input_channels"],
                           "default": idx == default_in})
        if d["max_output_channels"] > 0:
            outputs.append({**base, "channels": d["max_output_channels"],
                            "default": idx == default_out})
    return {"input": inputs, "output": outputs}


def get_audio_cfg(cfg: dict):
    """Достаёт (input_device, output_device, input_gain, output_gain) из cfg['audio'].

    device = None означает «системное по умолчанию» (sounddevice сам выберет).
    """
    a = cfg.get("audio") or {}
    return (
        a.get("input_device"),
        a.get("output_device"),
        float(a.get("input_gain", 1.0)),
        float(a.get("output_gain", 1.0)),
    )


def apply_gain(block, gain: float):
    """Умножает float32-блок на gain с защитой от клиппинга."""
    if gain == 1.0:
        return block
    import numpy as np

    return np.clip(block * gain, -1.0, 1.0)


def rms_db(block) -> float:
    """Уровень блока в dBFS (−120 = тишина, 0 = максимум) для VU-метра."""
    import numpy as np

    if block is None or len(block) == 0:
        return -120.0
    rms = float(np.sqrt(np.mean(np.square(block.astype(np.float64)))))
    if rms <= 1e-7:
        return -120.0
    return max(-120.0, 20.0 * math.log10(rms))


def play(data, samplerate, device=None, gain: float = 1.0, on_level=None) -> None:
    """Воспроизводит аудио на заданном устройстве вывода.

    Если передан on_level(db) — воспроизводит чанками ~50мс и сообщает уровень
    каждого чанка (для VU-метра выхода). Иначе — простой sd.play/wait.
    """
    import numpy as np
    import sounddevice as sd

    if data.ndim == 1:
        data = data.reshape(-1, 1)
    if gain != 1.0:
        data = np.clip(data * gain, -1.0, 1.0)

    if on_level is None:
        sd.play(data, samplerate, device=device)
        sd.wait()
        return

    channels = data.shape[1]
    chunk = max(1, int(samplerate * 0.05))
    with sd.OutputStream(samplerate=samplerate, channels=channels,
                         dtype="float32", device=device) as stream:
        for i in range(0, len(data), chunk):
            block = data[i:i + chunk]
            stream.write(block)
            on_level(rms_db(block[:, 0]))
