from nodes.planner import planner_node
from nodes.researcher import researcher_node
from nodes.analyst import analyst_node

if __name__ == "__main__":
    question = "What themes and lyrical motifs recur across The Beatles’ songs?"

    print("\nQUESTION:")
    print(question)

    state = {"question": question, "logs": []}

    # 1) planner
    state = planner_node(state)
    print("\nSUB_TASKS:")
    for task in state.get("sub_tasks", []):
        print("-", task)

    # 2) researcher
    state = researcher_node(state)

    # 3) analyst
    state = analyst_node(state)

    print("\nANALYSIS:")
    print(state.get("analysis", ""))

    print("\nLOGS:")
    for log in state.get("logs", []):
        print(log)
