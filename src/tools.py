from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding

# QueryFusionRetriever has lived in a few places across versions; prefer core.
try:
    from llama_index.core.retrievers import QueryFusionRetriever
except ImportError:  # older layout
    from llama_index.core.retrievers import QueryFusionRetriever  # type: ignore

# BM25Retriever moved between namespaces across versions.
try:
    # Newer layout (commonly available in recent llama-index releases)
    from llama_index.core.retrievers import BM25Retriever
except ImportError:
    # Older layout
    from llama_index.retrievers.bm25 import BM25Retriever  # type: ignore

# SentenceTransformerRerank also moved in some releases.
try:
    from llama_index.core.postprocessor import SentenceTransformerRerank
except ImportError:
    try:
        from llama_index.core.postprocessor import SentenceTransformerRerank  # type: ignore
    except ImportError:
        from llama_index.postprocessor import SentenceTransformerRerank  # type: ignore

from src.config import (
    EMBED_MODEL,
    INDEX_PERSIST_DIR,
    OPENAI_API_KEY,
    MODEL_NAME,
    client,
)


# -----------------------------------------------------------------------------
# Retrieval contracts
# -----------------------------------------------------------------------------
#
# Public API:
#   - rag_retrieve(query, k) -> List[RetrievedChunk]
#   - rag_search(query, k) -> str
#   - call_llm(system_prompt, user_prompt) -> str
#
# Retrieval (rag_*) is corpus-only (no LLM). Generation is in call_llm().
# -----------------------------------------------------------------------------


@dataclass
class RetrievedChunk:
    """Stable retrieval result: chunk text + metadata for attribution/debugging."""
    page_content: str
    metadata: Dict[str, Any]


_index: Optional[VectorStoreIndex] = None


def _get_index() -> VectorStoreIndex:
    """
    Load and cache the persisted local LlamaIndex index.

    Prerequisite: run `python -m src.index_build` (or `make index`) once.
    """
    global _index
    if _index is not None:
        return _index

    # Ensure LlamaIndex is configured with the embedding model used at build time.
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL, api_key=OPENAI_API_KEY)

    storage_context = StorageContext.from_defaults(persist_dir=INDEX_PERSIST_DIR)
    _index = load_index_from_storage(storage_context)
    return _index


def _retrieve_nodes(query: str, k: int) -> List[Any]:
    """
    Hybrid retrieval + rerank:
      1) dense retrieval (vector)
      2) sparse retrieval (BM25)
      3) fusion
      4) cross-encoder rerank down to top-k
    """
    index = _get_index()

    # Retrieve more than k so reranking has room to improve precision.
    candidate_k = max(30, k * 6)

    vector_retriever = index.as_retriever(similarity_top_k=candidate_k)

    bm25_retriever = BM25Retriever.from_defaults(
        docstore=index.docstore,
        similarity_top_k=candidate_k,
    )

    fusion = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        similarity_top_k=candidate_k,
        num_queries=1,
        use_async=False,
    )
    nodes = fusion.retrieve(query)

    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-2-v2",
        top_n=k,
    )
    nodes = reranker.postprocess_nodes(nodes, query_str=query)
    return nodes


def rag_retrieve(query: str, k: int = 5) -> List[RetrievedChunk]:
    """
    Retrieve top-k chunks with metadata (song/album/source_path if indexed).
    """
    nodes = _retrieve_nodes(query, k=k)

    out: List[RetrievedChunk] = []
    for nw in nodes:
        node = nw.node
        meta = dict(getattr(node, "metadata", {}) or {})

        # Be defensive across LlamaIndex versions:
        if hasattr(node, "get_content"):
            text = node.get_content()
        else:
            text = getattr(node, "text", "")

        out.append(RetrievedChunk(page_content=text, metadata=meta))

    return out


def rag_search(query: str, k: int = 5) -> str:
    """
    Return a single context string for prompting, with metadata headers per chunk.
    """
    chunks = rag_retrieve(query, k=k)

    parts: List[str] = []
    for c in chunks:
        song = c.metadata.get("song", "Unknown")
        album = c.metadata.get("album", "Unknown")
        src = c.metadata.get("source_path", "Unknown")

        header = f"[SONG={song} | ALBUM={album} | SRC={src}]"
        parts.append(header + "\n" + c.page_content.strip())

    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call the OpenAI Responses API for generation.
    """
    resp = client.responses.create(
        model=MODEL_NAME,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=1200,
        temperature=0,
    )
    return resp.output[0].content[0].text
