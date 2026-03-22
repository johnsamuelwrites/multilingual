# Core 1.0 Pattern Matching — English
# Demonstrates: match / case with literal patterns, capture patterns,
#               guard clauses (if), OR patterns (|), record/struct patterns,
#               wildcard (_), and integration with enum and type declarations

# ── Type and enum declarations used in the examples ──────────────────────────
enum Status   = | Ok | Err | Pending
enum Shape    = | Circle { radius: float } | Rectangle { width: float, height: float }
enum Command  = | Quit | Move { x: int, y: int } | Write { text: str } | Print

type Point    = { x: float, y: float }
type Response = { code: int, body: str }

# ── Literal pattern matching ──────────────────────────────────────────────────
fn describe_status(status: Status) -> str:
    match status:
        case Ok:
            return "operation succeeded"
        case Err:
            return "operation failed"
        case Pending:
            return "operation in progress"

fn http_message(code: int) -> str:
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Internal Server Error"
        case _:
            return "Unknown status"

# ── Capture patterns — bind the matched value to a name ──────────────────────
fn first_element(items):
    match items:
        case [first, *rest]:
            return first
        case []:
            return None

fn classify_number(n: int) -> str:
    match n:
        case 0:
            return "zero"
        case x if x < 0:
            return "negative"
        case x if x > 100:
            return "large"
        case x:
            return "positive"

# ── Guard clauses (if) in cases ───────────────────────────────────────────────
fn grade(score: int) -> str:
    match score:
        case s if s >= 90:
            return "A"
        case s if s >= 80:
            return "B"
        case s if s >= 70:
            return "C"
        case s if s >= 60:
            return "D"
        case _:
            return "F"

# ── OR patterns — match multiple alternatives in one case ────────────────────
fn is_vowel(letter: str) -> bool:
    match letter:
        case "a" | "e" | "i" | "o" | "u":
            return True
        case _:
            return False

fn weekend_or_weekday(day: str) -> str:
    match day:
        case "Saturday" | "Sunday":
            return "weekend"
        case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":
            return "weekday"
        case _:
            return "unknown"

# ── Struct/record patterns — destructure typed records ────────────────────────
fn process_command(cmd: Command) -> str:
    match cmd:
        case Quit:
            return "quitting"
        case Move { x: px, y: py }:
            return "moving to " + str(px) + "," + str(py)
        case Write { text: t }:
            return "writing: " + t
        case Print:
            return "printing"

fn area(shape: Shape) -> float:
    match shape:
        case Circle { radius: r }:
            return 3.14159 * r * r
        case Rectangle { width: w, height: h }:
            return w * h

# ── Pattern matching on API responses ─────────────────────────────────────────
fn handle_response(resp: Response) -> str:
    match resp:
        case Response { code: 200, body: b }:
            return "success: " + b
        case Response { code: c } if c >= 400 and c < 500:
            return "client error " + str(c)
        case Response { code: c } if c >= 500:
            return "server error " + str(c)
        case _:
            return "unhandled response"

fn main():
    print(describe_status(Ok))
    print(http_message(404))
    print(classify_number(-5))
    print(grade(87))
    print(is_vowel("e"))
    print(weekend_or_weekday("Saturday"))
    print(area(Circle(radius=3.0)))
    print(area(Rectangle(width=4.0, height=5.0)))
