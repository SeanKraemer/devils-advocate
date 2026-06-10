from unittest.mock import AsyncMock, patch

import pytest

from report import ReportResult, generate_report
from session_state import SessionState


@pytest.fixture
def state():
    s = SessionState(user_claim="B2B SaaS for HR teams")
    s.add_turn("user", "We target mid-market companies")
    s.add_turn("agent", "What's your CAC payback period?")
    s.add_turn("user", "Under 12 months based on our pilots")
    return s


def make_report(**overrides):
    data = {
        "idea_summary": "A B2B SaaS for HR",
        "overall_score": 7,
        "verdict": "Strong defense",
        "strengths": ["cited real data"],
        "weaknesses": ["market sizing unclear"],
        "sharpest_moment": "CAC payback answer",
        "biggest_gap": "distribution",
        "recommendation": "Nail down TAM",
    }
    data.update(overrides)
    return ReportResult(**data)


class TestGenerateReport:
    @pytest.mark.asyncio
    async def test_returns_valid_report(self, state):
        with patch("report._report_client.generate", new=AsyncMock(return_value=make_report())):
            result = await generate_report(state)

        assert result["overall_score"] == 7
        assert result["idea_summary"] == "A B2B SaaS for HR"
        assert len(result["strengths"]) == 1

    @pytest.mark.asyncio
    async def test_sets_defaults_on_missing_optional_fields(self, state):
        with patch(
            "report._report_client.generate",
            new=AsyncMock(return_value=ReportResult(overall_score=5)),
        ):
            result = await generate_report(state)

        assert result["verdict"] == ""
        assert result["strengths"] == []

    @pytest.mark.asyncio
    async def test_returns_none_on_api_failure(self, state):
        with patch("report._report_client.generate", new=AsyncMock(side_effect=Exception("API down"))):
            result = await generate_report(state)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_short_session(self):
        state = SessionState(user_claim="Too short")
        state.add_turn("user", "one turn")

        result = await generate_report(state)

        assert result is None
