from datetime import UTC, datetime
from enum import StrEnum
from threading import Lock
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_id: UUID = Field(default_factory=uuid4)
    action: str = Field(min_length=1, max_length=200)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = None


class ApprovalService:
    """In-memory approval service; decisions require an explicit caller action."""

    def __init__(self) -> None:
        self._records: dict[UUID, ApprovalRecord] = {}
        self._lock = Lock()

    def request(self, action: str) -> ApprovalRecord:
        record = ApprovalRecord(action=action)
        with self._lock:
            self._records[record.approval_id] = record
        return record

    def decide(
        self,
        approval_id: UUID,
        *,
        approved: bool,
        user_confirmed: bool,
    ) -> ApprovalRecord:
        if not user_confirmed:
            raise PermissionError("An explicit user confirmation is required.")

        with self._lock:
            record = self._records.get(approval_id)
            if record is None:
                raise KeyError("Approval request not found.")
            if record.status != ApprovalStatus.PENDING:
                raise ValueError("This approval request has already been decided.")

            updated = record.model_copy(
                update={
                    "status": (ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED),
                    "decided_at": datetime.now(UTC),
                }
            )
            self._records[approval_id] = updated
            return updated

    def get(self, approval_id: UUID) -> ApprovalRecord | None:
        with self._lock:
            return self._records.get(approval_id)

    def is_approved(self, approval_id: UUID, action: str) -> bool:
        """Return True only for an approved record matching this exact action."""
        with self._lock:
            record = self._records.get(approval_id)
            return (
                record is not None
                and record.status == ApprovalStatus.APPROVED
                and record.action == action
            )
