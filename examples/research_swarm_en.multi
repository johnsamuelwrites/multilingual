# Multi-Agent Research Swarm — English
# Demonstrates: @swarm, delegate, channel<T>, @edge/@cloud placement,
#               memory (persistent), par, spawn

@edge
@tool(description="Search recent news articles")
fn search_news(query: str) -> str uses net:
    pass

@cloud
@agent(model=@claude-sonnet)
fn fact_checker(claim: str) -> str uses ai:
    let result = think @claude-sonnet:
        Verify this claim with reasoning: claim
    return result.conclusion

@cloud
@agent(model=@claude-sonnet)
fn summariser(text: str) -> str uses ai:
    return prompt @claude-sonnet: "Summarise in three sentences:\n" + text

@swarm(agents=[fact_checker, summariser])
fn research_coordinator(question: str) -> str uses ai, net:
    # Persistent memory for research cache
    let cache = memory("research_cache", scope="persistent")

    # Check cache first
    if question in cache:
        return cache[question]

    # Fan-out: fact-check and summarise in parallel
    let checked, summary = par [
        delegate(fact_checker, question),
        delegate(summariser, question)
    ]

    # Spawn a background task to update the news index (fire-and-forget)
    spawn search_news(question)

    # Merge results
    let final_answer = prompt @claude-sonnet:
        "Merge these research findings:\n"
        + "Facts: " + checked + "\n"
        + "Summary: " + summary

    # Cache for next time
    cache[question] = final_answer
    return final_answer

fn main() uses ai, net:
    let answer = research_coordinator("What breakthroughs happened in AI in 2025?")
    print(answer)
