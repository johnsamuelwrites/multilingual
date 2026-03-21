# Multilingual AI Dashboard — Multilingual 1.0 Core
# Shows: reactive state, AI streaming, multilingual surface syntax

observe var status: str = "idle"
observe var output: str = ""
observe var error: str = ""

@agent(model=@claude-sonnet)
fn dashboard_agent(query: str) -> str uses ai, net:
    status = "thinking"
    let result = think @claude-sonnet:
        Analyze the query and decide how to respond.
        query: query
    status = "responding"
    let response = stream @claude-sonnet: result.conclusion
    bind response -> output_view
    status = "done"
    return output

canvas output_view {
    observe status
    observe output
}

canvas error_view {
    observe error
}

on status.change:
    render output_view with status

on output.change:
    render output_view with output
