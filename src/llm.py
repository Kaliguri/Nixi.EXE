"""LLM-агенты (Claude / GPT / Gemini) и роутер выбора модели."""
import os
from typing import List, Dict

SYSTEM_PROMPT = (
    "Ты — голосовой ассистент по имени {name}. "
    "Отвечай кратко и по делу, на русском, разговорным языком. "
    "Не используй markdown, списки и эмодзи — твой ответ будет озвучен вслух. "
    "Если ответ длинный — сократи до сути в пару предложений."
)


class ClaudeAgent:
    def __init__(self, assistant_name: str, model: str):
        from anthropic import Anthropic

        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY не задан в .env")
        self.client = Anthropic(api_key=key)
        self.model = model
        self.system = SYSTEM_PROMPT.format(name=assistant_name)

    def chat(self, history: List[Dict]) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=600,
            system=self.system,
            messages=history,
        )
        return "".join(b.text for b in resp.content if b.type == "text").strip()


class OpenAIAgent:
    def __init__(self, assistant_name: str, model: str):
        from openai import OpenAI

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY не задан в .env")
        self.client = OpenAI(api_key=key)
        self.model = model
        self.system = SYSTEM_PROMPT.format(name=assistant_name)

    def chat(self, history: List[Dict]) -> str:
        messages = [{"role": "system", "content": self.system}] + history
        resp = self.client.chat.completions.create(
            model=self.model, max_tokens=600, messages=messages
        )
        return (resp.choices[0].message.content or "").strip()


class GeminiAgent:
    """Google Gemini через OpenAI-совместимый эндпоинт.

    Переиспользуем уже установленный пакет openai с другим base_url —
    отдельный SDK ставить не нужно.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def __init__(self, assistant_name: str, model: str):
        from openai import OpenAI

        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY не задан в .env")
        self.client = OpenAI(api_key=key, base_url=self.BASE_URL)
        self.model = model
        self.system = SYSTEM_PROMPT.format(name=assistant_name)

    def chat(self, history: List[Dict]) -> str:
        messages = [{"role": "system", "content": self.system}] + history
        resp = self.client.chat.completions.create(
            model=self.model, max_tokens=600, messages=messages
        )
        return (resp.choices[0].message.content or "").strip()


_PROVIDERS = {"anthropic": ClaudeAgent, "openai": OpenAIAgent, "google": GeminiAgent}


class Router:
    """Маршрутизирует фразу: сначала локальные скиллы, потом нужная LLM.

    Двухуровневая схема как в Home Assistant: быстрые команды решаются
    скиллами без похода в сеть, остальное уходит в LLM.
    """

    def __init__(self, cfg: dict, skills):
        self.cfg = cfg
        self.skills = skills
        self.name = cfg["assistant"]["name"]
        self.model_cfgs: Dict[str, dict] = cfg["models"]
        self.current = cfg["assistant"]["default_model"]
        self._agents: Dict[str, object] = {}
        self.history: List[Dict] = []

    def _agent(self, key: str):
        if key not in self._agents:
            mc = self.model_cfgs[key]
            cls = _PROVIDERS[mc["provider"]]
            self._agents[key] = cls(self.name, mc["model"])
        return self._agents[key]

    def _detect_model(self, text: str):
        """Если фраза начинается с триггера модели — вернуть (ключ, остаток)."""
        low = text.lower().lstrip()
        for key, mc in self.model_cfgs.items():
            for trig in mc.get("triggers", []):
                if low.startswith(trig):
                    rest = text[len(trig):].lstrip(" ,.:!?-—")
                    return key, rest
        return None, text

    def handle(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""

        # 1) Локальные скиллы (мгновенно, без LLM)
        skill = self.skills.match(text)
        if skill is not None:
            return skill.run(text)

        # 2) Выбор / переключение модели
        key, rest = self._detect_model(text)
        if key is not None:
            switched = key != self.current
            self.current = key
            text = rest
            if not text:  # просто "переключись на клода"
                return f"Готово, теперь отвечает {key.upper()}."
            del switched

        # 3) Запрос к LLM с сохранением контекста
        agent = self._agent(self.current)
        self.history.append({"role": "user", "content": text})
        reply = agent.chat(self.history)
        self.history.append({"role": "assistant", "content": reply})
        self.history = self.history[-12:]  # держим последние ~6 реплик
        return reply
