# tests/backend/test_session_state.py
import pytest
from session_state import SessionState

@pytest.fixture
def state():
    return SessionState(user_claim="I want to build an AI HR tool")

class TestAddTurn:
    def test_increments_turn_count(self, state):
        state.add_turn("user", "hello")
        assert state.turn_count == 1

    def test_stores_turn(self, state):
        state.add_turn("agent", "interesting")
        assert state.turns[-1].text == "interesting"
        assert state.turns[-1].speaker == "agent"

class TestGetUserClaims:
    def test_returns_only_user_turns(self, state):
        state.add_turn("user", "claim 1")
        state.add_turn("agent", "response")
        state.add_turn("user", "claim 2")
        assert state.get_user_claims() == ["claim 1", "claim 2"]

class TestGetRecentContext:
    def test_returns_last_n_turns(self, state):
        for i in range(10):
            state.add_turn("user", f"turn {i}")
        context = state.get_recent_context(n=3)
        assert "turn 9" in context
        assert "turn 8" in context
        assert "turn 7" in context
        assert "turn 6" not in context

    def test_returns_all_if_fewer_than_n(self, state):
        state.add_turn("user", "only turn")
        context = state.get_recent_context(n=6)
        assert "only turn" in context

class TestAddJudgeUpdate:
    def test_stores_judge_update(self, state):
        state.add_judge_update("my argument", {
            "classification": "DEFENDED",
            "summary": "good point",
            "strength": 8,
            "suggested_argument": "cite pilot results",
        })
        assert len(state.judge_updates) == 1
        assert state.judge_updates[0].classification == "DEFENDED"
        assert state.judge_updates[0].suggested_argument == "cite pilot results"

class TestToDict:
    def test_serializes_correctly(self, state):
        state.add_turn("user", "hello")
        d = state.to_dict()
        assert d["user_claim"] == "I want to build an AI HR tool"
        assert len(d["turns"]) == 1
        assert d["turns"][0]["speaker"] == "user"
