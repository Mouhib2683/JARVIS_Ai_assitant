from fastapi.testclient import TestClient

import services.api.routes.chat as chat_routes
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
    assert response.json()["reply"] == (
    "JARVIS is currently operating in mock mode. "
    "I received your message: Good morning, JARVIS."
)
    assert isinstance(response.json()["conversation_id"], str)
    assert response.json()["conversation_id"]   


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
    

def test_chat_reuses_previous_conversation_history(monkeypatch):
    received_histories = []

    class HistoryCheckingProvider:
        def generate_reply(self, message, history=None):
            received_histories.append(history or [])
            return f"Reply to: {message}"

    monkeypatch.setattr(
        chat_routes,
        "provider",
        HistoryCheckingProvider(),
    )

    first_response = client.post(
        "/chat/",
        json={"message": "My project is called JARVIS."},
    )
    assert first_response.status_code == 200

    conversation_id = first_response.json()["conversation_id"]

    second_response = client.post(
        "/chat/",
        json={
            "message": "What is my project called?",
            "conversation_id": conversation_id,
        },
    )

    assert second_response.status_code == 200
    assert len(received_histories) == 2

    second_history = received_histories[1]
    assert any(
        item["role"] == "user"
        and item["content"] == "My project is called JARVIS."
        for item in second_history
    )
    assert any(
        item["role"] == "assistant"
        and item["content"] == "Reply to: My project is called JARVIS."
        for item in second_history
    )

