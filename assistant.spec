# PyInstaller-спека: standalone CPU-сборка ассистента (трей + веб-панель + голос).
# Сборка: см. build-exe.ps1 (создаёт чистое CPU-окружение и зовёт pyinstaller).
#
# Что НЕ кладём внутрь и что возим рядом с exe (frozen ROOT = папка exe):
#   config.yaml, .env, models/, wake_phrases.txt, logs/.
# Внутрь бандла кладём собранный фронт (apps/web/dist -> web_dist).
from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas, binaries, hiddenimports = [], [], []

# Пакеты с динамическими импортами / нативными DLL / данными — тащим целиком.
for pkg in (
    "ctranslate2",       # движок faster-whisper (CPU)
    "faster_whisper",
    "vosk",              # wake word (нативные DLL + модельные данные пакета)
    "sounddevice",       # PortAudio DLL едет в _sounddevice_data
    "soundfile",         # libsndfile
    "edge_tts",          # TTS по умолчанию (нужен интернет)
    "pyttsx3",           # офлайн TTS (SAPI5) — фолбэк
    "comtypes",          # нужен pyttsx3/sapi5 на Windows
    "anthropic",
    "openai",
    "uvicorn",           # много динамических подмодулей (protocols/loops)
    "fastapi",
    "starlette",
    "huggingface_hub",   # faster-whisper тянет модели/таблицы через него
    "tokenizers",
):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Собранный фронт панели.
datas += [("apps/web/dist", "web_dist")]

# Наши модули с ленивыми импортами — на всякий случай явно.
hiddenimports += [
    "src.voice", "src.audio", "src.skills", "src.llm",
    "src.engine", "src.server.app", "src.server.api",
    "src.server.events", "src.server.schemas",
    "websockets", "h11", "anyio",
]

a = Analysis(
    ["src/tray.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "torch", "tensorflow"],  # CPU-сборка: ничего тяжёлого лишнего
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Gaida",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,            # без окна консоли (трей)
    icon="assets/tray/assistant.ico",
)
