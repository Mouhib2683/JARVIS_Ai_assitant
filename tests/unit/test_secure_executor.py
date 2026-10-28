from integrations.desktop.mock_adapter import MockToolRequest
from integrations.desktop.secure_executor import PermissionedDesktopExecutor
from services.security.permissions import PermissionCategory, PermissionOutcome


def make_request():
    return MockToolRequest(tool_name="open_application", application="Brave")


def test_executor_runs_adapter_after_permission_is_allowed():
    result = PermissionedDesktopExecutor().execute(
        make_request(),
        category=PermissionCategory.READ_ONLY,
        required_scope="desktop.open_application",
        granted_scopes=frozenset({"desktop.open_application"}),
    )

    assert result.permission == PermissionOutcome.ALLOW
    assert result.success is True
    assert result.simulated is True


def test_executor_does_not_run_adapter_when_approval_is_pending():
    result = PermissionedDesktopExecutor().execute(
        make_request(),
        category=PermissionCategory.EXTERNAL_WRITE,
        required_scope="desktop.open_application",
        granted_scopes=frozenset({"desktop.open_application"}),
    )

    assert result.permission == PermissionOutcome.REQUIRE_APPROVAL
    assert result.success is False


def test_executor_does_not_run_adapter_when_scope_is_missing():
    result = PermissionedDesktopExecutor().execute(
        make_request(),
        category=PermissionCategory.READ_ONLY,
        required_scope="desktop.open_application",
        granted_scopes=frozenset(),
    )

    assert result.permission == PermissionOutcome.DENY
    assert result.success is False


def test_allowed_execution_is_audited():
    from integrations.desktop.secure_executor import PermissionedDesktopExecutor
    from services.security.audit import AuditLog
    from services.security.permissions import PermissionCategory, PermissionOutcome

    log = AuditLog()
    executor = PermissionedDesktopExecutor(audit_log=log)
    result = executor.execute(
        make_request(),
        category=PermissionCategory.READ_ONLY,
        required_scope="desktop.open_application",
        granted_scopes=frozenset({"desktop.open_application"}),
    )

    records = log.list_records()
    assert result.success is True
    assert len(records) == 1
    assert records[0].permission == PermissionOutcome.ALLOW
    assert records[0].success is True


def test_pending_approval_is_audited():
    from integrations.desktop.secure_executor import PermissionedDesktopExecutor
    from services.security.audit import AuditLog
    from services.security.permissions import PermissionCategory, PermissionOutcome

    log = AuditLog()
    executor = PermissionedDesktopExecutor(audit_log=log)
    result = executor.execute(
        make_request(),
        category=PermissionCategory.EXTERNAL_WRITE,
        required_scope="desktop.open_application",
        granted_scopes=frozenset({"desktop.open_application"}),
    )

    records = log.list_records()
    assert result.permission == PermissionOutcome.REQUIRE_APPROVAL
    assert len(records) == 1
    assert records[0].permission == PermissionOutcome.REQUIRE_APPROVAL
    assert records[0].success is False


def test_missing_scope_denial_is_audited():
    from integrations.desktop.secure_executor import PermissionedDesktopExecutor
    from services.security.audit import AuditLog
    from services.security.permissions import PermissionCategory, PermissionOutcome

    log = AuditLog()
    executor = PermissionedDesktopExecutor(audit_log=log)
    executor.execute(
        make_request(),
        category=PermissionCategory.READ_ONLY,
        required_scope="desktop.open_application",
        granted_scopes=frozenset(),
    )

    records = log.list_records()
    assert len(records) == 1
    assert records[0].permission == PermissionOutcome.DENY
    assert records[0].success is False
