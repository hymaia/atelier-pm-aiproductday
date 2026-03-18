---
name: explain-code
user-invocable: false
description: >
  Charge et retourne le contenu brut de fichiers source (Python, TypeScript, etc.)
  pour expliquer du code à un Product Manager. Utiliser quand l'utilisateur pose
  une question sur le fonctionnement technique d'une feature, d'un endpoint, d'un
  fichier ou d'un composant du codebase. Exemples : "comment fonctionne l'API batch ?",
  "explique-moi le webhook handler", "qu'est-ce que fait dashboard_cache.py ?",
  "c'est quoi la limite de l'API produits ?".
---

## Instructions

Exécute le script pour charger le code source, puis explique-le au PM en langage accessible.

```
!python3 ${CLAUDE_SKILL_DIR}/fetch_code.py "$USER_INPUT"
```

## Règles d'explication

1. **Jamais de jargon sans définition** — si tu utilises un terme technique, explique-le en une phrase.
2. **Impact produit en premier** — commence par "Ce fichier gère X pour les clients Y."
3. **Constantes = règles métier** — présente les constantes comme des règles business (BATCH_SIZE_LIMIT = 200 → "les clients peuvent envoyer max 200 produits par appel").
4. **Erreurs = cas utilisateur** — traduis chaque exception en scénario concret ("si le client dépasse 200 produits → il reçoit une erreur claire avec le message XYZ").
5. **Résumé en 3 bullet points maximum** si la question est générale.
