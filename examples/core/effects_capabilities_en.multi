# Core 1.0 Effects & Capabilities — English
# Demonstrates: all six capability effects (ai, net, fs, ui, time, process),
#               cost wrapper, trace wrapper, explain wrapper,
#               multi-effect function signatures

# ── Single-effect functions ───────────────────────────────────────────────────
fn fetch_page(url: str) -> str uses net:
    pass

fn read_config(path: str) -> str uses fs:
    pass

fn write_output(path: str, content: str) uses fs:
    pass

fn ai_classify(text: str) -> str uses ai:
    let label = prompt @claude-sonnet: "Classify this text: " + text
    return label

fn show_progress(value: int) uses ui:
    observe var progress: int = 0
    progress = value

fn current_timestamp() -> str uses time:
    pass

fn run_subprocess(command: str) -> str uses process:
    pass

# ── Multi-effect combinations ─────────────────────────────────────────────────
fn enrich_and_answer(question: str) -> str uses ai, net:
    let context = fetch_page("https://example.com/facts")
    let answer  = prompt @claude-sonnet: question + "\nContext: " + context
    return answer

fn analyse_and_log(data: str) uses ai, fs:
    let insight = prompt @claude-sonnet: "Analyse this data:\n" + data
    write_output("analysis.txt", insight)

# ── cost wrapper — tracks token spend around any AI expression ───────────────
fn cost_aware_summary(text: str) -> str uses ai:
    let result, spend = cost(prompt @claude-sonnet: "Summarise: " + text)
    print("tokens spent:", spend)
    return result

# ── trace wrapper — labels an expression for observability ───────────────────
fn traced_reasoning(problem: str) -> str uses ai:
    let reasoning = trace(
        think @claude-sonnet: problem,
        "chain-of-thought"
    )
    return reasoning.conclusion

fn traced_retrieval(query: str) -> str uses ai:
    let context = trace(retrieve knowledge_base: query, "retrieval-stage")
    return context

# ── explain wrapper — returns (value, explanation) pair ──────────────────────
fn explained_answer(query: str) -> str uses ai:
    let raw                = prompt @claude-sonnet: query
    let answer, rationale  = explain(raw)
    print("model rationale:", rationale)
    return answer

# ── Full observability pipeline ───────────────────────────────────────────────
fn full_pipeline(question: str) -> str uses ai, net:
    let context            = trace(fetch_page("https://example.com"), "fetch")
    let raw_answer, spend  = cost(prompt @claude-sonnet: question + "\n" + context)
    let answer, rationale  = explain(raw_answer)
    print("cost:", spend)
    print("rationale:", rationale)
    return answer

fn main() uses ai, net:
    let answer = full_pipeline("Explain the CAP theorem.")
    print(answer)
