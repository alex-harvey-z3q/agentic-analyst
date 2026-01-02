# src/nodes/writer.py
from __future__ import annotations

import json
from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are an executive brief writer.

You will be given:
- The user's question
- The analyst's analysis
- A JSON list of evidence items (song, quote, theme)

Rules:
- You may ONLY include lyric quotes that appear in evidence items.
- Every section must include evidence quotes (short).
- If you cannot support a claim, omit it.
- Keep it concise.

Return markdown with:
# Executive summary
# Key themes (each theme includes quotes + song)
# Motifs & imagery (quotes + song)
# Caveats (evidence limits)
"""


def writer_node(state: AgentState) -> AgentState:
    question = state["question"]
    analysis = state.get("analysis", "")
    evidence = state.get("evidence", [])

    draft = call_llm(
        system_prompt=SYSTEM,
        user_prompt=(
            f"Question:\n{question}\n\n"
            f"Analysis:\n{analysis}\n\n"
            f"Evidence (JSON):\n{json.dumps(evidence, ensure_ascii=False)}\n\n"
            "Write the report now."
        ),
    )

    state["draft_report"] = draft
    state.setdefault("logs", []).append("[writer] draft produced from evidence")
    return state
