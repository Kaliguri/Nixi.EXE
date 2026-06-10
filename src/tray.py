"""Иконка ассистента в системном трее Windows.

Лёгкий лаунчер поверх веб-панели (см. src/server/app.py):
  * двойной ЛКМ по иконке   — открыть панель в браузере;
  * ПКМ — меню              — запуск/остановка/перезапуск сервера,
                              переключение автозапуска с Windows, выход.

Сервер поднимается как дочерний процесс (без окна консоли), его вывод
пишется в logs/server.log. Цвет иконки отражает состояние сервера.

Запуск:
  .\run.ps1 -tray
  либо  pythonw src\tray.py  (без окна — так его дёргает ярлык и автозапуск)
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Файл запускается тремя путями: `python -m src.tray`, напрямую `pythonw src\tray.py`
# и как собранный PyInstaller-exe. В неморожёном запуске добавляем корень проекта в
# sys.path, чтобы импорты `src.*` работали независимо от cwd (в т.ч. из ключа
# автозапуска реестра, где cwd не задаётся). В exe модули уже в бандле.
_FROZEN = getattr(sys, "frozen", False)
if not _FROZEN:
    _ROOT = Path(__file__).resolve().parent.parent
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem

from src.config import ROOT, load_config

# Рабочая директория = где лежат изменяемые данные (config.yaml, models/, .env, logs/):
# рядом с exe в собранном виде, корень проекта — в обычном. Так относительные пути
# в config (models/...) и запись логов резолвятся правильно.
os.chdir(ROOT)

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"

LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Ключ автозапуска в реестре текущего пользователя.
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "HomeAIAssistant"

# Один экземпляр трея: держим занятым локальный порт-замок.
_LOCK_PORT = 49210

# Цвета статуса (server).
_COLORS = {
    "stopped": (120, 120, 120, 255),  # серый  — сервер не запущен
    "starting": (230, 180, 40, 255),  # жёлтый — поднимается
    "running": (60, 200, 90, 255),    # зелёный — отвечает
    "error": (220, 70, 60, 255),      # красный — упал/ошибка
}


# --- иконки -----------------------------------------------------------------

def _make_icon(color: tuple[int, int, int, int]) -> Image.Image:
    """Простая круглая иконка-индикатор заданного цвета."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, size - 6, size - 6], fill=color, outline=(20, 20, 20, 255), width=3)
    return img


_ICON_CACHE: dict[str, Image.Image] = {}


def _icon_for(state: str) -> Image.Image:
    if state not in _ICON_CACHE:
        _ICON_CACHE[state] = _make_icon(_COLORS.get(state, _COLORS["stopped"]))
    return _ICON_CACHE[state]


# --- автозапуск (реестр) -----------------------------------------------------

def _autostart_command() -> str:
    """Команда автозапуска.

    В собранном exe — просто путь к самому exe. В обычном запуске — pythonw с
    модулем трея (без окна консоли).
    """
    if _FROZEN:
        return f'"{Path(sys.executable).resolve()}"'
    pythonw = Path(sys.executable)
    if pythonw.name.lower() == "python.exe":
        cand = pythonw.with_name("pythonw.exe")
        if cand.exists():
            pythonw = cand
    return f'"{pythonw}" "{ROOT / "src" / "tray.py"}"'


def is_autostart_enabled() -> bool:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False
    except OSError:
        return False


def set_autostart(enable: bool) -> None:
    import winreg

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _autostart_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


# --- управление сервером -----------------------------------------------------

class ServerController:
    """Гоняет uvicorn в фоновом потоке внутри процесса трея.

    В отдельном потоке (не subprocess), чтобы одинаково работать и из .venv, и в
    собранном PyInstaller-exe, где `python -m src.server.app` не запустить. uvicorn
    штатно работает не в главном потоке — он просто не ставит обработчики сигналов.
    """

    def __init__(self) -> None:
        self._server = None  # uvicorn.Server
        self._thread: threading.Thread | None = None

    @staticmethod
    def is_port_open() -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex((HOST, PORT)) == 0

    def is_running(self) -> bool:
        if self._thread is not None and self._thread.is_alive():
            return True
        return self.is_port_open()  # вдруг сервер уже подняли извне

    def start(self) -> None:
        if self.is_running():
            return
        import uvicorn

        from src.server.app import create_app

        config = uvicorn.Config(create_app(), host=HOST, port=PORT, log_config=None)
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=10)
        self._server = None
        self._thread = None

    def restart(self) -> None:
        self.stop()
        time.sleep(0.5)
        self.start()

    def wait_until_ready(self, timeout: float = 30.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_port_open():
                return True
            if self._thread is not None and not self._thread.is_alive():
                return False  # поток сервера упал — смотри logs/app.log
            time.sleep(0.3)
        return False


# --- приложение трея ---------------------------------------------------------

class TrayApp:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.server = ServerController()
        self.icon = pystray.Icon(
            "home_ai_assistant",
            icon=_icon_for("stopped"),
            title="Домашний ассистент",
            menu=self._build_menu(),
        )
        self._stop_watcher = threading.Event()

    # меню --------------------------------------------------------------------

    def _build_menu(self) -> Menu:
        return Menu(
            MenuItem("Открыть панель", self._on_open, default=True),
            Menu.SEPARATOR,
            MenuItem(
                lambda _: "Остановить сервер" if self.server.is_running() else "Запустить сервер",
                self._on_toggle_server,
            ),
            MenuItem("Перезапустить сервер", self._on_restart),
            Menu.SEPARATOR,
            MenuItem(
                "Автозапуск с Windows",
                self._on_toggle_autostart,
                checked=lambda _: is_autostart_enabled(),
            ),
            Menu.SEPARATOR,
            MenuItem("Выход", self._on_quit),
        )

    # действия ----------------------------------------------------------------

    def _on_open(self, *_: object) -> None:
        def run() -> None:
            if not self.server.is_running():
                self._set_state("starting")
                self.server.start()
                if not self.server.wait_until_ready():
                    self._set_state("error")
                    self.icon.notify("Сервер не поднялся — см. logs/server.log", "Ошибка")
                    return
            self._set_state("running")
            webbrowser.open(URL)

        threading.Thread(target=run, daemon=True).start()

    def _on_toggle_server(self, *_: object) -> None:
        def run() -> None:
            if self.server.is_running():
                self.server.stop()
                self._set_state("stopped")
            else:
                self._set_state("starting")
                self.server.start()
                self._set_state("running" if self.server.wait_until_ready() else "error")
            self.icon.update_menu()

        threading.Thread(target=run, daemon=True).start()

    def _on_restart(self, *_: object) -> None:
        def run() -> None:
            self._set_state("starting")
            self.server.restart()
            self._set_state("running" if self.server.wait_until_ready() else "error")
            self.icon.update_menu()

        threading.Thread(target=run, daemon=True).start()

    def _on_toggle_autostart(self, *_: object) -> None:
        set_autostart(not is_autostart_enabled())
        self.icon.update_menu()

    def _on_quit(self, *_: object) -> None:
        self._stop_watcher.set()
        self.server.stop()
        self.icon.stop()

    # статус-иконка -----------------------------------------------------------

    def _set_state(self, state: str) -> None:
        self.server.state = state
        self.icon.icon = _icon_for(state)

    def _watch_loop(self) -> None:
        """Фоновая синхронизация цвета иконки с реальным состоянием порта."""
        while not self._stop_watcher.wait(3.0):
            if self.server.state in ("starting",):
                continue
            actual = "running" if self.server.is_running() else "stopped"
            if actual != self.server.state:
                self._set_state(actual)
                self.icon.update_menu()

    # запуск ------------------------------------------------------------------

    def run(self) -> None:
        tray_cfg = self.cfg.get("tray") or {}
        if tray_cfg.get("start_server", True):
            self._set_state("starting")
            self.server.start()
        if tray_cfg.get("open_browser_on_launch", False):
            self._on_open()
        threading.Thread(target=self._watch_loop, daemon=True).start()
        self.icon.run()


def _acquire_single_instance() -> socket.socket | None:
    """Возвращает сокет-замок или None, если трей уже запущен."""
    lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock.bind((HOST, _LOCK_PORT))
        lock.listen(1)
        return lock
    except OSError:
        return None


def _redirect_output_to_log() -> None:
    """Без консоли (exe/pythonw) stdout/stderr = None — шлём вывод в logs/app.log,
    чтобы ошибки сервера и трейсбеки было где смотреть."""
    if sys.stdout is not None and sys.stderr is not None:
        return
    LOG_DIR.mkdir(exist_ok=True)
    log = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    sys.stdout = log
    sys.stderr = log


def _selftest() -> int:
    """`Gaida.exe --selftest` — проверка, что тяжёлые либы реально грузятся в сборке.

    Результат пишется в logs/selftest.log (у exe нет консоли). Возвращает код выхода.
    """
    LOG_DIR.mkdir(exist_ok=True)
    out = LOG_DIR / "selftest.log"
    mods = [
        "faster_whisper", "ctranslate2", "vosk", "sounddevice",
        "soundfile", "edge_tts", "pyttsx3", "anthropic", "openai",
        "fastapi", "uvicorn",
    ]
    lines, ok = [], True
    for m in mods:
        try:
            __import__(m)
            lines.append(f"OK   {m}")
        except Exception as e:  # noqa: BLE001
            ok = False
            lines.append(f"FAIL {m}: {e!r}")
    lines.append("RESULT: " + ("ALL OK" if ok else "HAS FAILURES"))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


def main() -> None:
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    _redirect_output_to_log()
    lock = _acquire_single_instance()
    if lock is None:
        # Уже запущен другой экземпляр — тихо выходим.
        return
    try:
        TrayApp().run()
    finally:
        lock.close()


if __name__ == "__main__":
    main()
