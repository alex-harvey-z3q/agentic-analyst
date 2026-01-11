from __future__ import annotations

from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from src.config import (
    CORPUS_PATH,
    EMBED_MODEL,
    INDEX_PERSIST_DIR,
    OPENAI_API_KEY,
)

from src.corpus import load_beatles_lyrics_corpus


def build_and_persist_index() -> None:
    """
    Builds a local on-disk LlamaIndex index (vectors + docstore) under INDEX_PERSIST_DIR.
    No external vector DB required.
    """
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL, api_key=OPENAI_API_KEY)

    docs = load_beatles_lyrics_corpus(CORPUS_PATH)

    splitter = SentenceSplitter(chunk_size=800, chunk_overlap=150)

    index = VectorStoreIndex.from_documents(
        docs,
        transformations=[splitter],
        show_progress=True,
    )

    storage_context: StorageContext = index.storage_context
    storage_context.persist(persist_dir=INDEX_PERSIST_DIR)

    print(f"✅ Local index persisted to: {INDEX_PERSIST_DIR}")


if __name__ == "__main__":
    build_and_persist_index()
