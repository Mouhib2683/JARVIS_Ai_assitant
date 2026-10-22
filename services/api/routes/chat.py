
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.llm.provider import (
    LLMProvider,
    MockLLMProvider,
    OpenRouterLLMProvider,
)

load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])

# Tests can replace this with MockLLMProvider.
# In normal operation, the configured provider is selected below.
provider: LLMProvider | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    reply: str


def get_provider() -> LLMProvider:
    if provider is not None:
        return provider

    selected_provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    if selected_provider == "openrouter":
        return OpenRouterLLMProvider()

    return MockLLMProvider()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = get_provider().generate_reply(request.message)
        return ChatResponse(reply=reply)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
