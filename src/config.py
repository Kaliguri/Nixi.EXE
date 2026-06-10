"""Загрузка и сохранение конфигурации и переменных окружения."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

# В собранном PyInstaller-exe изменяемые данные (config.yaml, .env, models/, logs/)
# лежат РЯДОМ с exe, а не во временной распаковке _MEIPASS — иначе правки конфига
# и модели не находились бы. В обычном запуске это корень проекта.
if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
ENV_PATH = ROOT / ".env"


def load_config(path: str | None = None) -> dict:
    load_dotenv(ENV_PATH)
    cfg_path = Path(path) if path else CONFIG_PATH
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_root"] = str(ROOT)
    return cfg


def _deep_merge(target, updates) -> None:
    """Рекурсивно вливает updates в target. Списки и скаляры заменяются целиком."""
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def save_config(updates: dict, path: str | None = None) -> dict:
    """Вливает частичные обновления в config.yaml, сохраняя комментарии и порядок.

    Возвращает свежий dict (как load_config), пригодный для engine.reload().
    """
    from ruamel.yaml import YAML

    cfg_path = Path(path) if path else CONFIG_PATH
    yaml_rt = YAML()
    yaml_rt.preserve_quotes = True
    with open(cfg_path, encoding="utf-8") as f:
        data = yaml_rt.load(f)

    updates = {k: v for k, v in updates.items() if k != "_root"}
    _deep_merge(data, updates)

    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml_rt.dump(data, f)

    return load_config(str(cfg_path))


# --- .env (API-ключи) ---

def read_env() -> dict:
    """Читает пары KEY=VALUE из .env (без раскрытия в окружение)."""
    result: dict[str, str] = {}
    if not ENV_PATH.exists():
        return result
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def mask_key(value: str | None) -> str | None:
    """Маскирует ключ для отдачи в браузер: первые 3 и последние 4 символа."""
    if not value:
        return None
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:3]}…{value[-4:]}"


def write_env(updates: dict[str, str | None]) -> None:
    """Обновляет/добавляет ключи в .env, не трогая прочие строки и комментарии.

    Значение None у ключа удаляет строку. Также применяет ключи к os.environ,
    чтобы изменения подхватились без перезапуска процесса.
    """
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if "=" in s and not s.startswith("#"):
            key = s.split("=", 1)[0].strip()
            if key in updates:
                seen.add(key)
                if updates[key] is not None:
                    out.append(f"{key}={updates[key]}")
                continue
        out.append(line)
    for key, value in updates.items():
        if key not in seen and value is not None:
            out.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")

    for key, value in updates.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
