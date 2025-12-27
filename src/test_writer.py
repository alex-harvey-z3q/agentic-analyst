from nodes.planner import planner_node
from nodes.researcher import researcher_node
from nodes.analyst import analyst_node
from nodes.writer import writer_node

if __name__ == "__main__":
    question = "What themes and lyrical motifs recur across The Beatles’ songs?"

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
