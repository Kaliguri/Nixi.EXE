"""Управляемый движок ассистента.

Тот же голосовой тракт, что в консольном voice_loop (wake → запись → STT →
Router → TTS), но вынесенный в фоновый поток с контролем (старт/стоп/пауза/
push-to-talk/reload) и шиной событий (статус, уровни, лог, ошибки).
Используется и веб-UI (src/server), и CLI (src/main).
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from src.llm import Router
from src.skills import load_skills

Event = dict
OnEvent = Callable[[Event], None]


class AssistantEngine:
    """Конечный автомат голосового ассистента в отдельном потоке.

    Состояния: stopped | loading | listening | recording | thinking | speaking
              | paused | error.
    """

    def __init__(self, cfg: dict, on_event: Optional[OnEvent] = None):
        self.cfg = cfg
        self.on_event: OnEvent = on_event or (lambda e: None)
        self.state = "stopped"

        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._ptt = threading.Event()

        self.router: Optional[Router] = None
        self.skills = None
        self.stt = None
        self.tts = None
        self.trigger = None

    # --- события ---
    def emit(self, type_: str, **data) -> None:
        self.on_event({"type": type_, **data})

    def set_state(self, state: str) -> None:
        self.state = state
        self.emit("status", state=state)

    def snapshot(self) -> dict:
        return {"state": self.state}

    # --- жизненный цикл ---
    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop.clear()
            self._pause.clear()
            self._ptt.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._ptt.set()  # разблокировать ожидание триггера
        t = self._thread
        if t is not None and t.is_alive() and t is not threading.current_thread():
            t.join(timeout=5)
        self.set_state("stopped")

    def pause(self) -> None:
        self._pause.set()

    def resume(self) -> None:
        self._pause.clear()

    def push_to_talk(self) -> None:
        self._ptt.set()

    def reload(self, new_cfg: dict) -> None:
        """Применяет новые настройки без перезапуска процесса.

        Живо применяется: модель LLM, голос/скорость TTS, громкость и
        устройства (читаются при следующем захвате), скиллы, beep, тайминги.
        Смена wake-фразы и модели STT требует Стоп→Старт (модели грузятся при старте).
        """
        self.cfg = new_cfg
        if self.trigger is not None and hasattr(self.trigger, "cfg"):
            self.trigger.cfg = new_cfg
        if self.router is not None:
            self.skills = load_skills(new_cfg)
            self.router = Router(new_cfg, self.skills)
        if self.tts is not None:
            from src.voice import TTS
            try:
                self.tts = TTS(new_cfg)
            except Exception as e:  # noqa: BLE001
                self.emit("error", message=f"Не удалось применить настройки TTS: {e}")
        self.emit("status", state=self.state)

    # --- внутреннее ---
    def _on_input_block(self, mono) -> None:
        from src.audio import rms_db
        self.emit("level", source="input", db=rms_db(mono))

    def _on_output_level(self, db: float) -> None:
        self.emit("level", source="output", db=db)

    def _wait_trigger(self, mode: str) -> bool:
        if mode == "wakeword":
            return self.trigger.wait(
                on_block=self._on_input_block,
                should_stop=self._stop.is_set,
                ptt=self._ptt,
            )
        # push_to_talk: ждём ручной активации из UI (или Enter в CLI)
        while not self._stop.is_set():
            if self._ptt.wait(timeout=0.1):
                self._ptt.clear()
                return True
        return False

    def _run(self) -> None:
        from src.voice import (STT, TTS, ModelNotReady, beep, end_phrases,
                               make_trigger, record_until_phrase,
                               record_until_silence, strip_end_phrases)

        self.set_state("loading")
        try:
            self.trigger = make_trigger(self.cfg)
            self.stt = STT(self.cfg)
            self.tts = TTS(self.cfg)
        except ModelNotReady as e:
            self.emit("error", message=f"Модель не готова: {e}")
            self.set_state("error")
            return
        except Exception as e:  # noqa: BLE001
            self.emit("error", message=f"Не удалось запустить голосовой режим: {e}")
            self.set_state("error")
            return

        self.skills = load_skills(self.cfg)
        self.router = Router(self.cfg, self.skills)
        mode = self.cfg.get("trigger", {}).get("mode", "push_to_talk")

        try:
            while not self._stop.is_set():
                if self._pause.is_set():
                    if self.state != "paused":
                        self.set_state("paused")
                    time.sleep(0.1)
                    continue

                self.set_state("listening")
                triggered = self._wait_trigger(mode)
                if self._stop.is_set():
                    break
                if not triggered or self._pause.is_set():
                    continue

                if self.cfg.get("trigger", {}).get("beep", True):
                    beep()

                self.set_state("recording")
                end_mode = self.cfg.get("trigger", {}).get("end_mode", "phrase")
                if end_mode == "silence":
                    audio = record_until_silence(self.cfg, on_block=self._on_input_block)
                else:
                    try:
                        vmodel = getattr(self.trigger, "model", None)
                        audio = record_until_phrase(
                            self.cfg, on_block=self._on_input_block, vosk_model=vmodel
                        )
                    except ModelNotReady as e:
                        self.emit("error", message=f"Режим фразы конца недоступен ({e}); жду паузу.")
                        audio = record_until_silence(self.cfg, on_block=self._on_input_block)

                self.set_state("thinking")
                text = self.stt.transcribe(audio)
                if end_mode != "silence":
                    text = strip_end_phrases(text, end_phrases(self.cfg))
                if not text:
                    self.emit("transcript", role="system", text="(не расслышал)")
                    continue
                self.emit("transcript", role="user", text=text)

                try:
                    reply = self.router.handle(text)
                except Exception as e:  # noqa: BLE001
                    reply = f"Произошла ошибка: {e}"
                    self.emit("error", message=str(e))
                self.emit("transcript", role="assistant", text=reply,
                          model=self.router.current)

                self.set_state("speaking")
                self.tts.say(reply, on_level=self._on_output_level)
        except Exception as e:  # noqa: BLE001
            self.emit("error", message=str(e))
            self.set_state("error")
            return
        finally:
            if self.state != "error":
                self.set_state("stopped")
