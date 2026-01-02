from __future__ import annotations

import json
from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are a senior analyst.

Input is a JSON list of evidence items:
- song, quote, theme, task

Rules:
- You may ONLY make claims supported by evidence items.
- Every theme you mention must cite at least 2 evidence items (by quoting their 'quote' fields).
- If evidence is thin, say so and keep the analysis short.
- Do NOT invent lyrics or add songs not present.

Return markdown with:
# Themes (with supporting quotes)
# Motifs & imagery (with supporting quotes)
# Gaps / what to retrieve next
"""


def analyst_node(state: AgentState) -> AgentState:
    question = state["question"]
    evidence = state.get("evidence", [])

    analysis = call_llm(
        system_prompt=SYSTEM,
        user_prompt=(
            f"Question:\n{question}\n\n"
            f"Evidence (JSON):\n{json.dumps(evidence, ensure_ascii=False)}\n\n"
            "Write the analysis now."
        ),
    )

    state["analysis"] = analysis
    state.setdefault("logs", []).append("[analyst] analysis produced from evidence")
    return state
