from __future__ import annotations

from pathlib import Path

import pytest

import src.tools as tools


@pytest.fixture
def sample_corpus_file(tmp_path: Path) -> Path:
    content = """lyrics/AbbeyRoad/Because.txt
===
Ah
Because the world is round
It turns me on
===
lyrics/AbbeyRoad/Carry_That_Weight.txt
===
Boy, you're gonna carry that weight
Carry that weight a long time
===
"""
    p = tmp_path / "beatles_lyrics.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_load_beatles_lyrics_corpus_parses_blocks(sample_corpus_file: Path):
    docs = tools.load_beatles_lyrics_corpus(str(sample_corpus_file))
    assert len(docs) == 2

    d0, d1 = docs

    assert d0.metadata["album"] == "AbbeyRoad"
    assert d0.metadata["song"] == "Because"
    assert d0.metadata["source_path"] == "lyrics/AbbeyRoad/Because.txt"
    assert "Because the world is round" in d0.page_content

    assert d1.metadata["song"] == "Carry That Weight"
    assert "carry that weight" in d1.page_content.lower()


def test_build_vectorstore_passes_documents_with_metadata(monkeypatch, sample_corpus_file: Path):
    # 1) Stub embeddings so no network calls happen
    class FakeEmbeddings:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(tools, "OpenAIEmbeddings", FakeEmbeddings)

    # 2) Capture what goes into Chroma.from_documents
    captured = {}

    class FakeChroma:
        @classmethod
        def from_documents(cls, split_docs, embedding, collection_name):
            captured["split_docs"] = split_docs
            captured["embedding"] = embedding
            captured["collection_name"] = collection_name
            return "FAKE_VECTORSTORE"

    monkeypatch.setattr(tools, "Chroma", FakeChroma)

    # 3) Run
    vectordb = tools.build_vectorstore(corpus_path=str(sample_corpus_file))

    # 4) Assert
    assert vectordb == "FAKE_VECTORSTORE"
    assert captured["collection_name"] == "corpus"
    assert "split_docs" in captured
    assert len(captured["split_docs"]) >= 2  # chunking may keep it at 2 or more

    # Ensure metadata made it through splitting
    songs = {d.metadata.get("song") for d in captured["split_docs"]}
    assert "Because" in songs
    assert "Carry That Weight" in songs
