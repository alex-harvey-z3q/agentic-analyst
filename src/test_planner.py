from nodes.planner import planner_node

if __name__ == "__main__":
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
