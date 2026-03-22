# Agent IA Multilingue — Français
# La même logique d'agent que agent_en.ml et agent_ja.ml.
# Prouve que Multilingual est la seule plateforme IA où le code d'agent
# est idiomatique dans n'importe quelle langue humaine.

@outil(description="Chercher sur le web des informations actuelles")
fn recherche_web(requête: str) -> str utilise réseau:
    passer

@outil(description="Calculer une expression mathématique")
fn calculer(expression: str) -> str:
    passer

@agent(modèle=@claude-sonnet)
fn agent_recherche(question: str) -> str utilise ai, réseau:
    soit plan = réfléchir @claude-sonnet:
        Décomposer cette question en étapes.
        question: question
    soit réponse = demander @claude-sonnet:
        plan.conclusion + "\n\n" + question
    retourner réponse

fn principal():
    soit résultat = agent_recherche("Quelle est la population de Tokyo?")
    afficher(résultat)
