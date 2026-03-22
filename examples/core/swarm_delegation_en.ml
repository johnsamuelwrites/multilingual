# Core 1.0 Swarm, Delegation, Memory & Placement — English
# Demonstrates: @swarm (multi-agent coordinator),
#               delegate (typed message-passing between agents),
#               memory (persistent named store across sessions),
#               @local / @edge / @cloud (placement annotations)

# ── Specialist agents — each runs where declared ──────────────────────────────
@edge
@tool(description="Fetch a news headline for a given topic")
fn fetch_headline(topic: str) -> str uses net:
    pass

@cloud
@agent(model=@claude-sonnet)
fn fact_checker(claim: str) -> str uses ai:
    let verdict = think @claude-sonnet:
        Verify this claim with step-by-step reasoning.
        Claim: claim
    return verdict.conclusion

@cloud
@agent(model=@claude-sonnet)
fn summariser(text: str) -> str uses ai:
    return prompt @claude-sonnet: "Summarise in three sentences:\n" + text

@local
@agent(model=@claude-sonnet)
fn formatter(content: str) -> str uses ai:
    return prompt @claude-sonnet: "Format this as a structured report:\n" + content

# ── memory — persistent named store accessible across agent sessions ──────────
fn remember_answer(question: str, answer: str) uses ai:
    let cache = memory("research_cache", scope="persistent")
    cache[question] = answer

fn recall_answer(question: str) uses ai:
    let cache = memory("research_cache", scope="persistent")
    if question in cache:
        return cache[question]
    return None

fn session_context() uses ai:
    let ctx = memory("conversation", scope="session")
    return ctx

# ── @swarm — coordinator that fans out work across registered agents ───────────
@swarm(agents=[fact_checker, summariser, formatter])
fn research_coordinator(question: str) -> str uses ai, net:
    # Consult persistent memory first
    let cache = memory("research_cache", scope="persistent")
    if question in cache:
        return cache[question]

    # Fetch a live headline at the edge
    let headline = fetch_headline(question)

    # Delegate to specialist agents in parallel
    let verified, summary = par [
        delegate(fact_checker, question),
        delegate(summariser, headline)
    ]

    # Delegate formatting to the local agent
    let report = delegate(formatter, verified + "\n\n" + summary)

    # Persist for future sessions
    cache[question] = report
    return report

# ── Hierarchical swarm: coordinator of coordinators ──────────────────────────
@cloud
@agent(model=@claude-sonnet)
fn domain_expert(query: str) -> str uses ai:
    return prompt @claude-sonnet: "As a domain expert, answer:\n" + query

@swarm(agents=[research_coordinator, domain_expert])
fn meta_coordinator(question: str) -> str uses ai, net:
    let ctx = memory("session", scope="session")
    let research_result = delegate(research_coordinator, question)
    let expert_opinion  = delegate(domain_expert, question)
    let final_answer = prompt @claude-sonnet:
        "Synthesise research and expert opinion.\n"
        + "Research: " + research_result + "\n"
        + "Expert: " + expert_opinion
    ctx["last_answer"] = final_answer
    return final_answer

fn main() uses ai, net:
    let answer = research_coordinator("What are the latest advances in quantum computing?")
    print(answer)
