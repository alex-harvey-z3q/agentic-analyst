from __future__ import annotations

from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are a reviewer and quality-control agent.

Input:
- A draft report
- Supporting research notes

Your job:
1) Identify unsupported or weak claims.
2) Flag any hallucinated lyrics or facts.
3) Check tone, structure, and clarity.
4) Produce a corrected, more cautious final report.

Rules:
- Do NOT add new evidence.
- Only use information present in the draft or research notes.
- If evidence is missing, explicitly note the limitation.
- Be conservative rather than expansive.

Output format:
## Issues found
- bullet list

## Final revised report
(full markdown report)
"""


def reviewer_node(state: AgentState) -> AgentState:
    draft = state.get("draft_report", "")
    notes = "\n\n---\n\n".join(state.get("research_notes", []))
    question = state["question"]

    review = call_llm(
        system_prompt=SYSTEM,
        user_prompt=(
            f"Question:\n{question}\n\n"
            f"Draft report:\n{draft}\n\n"
            f"Research notes:\n{notes}\n\n"
            "Review and revise now."
        ),
    )

    state["final_report"] = review
    state.setdefault("logs", []).append("[reviewer] final review completed")
    return state
