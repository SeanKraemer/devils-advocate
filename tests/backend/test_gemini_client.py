# tests/backend/test_gemini_client.py
from types import SimpleNamespace
from unittest.mock import AsyncMock

from gemini_client import GeminiLiveClient


def make_msg(turn_complete=False, transcription=None, interrupted=None):
    return SimpleNamespace(
        server_content=SimpleNamespace(
            model_turn=None,
            input_transcription=None,
            output_transcription=(
                SimpleNamespace(text=transcription) if transcription else None
            ),
            turn_complete=turn_complete,
            grounding_metadata=None,
            interrupted=interrupted,
        )
    )


class FakeSession:
    """Yields scripted messages once, then stops the client's listen loop."""

    def __init__(self, client_ref, messages):
        self._client_ref = client_ref
        self._messages = messages
        self.send_client_content = AsyncMock()

    async def receive(self):
        for msg in self._messages:
            yield msg
        self._client_ref['client'].running = False


def make_client(messages, on_error=None):
    ref = {}
    client = GeminiLiveClient(
        "prompt",
        on_text=AsyncMock(),
        on_audio=AsyncMock(),
        on_error=on_error,
    )
    ref['client'] = client
    client.session = FakeSession(ref, messages)
    client.running = True
    return client


class TestEmptyTurnNudge:
    async def test_empty_turn_triggers_nudge(self):
        client = make_client([make_msg(turn_complete=True)])
        await client._listen()
        client.session.send_client_content.assert_awaited_once()
        kwargs = client.session.send_client_content.await_args.kwargs
        assert kwargs["turn_complete"] is True

    async def test_turn_with_transcription_does_not_nudge(self):
        client = make_client([
            make_msg(transcription="I disagree."),
            make_msg(turn_complete=True),
        ])
        await client._listen()
        client.session.send_client_content.assert_not_awaited()
        client.on_text.assert_any_await("I disagree.", partial=False)

    async def test_repeated_empty_turns_surface_error(self):
        on_error = AsyncMock()
        client = make_client(
            [make_msg(turn_complete=True) for _ in range(3)],
            on_error=on_error,
        )
        await client._listen()
        # nudged twice, third empty turn escalates to the client
        assert client.session.send_client_content.await_count == 2
        on_error.assert_awaited_once()

    async def test_content_turn_resets_empty_counter(self):
        client = make_client([
            make_msg(turn_complete=True),                     # empty -> nudge 1
            make_msg(transcription="point"),                  # content
            make_msg(turn_complete=True),                     # completes content turn
            make_msg(turn_complete=True),                     # empty again -> nudge (not error)
        ])
        await client._listen()
        assert client.session.send_client_content.await_count == 2
        assert client._consecutive_empty_turns == 1
