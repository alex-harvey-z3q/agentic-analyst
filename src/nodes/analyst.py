from __future__ import annotations

from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are a senior analyst.

Input: research notes extracted from a Beatles-lyrics corpus.
Output: a structured analysis of recurring themes and motifs.

Rules:
- Ground claims in the notes (don’t invent lyrics).
- Prefer concise, high-signal bullets.
- If evidence is weak/incomplete, say so.

Return markdown with these sections:
# Themes
# Motifs & imagery
# Evolution over time
# Notable exceptions / outliers
# What to investigate next
"""


def analyst_node(state: AgentState) -> AgentState:
    notes = "\n\n---\n\n".join(state.get("research_notes", []))
    question = state["question"]

    analysis = call_llm(
        system_prompt=SYSTEM,
        user_prompt=f"Question:\n{question}\n\nResearch notes:\n{notes}\n\nWrite the analysis now.",
    )

    state["analysis"] = analysis
    state.setdefault("logs", []).append("[analyst] analysis produced")
    return state
