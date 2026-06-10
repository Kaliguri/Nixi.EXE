"""REST-эндпоинты панели управления."""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from src.audio import list_devices
from src.config import mask_key, read_env, save_config, write_env
from src.server.schemas import KeysUpdate, SettingsUpdate, TtsTestRequest

router = APIRouter(prefix="/api")


def _engine(request: Request):
    return request.app.state.engine


def serialize_settings(cfg: dict) -> dict:
    a = cfg.get("audio") or {}
    models = cfg.get("models") or {}
    tcfg = cfg.get("trigger") or {}
    wake = tcfg.get("wakeword") or {}
    tts = cfg.get("tts") or {}
    assistant = cfg.get("assistant") or {}
    return {
        "audio": {
            "input_device": a.get("input_device"),
            "output_device": a.get("output_device"),
            "input_gain": float(a.get("input_gain", 1.0)),
            "output_gain": float(a.get("output_gain", 1.0)),
        },
        "assistant": {
            "name": assistant.get("name", ""),
            "default_model": assistant.get("default_model", "claude"),
            "language": assistant.get("language", "ru"),
        },
        "models": {
            key: {
                "provider": mc.get("provider"),
                "model": mc.get("model"),
                "triggers": mc.get("triggers", []),
            }
            for key, mc in models.items()
        },
        "tts": {
            "engine": tts.get("engine", "edge"),
            "edge_voice": tts.get("edge_voice", ""),
            "edge_rate": tts.get("edge_rate", "+0%"),
        },
        "trigger": {
            "mode": tcfg.get("mode", "wakeword"),
            "end_mode": tcfg.get("end_mode", "phrase"),
            "end_phrases": tcfg.get("end_phrases", []),
            "silence_seconds": tcfg.get("silence_seconds", 1.2),
            "max_seconds": tcfg.get("max_seconds", 15),
            "beep": tcfg.get("beep", True),
            "wakeword": {
                "phrases": wake.get("phrases", []),
                "fuzzy": wake.get("fuzzy", 0.7),
            },
        },
        "skills": {"enabled": (cfg.get("skills") or {}).get("enabled", True)},
    }


# --- состояние и управление движком ---

@router.get("/state")
def get_state(request: Request) -> dict:
    return _engine(request).snapshot()


@router.post("/engine/{action}")
def engine_action(action: str, request: Request) -> dict:
    engine = _engine(request)
    handlers = {
        "start": engine.start,
        "stop": engine.stop,
        "pause": engine.pause,
        "resume": engine.resume,
        "ptt": engine.push_to_talk,
    }
    fn = handlers.get(action)
    if fn is None:
        raise HTTPException(status_code=404, detail=f"Неизвестное действие: {action}")
    fn()
    return engine.snapshot()


# --- устройства ---

@router.get("/devices")
async def get_devices() -> dict:
    # query_devices синхронный — уводим в пул, чтобы не блокировать loop.
    return await run_in_threadpool(list_devices)


# --- настройки ---

@router.get("/settings")
def get_settings(request: Request) -> dict:
    return serialize_settings(_engine(request).cfg)


@router.put("/settings")
def put_settings(body: SettingsUpdate, request: Request) -> dict:
    engine = _engine(request)
    updates = body.model_dump(exclude_unset=True)
    if updates:
        new_cfg = save_config(updates)
        engine.reload(new_cfg)
        request.app.state.cfg = new_cfg
    return serialize_settings(engine.cfg)


# --- API-ключи (маскированно) ---

@router.get("/keys")
def get_keys() -> dict:
    env = read_env()
    return {
        "ANTHROPIC_API_KEY": mask_key(env.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")),
        "OPENAI_API_KEY": mask_key(env.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        "GEMINI_API_KEY": mask_key(env.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")),
    }


@router.put("/keys")
def put_keys(body: KeysUpdate, request: Request) -> dict:
    # Пустые/None — оставляем как есть (не затираем существующий ключ).
    updates = {k: v for k, v in body.model_dump().items() if v}
    if updates:
        write_env(updates)
        engine = _engine(request)
        engine.reload(engine.cfg)  # сбросить закэшированные LLM-агенты
    return get_keys()


# --- TTS: голоса и тест ---

@router.get("/voices")
async def get_voices() -> list[dict]:
    import edge_tts

    voices = await edge_tts.list_voices()
    return [
        {
            "short_name": v["ShortName"],
            "gender": v.get("Gender", ""),
            "name": v.get("FriendlyName", v["ShortName"]),
        }
        for v in voices
        if v.get("Locale", "").startswith("ru")
    ]


@router.post("/tts/test")
async def tts_test(body: TtsTestRequest, request: Request) -> dict:
    cfg = _engine(request).cfg

    def _play() -> None:
        from src.voice import TTS
        TTS(cfg).say(body.text)

    try:
        await run_in_threadpool(_play)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True}


# --- скиллы ---

@router.get("/skills")
def get_skills(request: Request) -> dict:
    from src.skills import Skills

    cfg = _engine(request).cfg
    available = Skills(enabled=True).skills
    return {
        "enabled": (cfg.get("skills") or {}).get("enabled", True),
        "skills": [{"name": s.name} for s in available],
    }
