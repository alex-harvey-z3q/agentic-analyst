from __future__ import annotations

import re
from pathlib import Path
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import MODEL_NAME, client

# Embedding model used to convert text into vectors for similarity search.
EMBED_MODEL = "text-embedding-3-small"

# Matches: lyrics/AbbeyRoad/Because.txt
_PATH_LINE_RE = re.compile(r"^lyrics/(?P<album>[^/]+)/(?P<file>[^/]+)\.txt\s*$")

def _song_from_file_stem(stem: str) -> str:
    # Carry_That_Weight -> Carry That Weight
    return stem.replace("_", " ").strip()


def load_beatles_lyrics_corpus(corpus_path: str) -> List[Document]:
    """
    Parse beatles_lyrics.txt into one Document per song.

    Expected repeated block format:

      lyrics/Album/Song_Name.txt
      ===
      <lyrics...>
      ===

    - Album and song title are derived from the path line.
    - Lyrics are stored in page_content.
    - Metadata includes: song, album, source_path.
    """
    text = Path(corpus_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    docs: List[Document] = []
    i = 0

    while i < len(lines):
        # Skip blank lines
        if not lines[i].strip():
            i += 1
            continue

        m = _PATH_LINE_RE.match(lines[i].strip())
        if not m:
            # Unexpected line; skip rather than failing hard.
            i += 1
            continue

        album = m.group("album").strip()
        file_stem = m.group("file").strip()
        song = _song_from_file_stem(file_stem)
        source_path = lines[i].strip()
        i += 1

        # Seek opening delimiter ===
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines) or lines[i].strip() != "===":
            # Malformed block; skip
            continue
        i += 1

        # Collect lyrics until closing ===
        lyric_lines: List[str] = []
        while i < len(lines) and lines[i].strip() != "===":
            lyric_lines.append(lines[i])
            i += 1

        # Consume closing === if present
        if i < len(lines) and lines[i].strip() == "===":
            i += 1

        lyrics = "\n".join(lyric_lines).strip()
        if lyrics:
            docs.append(
                Document(
                    page_content=lyrics,
                    metadata={
                        "song": song,
                        "album": album,
                        "source_path": source_path,
                    },
                )
            )

    return docs


def build_vectorstore(corpus_path: str = "data/corpus/beatles_lyrics.txt") -> Chroma:
    """
    Build a Chroma vector store from the Beatles lyrics corpus.

    The corpus is stored as a single text file containing many songs in
    the following repeated format:

        lyrics/Album/Song_Name.txt
        ===
        <lyrics...>
        ===

    Processing steps:
    - Parse the file into one Document per song
    - Attach stable metadata (song title, album, source path)
    - Split lyrics into overlapping chunks for retrieval
    - Embed and index chunks in Chroma
    """

    # Parse the single lyrics file into per-song Documents
    song_docs = load_beatles_lyrics_corpus(corpus_path)

    # Split each song into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    split_docs = splitter.split_documents(song_docs)

    # Create embeddings for each chunk
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)

    # Build the vector store from the chunked documents
    vectordb = Chroma.from_documents(
        split_docs,
        embedding=embeddings,
        collection_name="corpus",
    )

    return vectordb


# Module-level cache for the vectorstore.
# This avoids rebuilding embeddings on every query.
_vectordb = None


def _get_vectordb() -> Chroma:
    """
    Internal helper to lazily initialise the vector store once per process.
    """
    global _vectordb
    if _vectordb is None:
        _vectordb = build_vectorstore()
    return _vectordb


def rag_retrieve(query: str, k: int = 5) -> List[Document]:
    """
    Retrieve the top-k most relevant chunks as Document objects.

    Use this when you need:
    - metadata (song/album/source_path) for attribution
    - programmatic inspection/debugging
    - evidence contracts in downstream agents
    """
    vectordb = _get_vectordb()
    return vectordb.similarity_search(query, k=k)


def rag_search(query: str, k: int = 5) -> str:
    """
    Perform the 'retrieval' part of RAG.

    Given a query, this:
    - Lazily builds the vectorstore on first use.
    - Runs a semantic similarity search to find the top-k most relevant chunks.
    - Returns those chunks concatenated into a single context string.

    Note: This does NOT return the whole corpus; only the most relevant pieces.
    """
    docs = rag_retrieve(query, k=k)

    # Join the retrieved text chunks with blank lines between them.
    # This string is what we pass as "Context" to the LLM.
    return "\n\n".join(d.page_content for d in docs)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call the OpenAI chat model (Responses API) with:
    - a system prompt (role / behaviour instructions)
    - a user prompt (which includes the question + retrieved context)

    Returns the model's generated text as a plain string.
    """
    resp = client.responses.create(
        model=MODEL_NAME,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=1200,  # Upper bound on response length.
        temperature=0,
    )

    # Extract the text from the Responses API structure:
    # - output[0] : first candidate
    # - content[0]: first content item
    # - .text     : actual text string generated by the model
    msg = resp.output[0].content[0].text
    return msg
