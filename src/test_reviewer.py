from nodes.planner import planner_node
from nodes.researcher import researcher_node
from nodes.analyst import analyst_node
from nodes.writer import writer_node
from nodes.reviewer import reviewer_node

if __name__ == "__main__":
    question = "What themes and lyrical motifs recur across The Beatles’ songs?"

    print("\nQUESTION:")
    print(question)

    state = {"question": question, "logs": []}

    state = planner_node(state)
    state = researcher_node(state)
    state = analyst_node(state)
    state = writer_node(state)
    state = reviewer_node(state)

    print("\nFINAL REPORT:")
    print(state.get("final_report", ""))

    print("\nLOGS:")
    for log in state.get("logs", []):
        print(log)
