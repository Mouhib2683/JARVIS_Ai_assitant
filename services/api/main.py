from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.routes.chat import router as chat_router

app = FastAPI(title="JARVIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "tauri://localhost",
        "http://tauri.localhost",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
