# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Dev Commands

```bash
# Install all dependencies (from project root)
cd packages/teacher-backend && pip install -r requirements.txt
cd packages/student-backend && pip install -r requirements.txt
cd packages/teacher-app && npm install
cd packages/student-app && npm install

# Start all 4 services at once (PowerShell, admin recommended)
.\scripts\dev-start.ps1

# Or start individually from root:
npm run dev:teacher-backend    # Python backend → 127.0.0.1:8771
npm run dev:student-backend    # Python backend → 127.0.0.1:8772 (needs admin)
npm run dev:teacher            # Vite + Electron → 127.0.0.1:5173
npm run dev:student            # Vite + Electron → 127.0.0.1:5174

# Build a single frontend (type-check + Vite + electron-builder)
cd packages/teacher-app && npm run build:win
cd packages/student-app && npm run build:win

# Build a single Python backend
cd packages/teacher-backend && pyinstaller main.spec --noconfirm
cd packages/student-backend && pyinstaller main.spec --noconfirm

# Full production build (PyInstaller + electron-builder)
scripts\build-teacher.bat
scripts\build-student.bat
```

There is no test suite, linter, or formatter configured.

## Architecture

This is a LAN classroom network-access-control system. Two machines are involved:

**Teacher machine** runs two processes:
- `teacher-backend` (Python FastAPI) — three concurrent Uvicorn servers: WebSocket server for student connections, local HTTP API for the Electron frontend, external HTTP API for third-party tools
- `teacher-app` (Electron + Vue 3) — desktop UI for managing student machines

**Student machine** runs two processes:
- `student-backend` (Python FastAPI agent) — WebSocket client to teacher, local HTTP API, DNS proxy, Windows firewall/route/DNS manipulation via PowerShell, system tray, PyQt6 lock screen
- `student-app` (Electron + Vue 3) — local status/config UI

In dev mode, each Electron main process spawns its Python backend as a child process. In production, the Electron app bundles the PyInstaller-compiled `.exe` via `extraResources` and spawns it from `process.resourcesPath`.

## Port Map

| Port | Service | Listener |
|------|---------|----------|
| 8765 | Teacher WebSocket | `0.0.0.0` — student backends connect here |
| 8770 | Teacher external HTTP | `127.0.0.1` — third-party tools |
| 8771 | Teacher local API | `127.0.0.1` — teacher Electron frontend |
| 8772 | Student local API | `127.0.0.1` — student Electron frontend |

## Key Conventions

- **Language**: Chinese for comments, docstrings, UI text, logs. English for identifiers, types, API routes.
- **Frontend**: Vue 3 `<script setup lang="ts">`, Pinia composition stores, Vue Router hash mode, `@/` alias → `src/renderer/`. Electron main/preload are plain JS (CommonJS).
- **Backend**: `BASE_DIR` pattern distinguishes dev paths from PyInstaller `sys.frozen` paths. Modules import `shared` via `sys.path.insert(0, ...)` at runtime.
- **Shared protocol**: `packages/shared/protocol.py` — pure Python, no deps. Defines `MsgType`, `FilterMode`, defaults, and message helpers. Both backends import from it.
- **Database**: Teacher only — `aiosqlite` with raw SQL, `asyncio.Lock` for concurrency. No migration tooling; schema changes go in `db.py` `init_db()`.
- **shadcn-vue**: Components in `src/renderer/components/ui/`. Add with `npx shadcn-vue@latest add <name>` inside the app package.
- **Default password**: `admin123` (SHA-256: `240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9`). Must be changed for production.

See `AGENTS.md` for full API reference, WebSocket protocol details, database schema, security notes, and FAQ.
