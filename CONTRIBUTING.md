# Modifier et maintenir codexskills

Ce document est le point d'entrée pour les prochaines modifications du dépôt.
`AGENTS.md` contient le routage ; ce guide décrit la maintenance du plugin.

## Versionner chaque évolution

Chaque évolution livrable, y compris une correction, une documentation ou une
modification des consignes, doit augmenter la version sans attendre une demande
de l'utilisateur. La source de vérité est le champ `version` de
`plugins/codexskills/.codex-plugin/plugin.json`.

- **PATCH** : correction compatible, documentation ou maintenance sans nouvelle
  capacité. Exemple : `0.9.0` → `0.9.1`.
- **MINOR** : nouvelle capacité, nouveau rôle ou nouveau routage compatible.
  Exemple : `0.8.5` → `0.9.0` pour l'intégration de Terra.
- **MAJOR** : changement incompatible du contrat public ; documenter la rupture
  et la migration avant de le livrer.

Une évolution cohérente reçoit une seule nouvelle version, même si elle comporte
plusieurs modifications et validations. Les ajustements du même lot non publié
restent dans cette version. Ne jamais modifier une version déjà publiée sous le
même numéro. La proposition `0.8.6`, non publiée, est regroupée dans la `0.9.0`.

À chaque évolution : modifier le manifeste, synchroniser la version courante
dans les deux README, compléter `CHANGELOG.md` avec la date et les changements,
puis exécuter les validations pertinentes. Conserver les anciens numéros dans
les fixtures, empreintes et notes historiques : aucun remplacement global.
La version du client simulé des tests natifs n'est pas la version du plugin.

Distinguer « préparée localement », « commitée », « poussée » et « publiée ».
Un numéro modifié ne prouve aucune étape suivante. Ne pas publier, pousser ou
créer un tag au seul motif que la version a changé.

## Carte du projet et synchronisation

| Fichiers | Responsabilité et règle |
|---|---|
| `AGENTS.md` | Consignes courtes de l'hôte. Copie identique dans `plugins/codexskills/templates/AGENTS.md`. La section maintenance ne concerne que le dépôt source. |
| `.codex/config.toml` | Configuration de secours. Copie identique dans `plugins/codexskills/templates/.codex/config.toml`. Respecter le modèle racine choisi par l'utilisateur. |
| `.codex/agents/*.toml` | Contrats, modèles et efforts des rôles. Synchroniser fichiers et contenu avec `plugins/codexskills/templates/.codex/agents/`. |
| `.agents/skills/quota-orchestrator/SKILL.md` | Politique locale française. Copie identique dans `plugins/codexskills/templates/.agents/skills/quota-orchestrator/SKILL.md`. |
| `plugins/codexskills/skills/quota-orchestrator/SKILL.md` | Skill du plugin en anglais avec setup et secours. Adapter les règles équivalentes ; ce n'est pas une copie littérale du skill français. |
| `plugins/codexskills/skills/quota-orchestrator-setup/` | Installation manuelle et reprise après conflit ; actualiser si les commandes ou garanties changent. |
| `install.py` | Installateur du dépôt ; `SOURCE` est la racine. |
| `plugins/codexskills/scripts/install.py` | Installateur embarqué ; `SOURCE` est `plugins/codexskills/templates`. Même logique, seule cette affectation diffère. |
| `plugins/codexskills/hooks/reconcile.py` | Réconciliation locale au démarrage, empreintes, verrou et sauvegardes. État sous `PLUGIN_DATA`, ou `CODEX_HOME/.codexskills-data`. Aucun téléchargement de version. |
| `plugins/codexskills/hooks/check_delegation.py` | Refuse les couples modèle/effort identiques et les paramètres indéterminables avant création d'un agent. |
| `plugins/codexskills/hooks/hooks.json` | Déclaration des hooks ; une modification peut nécessiter une nouvelle confiance dans l'application. |
| `plugins/codexskills/.codex-plugin/plugin.json` | Version et présentation du plugin. Actualiser listes et nombres de rôles quand ils changent. |
| `.agents/plugins/marketplace.json` | Catalogue local pointant sur le plugin. Ne pas inventer un champ de version supplémentaire. |
| `README.md`, `README.fr.md` | Documentation utilisateur anglaise et française ; garder version, profils, installation et limites cohérents. |
| `fixtures/release_*/` | Sources historiques des migrations, à préserver. |
| `test_install.py`, `test_reconcile.py`, `tests/` | Tests d'installation, de réconciliation, du garde-fou et de distribution. |

Aucune génération automatique ne synchronise les copies pendant une modification.
Les tests de distribution signalent leurs écarts.

## Faire évoluer les rôles et modèles

Définir le besoin, le périmètre, les critères d'acceptation et la validation avant
de choisir le modèle. Le nom d'un rôle ne lui accorde aucun outil ou permission.
Les paramètres effectifs du runtime priment sur les intentions du profil.

Pour un nouveau modèle, vérifier capacités, prix, efforts et disponibilité sur
des sources officielles actuelles. Documenter URLs, date et inconnues. Distinguer
API et Codex, coût par token et coût complet, effort demandé et effort appliqué.

Un rôle ajouté concerne ses deux profils, les deux `AGENTS.md`, les skills
français et anglais, les README, les listes et nombres du manifeste et les
fichiers attendus dans les tests. L'installateur découvre les profils par glob :
aucun registre manuel dans `config.toml` n'est à compléter.

Les profils couvrent exploration (`scout`), recherche (`researcher`), validation
(`runner`), implémentation (`builder_luna`, `builder`), cadrage (`strategist`),
architecture (`architect`), vision (`visual_operator`) et rédaction (`writer`).
Avec les deux variantes facultatives `scout_complex` et `researcher_complex`,
il existe onze fichiers de profil, dont neuf profils standard.

## Préserver les installations existantes

Un fichier connu peut être mis à niveau avec sauvegarde ; un fichier personnalisé
ou inconnu est conservé avec avertissement. Les blocs gérés de `AGENTS.md` ont
leurs propres empreintes. Ne jamais enregistrer un fichier personnalisé comme
ancienne distribution pour forcer son remplacement.

Avant de modifier un fichier distribué d'une version publiée :

1. Préserver son contenu authentique dans une nouvelle fixture si nécessaire.
   Ne jamais réécrire les fixtures existantes ni reconstruire l'ancien contenu
   depuis un fichier déjà modifié.
2. Enregistrer les empreintes nécessaires dans les deux installateurs : SHA-256
   après normalisation CRLF vers LF. Pour un bloc, suivre le découpage exact et
   la normalisation de `_merge_agents`.
3. Tester projet et global : mise à niveau, sauvegardes exactes, conservation
   des personnalisations et deuxième passage sans modification.

La `0.9.0` reconnaît déjà les fichiers de `0.8.5`. Une future évolution de fichiers
publiés en `0.9.0` devra reconnaître ceux-ci à son tour. Ne pas fabriquer une
migration depuis une version intermédiaire jamais distribuée.

## Validation

Python 3.11 ou supérieur est requis. Depuis la racine :

```powershell
python -m unittest discover -s tests -p '*_test.py'
python test_install.py
python test_reconcile.py
git diff --check
```

`tests/distribution_test.py` contrôle versions, copies et parité des installateurs.
Pour un changement uniquement documentaire, ces contrôles de cohérence et
`git diff --check` suffisent. Pour des profils, templates, installateurs ou hooks,
exécuter les trois suites Python. Une modification ultérieure n'invalide que les
validations qu'elle peut affecter ; ne pas répéter les autres sans raison.

Les tests natifs facultatifs requièrent `CODEX_GUARD_TEST_BINARY`, chemin de
l'exécutable Codex. Ils utilisent des réponses simulées et un environnement
jetable ; sans la variable, ils sont ignorés. Les tests hors ligne ne mesurent
pas les performances réelles des modèles. Rapporter codes de sortie, preuve
d'achèvement, tests réussis et tests ignorés.

Un refus de permissions sur un dossier temporaire est un problème d'environnement,
à diagnostiquer via les mécanismes d'autorisation de l'hôte, sans contourner le
bac à sable. Ne pas utiliser le vrai `CODEX_HOME` pour tester : les suites créent
des installations jetables. Ne pas modifier le cache installé à la place de la
source du dépôt.

## Clôture

Examiner le diff et les nouveaux fichiers, retirer les scripts temporaires de
la tâche, vérifier version, changelog, copies, migrations et tests concernés.
Rapporter ce qui a changé, les validations, les limites et l'état réel de
publication. Après une mise à jour installée, une nouvelle conversation charge
les profils.

Les outils locaux de mesure sont en partie ignorés par Git ; ne pas présenter
leurs chiffres comme une mesure reproductible de la révision sans leur harnais.
La règle `test_*.py` de `.gitignore` ignore les nouveaux tests racine : ajouter
les nouveaux tests versionnés sous `tests/` avec le suffixe `_test.py`.
Les deux tests racine existants restent suivis par Git.
