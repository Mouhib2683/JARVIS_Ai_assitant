from services.security.audit import AuditLog, AuditRecord
from services.security.permissions import PermissionOutcome


def test_audit_record_is_stored():
    log = AuditLog()
    entry = AuditRecord(
        action="open_application:Brave",
        permission=PermissionOutcome.ALLOW,
        success=True,
        outcome="Simulation completed",
        evidence="Mock adapter result",
    )

    stored = log.record(entry)

    assert stored.record_id == entry.record_id
    assert log.list_records() == [entry]


def test_audit_log_preserves_order():
    log = AuditLog()

    first = AuditRecord(
        action="open_application:Brave",
        permission=PermissionOutcome.ALLOW,
        success=True,
        outcome="First action",
    )
    second = AuditRecord(
        action="send_email",
        permission=PermissionOutcome.REQUIRE_APPROVAL,
        success=False,
        outcome="Approval pending",
    )

    log.record(first)
    log.record(second)

    assert log.list_records() == [first, second]


def test_audit_log_returns_a_separate_list():
    log = AuditLog()
    records = log.list_records()

    records.clear()

    assert log.list_records() == []
