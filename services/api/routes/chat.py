
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.llm.provider import (
    LLMProvider,
    MockLLMProvider,
    OpenRouterLLMProvider,
)
from services.memory.store import MemoryStore

load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chat"])

provider: LLMProvider | None = None
memory_store = MemoryStore()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


def get_provider() -> LLMProvider:
    if provider is not None:
        return provider

    selected_provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    if selected_provider == "openrouter":
        return OpenRouterLLMProvider()

    return MockLLMProvider()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id

    if conversation_id is None:
        conversation_id = memory_store.create_conversation(
            title=request.message[:60]
        )
        history: list[dict[str, str]] = []
    else:
        if not memory_store.conversation_exists(conversation_id):
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        history = memory_store.get_messages(conversation_id, limit=100)

    try:
        reply = get_provider().generate_reply(
            request.message,
            history=history,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        memory_store.save_exchange(
            conversation_id,
            request.message,
            reply,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ChatResponse(
        reply=reply,
        conversation_id=conversation_id,
    )
