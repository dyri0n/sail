# Backend scripts (backend_seil/scripts)

Scripts to setup and run the backend and its Postgres DB. These are provided in both PowerShell and Bash variants.

Prerequisites
- Python 3.11+ (system Python used to create venv)
- uv (https://docs.astral.sh/uv/) available on PATH (used to create venv and run pip)
- Docker & Docker Compose for Postgres

Files
- `setup-backend.ps1` / `setup-backend.sh` : create venv and install requirements (uses `uv`)
- `start-backend.ps1` / `start-backend.sh` : start uvicorn (background)
- `stop-backend.ps1` / `stop-backend.sh` : stop uvicorn using pid file
- `start-db.ps1` / `start-db.sh` : start Postgres docker-compose
- `stop-db.ps1` / `stop-db.sh` : stop Postgres stack

Quick usage (from `backend_seil/scripts`)

PowerShell (Windows)

1. Setup environment:
   - `./setup-backend.ps1`
2. Start DB:
   - `./start-db.ps1`
3. Start backend:
   - `./start-backend.ps1`
4. Stop backend:
   - `./stop-backend.ps1`
5. Stop DB:
   - `./stop-db.ps1`

Bash (macOS / Linux / WSL / Git Bash)

1. Setup environment:
   - `./setup-backend.sh`
2. Start DB:
   - `./start-db.sh`
3. Start backend:
   - `./start-backend.sh`
4. Stop backend:
   - `./stop-backend.sh`
5. Stop DB:
   - `./stop-db.sh`

Notes
- If you do not want to use `uv`, you can still create a venv with `python -m venv .venv` and install requirements with the venv's pip.
- Logs are written to the repo folder `backend_seil/logs` and PID is stored in `backend_seil/scripts/backend.pid`.
