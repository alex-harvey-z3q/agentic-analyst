from __future__ import annotations

from pathlib import Path

import pytest

from llama_index.core.node_parser import SentenceSplitter

from src.corpus import load_beatles_lyrics_corpus


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
    docs = load_beatles_lyrics_corpus(str(sample_corpus_file))
    assert len(docs) == 2

    d0, d1 = docs

    assert d0.metadata["album"] == "AbbeyRoad"
    assert d0.metadata["song"] == "Because"
    assert d0.metadata["source_path"] == "lyrics/AbbeyRoad/Because.txt"
    assert "Because the world is round" in d0.text

    assert d1.metadata["song"] == "Carry That Weight"
    assert "carry that weight" in d1.text.lower()


def test_sentence_splitter_preserves_metadata(sample_corpus_file: Path):
    docs = load_beatles_lyrics_corpus(str(sample_corpus_file))

    # Must be larger than metadata token length because SentenceSplitter is metadata-aware
    splitter = SentenceSplitter(chunk_size=128, chunk_overlap=20)
    nodes = splitter.get_nodes_from_documents(docs)

    assert len(nodes) >= 2

    songs = {n.metadata.get("song") for n in nodes}
    assert "Because" in songs
    assert "Carry That Weight" in songs

    assert any(n.metadata.get("source_path") == "lyrics/AbbeyRoad/Because.txt" for n in nodes)
