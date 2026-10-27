import pytest
from pydantic import ValidationError

from services.security.permissions import (
    PermissionCategory,
    PermissionOutcome,
    PermissionRequest,
    evaluate_permission,
)


SCOPE = "desktop:launch"
SCOPES = frozenset({SCOPE})


def make_request(category):
    return PermissionRequest(
        action="Open Brave",
        category=category,
        required_scope=SCOPE,
    )


def test_read_only_action_with_scope_is_allowed():
    result = evaluate_permission(
        make_request(PermissionCategory.READ_ONLY),
        granted_scopes=SCOPES,
    )
    assert result.outcome == PermissionOutcome.ALLOW


def test_missing_scope_is_denied_even_with_approval():
    result = evaluate_permission(
        make_request(PermissionCategory.EXTERNAL_WRITE),
        granted_scopes=frozenset(),
        approval_granted=True,
    )
    assert result.outcome == PermissionOutcome.DENY


def test_low_risk_local_requires_approval_by_default():
    result = evaluate_permission(
        make_request(PermissionCategory.LOW_RISK_LOCAL),
        granted_scopes=SCOPES,
    )
    assert result.outcome == PermissionOutcome.REQUIRE_APPROVAL


def test_low_risk_local_can_be_allowed_by_setting():
    result = evaluate_permission(
        make_request(PermissionCategory.LOW_RISK_LOCAL),
        granted_scopes=SCOPES,
        allow_low_risk_local=True,
    )
    assert result.outcome == PermissionOutcome.ALLOW


def test_external_write_requires_approval():
    result = evaluate_permission(
        make_request(PermissionCategory.EXTERNAL_WRITE),
        granted_scopes=SCOPES,
    )
    assert result.outcome == PermissionOutcome.REQUIRE_APPROVAL


def test_sensitive_action_needs_separate_confirmation():
    result = evaluate_permission(
        make_request(PermissionCategory.SENSITIVE),
        granted_scopes=SCOPES,
        approval_granted=True,
    )
    assert result.outcome == PermissionOutcome.REQUIRE_APPROVAL


def test_sensitive_action_is_allowed_after_confirmation():
    result = evaluate_permission(
        make_request(PermissionCategory.SENSITIVE),
        granted_scopes=SCOPES,
        sensitive_confirmation=True,
    )
    assert result.outcome == PermissionOutcome.ALLOW


def test_prohibited_action_is_denied():
    result = evaluate_permission(
        make_request(PermissionCategory.PROHIBITED),
        granted_scopes=SCOPES,
    )
    assert result.outcome == PermissionOutcome.DENY


def test_unknown_request_fields_are_rejected():
    with pytest.raises(ValidationError):
        PermissionRequest(
            action="Open Brave",
            category=PermissionCategory.READ_ONLY,
            required_scope=SCOPE,
            permission_override=True,
        )
