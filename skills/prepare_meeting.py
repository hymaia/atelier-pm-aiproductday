"""
prepare_meeting.py — Skill 2 : Préparer une réunion spécifique

Génère une fiche de préparation à partir du nom d'une réunion ou d'un participant :
- Historique chronologique : sujets, décisions, actions
- Last touchpoint : date + résumé de la dernière interaction
- Fiche synthétique lisible en 2 minutes

Pattern deux étapes :
  1. Filtrage sur index.json (jamais de lecture de fichiers)
  2. Lecture ciblée des fichiers retenus (max 5 les plus récents, total ≤10)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loaders import calendar_loader, transcript_loader, notes_loader, summary_loader
from skills.claude_client import get_client

console = Console()
BASE_DIR = Path(__file__).parent.parent
INDEX_FILE = BASE_DIR / "index.json"


def load_index() -> list[dict]:
    """Charge l'index depuis index.json."""
    if not INDEX_FILE.exists():
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """Normalise un texte pour la comparaison : minuscules, sans accents."""
    import unicodedata
    text = text.lower()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    return text


def search_in_index(index: list[dict], query: str) -> list[dict]:
    """
    Étape 1 : Filtre l'index sur la query (nom de réunion ou participant).
    Retourne les entrées pertinentes triées par date décroissante, max 5.

    La query est comparée contre :
    - client
    - title
    - participants (chaque nom)
    """
    query_norm = normalize_text(query)
    query_parts = [p for p in query_norm.split() if len(p) > 2]

    scored = []
    for entry in index:
        if entry.get("type") == "calendar":
            continue  # Exclure le calendrier de la recherche historique

        score = 0

        # Match sur le client
        client_norm = normalize_text(entry.get("client") or "")
        if query_norm in client_norm or client_norm in query_norm:
            score += 3
        else:
            for part in query_parts:
                if part in client_norm:
                    score += 1

        # Match sur le titre
        title_norm = normalize_text(entry.get("title") or "")
        if query_norm in title_norm:
            score += 2
        else:
            for part in query_parts:
                if part in title_norm:
                    score += 1

        # Match sur les participants
        for participant in (entry.get("participants") or []):
            p_norm = normalize_text(participant)
            if query_norm in p_norm or p_norm in query_norm:
                score += 2
                break
            for part in query_parts:
                if part in p_norm:
                    score += 1
                    break

        if score > 0:
            scored.append((score, entry.get("date") or "0000-00-00", entry))

    # Trier par score DESC, puis par date DESC pour avoir les plus récents
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # Retourner les 5 plus pertinents et récents
    return [entry for _, _, entry in scored[:5]]


def load_files(entries: list[dict]) -> list[dict]:
    """
    Étape 2 : charge les fichiers listés dans les entrées d'index.
    Retourne une liste de contenus normalisés.
    """
    loaders = {
        "transcript": transcript_loader,
        "note": notes_loader,
        "summary": summary_loader,
    }

    results = []
    for entry in entries:
        file_type = entry.get("type")
        loader = loaders.get(file_type)
        if not loader:
            continue

        filepath = BASE_DIR / entry["path"]
        try:
            loaded = loader.load(filepath)
            for item in loaded:
                item["_source_type"] = file_type
                item["_source_path"] = entry["path"]
                item["_entry_date"] = entry.get("date") or ""
            results.extend(loaded)
        except Exception as e:
            console.print(f"  ⚠ Erreur chargement {entry['path']}: {e}", style="yellow")

    # Trier par date décroissante pour avoir le plus récent en premier
    results.sort(key=lambda x: x.get("_entry_date") or x.get("date") or "", reverse=True)
    return results


def generate_preparation_with_claude(
    query: str,
    files_content: list[dict],
) -> str:
    """
    Utilise Claude pour générer une fiche de préparation synthétique.

    Args:
        query: La requête initiale (nom de réunion ou participant)
        files_content: Liste des contenus chargés
    """
    client = get_client()

    if not files_content:
        # Pas d'historique trouvé
        return f"""## Fiche de préparation — {query}

⚠️ **Aucun historique trouvé** pour "{query}".

Il s'agit probablement d'une première interaction ou les fichiers ne sont pas encore indexés.

### Conseils de préparation
- Faites des recherches sur le contexte de {query} avant la réunion
- Préparez une présentation de votre solution et de votre équipe
- Définissez vos objectifs pour cette première rencontre
- Préparez des questions pour comprendre leurs besoins
"""

    # Construire le contexte pour Claude
    history_sections = []
    for i, item in enumerate(files_content):
        source_type = item.get("_source_type", "document")
        date_str = item.get("date") or item.get("_entry_date") or "date inconnue"
        title = item.get("title", "Sans titre")

        section = f"""
---
**[{source_type.upper()} — {date_str}] {title}**

{item.get('raw_text', '')[:800]}
"""
        if item.get("decisions"):
            section += f"\n**Décisions :** {item['decisions'][:300]}"
        if item.get("actions"):
            section += f"\n**Actions :** {item['actions'][:300]}"

        history_sections.append(section)

    prompt = f"""Tu es un assistant PM (Product Manager). Génère une fiche de préparation pour la réunion avec : **{query}**

## Historique disponible (du plus récent au plus ancien)
{"".join(history_sections)}

## Instructions
Génère une fiche de préparation professionnelle avec ces sections :

### 1. Vue d'ensemble
- Qui est {query} ? (déduit de l'historique)
- Relation : ancienneté, type de collaboration

### 2. Chronologie des interactions
Pour chaque réunion passée (brève, max 2 lignes par réunion) :
- Date + titre
- Sujets abordés
- Décisions prises

### 3. Last touchpoint
- Date de la dernière interaction
- Ce dont on a parlé
- Ce qui était prévu ensuite

### 4. Actions en cours (non résolues)
- Liste des actions [OPEN] qui n'ont pas encore été clôturées
- Pour chaque action : qui, quoi

### 5. Points à préparer pour la prochaine réunion
- Sujets à traiter en priorité
- Questions à poser
- Ce qu'ils attendent probablement de cette réunion

Format : markdown concis, ton professionnel. La fiche doit se lire en 2 minutes maximum.
"""

    console.print("\n[dim]Génération de la fiche de préparation avec Claude...[/dim]")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        full_text = ""
        for text in stream.text_stream:
            full_text += text

    return full_text


def run(query: str | None = None) -> None:
    """
    Point d'entrée du skill prepare_meeting.

    Args:
        query: Nom de la réunion ou du participant à rechercher.
               Si None, demande à l'utilisateur.
    """
    if query is None:
        query = console.input("\n[bold]Nom de la réunion ou du participant[/bold] : ").strip()

    if not query:
        console.print("[red]Veuillez entrer un nom de réunion ou de participant.[/red]")
        return

    console.print(f"\n[bold blue]🔍 Préparation de la réunion : {query}[/bold blue]\n")

    # Charger l'index
    index = load_index()
    if not index:
        console.print("[yellow]⚠ Index vide. Lancez d'abord : python indexer.py[/yellow]")
        return

    console.print(f"[dim]Index chargé : {len(index)} fichiers[/dim]")

    # ═══ ÉTAPE 1 : Filtrage sur index.json ═══
    relevant_entries = search_in_index(index, query)

    if not relevant_entries:
        console.print(f"[yellow]Aucun fichier trouvé pour '{query}' dans l'index.[/yellow]")
        console.print("[dim]Essayez avec un autre terme ou vérifiez que les fichiers sont indexés.[/dim]")
        # Générer quand même une fiche vide
        briefing = generate_preparation_with_claude(query, [])
    else:
        console.print(f"[green]✓ {len(relevant_entries)} fichier(s) pertinent(s) trouvé(s)[/green]")
        for e in relevant_entries:
            console.print(f"  [dim]→ [{e['type']:10s}] {e.get('date', '?')} | {e.get('title', 'Sans titre')}[/dim]")

        # ═══ ÉTAPE 2 : Charger les fichiers ═══
        files_content = load_files(relevant_entries)
        console.print(f"[dim]Fichiers chargés : {len(files_content)}[/dim]")

        # ═══ Génération avec Claude ═══
        briefing = generate_preparation_with_claude(query, files_content)

    # Affichage avec rich
    console.print(Rule(style="blue"))
    console.print(Panel(
        briefing,
        title=f"[bold]Fiche de préparation — {query}[/bold]",
        border_style="blue",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    query_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run(query_arg)
