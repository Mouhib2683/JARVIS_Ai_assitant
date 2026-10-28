from datetime import UTC, datetime
from threading import Lock
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from services.security.permissions import PermissionOutcome


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    record_id: UUID = Field(default_factory=uuid4)
    action: str = Field(min_length=1, max_length=200)
    permission: PermissionOutcome
    success: bool
    outcome: str = Field(min_length=1, max_length=500)
    evidence: str | None = Field(default=None, max_length=1_000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditLog:
    """Thread-safe in-memory audit log."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []
        self._lock = Lock()

    def record(self, entry: AuditRecord) -> AuditRecord:
        with self._lock:
            self._records.append(entry)
        return entry

    def list_records(self) -> list[AuditRecord]:
        with self._lock:
            return list(self._records)
