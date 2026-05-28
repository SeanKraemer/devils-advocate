import os
from google import genai
from google.genai import types

MOCK_SERVICES = os.getenv("MOCK_SERVICES") == "1"
client = None if MOCK_SERVICES else genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MAX_INPUT_CHARS = 8000


async def summarize_documents(doc_texts: list[str]) -> str:
    """
    Produce a 1-3 sentence summary of the founder's position from extracted document text.
    Used when the user starts a debate with only uploads (no typed claim).
    """
    if not doc_texts:
        raise ValueError("No document text to summarize")
    combined = "\n\n".join(doc_texts).strip()
    if not combined:
        raise ValueError("Document text is empty")
    if len(combined) > MAX_INPUT_CHARS:
        combined = combined[:MAX_INPUT_CHARS] + "..."
    if MOCK_SERVICES:
        first_sentence = combined.split(".")[0].strip()
        return first_sentence[:300] if first_sentence else "Mock document summary."

    prompt = f"""The following is extracted text from a founder's pitch deck, business plan, or notes.
Summarize their idea in 1-3 clear sentences: what they're building, for whom, and the core hypothesis or business model.
Write as if the founder is stating their position to an investor. Be concise and specific.
Do not add preamble or attribution (e.g. "The founder believes...").

DOCUMENT TEXT:
{combined}
"""

    try:
        response = await client.aio.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=300,
                temperature=0.3,
            ),
        )
        summary = (response.text or "").strip()
        if not summary:
            raise ValueError("Summary was empty")
        return summary
    except Exception as e:
        print(f"[Summary] Error: {e}")
        raise
