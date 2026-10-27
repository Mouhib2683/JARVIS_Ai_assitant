from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MockToolRequest(BaseModel):
    """Describes a desktop action to simulate."""

    model_config = ConfigDict(extra="forbid")

    tool_name: Literal["open_application"]
    application: str = Field(min_length=1, max_length=100)


class MockToolResult(BaseModel):
    """Describes the simulated result of an action."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    success: bool
    simulated: bool = True
    message: str


class MockDesktopAdapter:
    """Simulates desktop actions without touching the real desktop."""

    def execute(self, request: MockToolRequest) -> MockToolResult:
        return MockToolResult(
            tool_name=request.tool_name,
            success=True,
            simulated=True,
            message=f"Simulation only: would open {request.application}.",
        )
