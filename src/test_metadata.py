import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tools import rag_retrieve

_WORDISH = re.compile(r"[^a-z0-9\s]+")

def _normalize(s: str) -> str:
    s = s.lower()
    s = _WORDISH.sub(" ", s)          # drop punctuation
    s = " ".join(s.split())           # collapse whitespace
    return s


def _contains(haystack: str, needle: str) -> bool:
    return _normalize(needle) in _normalize(haystack)


def main() -> None:
    queries = [
        "Yes I'm lonely wanna die",
        "Feel so suicidal",
        "Wearing a face that she keeps in a jar by the door",
        "Because the world is round",
    ]

    snippet_chars = 320  # bump this so we can actually see the matching phrase

    for q in queries:
        print(f"\nQUERY: {q}")
        docs = rag_retrieve(q, k=5)

        for i, d in enumerate(docs, start=1):
            song = d.metadata.get("song", "Unknown")
            album = d.metadata.get("album", "Unknown")
            src = d.metadata.get("source_path", "Unknown")

            text = " ".join(d.page_content.strip().split())
            snippet = text[:snippet_chars]

            hit = "HIT" if _contains(text, q) else "—"

            print(f"  {i}. [{hit}] song={song} album={album}")
            print(f"     src={src}")
            print(f"     snippet={snippet}...")

        # Quick summary signal: did we retrieve at least one verbatim hit?
        any_hit = any(_contains(d.page_content, q) for d in docs)
        print(f"  -> Verbatim hit in top-{len(docs)}: {'YES' if any_hit else 'NO'}")


if __name__ == "__main__":
    main()
