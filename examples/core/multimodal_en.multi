# Core 1.0 Multimodal — English
# Demonstrates: transcribe (audio/video → text),
#               generate with target type (→ TypeName),
#               multimodal prompt patterns

# ── transcribe — convert audio or video bytes to text ────────────────────────
fn transcribe_audio(recording) -> str uses ai:
    let transcript = transcribe @whisper: recording
    return transcript

fn transcribe_meeting(audio_blob) -> str uses ai:
    let notes = transcribe @whisper: audio_blob
    return notes

fn minutes_from_recording(audio_data) -> str uses ai:
    let raw  = transcribe @whisper: audio_data
    let tidy = prompt @claude-sonnet: "Format these raw transcription notes as meeting minutes:\n" + raw
    return tidy

# ── generate with target type — structured typed output ──────────────────────
fn generate_invoice(description: str) -> str uses ai:
    let invoice = generate @claude-sonnet: "Create an invoice for:\n" + description -> Invoice
    return invoice

fn generate_report(brief: str) -> str uses ai:
    let report = generate @claude-sonnet: brief -> Report
    return report

fn extract_action_items(transcript: str) -> str uses ai:
    let items = generate @claude-sonnet:
        "Extract a numbered list of action items from this transcript:\n"
        + transcript -> ActionItems
    return items

# ── combined pipeline: transcribe then summarise ─────────────────────────────
fn meeting_summary(recording) -> str uses ai:
    let transcript = transcribe @whisper: recording
    let summary    = prompt @claude-sonnet:
        "Summarise the key decisions and action items from this transcript:\n"
        + transcript
    return summary

fn main() uses ai:
    let invoice = generate_invoice("Software consulting, 5 days at $800/day")
    print(invoice)
