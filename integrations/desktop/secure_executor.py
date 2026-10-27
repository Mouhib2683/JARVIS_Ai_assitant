from uuid import UUID

from pydantic import BaseModel, ConfigDict

from integrations.desktop.mock_adapter import (
    MockDesktopAdapter,
    MockToolRequest,
    MockToolResult,
)
from services.security.approvals import ApprovalService
from services.security.audit import AuditLog, AuditRecord
from services.security.permissions import (
    PermissionCategory,
    PermissionOutcome,
    PermissionRequest,
    evaluate_permission,
)


class GuardedExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission: PermissionOutcome
    success: bool
    simulated: bool
    message: str


class PermissionedDesktopExecutor:
    """Enforce action-specific approvals and audit every execution attempt."""

    def __init__(
        self,
        adapter: MockDesktopAdapter | None = None,
        audit_log: AuditLog | None = None,
        approval_service: ApprovalService | None = None,
    ) -> None:
        self._adapter = adapter or MockDesktopAdapter()
        self._audit_log = audit_log or AuditLog()
        self._approval_service = approval_service

    def execute(
        self,
        tool_request: MockToolRequest,
        *,
        category: PermissionCategory,
        required_scope: str,
        granted_scopes: frozenset[str],
        allow_low_risk_local: bool = False,
        approval_id: UUID | None = None,
    ) -> GuardedExecutionResult:
        action = f"{tool_request.tool_name}:{tool_request.application}"

        approved = (
            approval_id is not None
            and self._approval_service is not None
            and self._approval_service.is_approved(approval_id, action)
        )

        decision = evaluate_permission(
            PermissionRequest(
                action=action,
                category=category,
                required_scope=required_scope,
            ),
            granted_scopes=granted_scopes,
            allow_low_risk_local=allow_low_risk_local,
            approval_granted=approved,
            sensitive_confirmation=approved,
        )

        if decision.outcome != PermissionOutcome.ALLOW:
            self._audit_log.record(
                AuditRecord(
                    action=action,
                    permission=decision.outcome,
                    success=False,
                    outcome=decision.reason,
                )
            )
            return GuardedExecutionResult(
                permission=decision.outcome,
                success=False,
                simulated=True,
                message=decision.reason,
            )

        result: MockToolResult = self._adapter.execute(tool_request)

        self._audit_log.record(
            AuditRecord(
                action=action,
                permission=decision.outcome,
                success=result.success,
                outcome=result.message,
                evidence="Mock adapter result; no real desktop action performed.",
            )
        )

        return GuardedExecutionResult(
            permission=decision.outcome,
            success=result.success,
            simulated=result.simulated,
            message=result.message,
        )

    @property
    def audit_log(self) -> AuditLog:
        return self._audit_log
