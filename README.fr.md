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
| `scout` | `gpt-5.6-luna` | `high` | Exploration en lecture seule du code et des journaux |
| `researcher` | `gpt-5.6-luna` | `max` | Recherche externe à plusieurs sources |
| `runner` | `gpt-5.6-luna` | `medium` | Validations longues et lots mécaniques conséquents |
| `builder` | `gpt-5.6-terra` | `medium` | Implémentation bornée avec validation ciblée |
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

## Utilisation

### Héritage et priorité

Pour les instructions, Codex construit une chaîne au démarrage :

1. Il charge un fichier global depuis `~/.codex` : `AGENTS.override.md` s’il existe, sinon `AGENTS.md`.
2. Il parcourt ensuite le projet de la racine du dépôt jusqu’au répertoire courant et retient un fichier par dossier : `AGENTS.override.md` en priorité, sinon `AGENTS.md`.
3. Il concatène les fichiers retenus dans cet ordre. Les consignes les plus proches du répertoire courant sont donc lues en dernier et prévalent uniquement en cas de conflit ; les autres consignes restent actives.

Si votre projet contient déjà un `AGENTS.md`, **ne le remplacez pas** : conservez son contenu et ajoutez-y les consignes de routage de ce dépôt. Pour limiter une consigne à un sous-répertoire, placez un autre `AGENTS.md` dans celui-ci. N’utilisez `AGENTS.override.md` que si vous voulez volontairement ignorer le `AGENTS.md` situé dans le même dossier : les deux ne sont pas fusionnés.

Pour la configuration, `~/.codex/config.toml` fournit les valeurs utilisateur. Chaque `.codex/config.toml` du projet approuvé ajoute ses propres valeurs ; à clé identique, la couche de projet la plus proche du répertoire courant l’emporte, tandis que les clés absentes restent héritées. Les options passées en ligne de commande restent prioritaires. Codex ignore les couches `.codex/` locales tant que le projet n’est pas approuvé, et certaines clés sensibles ne peuvent pas être redéfinies au niveau du projet.

### Installation

Python 3.11 ou supérieur est requis. Depuis ce dépôt, exécutez :

```text
python install.py [chemin/vers/votre/projet]
```

Le répertoire courant est utilisé si le chemin est omis. Utilisez `--dry-run` pour prévisualiser chaque changement. L’installateur préserve les instructions et valeurs de configuration existantes, sauvegarde les fichiers modifiés sous `.codexskills-backup/` et avertit au lieu d’écraser les fichiers d’agent ou de skill divergents.

Après l’installation, vérifiez les éventuels avertissements ainsi que les noms de modèles, la politique d’approbation, le mode du bac à sable et la limite de concurrence pour votre environnement. Accordez votre confiance au projet lorsque Codex le demande, puis démarrez une nouvelle tâche Codex depuis ce dépôt afin de reconstruire la chaîne d’instructions. Le fichier `.codex/config.toml` du projet n’est chargé que pour les projets approuvés.

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
