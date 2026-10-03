from fastapi import FastAPI

app = FastAPI(title="JARVIS API")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
