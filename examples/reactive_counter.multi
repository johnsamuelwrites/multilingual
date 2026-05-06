# Reactive counter — Multilingual 1.0 Core
# Shows: observe var, on change, canvas block

observe var count: int = 0

fn increment():
    count = count + 1

fn decrement():
    count = count - 1

canvas counter_view {
    observe count
}

on count.change:
    render counter_view with count
