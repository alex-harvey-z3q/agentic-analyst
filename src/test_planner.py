import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nodes.planner import planner_node

question = "What themes and lyrical motifs recur across The Beatles’ songs?"

print("\nQUESTION:")
print(question)

state = {
    "question": question,
    "logs": []
}

out = planner_node(state)

print("\nSUB_TASKS:")
for task in out.get("sub_tasks", []):
    print("-", task)

print("\nLOGS:")
for log in out.get("logs", []):
    print(log)
