# src/nodes/writer.py
from __future__ import annotations

from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are an executive brief writer.

Input: an analysis of themes/motifs in Beatles lyrics.
Output: a polished, readable report.

Rules:
- Use clear headings and bullets.
- Keep it concise.
- Do NOT invent lyrics; only use what’s in the analysis/notes.
- When referencing lyrics, keep quotes very short (a phrase).

Return markdown with:
# Executive summary
# Key themes
# Motifs & imagery
# How it changes over time
# Caveats (data limits)
"""


def writer_node(state: AgentState) -> AgentState:
    question = state["question"]
    analysis = state.get("analysis", "")
    notes = "\n\n---\n\n".join(state.get("research_notes", []))

    draft = call_llm(
        system_prompt=SYSTEM,
        user_prompt=(
            f"Question:\n{question}\n\n"
            f"Analysis:\n{analysis}\n\n"
            f"Research notes (supporting detail):\n{notes}\n\n"
            "Write the report now."
        ),
    )

    state["draft_report"] = draft
    state.setdefault("logs", []).append("[writer] draft produced")
    return state
