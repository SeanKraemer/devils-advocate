import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
MOCK_SERVICES = os.getenv("MOCK_SERVICES") == "1"


class OpenAIClient:
    """Generic async OpenAI client for structured chat completions.

    Instantiate with a system prompt and call .generate() with a Pydantic
    response model to get validated structured output back.
    """

    def __init__(self, system_prompt: str, model: str = "gpt-5.4-mini-2026-03-17"):
        self.system_prompt = system_prompt
        self.model = model
        self._client = None if MOCK_SERVICES else AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _mock_response(self, response_model):
        fields = getattr(response_model, "model_fields", {})
        if "classification" in fields and "strength" in fields:
            return response_model(
                classification="DEFENDED",
                strength=5,
                classification_rationale="Mock mode is enabled, so no live judge model was called.",
                strength_rationale="Neutral score for local demo behavior.",
                summary="Local demo response recorded.",
                reaction="Mock judge feedback.",
                suggested_argument="Configure OpenAI credentials to enable live judging.",
            )
        if "scores" in fields and "winner" in fields:
            return response_model(
                scores={
                    "problem_clarity": 5,
                    "market_logic": 5,
                    "execution_risk": 5,
                    "competitive_awareness": 5,
                    "internal_coherence": 5,
                },
                overall=5,
                winner="agent",
                summary="Mock mode is enabled, so this is a placeholder verdict.",
            )
        if "overall_score" in fields:
            return response_model(
                overall_score=5,
                verdict="Mock mode generated a placeholder report.",
                strengths=["Local demo completed without live OpenAI calls."],
                weaknesses=["Configure service credentials for real analysis."],
                recommendation="Add credentials and rerun the debate for production results.",
            )
        if "summary" in fields:
            return response_model(summary="Mock mode is enabled; live synthesis was skipped.")
        return response_model()

    async def generate(self, prompt: str, response_model, temperature: float = 0.3, max_completion_tokens: int = 4000, timeout: float = 30.0):
        """Send a structured-output request and return a validated Pydantic instance."""
        if MOCK_SERVICES:
            return self._mock_response(response_model)
        response = await asyncio.wait_for(
            self._client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format=response_model,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
            ),
            timeout=timeout,
        )
        return response.choices[0].message.parsed
