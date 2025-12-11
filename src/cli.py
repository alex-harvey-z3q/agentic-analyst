from tools import rag_search
from tools import call_llm

# System prompt:
# This defines the model's role and behaviour.
# It instructs the LLM to act as a research assistant and
# to rely on the retrieved context rather than hallucinating.
SYSTEM = "You are a helpful research assistant. Use the provided context faithfully."


def answer_question(question: str) -> str:
    # Run the retrieval step of Retrieval-Augmented Generation (RAG):
    # This does NOT return the entire corpus — only the top-k most relevant
    # text chunks (default k=5) based on semantic similarity.
    context = rag_search(question)

    # Build the user prompt:
    # The question plus the retrieved context are merged into a single
    # input message for the LLM. The model sees the context and uses it
    # to ground its answer.
    user_prompt = f"Question:\n{question}\n\nContext:\n{context}"

    # Call the language model using the system prompt + user prompt.
    # The model will generate an answer based on the retrieved text.
    return call_llm(SYSTEM, user_prompt)


if __name__ == "__main__":
    # Get a question from the user.
    q = input("Enter your question: ")

    # Print the model's grounded answer.
    print(answer_question(q))
