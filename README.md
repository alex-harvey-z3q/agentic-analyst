# RAG Prototype

A minimal Retrieval-Augmented Generation (RAG) setup using OpenAI and Chroma.
Text files in data/corpus/ are embedded, indexed, and retrieved to provide context for LLM answers.

## Setup

Add `OPENAI_API_KEY` to a `.env` file

Install dependencies:

```
pip install -r requirements.txt
```

Run

```
python src/cli.py
```

Enter a question and the system will answer using retrieved text from your corpus.

## LICENCE

MIT.
