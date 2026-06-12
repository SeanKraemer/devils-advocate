# tests/backend/test_prompts.py
from prompts import (
    MAX_RAG_CONTEXT_CHARS,
    build_system_prompt,
    build_early_stage_prompt,
    build_late_stage_prompt,
    build_rag_context,
)


class TestBuildSystemPromptRouting:
    def test_no_stage_defaults_to_late(self):
        assert build_system_prompt("idea") == build_late_stage_prompt("idea")

    def test_explicit_late_routes_to_late(self):
        assert build_system_prompt("idea", stage="late") == build_late_stage_prompt("idea")

    def test_explicit_early_routes_to_early(self):
        assert build_system_prompt("idea", stage="early") == build_early_stage_prompt("idea")

    def test_early_and_late_produce_different_prompts(self):
        assert build_early_stage_prompt("idea") != build_late_stage_prompt("idea")

class TestBuildSystemPrompt:
    def test_contains_user_claim(self):
        prompt = build_system_prompt("my SaaS idea")
        assert "my SaaS idea" in prompt

    def test_claim_wrapped_in_tags(self):
        prompt = build_system_prompt("my SaaS idea")
        # Verify structural injection defense is in place
        assert "<user_claim>" in prompt
        assert "</user_claim>" in prompt

    def test_contains_core_instructions(self):
        prompt = build_system_prompt("anything")
        assert "CHALLENGE MODE" in prompt
        assert "QUESTION MODE" in prompt

class TestBuildRagContext:
    def test_contains_chunks(self):
        context = build_rag_context("some data point here")
        assert "some data point here" in context

    def test_contains_grounding_header(self):
        context = build_rag_context("data")
        assert "GROUNDING CONTEXT" in context

    def test_oversized_chunks_are_capped(self):
        # Gemini Live native-audio goes silent on oversized context turns
        chunks = "\n".join(f"data point {i}: " + "x" * 100 for i in range(200))
        context = build_rag_context(chunks)
        template_overhead = len(build_rag_context(""))
        assert len(context) <= MAX_RAG_CONTEXT_CHARS + template_overhead

    def test_cap_breaks_at_line_boundary(self):
        lines = [f"line {i}: " + "y" * 80 for i in range(100)]
        context = build_rag_context("\n".join(lines))
        assert "[END GROUNDING CONTEXT]" in context
        kept = [ln.strip() for ln in context.splitlines() if ln.strip().startswith("line ")]
        assert kept, "expected some chunk lines to survive the cap"
        assert all(ln in lines for ln in kept), "truncation must not cut mid-line"

    def test_small_chunks_unchanged(self):
        chunks = "a single small data point"
        assert chunks in build_rag_context(chunks)