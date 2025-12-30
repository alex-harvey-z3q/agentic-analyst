# Agentic RAG Prototype

A learning project for **Agentic AI** using a **Retrieval-Augmented Generation (RAG)** system exploring how multiple AI (LLM) agents can collaborate to perform analysis over a **text corpus**. In the example project, the text corpus is all lyrics to all Beatles songs.

The project embeds and indexes documents using [Chroma](https://pypi.org/project/chromadb/), retrieves relevant context, and then coordinates multiple agents coordinates multiple agents (planner, researcher, analyst, writer, reviewer) to produce synthesised outputs such as thematic analyses and executive-style briefs.

This is a learning and research project focused on **understanding agentic AI behavior**, not a polished production system.

---

## What this project explores

- Multi-agent workflows (planner → researcher → analyst → writer → reviewer)
- Retrieval bias and coverage gaps in RAG pipelines
- Variance and divergence across repeated agent runs
- The difference between *coherent narratives* and *evidence-grounded analysis*
- How unconstrained agents invent structure when schemas are absent
- Evidence drift and hallucination risk in unconstrained multi-agent systems

---

## How it works (high level)

1. Text files in `data/corpus/` are embedded and indexed with Chroma
2. A planner agent decomposes the user question into subtasks
3. A researcher agent retrieves and summarizes relevant corpus chunks
4. An analyst agent synthesizes themes and patterns
5. A writer agent produces a final report, including limitations

⚠️ **Important**:
Each downstream agent only sees outputs from upstream agents plus retrieved evidence.
Apparent “data gaps” or claims about missing material often reflect **retrieval scope, planner framing, or synthesis constraints**, not missing source data.

---

## Architecture

```
     ┌────────────────────────────────┐      ┌───────────────────────────────────┐
     │            LangGraph           │◄────►│               Corpus              │
     │ src/graph.py                   │      │ data/corpus/*.txt                 │
     │ (workflow + AgentState flow)   │      │ → embeddings → Chroma (tools.py)  │
     └───────────────┬────────────────┘      └───────────────────────────────────┘
                     │
                     v
            ┌────────────────────────┐
            │     Planner Agent      │
            │ src/nodes/planner.py   │
            └───────────┬────────────┘
                        │
                        v
            ┌────────────────────────┐
            │   Researcher Agent     │
            │ src/nodes/researcher.py│
            └───────────┬────────────┘
                        │
                        v
            ┌────────────────────────┐
            │     Analyst Agent      │
            │ src/nodes/analyst.py   │
            └───────────┬────────────┘
                        │
                        v
            ┌────────────────────────┐
            │      Writer Agent      │
            │ src/nodes/writer.py    │
            └────────────────────────┘
                        │
                        v
            ┌────────────────────────┐
            │    Reviewer Agent      │
            │ src/nodes/reviewer.py  │
            └────────────────────────┘
```

## Setup

Add your OpenAI API key to a `.env` file:

```
OPENAI_API_KEY=your_key_here
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the CLI:

```
python src/cli.py
```

Enter a question and the system will respond using retrieved context and coordinated agents.

---

## Known limitations (by design)

- Retrieval is similarity-based and may under-represent parts of the corpus
- Outputs are **non-deterministic** across runs
- Thematic categories are not yet schema-constrained
- Claims may be narratively coherent but not fully evidence-audited
- Frequency and “evolution over time” analyses are qualitative unless explicitly computed

These limitations are intentional exploration targets, not bugs.

---

## Project status

- Early-stage experimental
- Actively iterating on agent roles, constraints, and validation
- Intended as a foundation for future stabilization layers (schemas, aggregation, verification)

---

## Licence

MIT
