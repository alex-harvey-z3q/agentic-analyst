from __future__ import annotations

from typing import List

from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are a planning agent for a Beatles-lyrics-only corpus.

Break the user's question into 3–5 sub-tasks that are answerable using lyrics alone.

Rules:
- Each sub-task must be phrased like a retrieval query (start with "Find lyrics about ...")
- Avoid words like "comprehensive", "all songs", or "entire catalogue".
- Prefer specific themes (e.g. loneliness, memory, nature, jealousy, travel, money).
- Return ONLY a numbered list (1., 2., 3., ...). No extra text.
"""

def _parse_numbered_lines(text: str) -> List[str]:
    tasks: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Accept "1. ..." or "1) ..."
        if s[0].isdigit() and (". " in s[:4] or ") " in s[:4]):
            tasks.append(s)
    return tasks


def planner_node(state: AgentState) -> AgentState:
    question = state["question"]

    plan_text = call_llm(
        system_prompt=SYSTEM,
        user_prompt=f"Research question:\n{question}\n\nCreate the sub-tasks now.",
    )

    sub_tasks = _parse_numbered_lines(plan_text)

    # Fallback if formatting was weird
    # Note that LLMs often ignore instructions and return bulleted lists instead of numbered lists!
    if not sub_tasks:
        sub_tasks = [line.strip("- ").strip() for line in plan_text.splitlines() if line.strip()][:5]

    state["sub_tasks"] = sub_tasks
    state.setdefault("logs", []).append(f"[planner]\n{plan_text}")
    return state
