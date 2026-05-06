# Clavardage en streaming — Multilingual 1.0 Noyau
# Montre : prompt en streaming, observe var, liaison vue réactive
# (Streaming chat in French)

observe var réponse: str = ""
observe var entrée: str = ""

fn demander(question: str) -> str uses ai:
    let résultat = stream @claude-sonnet: question
    bind résultat -> vue_clavardage
    return réponse

canvas vue_clavardage {
    observe réponse
}

on réponse.change:
    render vue_clavardage with réponse
