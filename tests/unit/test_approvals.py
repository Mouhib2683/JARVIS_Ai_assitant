import pytest

from services.security.approvals import ApprovalService, ApprovalStatus


def test_approval_starts_pending():
    service = ApprovalService()
    record = service.request("Send an email")
    assert record.status == ApprovalStatus.PENDING


def test_explicit_approval_is_recorded():
    service = ApprovalService()
    record = service.request("Send an email")
    result = service.decide(
        record.approval_id, approved=True, user_confirmed=True
    )
    assert result.status == ApprovalStatus.APPROVED
    assert result.decided_at is not None


def test_rejection_is_recorded():
    service = ApprovalService()
    record = service.request("Publish a post")
    result = service.decide(
        record.approval_id, approved=False, user_confirmed=True
    )
    assert result.status == ApprovalStatus.REJECTED


def test_unconfirmed_decision_is_blocked():
    service = ApprovalService()
    record = service.request("Send an email")
    with pytest.raises(PermissionError):
        service.decide(
            record.approval_id, approved=True, user_confirmed=False
        )


def test_decision_cannot_be_changed():
    service = ApprovalService()
    record = service.request("Send an email")
    service.decide(
        record.approval_id, approved=True, user_confirmed=True
    )
    with pytest.raises(ValueError):
        service.decide(
            record.approval_id, approved=False, user_confirmed=True
        )

def test_approval_matches_exact_action():
    service = ApprovalService()
    record = service.request("open_application:Brave")
    service.decide(
        record.approval_id, approved=True, user_confirmed=True
    )

    assert service.is_approved(record.approval_id, "open_application:Brave")
    assert not service.is_approved(record.approval_id, "open_application:PowerShell")


def test_pending_approval_is_not_valid():
    service = ApprovalService()
    record = service.request("open_application:Brave")

    assert not service.is_approved(record.approval_id, "open_application:Brave")
