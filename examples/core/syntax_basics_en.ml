# Core 1.0 Syntax Basics — English
# Demonstrates: fn, let, var, pipe |>, ? result propagation,
#               ~= semantic match, enum, type (record), observe var,
#               uses capability effects

# ── Immutable and mutable bindings ──────────────────────────────────────────
let greeting = "Hello, Multilingual!"
var attempt_count: int = 0

# ── Record type declaration (named struct) ───────────────────────────────────
type Point = { x: float, y: float }
type User  = { id: int, name: str, email: str }

# ── Enum with plain variants ─────────────────────────────────────────────────
enum Direction = | North | South | East | West

# ── Enum with associated data (tagged union) ─────────────────────────────────
enum Shape = | Circle { radius: float } | Rectangle { width: float, height: float }

# ── Plain functions ──────────────────────────────────────────────────────────
fn distance(p: Point) -> float:
    return (p.x * p.x + p.y * p.y)

fn area(shape: Shape) -> float:
    return 0.0

# ── Functions with capability effects ────────────────────────────────────────
fn fetch_page(url: str) -> str uses net:
    pass

fn write_log(path: str, message: str) uses fs:
    pass

fn ai_classify(text: str) -> str uses ai:
    let label = prompt("Classify this text: " + text)
    return label

# ── Pipe operator |> — left-associative function chaining ───────────────────
fn process(items) -> str:
    let cleaned = items |> sorted |> list
    return str(cleaned)

# ── ? result-propagation — short-circuits on failure ─────────────────────────
fn safe_divide(numerator: float, denominator: float) -> float:
    let result = numerator / denominator
    return result

fn parse_and_double(raw: str) -> int:
    let value = int(raw)?
    return value * 2

# ── ~= semantic match — meaning-based equality ───────────────────────────────
fn is_affirmative(answer: str) -> bool uses ai:
    let ok = answer ~= "yes"
    return ok

fn classify_sentiment(text: str) -> bool uses ai:
    let positive = text ~= "I enjoyed this"
    return positive

# ── observe var — reactive binding ───────────────────────────────────────────
observe var score: int = 0
observe var status: str = "idle"

fn increment():
    score = score + 1

fn reset():
    score = 0
    status = "idle"

fn main():
    attempt_count = attempt_count + 1
    let origin = Point(x=0.0, y=0.0)
    let p = Point(x=3.0, y=4.0)
    let d = distance(p)
    print("distance from origin:", d)
    print(greeting)
