from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class PermissionCategory(StrEnum):
    READ_ONLY = "read_only"
    LOW_RISK_LOCAL = "low_risk_local"
    EXTERNAL_WRITE = "external_write"
    SENSITIVE = "sensitive"
    PROHIBITED = "prohibited"


class PermissionOutcome(StrEnum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


class PermissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1, max_length=200)
    category: PermissionCategory
    required_scope: str = Field(min_length=1, max_length=200)


class PermissionDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: PermissionOutcome
    reason: str


def evaluate_permission(
    request: PermissionRequest,
    *,
    granted_scopes: frozenset[str],
    allow_low_risk_local: bool = False,
    approval_granted: bool = False,
    sensitive_confirmation: bool = False,
) -> PermissionDecision:
    """Evaluate an action using trusted permissions supplied by the caller."""

    if request.category == PermissionCategory.PROHIBITED:
        return PermissionDecision(
            outcome=PermissionOutcome.DENY,
            reason="This action is prohibited by policy.",
        )

    if request.required_scope not in granted_scopes:
        return PermissionDecision(
            outcome=PermissionOutcome.DENY,
            reason="The required permission scope has not been granted.",
        )

    if request.category == PermissionCategory.READ_ONLY:
        return PermissionDecision(
            outcome=PermissionOutcome.ALLOW,
            reason="Read-only action is within the granted scope.",
        )

    if request.category == PermissionCategory.LOW_RISK_LOCAL:
        if allow_low_risk_local or approval_granted:
            return PermissionDecision(
                outcome=PermissionOutcome.ALLOW,
                reason="Low-risk local action is authorized.",
            )
        return PermissionDecision(
            outcome=PermissionOutcome.REQUIRE_APPROVAL,
            reason="Approval is required for this local action.",
        )

    if request.category == PermissionCategory.EXTERNAL_WRITE:
        if approval_granted:
            return PermissionDecision(
                outcome=PermissionOutcome.ALLOW,
                reason="Explicit approval was granted for the external action.",
            )
        return PermissionDecision(
            outcome=PermissionOutcome.REQUIRE_APPROVAL,
            reason="External changes require explicit approval.",
        )

    if request.category == PermissionCategory.SENSITIVE:
        if sensitive_confirmation:
            return PermissionDecision(
                outcome=PermissionOutcome.ALLOW,
                reason="Separate confirmation was provided for the sensitive action.",
            )
        return PermissionDecision(
            outcome=PermissionOutcome.REQUIRE_APPROVAL,
            reason="This sensitive action requires separate explicit confirmation.",
        )

    return PermissionDecision(
        outcome=PermissionOutcome.DENY,
        reason="Unknown permission category.",
    )
