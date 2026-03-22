# Multilingual AI Agent — English
# The same agent logic as agent_fr.ml and agent_ja.ml.
# Proves that Multilingual is the only AI platform where agent code
# is idiomatic in any human language.

@tool(description="Search the web for current information")
fn web_search(query: str) -> str uses net:
    pass

@tool(description="Calculate a mathematical expression")
fn calculate(expression: str) -> str:
    pass

@agent(model=@claude-sonnet)
fn research_agent(question: str) -> str uses ai, net:
    let plan = think @claude-sonnet:
        Break down this question into steps.
        question: question
    let answer = prompt @claude-sonnet:
        plan.conclusion + "\n\n" + question
    return answer

fn main():
    let result = research_agent("What is the population of Tokyo?")
    print(result)
