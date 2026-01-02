"""
graph_state.py

Defines the shared state passed between agents in the LangGraph workflow.

LangGraph is a Python library for building stateful, multi-agent workflows as graphs.

In short:
- We model agents as nodes (functions).
- We connect them with edges (execution order or branching).
- A shared state flows through the graph.

The shared state is the *contract* between agents:
- Each agent reads from the state.
- Each agent writes its outputs back to the state.
- LangGraph moves this state through the agent pipeline.

Keeping the shared state explicitly defined in one place makes the system:
- Easier to reason about
- Easier to debug
- Safer to extend (new agents = new fields)
"""

from typing import List, Dict, TypedDict, Any


class AgentState(TypedDict, total=False):
    """
    Shared mutable state for the agentic pipeline.

    Fields are optional because not every agent
    produces or consumes every field.
    """

    # Original user question
    question: str

    # Planner output: concrete research steps
    sub_tasks: List[str]

    # Optional debug / trace messages added by agents
    logs: List[str]

    # Each item should be a dict like:
    # {"task": str, "song": str, "quote": str, "theme": str}
    evidence: List[Dict[str, Any]]

    # Analyst output: synthesized insights and patterns
    # derived from the research notes
    analysis: str

    # Writer output: polished draft report
    # structured for readability and presentation
    draft_report: str

    # Reviewer output: final, quality-checked report
    # with unsupported claims removed or caveated
    final_report: str
