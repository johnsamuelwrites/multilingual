# Core 1.0 Agent & Tool Patterns — English
# Demonstrates: @tool decorator, @agent with tools, plan primitive,
#               multi-capability orchestration

# ── @tool — callable by agents via the tool registry ────────────────────────
@tool(description="Convert a temperature from Celsius to Fahrenheit")
fn celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9.0 / 5.0 + 32.0

@tool(description="Return the number of words in a string")
fn word_count(text: str) -> int:
    return len(text.split())

@tool(description="Look up current weather conditions for a city name")
fn get_weather(city: str) -> str uses net:
    pass

@tool(description="Search the web and return the top result snippet")
fn web_search(query: str) -> str uses net:
    pass

@tool(description="Retrieve stored facts about a topic from the knowledge base")
fn lookup_fact(topic: str) -> str uses net:
    pass

# ── plan — structured multi-step planning ────────────────────────────────────
fn research_plan(goal: str) uses ai:
    let steps = plan @claude-sonnet: goal
    return steps

# ── @agent with tools — autonomous agent that calls registered tools ─────────
@agent(model=@claude-sonnet)
fn weather_assistant(location: str) -> str uses ai, net:
    let conditions = get_weather(location)
    let answer = prompt @claude-sonnet:
        "Given this weather data for " + location + ", give a helpful summary.\n"
        + "Data: " + conditions
    return answer

@agent(model=@claude-sonnet)
fn research_assistant(question: str) -> str uses ai, net:
    let facts = lookup_fact(question)
    let web   = web_search(question)
    let plan  = think @claude-sonnet:
        Combine the retrieved facts and web results into a coherent answer.
        Facts: facts
        Web: web
        Question: question
    return plan.conclusion

# ── multi-step planning then execution ───────────────────────────────────────
fn plan_and_execute(goal: str) -> str uses ai, net:
    let roadmap = plan @claude-sonnet: goal
    let answer  = prompt @claude-sonnet:
        "Execute this plan and return the final result.\n"
        + "Plan: " + str(roadmap)
    return answer

fn main() uses ai, net:
    let summary = weather_assistant("Tokyo")
    print(summary)
    let answer = research_assistant("What is retrieval-augmented generation?")
    print(answer)
