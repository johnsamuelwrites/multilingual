# Core 1.0 Concurrency — English
# Demonstrates: par [ ... ] (parallel fan-out), spawn (fire-and-forget),
#               combined with cost, trace, delegate, channel

# ── par — run branches concurrently, collect results as a tuple ──────────────
fn parallel_queries(question: str) -> str uses ai:
    let fast, detailed = par [
        prompt @claude-sonnet: "Answer concisely: " + question,
        prompt @claude-sonnet: "Give a detailed explanation: " + question
    ]
    let combined = prompt @claude-sonnet:
        "Merge these two answers into one response.\n"
        + "Concise: " + fast + "\n"
        + "Detailed: " + detailed
    return combined

fn parallel_embeddings(a: str, b: str, c: str) uses ai:
    let va, vb, vc = par [
        embed(a),
        embed(b),
        embed(c)
    ]
    return va, vb, vc

# ── par with observability wrappers ──────────────────────────────────────────
fn observed_parallel(question: str) uses ai:
    let answer_with_cost, traced_context = par [
        cost(prompt @claude-sonnet: "Answer concisely: " + question),
        trace(
            prompt @claude-sonnet: "Give detailed context: " + question,
            "context-stage"
        )
    ]
    let answer, spend = answer_with_cost
    print("tokens spent:", spend)
    return answer

# ── spawn — launch a background task (fire-and-forget) ───────────────────────
@tool(description="Index a document into the background search store")
fn index_document(doc_id: str, content: str) uses fs, net:
    pass

@tool(description="Send an analytics event to the logging service")
fn log_event(event: str) uses net:
    pass

fn answer_and_log(question: str) -> str uses ai, net, fs:
    # Answer the user immediately ...
    let answer = prompt @claude-sonnet: question
    # ... while indexing and logging run in the background
    spawn index_document("last_query", question)
    spawn log_event("query:" + question)
    return answer

# ── par + spawn together: respond fast, background work continues ─────────────
fn respond_and_enrich(query: str) -> str uses ai, net, fs:
    # Fan out two AI calls in parallel for the response
    let summary, keywords = par [
        prompt @claude-sonnet: "Summarise: " + query,
        prompt @claude-sonnet: "List five keywords for: " + query
    ]
    # Fire background tasks without blocking
    spawn log_event("responded:" + query)
    spawn index_document("q_" + query, summary)
    return summary + "\nKeywords: " + keywords

# ── parallel multi-agent fan-out ─────────────────────────────────────────────
@agent(model=@claude-sonnet)
fn fact_checker(claim: str) -> str uses ai:
    let result = think @claude-sonnet:
        Verify this claim with step-by-step reasoning: claim
    return result.conclusion

@agent(model=@claude-sonnet)
fn summariser(text: str) -> str uses ai:
    return prompt @claude-sonnet: "Summarise in three sentences:\n" + text

fn multi_agent_parallel(question: str) -> str uses ai:
    let checked, summary = par [
        fact_checker(question),
        summariser(question)
    ]
    let merged = prompt @claude-sonnet:
        "Combine fact-check and summary into a final answer.\n"
        + "Facts: " + checked + "\n"
        + "Summary: " + summary
    return merged

fn main() uses ai, net, fs:
    let answer = parallel_queries("What is WebAssembly?")
    print(answer)
    let result = respond_and_enrich("Explain language models")
    print(result)
