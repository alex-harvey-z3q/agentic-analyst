from __future__ import annotations

from typing import List

from graph_state import AgentState
from tools import rag_search, call_llm

SYSTEM = """You are a research agent.

You will be given:
- A single research sub-task
- Context retrieved from a Beatles-lyrics corpus

Your job:
- Extract relevant evidence from the context
- Summarise it as concise research notes

Rules:
- Be specific (quote short lyric fragments when useful)
- Do NOT invent lyrics or facts not present in the context
- If context seems insufficient, say so and suggest what to search for next
Return markdown with bullets.
"""


def researcher_node(state: AgentState) -> AgentState:
    sub_tasks: List[str] = state.get("sub_tasks", [])
    notes: List[str] = []

    for task in sub_tasks:
        context = rag_search(task, k=6)

        user_prompt = (
            f"Sub-task:\n{task}\n\n"
            f"Retrieved context:\n{context}\n\n"
            "Write research notes now."
        )
        summary = call_llm(SYSTEM, user_prompt)
        notes.append(f"## {task}\n{summary}")

    state["research_notes"] = notes
    state.setdefault("logs", []).append(f"[researcher] wrote {len(notes)} note blocks")
    return state
