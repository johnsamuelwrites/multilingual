# Core 1.0 Structured AI Operations — English
# Demonstrates: extract (typed extraction from text/documents),
#               classify (text classification into categories)

# ── extract — pull typed structured data from unstructured text ───────────────
fn extract_contact(raw_text: str) uses ai:
    let contact = extract @claude-sonnet: raw_text -> ContactInfo
    return contact

fn extract_invoice_fields(document: str) uses ai:
    let fields = extract @claude-sonnet: document -> InvoiceFields
    return fields

fn extract_key_dates(article: str) uses ai:
    let timeline = extract @claude-sonnet: article -> Timeline
    return timeline

fn extract_entities(text: str) uses ai:
    let entities = extract @claude-sonnet: text -> EntityList
    return entities

# ── extract pipeline — extract then act on structured result ─────────────────
fn process_support_ticket(ticket: str) -> str uses ai:
    let parsed   = extract @claude-sonnet: ticket -> SupportTicket
    let response = prompt @claude-sonnet:
        "Given this parsed ticket, draft a helpful reply.\n"
        + "Ticket: " + str(parsed)
    return response

# ── classify — assign a label from a known set of categories ─────────────────
fn classify_sentiment(text: str) uses ai:
    let label = classify @claude-sonnet: text
    return label

fn classify_topic(article: str) uses ai:
    let topic = classify @claude-sonnet: article -> Topic
    return topic

fn route_support_message(message: str) -> str uses ai:
    let department = classify @claude-sonnet: message -> Department
    return department

# ── classify with extract together — parse then route ────────────────────────
fn triage_email(email_body: str) -> str uses ai:
    let intent   = classify @claude-sonnet: email_body -> Intent
    let entities = extract  @claude-sonnet: email_body -> EmailEntities
    let reply    = prompt @claude-sonnet:
        "Draft a brief reply for intent=" + str(intent)
        + " and entities=" + str(entities)
    return reply

# ── batch classification pipeline via pipe ───────────────────────────────────
fn classify_reviews(reviews) uses ai:
    let labels = reviews |> list
    return labels

fn main() uses ai:
    let contact = extract_contact("Call John at john@example.com or +1-555-0100.")
    print(contact)
    let sentiment = classify_sentiment("The product exceeded all my expectations!")
    print("sentiment:", sentiment)
    let dept = route_support_message("My invoice has an incorrect amount.")
    print("route to:", dept)
