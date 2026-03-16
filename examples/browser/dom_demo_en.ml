# DOM bridge demo — English
# Build: python build.py dom_demo_en.ml
# Serve examples/browser/ over HTTP and open index.html.

# Clear and set up the demo panel
let panel = dom_get("ml-panel")
dom_text(panel, "")

# Heading created from WASM
let heading = dom_create("h3")
dom_text(heading, "DOM Bridge Demo")
dom_style(heading, "color", "#7ec8e3")
dom_style(heading, "marginBottom", "0.5rem")
dom_append(panel, heading)

# Body paragraph
let body = dom_create("p")
dom_text(body, "This content was created by Multilingual WASM running in your browser.")
dom_style(body, "color", "#c9d1d9")
dom_append(panel, body)

# Highlighted note
let note = dom_create("p")
dom_text(note, "The DOM bridge maps multilingual dom_get / dom_text / dom_create / dom_append / dom_style calls to real browser DOM APIs.")
dom_style(note, "color", "#7ee787")
dom_style(note, "fontFamily", "monospace")
dom_style(note, "fontSize", "0.85rem")
dom_append(panel, note)

# Badge / status
let badge = dom_create("span")
dom_text(badge, "wasm active")
dom_class(badge, "badge")
dom_append(panel, badge)

# Also print to stdout so the WASI output area shows something
print("dom_demo: DOM elements created successfully.")
print("panel heading set via dom_create + dom_text + dom_append.")
