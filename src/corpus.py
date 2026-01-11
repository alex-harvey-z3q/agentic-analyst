import re
from pathlib import Path
from typing import List

from llama_index.core import Document

_PATH_LINE_RE = re.compile(r"^lyrics/(?P<album>[^/]+)/(?P<file>[^/]+)\.txt\s*$")


def _song_from_file_stem(stem: str) -> str:
    return stem.replace("_", " ").strip()


def load_beatles_lyrics_corpus(corpus_path: str) -> List[Document]:
    """
    Parse beatles_lyrics.txt into one LlamaIndex Document per song.

    Expected repeated block format:

      lyrics/Album/Song_Name.txt
      ===
      <lyrics...>
      ===

    Metadata: song, album, source_path
    """
    text = Path(corpus_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    docs: List[Document] = []
    i = 0

    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue

        m = _PATH_LINE_RE.match(lines[i].strip())
        if not m:
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
                    text=lyrics,
                    metadata={
                        "song": song,
                        "album": album,
                        "source_path": source_path,
                    },
                )
            )

    return docs
