"""Сборка FastAPI: REST + WebSocket + раздача собранного фронта.

Запуск:  python -m src.server.app   (или .\run.ps1 -ui)
Слушает 127.0.0.1:8000 — только локально.
"""
from __future__ import annotations

import asyncio
import mimetypes
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# На Windows StaticFiles берёт MIME-типы из реестра, где .js нередко прописан как
# text/plain — тогда браузер отказывается исполнять ES-модули фронта и панель
# остаётся пустой. Принудительно задаём правильные типы для всего процесса.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("image/svg+xml", ".svg")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

# StaticFiles определяет Content-Type через mimetypes, а тот на Windows читает
# реестр, где .js часто прописан как text/plain — браузер тогда отказывается
# исполнять ES-модули и панель остаётся пустой. add_type выше это обычно чинит,
# но порядок инициализации mimetypes хрупкий; поэтому здесь жёстко перебиваем
# тип по расширению, не полагаясь на ОС вообще.
_FORCE_TYPES = {
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".css": "text/css",
    ".wasm": "application/wasm",
    ".svg": "image/svg+xml",
    ".json": "application/json",
}


class TypedStaticFiles(StaticFiles):
    def file_response(self, full_path, *args, **kwargs) -> Response:  # type: ignore[override]
        response = super().file_response(full_path, *args, **kwargs)
        forced = _FORCE_TYPES.get(Path(full_path).suffix.lower())
        if forced:
            response.headers["content-type"] = f"{forced}; charset=utf-8"
        # В деве запрещаем кэш: иначе один раз отклонённый по MIME модуль
        # «залипает» в кэше браузера и не перезапрашивается даже после фикса.
        response.headers["cache-control"] = "no-store"
        return response

from src.config import ROOT, load_config
from src.engine import AssistantEngine
from src.server.api import router as api_router
from src.server.events import EventBus

# Собранный фронт: в обычном запуске — apps/web/dist; в PyInstaller-exe он упакован
# в бандл (_MEIPASS/web_dist), а не лежит рядом с exe.
if getattr(sys, "frozen", False):
    DIST_DIR = Path(sys._MEIPASS) / "web_dist"  # type: ignore[attr-defined]
else:
    DIST_DIR = ROOT / "apps" / "web" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Связываем шину событий с текущим event loop, чтобы движок из своего
    # потока мог безопасно слать события в WebSocket-клиентов.
    app.state.bus.bind_loop(asyncio.get_running_loop())
    yield
    app.state.engine.stop()


def create_app() -> FastAPI:
    cfg = load_config()
    bus = EventBus()
    engine = AssistantEngine(cfg, on_event=bus.publish)

    app = FastAPI(title="Nixi.EXE — Home AI Assistant Control Panel", lifespan=lifespan)
    app.state.cfg = cfg
    app.state.bus = bus
    app.state.engine = engine

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.websocket("/ws")
    async def ws(websocket: WebSocket) -> None:
        await websocket.accept()
        queue = bus.register()
        try:
            await websocket.send_json({"type": "status", "state": engine.state})
            while True:
                event = await queue.get()
                await websocket.send_json(event)
        except WebSocketDisconnect:
            pass
        finally:
            bus.unregister(queue)

    # Прод: раздаём собранный фронт. В деве (dist нет) фронт поднимает Vite.
    if DIST_DIR.is_dir():
        app.mount("/", TypedStaticFiles(directory=str(DIST_DIR), html=True), name="static")
    else:
        @app.get("/")
        def _no_build() -> dict:
            return {
                "message": "Фронт не собран. В деве: cd apps/web && npm run dev "
                           "(откроется на :5173 с прокси на :8000). "
                           "Для прода: npm run build."
            }

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
