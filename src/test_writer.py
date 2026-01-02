import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nodes.planner import planner_node
from nodes.researcher import researcher_node
from nodes.analyst import analyst_node
from nodes.writer import writer_node

question = "How does the theme of loneliness appear across Beatles lyrics? Give examples."

print("\nQUESTION:")
print(question)

state = {"question": question, "logs": []}

state = planner_node(state)
state = researcher_node(state)
state = analyst_node(state)
state = writer_node(state)

print("\nDRAFT REPORT:")
print(state.get("draft_report", ""))

print("\nLOGS:")
for log in state.get("logs", []):
    print(log)
