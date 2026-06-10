"""Pydantic-модели запросов. Зеркалят Zod-схемы фронта (shared/api)."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AudioSettings(BaseModel):
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    input_gain: float = Field(1.0, ge=0.0, le=2.0)
    output_gain: float = Field(1.0, ge=0.0, le=2.0)


class AssistantSettings(BaseModel):
    name: Optional[str] = None
    default_model: Optional[str] = None  # claude | gpt
    language: Optional[str] = None


class ModelSettings(BaseModel):
    model: Optional[str] = None


class TtsSettings(BaseModel):
    engine: Optional[str] = None         # edge | pyttsx3
    edge_voice: Optional[str] = None
    edge_rate: Optional[str] = None


class WakeSettings(BaseModel):
    phrases: Optional[list[str]] = None
    fuzzy: Optional[float] = Field(None, ge=0.0, le=1.0)


class TriggerSettings(BaseModel):
    mode: Optional[str] = None           # wakeword | push_to_talk
    end_mode: Optional[str] = None       # phrase | silence
    end_phrases: Optional[list[str]] = None
    silence_seconds: Optional[float] = None
    max_seconds: Optional[float] = None
    beep: Optional[bool] = None
    wakeword: Optional[WakeSettings] = None


class SkillsSettings(BaseModel):
    enabled: Optional[bool] = None


class SettingsUpdate(BaseModel):
    """Частичное обновление config.yaml. Передаются только изменённые секции."""
    audio: Optional[AudioSettings] = None
    assistant: Optional[AssistantSettings] = None
    models: Optional[dict[str, ModelSettings]] = None
    tts: Optional[TtsSettings] = None
    trigger: Optional[TriggerSettings] = None
    skills: Optional[SkillsSettings] = None


class KeysUpdate(BaseModel):
    """Новые значения ключей. Пустая строка/None — оставить без изменений."""
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None


class TtsTestRequest(BaseModel):
    text: str = "Привет! Это проверка голоса."
