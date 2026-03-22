# Multilingual AI Agent — English
# The same agent logic as agent_fr.ml and agent_ja.ml.
# Proves that Multilingual is the only AI platform where agent code
# is idiomatic in any human language.
#
# Features demonstrated:
#   @tool, @agent, think, prompt, par [ ... ], spawn, uses effects

@tool(description="Search the web for current information")
fn web_search(query: str) -> str uses net:
    pass

@tool(description="Calculate a mathematical expression")
fn calculate(expression: str) -> str:
    pass

@agent(model=@claude-sonnet)
fn research_agent(question: str) -> str uses ai, net:
    # Think first: break the question into parallel sub-queries
    let plan = think @claude-sonnet:
        Break down this research question into two independent sub-queries
        that can be answered in parallel.
        question: question

    # Run both sub-queries concurrently via par
    let results = par [
        prompt @claude-sonnet: plan.conclusion + "\nFocus on facts.",
        prompt @claude-sonnet: plan.conclusion + "\nFocus on context."
    ]

    # Synthesise the parallel results into a final answer
    let answer = prompt @claude-sonnet:
        "Synthesise these two research threads into one clear answer:\n"
        + results[0] + "\n---\n" + results[1]

    return answer

fn main():
    let result = research_agent("What is the population of Tokyo?")
    print(result)
