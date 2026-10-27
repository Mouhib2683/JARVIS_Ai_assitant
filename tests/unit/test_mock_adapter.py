import pytest
from pydantic import ValidationError

from integrations.desktop.mock_adapter import (
    MockDesktopAdapter,
    MockToolRequest,
)


def test_open_application_is_simulated():
    request = MockToolRequest(
        tool_name="open_application",
        application="Brave",
    )

    result = MockDesktopAdapter().execute(request)

    assert result.success is True
    assert result.simulated is True
    assert result.message == "Simulation only: would open Brave."


def test_request_rejects_unknown_tool():
    with pytest.raises(ValidationError):
        MockToolRequest(
            tool_name="delete_file",
            application="Brave",
        )


def test_request_rejects_empty_application():
    with pytest.raises(ValidationError):
        MockToolRequest(
            tool_name="open_application",
            application="",
        )
