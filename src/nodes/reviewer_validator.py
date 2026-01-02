from __future__ import annotations

import json
from graph_state import AgentState
from tools import call_llm

SYSTEM = """You are a strict validator.

You will be given:
- A draft report
- Evidence items (JSON)

Goal:
- Remove or rewrite any sentence/quote that is not supported by evidence.
- Do NOT add new themes or new quotes.
- If a section can't be supported, delete it.

Output format:
## Issues removed
- bullet list of removed/changed claims

## Validated report
(full markdown report)
"""


def reviewer_validator_node(state: AgentState) -> AgentState:
    draft = state.get("draft_report", "")
    evidence = state.get("evidence", [])

    validated = call_llm(
        system_prompt=SYSTEM,
        user_prompt=(
            f"Draft report:\n{draft}\n\n"
            f"Evidence (JSON):\n{json.dumps(evidence, ensure_ascii=False)}\n\n"
            "Validate now."
        ),
    )

    state["validated_report"] = validated
    state.setdefault("logs", []).append("[reviewer_validator] validation pass completed")
    return state
