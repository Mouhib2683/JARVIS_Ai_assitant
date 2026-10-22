
from fastapi import FastAPI

from services.api.routes.chat import router as chat_router

app = FastAPI(title="JARVIS API")

app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
