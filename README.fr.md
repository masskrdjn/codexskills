# Routage multi-modèles sélectif pour Codex

[English](README.md)

Une configuration Codex propre au projet qui confie le travail à des agents spécialisés uniquement lorsque la délégation devrait préserver la qualité tout en réduisant le coût total ou le délai. L’agent principal reste responsable des décisions, de l’intégration et de la communication avec l’utilisateur.

## Politique de routage

Priorités, dans l’ordre :

1. Préserver la qualité et la pertinence du résultat.
2. Réduire le coût total, coordination et reprises comprises.
3. Réduire le délai.

Les petites tâches bornées restent à l’agent principal. La délégation est utilisée lorsqu’un rôle clairement défini peut effectuer un travail substantiel plus efficacement ou fournir une analyse indépendante utile.

| Rôle | Modèle | Effort | Responsabilité |
| --- | --- | --- | --- |
| Principal | `gpt-5.6-sol` | `medium` | Triage, décisions, intégration et petites tâches locales |
| `scout` | `gpt-5.6-luna` | `max` | Exploration en lecture seule du code et des journaux |
| `researcher` | `gpt-5.6-luna` | `max` | Recherche externe à plusieurs sources |
| `runner` | `gpt-5.6-luna` | `medium` | Validations longues et lots mécaniques conséquents |
| `builder` | `gpt-5.6-terra` | `high` | Implémentation bornée avec validation ciblée |
| `architect` | `gpt-6-astra` | `low` | Rares décisions d’architecture, strictement cadrées |

Le sous-agent par défaut est Luna avec un effort `max`. Le nombre de threads enfants simultanés est limité à quatre par session.

## Structure du projet

```text
.
├── AGENTS.md
├── .agents/skills/quota-orchestrator/SKILL.md
└── .codex/
    ├── config.toml
    └── agents/
        ├── architect.toml
        ├── builder.toml
        ├── researcher.toml
        ├── runner.toml
        └── scout.toml
```

- `AGENTS.md` définit les règles de routage et de sécurité du dépôt.
- `quota-orchestrator` détermine si la délégation justifie son coût complet.
- `.codex/config.toml` sélectionne le modèle principal et active le travail multi-agent.
- `.codex/agents/*.toml` définit le modèle, les outils, les limites et le contrat de compte rendu de chaque rôle.

## Installation

Clonez le dépôt dans un répertoire que vous souhaitez utiliser comme projet Codex :

```bash
git clone https://github.com/masskrdjn/codexskills.git
cd codexskills
```

Vous pouvez aussi copier ou fusionner `AGENTS.md`, `.agents/` et `.codex/` à la racine d’un dépôt existant, puis vérifier la configuration de ce projet avant de lui accorder votre confiance dans Codex.

## Utilisation

1. Vérifiez les noms de modèles, la politique d’approbation, le mode du bac à sable et la limite de concurrence pour votre environnement.
2. Accordez votre confiance au projet lorsque Codex le demande ; le fichier `.codex/config.toml` du projet n’est chargé que pour les projets approuvés.
3. Démarrez une nouvelle tâche Codex depuis ce dépôt.
4. Demandez à Codex de résumer ses instructions actives si vous souhaitez vérifier leur détection.

Codex détecte les instructions du dépôt dans `AGENTS.md`, les skills locaux dans `.agents/skills` et les agents personnalisés dans `.codex/agents`. Consultez la documentation officielle sur [AGENTS.md](https://developers.openai.com/codex/guides/agents-md), les [skills](https://developers.openai.com/codex/skills), les [sous-agents](https://developers.openai.com/codex/subagents) et la [configuration](https://developers.openai.com/codex/config-reference).

## Limites de sécurité

- Ne jamais utiliser `--yolo` ni `--dangerously-bypass-approvals-and-sandbox`.
- Les permissions imposées au parent pendant l’exécution s’appliquent aussi aux agents enfants.
- Ne pas utiliser `architect` si ces permissions annulent ses restrictions de lecture seule.
- `architect` n’explore pas, n’exécute aucune commande, ne modifie aucun fichier et ne délègue pas.
- Les sous-agents restent dans leur rôle et n’effectuent pas eux-mêmes le routage.

## Personnalisation

Modifiez `.codex/config.toml` pour changer le modèle principal, les valeurs par défaut ou la concurrence. Modifiez le fichier correspondant dans `.codex/agents/` pour changer un rôle. Conservez les limites des rôles et les noms de modèles synchronisés avec `AGENTS.md` et `quota-orchestrator/SKILL.md`.

La disponibilité des modèles dépend de votre compte Codex et de votre environnement.
