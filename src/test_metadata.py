import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tools import load_beatles_lyrics_corpus, rag_retrieve

def main() -> None:
    corpus_path = "data/corpus/beatles_lyrics.txt"

    print("\n=== PARSE CHECK (first 5 song docs) ===")
    song_docs = load_beatles_lyrics_corpus(corpus_path)
    print(f"Parsed {len(song_docs)} song documents.\n")

    for d in song_docs[:5]:
        print(f"- song={d.metadata.get('song')} album={d.metadata.get('album')}")
        print(f"  source_path={d.metadata.get('source_path')}")
        preview = d.page_content.strip().splitlines()[:3]
        print("  preview:")
        for line in preview:
            print(f"    {line}")
        print()

    print("\n=== RETRIEVAL CHECK (docs + metadata) ===")
    queries = [
        "Yes I'm lonely wanna die",
        "Feel so suicidal",
        "Wearing a face that she keeps in a jar by the door",
        "Because the world is round",
    ]

    for q in queries:
        print(f"\nQUERY: {q}")
        docs = rag_retrieve(q, k=5)
        for i, d in enumerate(docs, start=1):
            song = d.metadata.get("song", "Unknown")
            album = d.metadata.get("album", "Unknown")
            src = d.metadata.get("source_path", "Unknown")
            snippet = " ".join(d.page_content.strip().split())[:120]
            print(f"  {i}. song={song} album={album}")
            print(f"     src={src}")
            print(f"     snippet={snippet}...")
    print()


if __name__ == "__main__":
    main()
