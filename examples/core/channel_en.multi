# Core 1.0 Typed Channels — English
# Demonstrates: channel<T> (bounded/unbounded FIFO pipe between concurrent tasks),
#               send (put a value into a channel),
#               receive (take a value from a channel),
#               producer/consumer and pipeline coordination patterns

# ── Basic channel: producer and consumer ─────────────────────────────────────
fn producer(ch) uses ai:
    let items = ["apple", "banana", "cherry"]
    for item in items:
        send(ch, item)
    send(ch, None)

fn consumer(ch) -> str uses ai:
    var result = ""
    var running = True
    while running:
        let value = receive(ch)
        if value is None:
            running = False
        else:
            result = result + value + " "
    return result

fn run_producer_consumer() uses ai:
    let ch = channel()
    spawn producer(ch)
    let output = consumer(ch)
    return output

# ── Bounded channel: apply back-pressure between stages ──────────────────────
fn bounded_pipeline() uses ai:
    let ch = channel(10)
    spawn producer(ch)
    let result = consumer(ch)
    return result

# ── Channel as AI pipeline: generate → process → collect ─────────────────────
fn ai_generator(ch) uses ai:
    let topics = ["climate", "technology", "health"]
    for topic in topics:
        let summary = prompt @claude-sonnet: "Write one sentence about: " + topic
        send(ch, summary)
    send(ch, None)

fn ai_collector(ch) -> str uses ai:
    var collected = ""
    var active = True
    while active:
        let chunk = receive(ch)
        if chunk is None:
            active = False
        else:
            collected = collected + chunk + "\n"
    return collected

fn summarise_topics() -> str uses ai:
    let ch = channel()
    spawn ai_generator(ch)
    let summaries = ai_collector(ch)
    return summaries

# ── Fan-out with multiple channels ───────────────────────────────────────────
fn dispatch_to_workers(task: str) -> str uses ai:
    let results_ch = channel()
    spawn send(results_ch, prompt @claude-sonnet: "Approach A for: " + task)
    spawn send(results_ch, prompt @claude-sonnet: "Approach B for: " + task)
    let a = receive(results_ch)
    let b = receive(results_ch)
    let merged = prompt @claude-sonnet:
        "Compare and merge these two approaches:\nA: " + a + "\nB: " + b
    return merged

fn main() uses ai:
    let output = run_producer_consumer()
    print("consumed:", output)
    let topics_summary = summarise_topics()
    print(topics_summary)
