# Core 1.0 Reactive UI — English
# Demonstrates: observe var, on_change handler, canvas block,
#               bind (stream → signal), render (signal → canvas)

# ── Reactive state ────────────────────────────────────────────────────────────
observe var input_text: str  = ""
observe var response_text: str = ""
observe var loading: bool    = False
observe var error_msg: str   = ""

# ── AI function that streams into a reactive signal ──────────────────────────
fn ask_and_stream(query: str) uses ai, ui:
    loading = True
    let stream_result = stream @claude-sonnet: query
    bind stream_result -> chat_view
    loading = False

fn clear_chat() uses ui:
    response_text = ""
    error_msg     = ""
    loading       = False

# ── Canvas blocks — declarative UI containers ────────────────────────────────
canvas chat_view {
    observe response_text
    observe loading
}

canvas input_view {
    observe input_text
}

canvas error_view {
    observe error_msg
}

# ── on_change handlers — react to signal changes ─────────────────────────────
on input_text.change:
    render input_view with input_text

on response_text.change:
    render chat_view with response_text

on loading.change:
    render chat_view with loading

on error_msg.change:
    render error_view with error_msg

# ── Main orchestration ────────────────────────────────────────────────────────
fn main() uses ai, ui:
    input_text = "Explain reactive programming in three sentences."
    ask_and_stream(input_text)
