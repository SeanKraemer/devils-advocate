import os
from .base import RAGBackend

class MockRAGBackend(RAGBackend):
    def ingest_documents(self, participant_id: str, texts: list[str], metadatas: list[dict]) -> None:
        return

    def retrieve(self, participant_id: str, query: str, n_results: int = 8) -> str:
        return ""

    def delete_participant(self, participant_id: str) -> None:
        return

def get_backend() -> RAGBackend:
    if os.getenv("MOCK_SERVICES") == "1":
        return MockRAGBackend()

    backend = os.getenv("RAG_BACKEND", "chroma")

    if backend == "chroma":
        from .chroma_backend import ChromaBackend
        return ChromaBackend()

    if backend == "vertex":
        from .vertex_backend import VertexBackend  # wire in later
        return VertexBackend()

    raise ValueError(f"Unknown RAG_BACKEND: {backend}")

# Singleton — one backend instance for the lifetime of the process
rag = get_backend()
