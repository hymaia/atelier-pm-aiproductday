---
name: summarize-releases
user-invocable: false
description: >
  Charge et retourne le contenu des changelogs et release notes pour les résumer
  en termes business. Utiliser quand l'utilisateur demande ce qui a été livré,
  les nouveautés d'une version, l'impact d'une release sur les clients, ou ce que
  les devs ont livré récemment. Exemples : "qu'est-ce qui a été livré en mars ?",
  "résume la v2.3", "quels changements impactent Carrefour ?", "c'est quoi les
  nouveautés de la dernière release ?".
---

## Instructions

Exécute le script pour charger les changelogs, puis résume l'impact business.

```
!python3 ${CLAUDE_SKILL_DIR}/fetch_releases.py "$USER_INPUT"
```

## Règles de résumé

1. **Impact client d'abord** — pour chaque changement, dis quel client ou persona est concerné.
2. **Avant / Après** — utilise ce format pour les améliorations de performance ou de comportement.
3. **Pas de détails techniques bruts** — traduis les changements en bénéfices concrets.
4. **Breaking changes en rouge (gras)** — si une version contient un breaking change, le signaler en premier.
5. **Format synthétique** : titre de version + date + 3-5 bullet points d'impact produit.
