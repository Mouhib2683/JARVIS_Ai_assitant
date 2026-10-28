
from pathlib import Path

import pytest

from services.memory.store import MemoryStore


@pytest.fixture
def memory_store(tmp_path: Path) -> MemoryStore:
    return MemoryStore(tmp_path / "memory.sqlite3")


def test_create_conversation(memory_store: MemoryStore) -> None:
    conversation_id = memory_store.create_conversation("JARVIS project")

    conversations = memory_store.list_conversations()

    assert len(conversations) == 1
    assert conversations[0]["conversation_id"] == conversation_id
    assert conversations[0]["title"] == "JARVIS project"


def test_save_and_retrieve_exchange(memory_store: MemoryStore) -> None:
    conversation_id = memory_store.create_conversation()

    memory_store.save_exchange(
        conversation_id,
        "Hello, JARVIS.",
        "Good day, sir.",
    )

    messages = memory_store.get_messages(conversation_id)

    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[0]["content"] == "Hello, JARVIS."
    assert messages[1]["content"] == "Good day, sir."


def test_history_survives_store_recreation(tmp_path: Path) -> None:
    db_path = tmp_path / "memory.sqlite3"
    first_store = MemoryStore(db_path)
    conversation_id = first_store.create_conversation()

    first_store.save_exchange(conversation_id, "Remember this.", "I have it in history.")

    reopened_store = MemoryStore(db_path)

    assert reopened_store.get_messages(conversation_id)[0]["content"] == "Remember this."


def test_conversations_are_isolated(memory_store: MemoryStore) -> None:
    first = memory_store.create_conversation("First")
    second = memory_store.create_conversation("Second")

    memory_store.save_exchange(first, "Secret for first chat.", "First reply.")

    assert memory_store.get_messages(second) == []


def test_save_exchange_rejects_unknown_conversation(
    memory_store: MemoryStore,
) -> None:
    with pytest.raises(ValueError, match="Conversation does not exist"):
        memory_store.save_exchange("unknown-id", "Hello", "Reply")


def test_message_history_limit(memory_store: MemoryStore) -> None:
    conversation_id = memory_store.create_conversation()
    memory_store.save_exchange(conversation_id, "First", "First reply")
    memory_store.save_exchange(conversation_id, "Second", "Second reply")

    messages = memory_store.get_messages(conversation_id, limit=2)

    assert len(messages) == 2
    assert messages[0]["content"] == "Second"
    assert messages[1]["content"] == "Second reply"


def test_message_history_rejects_nonpositive_limit(
    memory_store: MemoryStore,
) -> None:
    conversation_id = memory_store.create_conversation()

    with pytest.raises(ValueError, match="Limit must be positive"):
        memory_store.get_messages(conversation_id, limit=0)
