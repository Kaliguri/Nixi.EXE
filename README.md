<!-- ============================================================
     README.md — single file, BILINGUAL via in-page anchors.
     EN block first (canonical), RU block below.
     ============================================================ -->

<a id="top"></a>

<p>
  <a href="#english"><b>English</b></a>
  &nbsp;·&nbsp;
  <a href="#русский"><b>Русский</b></a>
</p>

# Nixi.EXE — Home AI Assistant

> A home voice assistant powered by cloud LLMs — say “Nixi”, speak, get a spoken answer. Switch between Claude, GPT and Gemini by voice.

<p>
  <img alt="Status" src="https://img.shields.io/badge/Status-in_development-f5a623?style=flat-square"/>
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white"/>
  <img alt="License: All rights reserved" src="https://img.shields.io/badge/License-All_rights_reserved-red?style=flat-square"/>
</p>

|                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Core**                | <img alt="Python" src="https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **LLM providers**       | <img alt="Anthropic Claude" src="https://img.shields.io/badge/Anthropic_Claude-D97757?style=flat-square&logo=anthropic&logoColor=white"/> <img alt="OpenAI GPT" src="https://img.shields.io/badge/OpenAI_GPT-412991?style=flat-square&logo=openai&logoColor=white"/> <img alt="Google Gemini" src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white"/>                                                                                                                                                                                                                                                                                                                                   |
| **Speech**              | <a href="https://github.com/SYSTRAN/faster-whisper"><img alt="faster-whisper" src="https://img.shields.io/badge/faster--whisper_(STT)-1f6feb?style=flat-square"/></a> <a href="https://alphacephei.com/vosk/"><img alt="Vosk" src="https://img.shields.io/badge/Vosk_(wake_word)-1f6feb?style=flat-square"/></a> <a href="https://github.com/rany2/edge-tts"><img alt="edge-tts" src="https://img.shields.io/badge/edge--tts-1f6feb?style=flat-square"/></a> <img alt="CUDA" src="https://img.shields.io/badge/CUDA_12-76B900?style=flat-square&logo=nvidia&logoColor=white"/>                                                                                                                                                                |
| **Web panel — front**   | <img alt="React" src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black"/> <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white"/> <img alt="Vite" src="https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white"/> <img alt="Tailwind CSS" src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white"/> <a href="https://zod.dev"><img alt="Zod" src="https://img.shields.io/badge/Zod-3E67B1?style=flat-square"/></a> <a href="https://www.i18next.com"><img alt="i18next" src="https://img.shields.io/badge/i18next-26A69A?style=flat-square"/></a> |
| **Web panel — back**    | <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/> <img alt="Pydantic" src="https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white"/> <a href="https://www.uvicorn.org"><img alt="Uvicorn" src="https://img.shields.io/badge/Uvicorn-1f6feb?style=flat-square"/></a> <img alt="WebSocket" src="https://img.shields.io/badge/WebSocket-8957e5?style=flat-square"/>                                                                                                                                                                                                                                                                    |
| **Desktop / packaging** | <a href="https://pyinstaller.org"><img alt="PyInstaller" src="https://img.shields.io/badge/PyInstaller-1f6feb?style=flat-square"/></a> <a href="https://github.com/moses-palmer/pystray"><img alt="pystray" src="https://img.shields.io/badge/pystray_(tray_icon)-1f6feb?style=flat-square"/></a>                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Patterns**            | <img alt="Two-tier Router" src="https://img.shields.io/badge/Two--tier_Router-8957e5?style=flat-square"/> <img alt="State Machine" src="https://img.shields.io/badge/State_Machine-8957e5?style=flat-square"/> <img alt="Feature-Sliced Design" src="https://img.shields.io/badge/Feature--Sliced_Design-8957e5?style=flat-square"/> <img alt="Event bus" src="https://img.shields.io/badge/Event_bus-8957e5?style=flat-square"/>                                                                                                                                                                                                                                                                                                             |

<p>
  <a href="DISTRIBUTION.md"><b>📦 Standalone build</b></a>
  &nbsp;·&nbsp;
  <a href="ROADMAP.md"><b>🗺 Roadmap</b></a>
  &nbsp;·&nbsp;
  <a href="config.yaml"><b>⚙ Configuration</b></a>
</p>

---

<details>
<summary><b>Screenshots</b></summary>

**Web control panel**

> 🖼 Coming soon — control panel screenshots (devices, VU-meters, live dialog, settings tabs).

</details>

---

## English

<a href="#top"><b>[↑ Back to top]</b></a>

**Nixi.EXE** is a home voice assistant for Windows that behaves like a smart speaker but thinks with cloud LLMs. Say the wake word **“Nixi”**, speak a command, and get a spoken reply — with the model of your choice (**Claude**, **GPT** or **Gemini**), switchable by voice mid-conversation. Speech recognition runs locally on `faster-whisper` (GPU with CPU fallback), the reply is voiced through a neural Russian voice, and a two-tier router answers simple commands instantly via local skills without ever calling the network. A browser control panel gives you devices, live VU-meters, the running dialog and all settings.

> **What this project demonstrates:** a custom Python orchestrator (not Home Assistant) with local STT/TTS, a state-machine engine driving a background voice loop, real-time UI over WebSocket, a full-stack React + FastAPI panel in Feature-Sliced Design, and a standalone PyInstaller build for distribution without a Python install.

### Key features

| Feature                         | Description                                                                                                                                                                |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Multi-LLM, voice-switchable** | Claude, GPT and Gemini side by side. Say “Claude, …” / “GPT, …” to address or switch models on the fly; each model and its triggers are configurable.                      |
| **Wake word activation**        | Always-on listening for the name “Nixi” via an offline Vosk spotter with fuzzy matching, plus a voice-calibration tool. Push-to-talk is an alternative.                    |
| **Two end-of-command modes**    | Finish a command by an **end phrase** (e.g. “go ahead”, default) for long dictation, or by a **silence pause** — switchable in settings.                                   |
| **Local + cloud routing**       | A two-tier router resolves quick commands (music, time/date) through local skills instantly; everything else goes to the LLM with short conversation memory.               |
| **Local speech I/O**            | `faster-whisper` STT on CUDA with a CPU/int8 fallback; neural `edge-tts` Russian voice with an offline `pyttsx3` fallback.                                                 |
| **Browser control panel**       | FastAPI + React panel: input/output device pickers, gain, live VU-meters, start/stop/pause, status, live dialog log, settings tabs and masked API keys — all on localhost. |
| **Tray app & standalone .exe**  | Windows tray icon to run the panel and manage the server (+ autostart), and a CPU-only PyInstaller build that ships without Python.                                        |

---

## Русский

<a href="#top"><b>[↑ Наверх]</b></a>

> Домашний голосовой ассистент на облачных LLM — скажи «Никси», говори, получай голосовой ответ. Переключай Claude, GPT и Gemini голосом.

**Nixi.EXE** — домашний голосовой ассистент для Windows: ведёт себя как умная колонка, но думает облачными LLM. Скажи фразу активации **«Никси»**, произнеси команду — и получи голосовой ответ от выбранной модели (**Claude**, **GPT** или **Gemini**), переключаемой голосом прямо посреди диалога. Распознавание речи (STT) работает локально на `faster-whisper` (GPU с фолбэком на CPU), ответ озвучивается русским нейро-голосом, а двухуровневый роутер (router) отвечает на простые команды мгновенно через локальные скиллы, не обращаясь в сеть. Веб-панель в браузере даёт устройства, живые VU-метры, лог диалога и все настройки.

> **Что демонстрирует проект:** кастомный Python-оркестратор (не Home Assistant) с локальными STT/TTS, движок-конечный автомат (state machine) для фонового голосового цикла, real-time UI поверх WebSocket, full-stack панель React + FastAPI в архитектуре Feature-Sliced Design и сборку standalone-`.exe` (PyInstaller) для раздачи без установленного Python.

### Ключевые возможности

| Возможность                             | Описание                                                                                                                                                                               |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Несколько LLM, переключение голосом** | Claude, GPT и Gemini рядом. Скажи «Клод, …» / «ГПТ, …», чтобы адресовать запрос или переключить модель на лету; модели и их триггеры настраиваются.                                    |
| **Активация по фразе (wake word)**      | Постоянное прослушивание имени «Никси» через офлайн-споттер Vosk с нечётким совпадением + калибровка под голос. Альтернатива — push-to-talk.                                           |
| **Два режима конца команды**            | Завершай команду **фразой конца** (например «выполняй», по умолчанию) — удобно для длинных команд — или **паузой (тишиной)**; переключается в настройках.                              |
| **Локально + облако (роутинг)**         | Двухуровневый роутер решает быстрые команды (музыка, время/дата) локальными скиллами мгновенно; остальное уходит в LLM с короткой памятью диалога.                                     |
| **Локальные речь-ввод/вывод**           | STT `faster-whisper` на CUDA с фолбэком на CPU/int8; нейро-голос `edge-tts` (рус.) с офлайн-фолбэком `pyttsx3`.                                                                        |
| **Веб-панель в браузере**               | Панель FastAPI + React: выбор устройств ввода/вывода, громкость, живые VU-метры, старт/стоп/пауза, статус, лог диалога, вкладки настроек и маскированные API-ключи — всё на localhost. |
| **Трей-приложение и standalone .exe**   | Иконка в трее Windows для запуска панели и управления сервером (+ автозапуск) и CPU-сборка PyInstaller, которая работает без Python.                                                   |

---

<details id="for-developers">
<summary><b>For developers</b></summary>

<br>

### How it works

```
voice ──▶ record (VAD / end phrase) ──▶ STT (faster-whisper, GPU) ──▶ Router
                                                                        │
                            ┌── local skill? ──── yes ─────────────────┤  ("play music", "what time is it")
                            │                                           │
                            └── no ──▶ LLM (Claude / GPT / Gemini) ──────┘
                                                                        │
                                                       reply ──▶ TTS ──▶ speaker
```

Two-tier processing like Home Assistant: simple commands are handled by skills instantly; everything else goes to an LLM. The `AssistantEngine` runs this loop in a background thread as a state machine (`stopped | loading | listening | recording | thinking | speaking | paused | error`) and emits events (status, audio levels, transcript, errors) consumed by both the web panel (over WebSocket) and the CLI.

### Local development

```powershell
# 1. Install (creates .venv, installs deps, creates .env)
.\setup.ps1            # core + voice stack
# .\setup.ps1 -GPU       # + CUDA-accelerated recognition (~1GB, needs NVIDIA)
# .\setup.ps1 -CoreOnly  # core only (no voice)

# 2. Download voice models
.\.venv\Scripts\python.exe download_model.py        # command recognition (faster-whisper, ~484MB)
.\.venv\Scripts\python.exe download_wake_model.py   # wake phrase (Vosk, ~45MB)

# 3. Put your keys in .env
#    ANTHROPIC_API_KEY=...   OPENAI_API_KEY=...   GEMINI_API_KEY=...

# 4. Run
.\run.ps1              # text mode (console chat)
.\run.ps1 -voice       # voice mode (mic + speaker)
.\run.ps1 -ui          # web control panel (http://127.0.0.1:8000)
```

Web panel (frontend):

```powershell
# Prod: build the front and serve a single process on :8000
cd apps/web; npm install; npm run build; cd ../..
.\run.ps1 -ui

# Dev: backend + Vite dev server with HMR (two terminals)
.\run.ps1 -ui                      # backend on :8000
cd apps/web; npm run dev           # front on :5173 (proxies /api and /ws to :8000)
```

The frontend uses **Feature-Sliced Design** (`app / pages / widgets / features / shared`), TanStack Query for server state, Zod schemas mirrored by Pydantic models on the backend, and `react-i18next` (EN/RU). Settings are saved to `config.yaml` (comments preserved via ruamel), keys live in `.env` (returned to the browser masked only). The server binds `127.0.0.1` — local only.

### Configuration

Everything lives in [`config.yaml`](config.yaml): assistant name and default model, per-provider model + triggers, STT (Whisper model, `cuda`/`cpu`), TTS, trigger mode (`wakeword` / `push_to_talk`), end-of-command mode (`phrase` / `silence`) and end phrases, wake phrases and audio devices. Without `-GPU`, set `stt.device: cpu` and `compute_type: int8`.

### Project layout

```
config.yaml            config
.env                   API keys (not in git)
setup.ps1 / run.ps1    install & run
src/
  main.py              entry point, text/voice loops (on top of engine)
  config.py            load/save config and .env
  llm.py               Claude/GPT/Gemini agents + Router
  skills.py            local skills
  voice.py             recording, STT, TTS, triggers, end-of-command
  audio.py             devices, gain, levels (VU)
  engine.py            managed engine (thread + events) for UI and CLI
  tray.py              Windows tray icon
  server/              FastAPI: REST + WebSocket (app, api, events, schemas)
apps/web/              web panel (Vite/React/TS/Tailwind, Feature-Sliced Design)
```

### Build a standalone .exe

A CPU-only PyInstaller build ships without a Python install — see [DISTRIBUTION.md](DISTRIBUTION.md). `build-exe.ps1` + `assistant.spec` produce the binary in a clean CPU `.venv-build`; self-check via `--selftest`.

</details>

---

## License

© 2026 Kaliguri. All rights reserved.

This repository is public for portfolio and demonstration purposes only.
No license is granted to use, copy, modify, or distribute any part of it
without prior written permission from the author.

See [LICENSE.md](LICENSE.md) for details.
