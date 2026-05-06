# Core 1.0 Retrieval & Semantic Search — English
# Demonstrates: retrieve (RAG), embed (dense vectors),
#               ~= semantic match operator

# ── embed — encode a passage into a vector ────────────────────────────────────
fn vectorise(text: str) uses ai:
    let vec = embed(text)
    return vec

fn embed_query(question: str) uses ai:
    let q_vec = embed(question)
    return q_vec

# ── retrieve — nearest-neighbour lookup in a knowledge base ──────────────────
fn search_docs(query: str) uses ai:
    let hits = retrieve knowledge_base: query
    return hits

fn search_faq(question: str) uses ai:
    let results = retrieve faq_store: question
    return results

# ── ~= semantic match — meaning-level equality with optional threshold ────────
fn user_said_yes(input: str) -> bool uses ai:
    let matched = input ~= "yes"
    return matched

fn matches_greeting(utterance: str) -> bool uses ai:
    let ok = utterance ~= "hello"
    return ok

# ── RAG pipeline — retrieve context, then generate a grounded answer ─────────
fn answer_grounded(question: str) -> str uses ai:
    let context = retrieve knowledge_base: question
    let answer  = prompt @claude-sonnet:
        "Answer the question using only the context below.\n"
        + "Context: " + context + "\n"
        + "Question: " + question
    return answer

# ── Semantic routing — dispatch by meaning, not exact string ─────────────────
fn route_intent(utterance: str) -> str uses ai:
    let is_help    = utterance ~= "I need help"
    let is_pricing = utterance ~= "How much does it cost"
    if is_help:
        return "support"
    if is_pricing:
        return "sales"
    return "general"

fn main() uses ai:
    let intent = route_intent("Can you assist me?")
    print("intent:", intent)
    let answer = answer_grounded("What is a vector database?")
    print(answer)
