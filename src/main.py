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


def voice_loop(router: Router, cfg: dict) -> None:
    from src.voice import make_trigger, beep, STT, TTS, ModelNotReady, record_until_silence

    print(f"=== {router.name}: голосовой режим ===")
    print("Загружаю модели...")
    try:
        trigger = make_trigger(cfg)
        stt = STT(cfg)
    except ModelNotReady as e:
        print(f"\n[!] Голосовой режим недоступен: модель не готова.\n{e}\n"
              "Пока можешь пользоваться текстовым режимом:  .\\run.ps1")
        return
    except Exception as e:  # noqa: BLE001
        print(f"\n[!] Не удалось запустить голосовой режим: {e}\n"
              "Проверь модель/конфиг. Текстовый режим работает:  .\\run.ps1")
        return
    tts = TTS(cfg)
    print("Готово.")

    mode = cfg.get("trigger", {}).get("mode", "push_to_talk")
    if mode == "wakeword":
        phrase = cfg["trigger"]["wakeword"]["phrases"][0]
        print(f"Слушаю фразу активации: «{phrase}» (Ctrl+C — выход)")
    tts.say(f"Привет! Я {router.name}.")

    try:
        while True:
            if not trigger.wait():
                break
            if cfg.get("trigger", {}).get("beep", True):
                beep()
            print("Слушаю команду...")
            audio = record_until_silence(cfg)
            text = stt.transcribe(audio)
            if not text:
                print("(не расслышал)")
                continue
            print(f"Ты(голос)> {text}")
            try:
                reply = router.handle(text)
            except Exception as e:  # noqa: BLE001
                reply = f"Произошла ошибка: {e}"
            print(f"{router.name}> {reply}\n")
            tts.say(reply)
    except KeyboardInterrupt:
        print("\nВыход.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Домашний голосовой LLM-ассистент")
    ap.add_argument("--voice", action="store_true",
                    help="голосовой режим (микрофон + динамик)")
    ap.add_argument("--config", default=None, help="путь к config.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)
    skills = load_skills(cfg)
    router = Router(cfg, skills)

    if args.voice:
        voice_loop(router, cfg)
    else:
        text_loop(router)


if __name__ == "__main__":
    main()
