# Agent IA Multilingue — Français
# La même logique d'agent que agent_en.ml et agent_ja.ml.
# Prouve que Multilingual est la seule plateforme IA où le code d'agent
# est idiomatique dans n'importe quelle langue humaine.
#
# Fonctionnalités démontrées :
#   @outil, @agent, réfléchir, demander, par [ ... ], lancer, utilise effets

@outil(description="Chercher sur le web des informations actuelles")
fn recherche_web(requête: str) -> str utilise réseau:
    passer

@outil(description="Calculer une expression mathématique")
fn calculer(expression: str) -> str:
    passer

@agent(modèle=@claude-sonnet)
fn agent_recherche(question: str) -> str utilise ai, réseau:
    # Réfléchir d'abord : décomposer la question en sous-requêtes parallèles
    soit plan = réfléchir @claude-sonnet:
        Décomposer cette question de recherche en deux sous-requêtes indépendantes
        pouvant être traitées en parallèle.
        question: question

    # Exécuter les deux sous-requêtes simultanément via par
    soit résultats = par [
        demander @claude-sonnet: plan.conclusion + "\nConcentrez-vous sur les faits.",
        demander @claude-sonnet: plan.conclusion + "\nConcentrez-vous sur le contexte."
    ]

    # Synthétiser les résultats parallèles en une réponse finale
    soit réponse = demander @claude-sonnet:
        "Synthétisez ces deux fils de recherche en une réponse claire :\n"
        + résultats[0] + "\n---\n" + résultats[1]

    retourner réponse

fn principal():
    soit résultat = agent_recherche("Quelle est la population de Tokyo?")
    afficher(résultat)
