
import services.api.routes.chat as chat_routes
from fastapi.testclient import TestClient

from services.api.main import app
from services.llm.provider import MockLLMProvider

client = TestClient(app)


def test_chat_returns_mock_reply(monkeypatch):
    monkeypatch.setattr(chat_routes, "provider", MockLLMProvider())

    response = client.post(
        "/chat/",
        json={"message": "Good morning, JARVIS."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "reply": (
            "JARVIS is currently operating in mock mode. "
            "I received your message: Good morning, JARVIS."
        )
    }


def test_chat_rejects_empty_message():
    response = client.post(
        "/chat/",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_chat_rejects_missing_message():
    response = client.post(
        "/chat/",
        json={},
    )

    assert response.status_code == 422
