# Observable Analysis Pipeline — English
# Demonstrates: channel<T>, trace, cost, explain, @cloud, memory

@cloud
@agent(model=@claude-sonnet)
fn analyser(question: str) -> str uses ai:
    let result = prompt @claude-sonnet: question
    return result

fn main() uses ai:
    # Named memory store for conversation history
    let history = memory("conversation")

    # Create a typed channel for streaming results between stages
    let ch = channel()

    # Cost-tracked, traced inference in parallel across two specialists
    let results = par [
        cost(prompt @claude-sonnet: "Answer concisely: " + question),
        trace(prompt @claude-sonnet: "Give detailed context: " + question,
              "context-stage")
    ]

    # Unpack cost info and inspect
    let answer, cost_info = results[0]
    let context = results[1]

    # Explain the answer
    let answer_text, explanation = explain(answer)

    # Persist to memory
    history["last_question"] = question
    history["last_answer"] = answer_text

    print(answer_text)
    print("Cost:", cost_info)
    print("Explanation:", explanation)
