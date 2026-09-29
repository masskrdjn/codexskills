# Routage multi-modèles sélectif pour Codex

[English](README.md)

Un modèle de configuration Codex qui confie le travail à des agents spécialisés uniquement lorsque la délégation devrait préserver la qualité tout en réduisant le coût total ou le délai. L’agent principal reste responsable des décisions, de l’intégration et de la communication avec l’utilisateur.

## Politique de routage

Priorités, dans l’ordre :

1. Préserver la qualité et la pertinence du résultat.
2. Réduire le coût total, coordination et reprises comprises.
3. Réduire le délai.

Les petites tâches bornées restent à l’agent principal. La délégation est utilisée lorsqu’un rôle clairement défini peut effectuer un travail substantiel plus efficacement ou fournir une analyse indépendante utile.

## Comparer les modèles indépendamment des rôles

Les rôles définissent les missions, restrictions et livrables. Ils ne classent
ni les modèles ni les efforts. Les cinq modèles suivants sont à comparer pour
la tâche; aucune hiérarchie universelle de qualité ou de tokens n'est établie ici.

| Modèle | Candidature dans le projet | Limite à conserver |
|---|---|---|
| GPT-6 Luna | Travail circonscrit; `high`, `xhigh` et `max` sont candidats, y compris pour une implémentation ou un cadrage bien définis | Plancher utilisateur `high`, dans les rôles comme dans le générique. Un faible prix par token ne prouve pas une consommation moindre. |
| GPT-6 Sol | Candidat ordinaire pour les missions techniques et les interactions complexes, indépendamment du rôle | Même exigence de qualité et même protocole comparatif que Sol 6.1; aucune preuve supplémentaire liée à son ancienneté. |
| GPT-5.6 Sol | Candidat ordinaire pour le raisonnement, le cadrage et les autres missions qu'il peut remplir | Même exigence que les autres Sol; ni exception de compatibilité ni inférieur présumé. |
| GPT-6.1 Sol | Candidat transversal pour l'implémentation, la recherche et les décisions | Sa nouveauté ne prouve ni moins de tokens ni un remplacement optimal des autres Sol. |
| GPT-6 Astra | Consultation `architect` lorsque la capacité supplémentaire répond à une difficulté identifiée | Quota et restrictions architect; pas d'exploration, commande, écriture ni délégation. |

Vérifier les modèles et efforts réellement disponibles dans le runtime.
La disponibilité API ne prouve pas leur disponibilité dans Codex. Les noms
d'effort ne sont pas équivalents entre modèles : Luna `xhigh` ne signifie pas
Sol `medium`, ni Sol `xhigh` Astra `low`.

## Choisir la capacité, puis l'efficience en tokens

Le couple modèle/effort dépend de l'ambiguïté du contrat, des dépendances et
interactions, des contradictions, de la validation et des conséquences d'une
erreur. La longueur du lot, le nombre de fichiers et le rôle ne suffisent pas.
Une information manquante appelle une collecte ciblée, pas automatiquement
plus d'effort. Cette qualification n'autorise pas l'exploration avant le routage.

1. **Capacité** : identifier les couples admissibles qui peuvent satisfaire
   les mêmes critères de qualité et de pertinence, avec une validation adaptée
   aux conséquences d'une erreur. Écarter un couple pour une limite identifiée,
   pas pour son ancienneté ou son prix. Une incertitude décisive reste explicite.
2. **Efficience** : parmi les couples admissibles, comparer les tokens du travail
   complet, racine, enfants et reviewers inclus, puis le coût monétaire et le
   délai séparément. Sans mesures comparables, le choix reste une hypothèse de
   politique, pas une économie démontrée ni un optimum.

La grille ci-dessous propose des candidats à évaluer; chaque Sol désigne
GPT-6 Sol, GPT-5.6 Sol et GPT-6.1 Sol, soumis aux mêmes conditions d'admission.
Les efforts proposés restent conditionnels à leur disponibilité effective.

| Difficulté et preuves disponibles | Couples candidats | Validation et signal de requalification |
|---|---|---|
| Contrat explicite, faible ambiguïté, validation directe | Luna `high`; chaque Sol `low`/`medium` | Vérification directe des critères. Une petite tâche reste à la racine par défaut. |
| Plusieurs étapes contraintes, jugement limité | Luna `high`/`xhigh`; chaque Sol `medium`/`high` | Vérifier les interactions entre étapes; remonter une ambiguïté décisive. |
| Interactions non triviales, invariants délicats, hypothèses concurrentes | Luna `high`/`xhigh`/`max` si sa capacité est admissible; chaque Sol `medium`/`high`/`xhigh` | Valider les invariants et départager les hypothèses; changer de modèle si la capacité est la limite. |
| Preuves contradictoires, synthèse difficile, validation indirecte | Chaque Sol `high`/`xhigh`/`max`; Luna `xhigh`/`max` si sa capacité est admissible | Préserver les réserves; requalifier si une contradiction décisive persiste. |
| Arbitrage structurant difficile à corriger, ambiguïté persistante | Chaque Sol `high`/`xhigh`/`max`; consultation Astra à l'effort adapté et disponible | Justifier la capacité supplémentaire et respecter l'enveloppe architect. |

`xhigh` et `max` sont des candidats à comparer, pas des promotions automatiques.
Un rôle researcher ou un prix bas ne déclenche pas `max`. Il n'est pas nécessaire
d'avoir épuisé tous les efforts inférieurs pour évaluer `max` : justifier sa
candidature par la tâche puis mesurer la qualité et les tokens complets.
Les secours Luna sont `high`, y compris runner et générique; ce choix provisoire
respecte le plancher utilisateur, sans établir que `high` est optimal.
Les modèles de secours existants restent en place; ni leurs valeurs TOML ni
leur exécution ne prouvent une économie. Les variantes scout_complex et
researcher_complex sont des facilités de runtime, pas un classement obligatoire.

Au lancement, annoncer rôle, modèle exact, effort, faits justifiant le choix,
hypothèses, inconnues, validation attendue et signal de requalification.
Utiliser les overrides explicites et `fork_turns = "none"` seulement si le
runtime les autorise. S'il verrouille le profil, choisir un profil disponible
préservant le contrat et les restrictions; sinon garder la mission à la racine
et signaler le couple non exécutable. Un générique ne convient que si ces
garanties peuvent être conservées. Une consigne ne remplace pas un outil désactivé.
Ne jamais annoncer un override non appliqué. Astra passe exclusivement par
architect vérifiable. Le modèle et l'effort racine choisis par l'utilisateur
restent prioritaires; le plancher Luna concerne les sélections des sous-agents.

L'enfant remonte les faits qui invalident son choix initial; seule la racine
requalifie. Une difficulté d'exécution ne justifie pas automatiquement plus de
capacité. Réutiliser les preuves et validations pertinentes plutôt que refaire
le travail. Une difficulté conceptuelle décisive se remonte immédiatement.

### Sources officielles et limites

Recherche transmise par la racine, consultée le 29 septembre 2026 :
[sélection](https://developers.openai.com/api/docs/guides/model-selection),
[migration](https://developers.openai.com/api/docs/guides/latest-model),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Sol 6](https://developers.openai.com/api/docs/models/gpt-6-sol),
[Sol 5.6](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Sol 6.1](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
Les fiches positionnent Luna sur le travail ciblé, Sol 6.1 sur le travail
complexe et Astra sur les missions exigeantes. Le guide recommande d'évaluer
les candidats sur les mêmes entrées et de retenir un réglage satisfaisant la
qualité requise. Le renvoi de Sol 6 vers 6.1 ne démontre pas moins de tokens
sur ce dépôt. Les tarifs API et résultats d'évaluations externes n'établissent
pas une économie de tokens du projet; le plancher Luna high est une préférence
utilisateur distincte des exemples documentaires. La grille reste une hypothèse
à valider, pas une recommandation comparative prouvée par ces sources.

## Mesurer sans confondre tokens, prix et qualité

Aucune économie ni réduction de tokens n'est mesurée par cette révision.
Une comparaison exige les mêmes tâches, critères d'acceptation, contexte
fourni, outils et permissions, validation et budget de tentatives. Identifier
chaque run, tâche, scénario, couple modèle/effort effectif, bras et répétition;
apparier les runs et randomiser l'ordre des candidats. Publier cache froid et
cache chaud séparément. Deux runs complets non appariés ne fondent pas une
conclusion économique. Une comparaison exploratoire requiert au moins deux
paires complètes par tâche/scénario; elle ne remplace pas le seuil existant de
cinq paires complètes comparables et randomisées pour promouvoir une tâche
locale vers une délégation économique en cache froid.

Compter tout le travail : contexte entrant, raisonnement, réponses et échanges
d'outils, cadrage, coordination, intégration, validation, corrections et reprises,
racine, enfants et reviewers compris. Les appels d'outils contribuent aux tokens
de leurs échanges avec le modèle; ne pas ajouter leur texte une deuxième fois
aux compteurs d'usage. Si `Reasoning` est inclus dans `Output`, le total est
`Input + Output`, pas `Input + Output + Reasoning`. Si `Cached` est inclus dans
`Input`, il ne s'ajoute pas à `Input`; distinguer `Uncached = Input - Cached`.
Vérifier ces inclusions dans la source des compteurs avant tout calcul.

Rapporter séparément tokens totaux et ventilés, coût monétaire selon les tarifs
datés propres à chaque modèle, délai, qualité et taux de succès. Les crédits
Codex ne sont pas des dollars API. Inclure les succès et les échecs complets,
leurs corrections et relances selon une règle fixée avant les runs; ne pas
comparer seulement les survivants. Un échec complet reste observable. Un run
`Complete = false` a exactement le statut `non observable` : exclure ses tokens
et durées de tous ratios, médianes et recommandations économiques; conserver
son diagnostic et le nombre d'incomplets. Ne pas fabriquer une paire depuis un
survivant; si les paires admissibles manquent, aucune conclusion économique.
Mesurer `guardian_review` séparément et l'inclure dans le total, sans le présenter
comme un levier directement contrôlable. Publier les limites de représentativité.

## Profils de secours

Ces valeurs servent lorsque le runtime ne permet pas un choix explicite. Elles ne remplacent pas la grille par tâche et ne prouvent pas un optimum.
Le sous-agent générique utilise aussi Luna `high`. Les réglages installés
personnalisés restent préservés avec avertissement; les revoir explicitement
s'ils contredisent le plancher Luna.

| Rôle | Modèle de secours | Effort de secours | Responsabilité |
| --- | --- | --- | --- |
| Principal | Choisi par l'utilisateur | Variable | Triage, décisions, intégration et petites tâches locales |
| `scout` | `gpt-6-luna` | `high` | Exploration en lecture seule du code et des journaux |
| `scout_complex` (facultatif) | `gpt-6.1-sol` | `xhigh` | Départager des preuves contradictoires entre composants |
| `researcher` | `gpt-6-luna` | `high` | Recherche externe à plusieurs sources |
| `researcher_complex` (facultatif) | `gpt-6.1-sol` | `xhigh` | Synthétiser des sources contradictoires pour une décision technique importante |
| `runner` | `gpt-6-luna` | `high` | Validations longues et lots mécaniques conséquents |
| `builder` | `gpt-6.1-sol` | `high` | Implémentation substantielle avec validation ciblée |
| `strategist` | `gpt-6.1-sol` | `medium` | Cadrage complexe, décomposition et arbitrages intermédiaires |
| `architect` | `gpt-6-astra` | `low` | Rares décisions d’architecture, strictement cadrées |

## Structure du projet

```text
.
├── AGENTS.md
├── .agents/skills/quota-orchestrator/SKILL.md
├── .agents/plugins/marketplace.json
├── plugins/codexskills/
│   ├── .codex-plugin/plugin.json
│   ├── hooks/hooks.json, hooks/reconcile.py
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
        ├── scout_complex.toml
        └── strategist.toml
```

- `AGENTS.md` définit les règles de routage et de sécurité du dépôt.
- `quota-orchestrator` détermine si la délégation justifie son coût complet.
- `.codex/config.toml` sélectionne le modèle principal et active le travail multi-agent.
- `.codex/agents/*.toml` définit le modèle, les outils, les limites et le contrat de compte rendu de chaque rôle.
- `.agents/plugins/marketplace.json` expose le catalogue Codex du dépôt.
- `plugins/codexskills/` contient le manifeste, les deux skills, l'installateur contrôlé et les profils complets distribués comme modèles.

## Installation comme plugin

> [!IMPORTANT]
> Version actuelle du plugin : **0.8.0**.
>
> Une marketplace de dépôt approuvée installe le plugin par défaut. Codex
> demande encore une fois votre confiance pour son hook SessionStart. Ce hook
> configure ensuite les six profils globaux et les vérifie aux sessions suivantes.

Depuis le clone local, pour tester avant publication :

```text
codex plugin marketplace add .
```

Après publication du dépôt :

```text
codex plugin marketplace add masskrdjn/codexskills
```

Quand Codex propose d'examiner le hook fourni, accordez-lui votre confiance
une fois si vous voulez la configuration automatique. À chaque SessionStart,
un script local Python 3.11+ réconcilie `scout`, `researcher`, `runner`,
`builder`, `strategist` et `architect` dans `CODEX_HOME` (ou `~/.codex`). Il ne
fait aucun appel réseau ni mise à niveau de marketplace. Il fusionne les
réglages compatibles, sauvegarde les fichiers modifiés sous
`CODEX_HOME/.codexskills-backup/` et préserve les fichiers divergents avec un
avertissement exploitable. L'état et un verrou de concurrence temporaire sont
stockés sous `PLUGIN_DATA`, ou sous `CODEX_HOME/.codexskills-data` si cette
variable est absente. Un échec reporte la réconciliation à la session suivante.
Ouvrez une nouvelle tâche Codex pour charger les profils installés.

Si le hook est refusé, indisponible, ou signale un conflit, demandez
« Configure les profils complets de codexskills » pour prévisualiser et
reprendre manuellement. L'installation par défaut ne contourne pas la confiance
requise pour le dépôt, le plugin ou le hook. Le rafraîchissement du paquet de
marketplace est distinct : le hook applique uniquement la version déjà
installée et ne télécharge jamais une nouvelle version. Si la commande `python`
ne lance pas Python 3.11 ou plus, utilisez la configuration manuelle ou rendez
cet interpréteur disponible avant d'approuver le hook.

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

### Installation manuelle et récupération

Ce parcours sert uniquement à l'installation sans plugin, à la récupération
après un refus du hook ou au test explicite de l'installateur. L'utilisation
normale du plugin ne nécessite pas cette commande. Python 3.11 ou supérieur est
requis :

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
- `strategist` prépare le plan mais ne lance pas lui-même de sous-agents.
- `architect` n’explore pas, n’exécute aucune commande, ne modifie aucun fichier et ne délègue pas.
- Les sous-agents restent dans leur rôle et n’effectuent pas eux-mêmes le routage.

## Personnalisation

Modifiez `.codex/config.toml` pour changer le modèle principal, les valeurs par défaut ou la concurrence. Modifiez le fichier correspondant dans `.codex/agents/` pour changer un rôle. Conservez les limites des rôles et les noms de modèles synchronisés avec `AGENTS.md` et `quota-orchestrator/SKILL.md`.

La disponibilité des modèles dépend de votre compte Codex et de votre environnement.
