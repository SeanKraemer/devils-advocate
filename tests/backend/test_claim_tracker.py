import pytest

from judges import JudgeTurnScore, run_live_judge_update
from session_state import SessionState


class FakeJudgeClient:
    def __init__(self, score):
        self.score = score
        self.last_prompt = None

    async def generate(self, prompt, response_model, **kwargs):
        self.last_prompt = prompt
        assert response_model is JudgeTurnScore
        return JudgeTurnScore(**self.score)


def make_score(classification="DEFENDED", strength=7):
    return {
        "classification": classification,
        "strength": strength,
        "classification_rationale": "The turn directly addresses the challenge.",
        "strength_rationale": "The answer gives some evidence but remains incomplete.",
        "summary": "User cited specific support for the idea.",
        "reaction": "Helpful, but still needs proof.",
        "suggested_argument": "Use customer or revenue evidence.",
    }


class TestLiveJudgeUpdate:
    @pytest.mark.asyncio
    async def test_returns_consensus_classification(self):
        state = SessionState(user_claim="I want to build a B2B SaaS for HR teams")
        state.add_turn("agent", "What is your CAC?")

        judges = {
            "judge_a": FakeJudgeClient(make_score("DEFENDED", 7)),
            "judge_b": FakeJudgeClient(make_score("DEFENDED", 5)),
            "judge_c": FakeJudgeClient(make_score("CONCEDED", 2)),
        }

        result = await run_live_judge_update(
            judges,
            state,
            "Our pilots show 8 month payback.",
        )

        assert result["classification"] == "DEFENDED"
        assert result["strength"] == 6
        assert len(result["judge_scores"]) == 3

    @pytest.mark.asyncio
    async def test_prompt_contains_original_claim_and_turn(self):
        state = SessionState(user_claim="unique claim string XYZ123")
        client = FakeJudgeClient(make_score())

        await run_live_judge_update(
            {"judge": client},
            state,
            "latest user turn ABC",
        )

        assert "unique claim string XYZ123" in client.last_prompt
        assert "latest user turn ABC" in client.last_prompt
