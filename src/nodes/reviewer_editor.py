from __future__ import annotations

from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are an editor.

Input: a validated report.
Goal: improve clarity, reduce repetition, improve structure.

Rules:
- Do NOT add new claims, themes, or quotes.
- Do NOT remove caveats.
- Only rewrite for style and readability.

Return ONLY the final markdown report (no preamble).
"""


def reviewer_editor_node(state: AgentState) -> AgentState:
    validated = state.get("validated_report", "")

    final = call_llm(
        system_prompt=SYSTEM,
        user_prompt=f"Validated report:\n{validated}\n\nEdit for clarity now.",
    )

    state["final_report"] = final
    state.setdefault("logs", []).append("[reviewer_editor] edit pass completed")
    return state
