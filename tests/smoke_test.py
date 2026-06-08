# -*- coding: utf-8 -*-
"""Офлайн-проверка маршрутизации: скиллы и переключение моделей без вызова API.
Запуск:  .\.venv\Scripts\python.exe -m tests.smoke_test
"""
from src.config import load_config
from src.skills import load_skills
from src.llm import Router


def main() -> None:
    cfg = load_config()
    router = Router(cfg, load_skills(cfg))
    ok = True

    # 1) Скиллы отрабатывают локально (без API).
    t = router.handle("сколько времени")
    print("время       ->", t)
    ok &= t.startswith("Сейчас")

    d = router.handle("какое сегодня число")
    print("дата        ->", d)
    ok &= d.startswith("Сегодня")

    # 2) Переключение модели без текста — мгновенный ответ, без API.
    s = router.handle("гпт")
    print("switch gpt  ->", s, "| current:", router.current)
    ok &= (router.current == "gpt")

    s = router.handle("клод")
    print("switch клод ->", s, "| current:", router.current)
    ok &= (router.current == "claude")

    # 3) Детектор модели вычленяет остаток фразы.
    key, rest = router._detect_model("гпт расскажи анекдот")
    print("detect      ->", key, "|", repr(rest))
    ok &= (key == "gpt" and rest == "расскажи анекдот")

    print("\nSMOKE:", "OK" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
