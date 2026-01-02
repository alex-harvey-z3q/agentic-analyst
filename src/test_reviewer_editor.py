import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nodes.planner import planner_node
from src.nodes.researcher import researcher_node
from src.nodes.analyst import analyst_node
from src.nodes.writer import writer_node
from src.nodes.reviewer_validator import reviewer_validator_node
from src.nodes.reviewer_editor import reviewer_editor_node

question = "What themes and lyrical motifs recur across The Beatles’ songs?"

print("\nQUESTION:")
print(question)

state = {"question": question, "logs": []}

state = planner_node(state)
state = researcher_node(state)
state = analyst_node(state)
state = writer_node(state)
state = reviewer_validator_node(state)

print("\nVALIDATED REPORT (input to editor):")
print(state.get("validated_report", ""))

state = reviewer_editor_node(state)

print("\nFINAL REPORT (editor output):")
print(state.get("final_report", ""))

print("\nLOGS:")
for log in state.get("logs", []):
    print(log)
