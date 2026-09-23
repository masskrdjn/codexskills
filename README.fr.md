# Routage multi-modèles sélectif pour Codex

[English](README.md)

Un modèle de configuration Codex qui confie le travail à des agents spécialisés uniquement lorsque la délégation devrait préserver la qualité tout en réduisant le coût total ou le délai. L’agent principal reste responsable des décisions, de l’intégration et de la communication avec l’utilisateur.

## Politique de routage

Priorités, dans l’ordre :

1. Préserver la qualité et la pertinence du résultat.
2. Réduire le coût total, coordination et reprises comprises.
3. Réduire le délai.

Les petites tâches bornées restent à l’agent principal. La délégation est utilisée lorsqu’un rôle clairement défini peut effectuer un travail substantiel plus efficacement ou fournir une analyse indépendante utile.

| Rôle | Modèle | Effort | Responsabilité |
| --- | --- | --- | --- |
| Principal | Choisi par l'utilisateur | Variable | Triage, décisions, intégration et petites tâches locales |
| `scout` | `gpt-6-luna` | `high` | Exploration en lecture seule du code et des journaux |
| `scout_complex` (facultatif) | `gpt-6-sol` | `high` | Départager des preuves contradictoires entre composants |
| `researcher` | `gpt-6-luna` | `max` | Recherche externe à plusieurs sources |
| `researcher_complex` (facultatif) | `gpt-6-sol` | `max` | Synthétiser des sources contradictoires pour une décision technique importante |
| `runner` | `gpt-6-luna` | `medium` | Validations longues et lots mécaniques conséquents |
| `builder` | `gpt-6-luna` | `max` | Implémentation bornée avec validation ciblée |
| `architect` | `gpt-6-astra` | `low` | Rares décisions d’architecture, strictement cadrées |

Le sous-agent par défaut est GPT-6 Luna avec un effort `max`. Le nombre de threads enfants simultanés est limité à quatre par session. Les variantes Sol sont choisies dès le triage selon les critères ci-dessus ; les petites tâches locales restent à l'agent principal.

Aux [tarifs API Standard](https://developers.openai.com/api/docs/models/gpt-6-luna), GPT-6 Luna coûte 0,10 $ en entrée / 0,50 $ en sortie par million de tokens. [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol) coûte 2 $ / 10 $. Sol coûte vingt fois Luna par token en entrée ou sortie : son choix demande un besoin de qualité identifiable. Le builder utilise Luna avec un effort `max` pour les tâches clairement spécifiées ; les décisions d'implémentation complexes restent à la racine. Les [crédits Codex](https://learn.chatgpt.com/docs/pricing) constituent une unité distincte des dollars API. Aucun gain sur les tâches de ce projet n'est encore démontré. Les cinq profils initiaux restent obligatoires ; les deux variantes Sol sont facultatives.

## Structure du projet

```text
.
├── AGENTS.md
├── .agents/skills/quota-orchestrator/SKILL.md
├── .agents/plugins/marketplace.json
├── plugins/codexskills/
│   ├── .codex-plugin/plugin.json
│   ├── skills/
│   │   ├── quota-orchestrator/SKILL.md
│   │   └── quota-orchestrator-setup/SKILL.md
│   ├── scripts/install.py
│   └── templates/
└── .codex/
    ├── config.toml
    └── agents/
        ├── architect.toml
        ├── builder.toml
        ├── researcher.toml
        ├── researcher_complex.toml
        ├── runner.toml
        ├── scout.toml
        └── scout_complex.toml
```

- `AGENTS.md` définit les règles de routage et de sécurité du dépôt.
- `quota-orchestrator` détermine si la délégation justifie son coût complet.
- `.codex/config.toml` sélectionne le modèle principal et active le travail multi-agent.
- `.codex/agents/*.toml` définit le modèle, les outils, les limites et le contrat de compte rendu de chaque rôle.
- `.agents/plugins/marketplace.json` expose le catalogue Codex du dépôt.
- `plugins/codexskills/` contient le manifeste, les deux skills, l'installateur contrôlé et les profils complets distribués comme modèles.

## Installation comme plugin

> [!IMPORTANT]
> L'installation du plugin ne suffit pas à activer les cinq profils complets.
> Une configuration globale unique est requise. Sans elle, le
> plugin le signalera au début des tâches et ne prétendra pas que le routage
> complet est actif.

Depuis le clone local, pour tester avant publication :

```text
codex plugin marketplace add .
codex plugin add codexskills@codexskills
```

Après publication du dépôt :

```text
codex plugin marketplace add masskrdjn/codexskills
codex plugin add codexskills@codexskills
```

Première étape obligatoire après l'installation, demandez dans Codex :

```text
Configure les profils complets de codexskills.
```

Le skill de configuration prévisualise les changements puis installe
`scout`, `researcher`, `runner`, `builder` et `architect` dans `CODEX_HOME`
(ou `~/.codex` s'il est absent). Il fusionne les réglages compatibles,
sauvegarde les fichiers modifiés sous `CODEX_HOME/.codexskills-backup/` et
s'arrête devant tout avertissement ou profil divergent jusqu'à confirmation.
Ouvrez ensuite une nouvelle tâche Codex pour charger les profils. L'installation
du plugin ne modifie aucune configuration et n'utilise aucun hook. Après cette
configuration, le routage est détecté automatiquement : il n'est pas nécessaire
de nommer le plugin dans chaque demande.

## Installation sans plugin

Clonez le dépôt dans un répertoire que vous souhaitez utiliser comme projet Codex :

```bash
git clone https://github.com/masskrdjn/codexskills.git
cd codexskills
```

Vous pouvez aussi copier ou fusionner `AGENTS.md`, `.agents/` et `.codex/` à la racine d’un dépôt existant, puis vérifier la configuration de ce projet avant de lui accorder votre confiance dans Codex.

### Choisir le périmètre : global, projet ou les deux

Il n’est **pas** nécessaire de copier tout ce dépôt dans chaque projet. Placez chaque élément selon sa portée :

| Portée | Emplacement | Cas d’usage |
| --- | --- | --- |
| Globale | Répertoire d’accueil de Codex (normalement `~/.codex/`) | Préférences personnelles applicables à tous les dépôts. Placez les instructions partagées dans `AGENTS.md`, les réglages partagés dans `config.toml` et les skills réutilisables dans `skills/`. |
| Projet | Racine du dépôt | Règles, réglages, skills et rôles d’agents propres à ce codebase. Utilisez la structure `AGENTS.md`, `.agents/` et `.codex/` de ce dépôt comme modèle. |
| Hybride (recommandé) | Les deux emplacements | Conservez la politique de routage et les valeurs par défaut en global ; ajoutez uniquement les commandes, conventions, restrictions et remplacements spécifiques au projet dans le dépôt. |

Codex charge d’abord les instructions globales, puis les instructions du projet, de la racine du dépôt vers le répertoire courant. Le fichier de projet le plus proche est prioritaire. De même, `.codex/config.toml` peut remplacer des réglages utilisateur, mais Codex ne charge les couches `.codex/` locales qu’après que vous avez accordé votre confiance au projet.

N’ajoutez pas de commandes, secrets, chemins ou exceptions de sécurité propres à un dépôt dans la configuration globale : ils affecteraient tous les projets. Si vous déplacez ce modèle vers `~/.codex/`, fusionnez les réglages utiles avec vos fichiers existants au lieu de les remplacer entièrement.

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
python install.py --global
```

La structure globale est `AGENTS.md`, `config.toml`, `agents/` et `skills/`
directement sous `CODEX_HOME` (ou `~/.codex` s'il est absent). Utilisez
`--dry-run` pour prévisualiser chaque changement. L’installateur met à niveau
les fichiers identiques à une version distribuée auparavant, sauvegarde les
fichiers modifiés sous `CODEX_HOME/.codexskills-backup/` et préserve avec
avertissement les fichiers personnalisés et les valeurs de configuration.
Pour une installation projet explicite,
exécutez `python install.py chemin/vers/votre/projet` ; sans chemin, le
comportement historique utilise le répertoire courant.
Pour migrer la valeur par défaut du sous-agent générique de GPT-5.6 Luna vers
GPT-6 Luna, ajoutez `--upgrade-default-model` à la prévisualisation et à
l'installation.

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
