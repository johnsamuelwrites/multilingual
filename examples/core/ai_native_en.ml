# Core 1.0 AI-Native Constructs — English
# Demonstrates: prompt, think, stream, embed, generate,
#               @agent decorator, model-ref syntax (@model-name)

# ── prompt — single-turn call to an AI model ────────────────────────────────
fn ask(question: str) -> str uses ai:
    let answer = prompt @claude-sonnet: question
    return answer

fn summarise(text: str) -> str uses ai:
    let summary = prompt @claude-sonnet: "Summarise in two sentences:\n" + text
    return summary

# ── think — chain-of-thought reasoning, returns Reasoning with .conclusion ──
fn reason(problem: str) -> str uses ai:
    let reasoning = think @claude-sonnet:
        Break this problem into steps and solve it carefully.
        Problem: problem
    return reasoning.conclusion

fn diagnose(symptoms: str) -> str uses ai:
    let plan = think @claude-sonnet:
        Given these symptoms, reason step-by-step about possible causes.
        symptoms: symptoms
    return plan.conclusion

# ── stream — streaming response, token by token ──────────────────────────────
fn stream_essay(topic: str) uses ai:
    let output = stream @claude-sonnet: "Write a short essay about: " + topic
    return output

# ── embed — encode text as a dense vector ────────────────────────────────────
fn vectorise(text: str) uses ai:
    let vec = embed(text)
    return vec

fn embed_pair(a: str, b: str) uses ai:
    let va = embed(a)
    let vb = embed(b)
    return va, vb

# ── generate — produce typed structured output ───────────────────────────────
fn generate_summary(document: str) -> str uses ai:
    let result = generate @claude-sonnet: "Summarise this document:\n" + document
    return result

fn generate_invoice(description: str) -> str uses ai:
    let invoice = generate @claude-sonnet: "Create an invoice for: " + description -> Invoice
    return invoice

# ── @agent — autonomous agent bound to a model ───────────────────────────────
@agent(model=@claude-sonnet)
fn code_reviewer(diff: str) -> str uses ai:
    let critique = think @claude-sonnet:
        Review this code change for correctness, readability, and edge cases.
        diff: diff
    let verdict = prompt @claude-sonnet: "Summarise findings:\n" + critique.conclusion
    return verdict

@agent(model=@claude-sonnet)
fn translator(text: str, target_language: str) -> str uses ai:
    let translated = prompt @claude-sonnet:
        "Translate the following text to " + target_language + ":\n" + text
    return translated

fn main() uses ai:
    let answer = ask("What is the boiling point of water at sea level?")
    print(answer)
    let steps = reason("If all roses are flowers and some flowers fade quickly, what can we infer?")
    print(steps)
