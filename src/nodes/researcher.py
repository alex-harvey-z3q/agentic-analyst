from __future__ import annotations

import json
from typing import List, Dict, Any

from graph_state import AgentState
from tools import rag_search, call_llm

SYSTEM = """You are a research agent working ONLY from retrieved Beatles lyrics.

Task:
Given a single sub-task and retrieved context, extract 3–6 evidence items.

Each evidence item must include:
- task: the sub-task string
- song: song title if known (or "Unknown")
- quote: a SHORT lyric fragment (<= 10 words) copied from context
- theme: 2–5 words describing the theme/motif

Rules:
- Do NOT invent lyrics. Quotes must appear verbatim in the provided context.
- If the context is not sufficient, return an empty list.

Return ONLY valid JSON: a list of objects. No markdown.
Example:
[
  {"task":"Find lyrics about loneliness", "song":"Eleanor Rigby", "quote":"all the lonely people", "theme":"loneliness / isolation"}
]
"""


def researcher_node(state: AgentState) -> AgentState:
    sub_tasks: List[str] = state.get("sub_tasks", [])
    all_evidence: List[Dict[str, Any]] = []

    for task in sub_tasks:
        context = rag_search(task, k=8)

        # If retrieval returns nothing useful, skip cleanly
        if not context or not context.strip():
            state.setdefault("logs", []).append(f"[researcher] empty context for task: {task}")
            continue

        raw = call_llm(
            system_prompt=SYSTEM,
            user_prompt=f"Sub-task:\n{task}\n\nRetrieved context:\n{context}",
        )

        try:
            items = json.loads(raw)
            if isinstance(items, list):
                # Basic sanity filter
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    it.setdefault("task", task)
                    if "quote" in it and isinstance(it["quote"], str) and it["quote"].strip():
                        all_evidence.append(it)
        except json.JSONDecodeError:
            state.setdefault("logs", []).append(f"[researcher] JSON parse failed for task: {task}")
            state.setdefault("logs", []).append(f"[researcher] raw:\n{raw}")

    state["evidence"] = all_evidence
    state.setdefault("logs", []).append(f"[researcher] extracted {len(all_evidence)} evidence items")
    return state
