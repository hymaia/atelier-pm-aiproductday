---
date: 2026-03-01
persona: CTO Startup
client: NovaTech
interviewer: Léa Moreau
duration: 30min
themes: [intégration, scalabilité, time-to-market]
---

# Interview — Amina Diallo, CTO NovaTech

**Contexte :** CTO d'une startup de 45 personnes en forte croissance (200% en 2025). Évalue la solution avant décision d'achat. Stack Node.js + Python, full cloud AWS.

---

## Verbatims clés

**Sur l'intégration :**
> "Notre contrainte principale c'est le time-to-market. On ne peut pas se permettre 6 mois d'intégration. Si c'est plus de 4 semaines, c'est éliminatoire pour nous."

> "J'ai lu votre doc API. Elle est bien structurée mais il manque des exemples pour des cas edge — pagination avec filtres complexes, gestion des erreurs réseau. Ce sont ces cas qui font perdre du temps à mes devs."

**Sur les webhooks :**
> "On est event-driven. Les webhooks c'est non-négociable. J'ai besoin de savoir : quel est le mécanisme de retry ? Est-ce qu'il y a un dead letter queue ? C'est là que beaucoup de solutions sont décevantes."

**Sur la scalabilité :**
> "On gère 12 villes aujourd'hui, on vise 50 dans 18 mois. Est-ce que votre solution scale horizontalement ou il y a un plafond de requêtes par tenant ?"

> "Je veux voir des benchmarks de charge, pas juste 'ça scale'. Montrez-moi des chiffres."

## Pain points identifiés
1. Documentation API insuffisante sur les cas edge
2. Manque de transparence sur la scalabilité (pas de benchmarks publics)
3. Incertitude sur le mécanisme de retry des webhooks
4. Processus de vente trop lent pour une startup en mode hypercroissance

## Ce qui fonctionne
- SDKs Node.js et Python disponibles nativement
- Sandbox disponible pour tester avant engagement
- Références sectorielles (Transdev, Keolis) rassurantes
