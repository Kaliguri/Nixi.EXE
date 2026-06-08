"""Локальные скиллы — простые команды без обращения к LLM.

Чтобы добавить свой скилл: наследуйся от Skill, реализуй match() и run(),
и добавь экземпляр в Skills.__init__.
"""
import datetime
import os
import webbrowser


class Skill:
    name = "base"

    def match(self, text: str) -> bool:
        return False

    def run(self, text: str) -> str:
        return ""


class MusicSkill(Skill):
    name = "music"
    KEYWORDS = ["включи музык", "поставь музык", "играй музык", "врубай музык",
                "включи песн", "поставь песн"]

    def match(self, text: str) -> bool:
        low = text.lower()
        return any(k in low for k in self.KEYWORDS)

    def run(self, text: str) -> str:
        # Сначала пробуем Spotify (по протоколу spotify:), иначе веб-плеер.
        try:
            os.startfile("spotify:")  # noqa: S606 (Windows)
            return "Включаю музыку в Spotify."
        except Exception:
            webbrowser.open("https://music.youtube.com")
            return "Открываю YouTube Music."


class TimeSkill(Skill):
    name = "time"
    KEYWORDS = ["который час", "сколько времени", "сколько сейчас времени",
                "какое сегодня число", "какая сегодня дата"]

    def match(self, text: str) -> bool:
        low = text.lower()
        return any(k in low for k in self.KEYWORDS)

    def run(self, text: str) -> str:
        now = datetime.datetime.now()
        if "число" in text.lower() or "дата" in text.lower():
            return now.strftime("Сегодня %d.%m.%Y.")
        return now.strftime("Сейчас %H:%M.")


class Skills:
    def __init__(self, enabled: bool = True):
        self.skills = [MusicSkill(), TimeSkill()] if enabled else []

    def match(self, text: str):
        for s in self.skills:
            if s.match(text):
                return s
        return None


def load_skills(cfg: dict) -> Skills:
    return Skills(cfg.get("skills", {}).get("enabled", True))
