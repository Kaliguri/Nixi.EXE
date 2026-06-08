"""Точка входа. Текстовый режим по умолчанию, --voice для голосового."""
import argparse
import sys

# Windows-консоль часто не в UTF-8 — принудительно переключаем потоки,
# иначе кириллица в выводе/вводе искажается.
for _stream in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

from src.config import load_config
from src.skills import load_skills
from src.llm import Router


def text_loop(router: Router) -> None:
    print(f"=== {router.name}: текстовый режим ===")
    print("Пиши сообщение. 'выход' — закончить.")
    print(f"Текущая модель: {router.current.upper()}. "
          "Скажи 'клод ...' или 'гпт ...' чтобы переключиться.\n")
    while True:
        try:
            user = input("Ты> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in ("выход", "exit", "quit", "стоп"):
            break
        try:
            reply = router.handle(user)
        except Exception as e:  # noqa: BLE001
            reply = f"[ошибка] {e}"
        print(f"{router.name}> {reply}\n")


def voice_loop(cfg: dict) -> None:
    """Консольный голосовой режим поверх AssistantEngine (печатает события)."""
    import time

    from src.engine import AssistantEngine

    name = cfg["assistant"]["name"]
    print(f"=== {name}: голосовой режим ===")

    def on_event(evt: dict) -> None:
        t = evt.get("type")
        if t == "status":
            state = evt["state"]
            if state == "loading":
                print("Загружаю модели...")
            elif state == "listening":
                print("Слушаю...")
        elif t == "transcript":
            role = evt.get("role")
            if role == "user":
                print(f"Ты(голос)> {evt['text']}")
            elif role == "assistant":
                print(f"{name}> {evt['text']}\n")
            elif role == "system":
                print(evt["text"])
        elif t == "error":
            print(f"[!] {evt['message']}")

    engine = AssistantEngine(cfg, on_event=on_event)
    engine.start()

    mode = cfg.get("trigger", {}).get("mode", "push_to_talk")
    try:
        if mode == "push_to_talk":
            while engine.state not in ("stopped", "error"):
                try:
                    input("\n[Enter — говорить, Ctrl+C — выход] ")
                except EOFError:
                    break
                engine.push_to_talk()
        else:
            while engine.state not in ("stopped", "error"):
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nВыход.")
    finally:
        engine.stop()


def main() -> None:
    ap = argparse.ArgumentParser(description="Домашний голосовой LLM-ассистент")
    ap.add_argument("--voice", action="store_true",
                    help="голосовой режим (микрофон + динамик)")
    ap.add_argument("--config", default=None, help="путь к config.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)

    if args.voice:
        voice_loop(cfg)
    else:
        skills = load_skills(cfg)
        router = Router(cfg, skills)
        text_loop(router)


if __name__ == "__main__":
    main()
