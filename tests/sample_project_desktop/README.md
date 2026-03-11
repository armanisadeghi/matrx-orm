# Sample Desktop App + matrx-orm API Server

This sample demonstrates how to run a local Python API server backed by
matrx-orm and connect to it from a desktop frontend (Electron, Tauri, or any
HTTP client).

## Architecture

```
┌──────────────────────┐         HTTP / WS          ┌──────────────────────┐
│   Desktop Frontend   │  ◄─────────────────────►  │   Python Backend     │
│  (Electron / Tauri)  │    localhost:8745          │  (matrx-orm API)     │
│                      │                            │                      │
│  TypeScript client   │    POST /auth/token        │  APIServer           │
│  MatrxClient class   │    POST /rpc               │  ├─ TokenAuth        │
│                      │    GET  /ws                 │  ├─ RequestHandler   │
│                      │                            │  └─ BaseManagers     │
└──────────────────────┘                            │         │            │
                                                     │    asyncpg pool     │
                                                     │         │            │
                                                     │    PostgreSQL       │
                                                     └──────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `server.py` | Python backend — starts the API server with sample managers |
| `client_example.py` | Python client — shows how to call the API from Python |
| `client_example.ts` | TypeScript client — copy into your Electron/Tauri app |
| `.env.example` | Environment variables for database connection |

## Quick Start

```bash
# 1. Install dependencies
pip install matrx-orm[api]

# 2. Set up environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Start the server
python server.py

# 4. In another terminal, run the Python client example
python client_example.py
```

## Security Model

1. Server generates a shared secret on startup (or you provide one).
2. Client exchanges the secret for a time-limited bearer token via `POST /auth/token`.
3. All subsequent requests include `Authorization: Bearer <token>`.
4. Server validates the HMAC signature and expiry on every request.
5. Server binds to `127.0.0.1` only — never exposed to the network.
