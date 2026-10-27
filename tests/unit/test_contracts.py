import pytest
from pydantic import ValidationError

from packages.contracts.events import TaskEvent, TaskEventType
from packages.contracts.tasks import Task, TaskStatus


def test_task_defaults():
    task = Task(objective="Open an approved application")

    assert task.status == TaskStatus.PENDING
    assert task.steps == []
    assert task.task_id is not None


def test_event_references_correct_task():
    task = Task(objective="Test task-event association")

    event = TaskEvent(
        task_id=task.task_id,
        event_type=TaskEventType.TASK_CREATED,
    )

    assert event.task_id == task.task_id
    assert event.event_type == TaskEventType.TASK_CREATED


def test_task_rejects_empty_objective():
    with pytest.raises(ValidationError):
        Task(objective="")


def test_task_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        Task(objective="Valid task", unexpected_field="not allowed")
