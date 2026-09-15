---
name: quota-orchestrator
description: Routage sélectif multi-modèles pour la racine lorsqu'une délégation ou un arbitrage de palier peut améliorer le résultat, le délai ou le coût global. Les tâches locales bornées et consultations documentaires ponctuelles peuvent rester directes. Ne s'applique pas aux sous-agents déjà mandatés.
---

# Routage sélectif — variante B

## Objectif et périmètre

Préserver la qualité et la pertinence du résultat, puis réduire le coût total,
puis le délai, sous contrainte de quota Astra. Ne pas abaisser les critères
d'acceptation, omettre une vérification nécessaire ou simplifier la demande
pour rendre un modèle moins coûteux utilisable.
Comparer le coût du travail complet : lancement, contexte, exécution, attente,
intégration et éventuelle reprise. Le modèle le moins cher par token ne rend
pas automatiquement une délégation rentable. Comparer les consommations de
tous les agents, racine comprise, pondérées par les tarifs applicables au
modèle et aux tokens entrants, en cache et sortants ; ne pas confondre crédits
Codex et facturation API. Sans mesure, annoncer un gain attendu, pas démontré.
Toute comparaison économique exige un rapport de mesure `Complete = true`.
Un run incomplet a exactement le statut `non observable` : ne jamais citer ses
tokens ou durées dans un ratio, une médiane, une comparaison ou une
recommandation économique. S'il reste moins de deux runs complets, conclure
qu'aucune comparaison économique n'est possible et conserver les diagnostics.

Ce skill est destiné à la racine uniquement. Un enfant déjà mandaté ne le
recharge pas, ne refait pas de triage et ne redélègue pas. Il suit sa mission,
son rôle et remonte les inconnues qui nécessitent une décision.

## Choisir le chemin

Une courte inspection initiale est autorisée : grouper les lectures et
recherches indépendantes, puis décider avec les faits disponibles. Ne pas
compter les opérations pour déclencher une délégation.

| Situation | Chemin normal |
|---|---|
| Petit travail local, lot déterministe borné ou implémentation locale au contrat explicite | Racine : lecture, modification et validation |
| Exploration étendue ou indépendante d'un travail utile de la racine | `scout` |
| Validation assez longue et indépendante pour amortir la coordination | `runner` |
| Implémentation substantielle ou indépendante dont la délégation est amortie | `builder`, validation ciblée comprise |
| Consultation documentaire ponctuelle | Racine directement |
| Recherche documentaire à plusieurs questions ou sources | `researcher` |
| Raisonnement complexe ou intégration | Racine |
| Arbitrage technique difficile, ou décision structurante coûteuse à corriger nécessitant un avis expert | `architect` |

Le routage `researcher` est impératif : créer ce sous-agent avant toute
consultation ou attente, vérifier qu'un identifiant actif a été retourné, puis
l'attendre. La racine ne réalise pas elle-même la recherche documentaire
multiple et n'appelle jamais `wait` sans enfant actif.
Le seuil se décide avant la première recherche, pas après : une consultation
est ponctuelle seulement si une seule requête sur une seule source suffit.
Dès qu'une deuxième requête, une deuxième source ou une deuxième question
devient nécessaire, arrêter et créer `researcher` avec ce qui est déjà acquis.
Une recherche déjà étendue ne se requalifie pas après coup en consultation
ponctuelle pour justifier l'absence de délégation.

Le routage `scout` est impératif lorsqu'il faut établir une cause en traçant
des appelants ou un flux à travers plusieurs fichiers ou modules. La racine
peut seulement inspecter assez pour borner la mission ; elle crée effectivement
`scout`, vérifie son identifiant actif et l'attend au lieu de réaliser elle-même
l'exploration.

Choisir le rôle le moins coûteux capable de respecter les critères
d'acceptation sans perte de pertinence, lorsque la coordination est amortie.
La capacité de la racine à faire le travail elle-même n'interdit pas de déléguer.
Une petite modification risquée peut demander une revue indépendante ; le
nombre de fichiers ne détermine ni le niveau nécessaire ni la rentabilité.
Si une ambiguïté décisive dépasse le rôle choisi, la racine garde cet arbitrage et
ne transmet que la partie suffisamment définie ; ne pas déléguer à bas coût
en comptant sur une reprise systématique pour obtenir la qualité attendue.

Quand un choix de palier est utile, annoncer une ligne de triage après cette
inspection et avant la délégation. Pour une simple lecture directe, ne pas
charger ce skill uniquement pour annoncer l'absence de délégation.
Ne pas lancer un enfant puis attendre si effectuer le petit lot directement
est plus économique. Une attente reste légitime pour un lot substantiel
dépendant ; ne pas inventer du travail parallèle ni dupliquer celui de l'enfant.

## Pendant qu'un enfant travaille

Le périmètre confié est réservé à l'enfant jusqu'à sa réponse. La racine n'y
lit plus, n'y cherche plus, et n'y fige ni plan, ni diagnostic, ni choix
d'architecture. Trois conduites seulement sont admises :
- attendre ;
- travailler sur un périmètre disjoint, nommé dans la ligne de triage avant
  la création ;
- poser à l'utilisateur une question que la réponse attendue ne peut pas
  changer ; sinon, attendre cette réponse avant de la formuler.

Reprendre l'exploration en parallèle « pour gagner du temps » double le coût
et annule le bénéfice annoncé : c'est le cas le plus fréquent de duplication.
Si la racine s'aperçoit qu'elle sait déjà conclure sans l'enfant, la réponse
correcte est `interrupt_agent`, pas une seconde exploration menée en même
temps. Une délégation interrompue tôt est un bon arbitrage, pas un échec.
Une conclusion établie avant la réponse de l'enfant sur son propre périmètre
est déclarée comme telle : ne pas présenter son rapport comme l'ayant fondée.

## Modèles et efforts

| Rôle | Modèle | Effort B |
|---|---|---|
| `scout` | `gpt-5.6-luna` | `high` |
| `researcher` | `gpt-5.6-luna` | `max` |
| `runner` | `gpt-5.6-luna` | `medium` |
| `builder` | `gpt-5.6-terra` | `medium` |
| Racine | Modèle et effort choisis par l'utilisateur | Variables |
| `architect` | `gpt-6-astra` | `low` |

`scout` utilise `high`, plus rapide et légèrement moins coûteux à qualité
préservée dans les mesures ; `researcher` reste en `max`, moins consommateur
que `high` sur le comparatif documentaire. `runner` et `builder` utilisent
`medium` lorsque leur délégation est amortie ; les ambiguïtés restent à la
racine. Les fichiers TOML de rôle fixent explicitement modèle et effort ; les
permissions effectives restent soumises au runtime parent, comme précisé dans
AGENTS.md. `builder` peut passer à `high` ou `xhigh` sur décision explicite.
Un générique n'est utilisé que si aucun rôle ne convient ; son défaut reste
Luna/max. Un sous-agent Astra passe par `architect`.

## Transmettre sans perdre les conditions

Utiliser les rôles nommés et préciser normalement `fork_turns = "none"` à chaque création.
Un fork complet n'est admis que si l'historique complet est indispensable,
avec justification explicite ; jamais par commodité pour une tâche mécanique.

Le message autonome contient les seuls éléments utiles :
- objectif et critères d'acceptation de l'utilisateur ;
- fichiers/périmètre et contraintes, dont les permissions ;
- faits établis et sources ou extraits probants ;
- hypothèses, inconnues et question à trancher, séparées des faits ;
- commandes, résultats, état des fichiers et environnement déjà vérifiés ;
- résultat attendu et limites de la mission.

Transmettre notamment l'absence déjà vérifiée de dépôt Git et les validations
réussies. Ne pas réexécuter une découverte d'environnement sans changement.
L'enfant groupe ses lectures indépendantes et répond proportionnellement au
travail : un résultat simple ne nécessite pas de rapport cérémoniel.

La synthèse conserve les réserves, alternatives conditionnelles et mesures
nécessaires de l'expert. La racine distingue toute décision nouvelle qu'elle ajoute.
Une hypothèse métier non établie reste une hypothèse. Si elle change le choix
et ne peut pas être résolue par inspection, demander la précision à l'utilisateur
ou présenter une recommandation conditionnelle, sans fabriquer de fait métier.

## Validation et arrêt

La validation ciblée appartient à celui qui réalise le changement. La racine lit le
résultat et inspecte les modifications (diff Git si disponible).
Ne pas créer un runner pour répéter une validation dont la commande, le
résultat et l'état pertinent des fichiers/environnement sont connus et
inchangés. Si cet état est incertain, vérifier avant de réutiliser le résultat.
Après une modification pertinente, un échec ou une nouvelle inquiétude, lancer
le contrôle nécessaire. Pour un changement à risque (sécurité, perte de données,
migration, contrat public), conserver une revue indépendante ciblée ; ne pas
confondre cette revue avec la répétition du même test. Astra n'est pas le testeur
final et n'exécute pas cette revue de validation.

L'échec est un livrable valide. Garder les bornes des rôles : runner, trois
cycles correction/test ; environnement, deux tentatives ; scout, trois
recherches infructueuses ; researcher, cinq requêtes ; builder, trois tentatives.
Deux fois la même erreur impose l'arrêt ou une reclassification avec un signal
nouveau ; pas de troisième essai identique. Toute relance change le périmètre,
la spécification ou le niveau pour une raison factuelle. Les problèmes
d'environnement ne montent pas d'un palier. Une contradiction factuelle appelle
une vérification ciblée, pas un arbitrage expert à l'aveugle.

## Consultation Astra

Le rôle `architect`, configuré avec Astra, traite uniquement les arbitrages
conceptuels ou d'architecture.
Jamais exploration, lecture répétitive, commande, test, log, retry, modification
mécanique, problème d'environnement ou choix d'intention de l'utilisateur.

Fixer le budget quand la consultation devient utile : zéro sans besoin ; un
appel initial, au plus deux par tâche standard. Annoncer le budget restant.
Un second appel nécessite des faits nouveaux ou une contradiction technique
restante susceptible d'invalider la décision. Pas de deuxième avis systématique
ni de retry sur le même échec. Au-delà, demander un nouveau budget.

Préparer une enveloppe concise (viser environ 60 lignes) avec objectif,
acceptation, extraits, faits, hypothèses, inconnues, résultats déjà obtenus et
question ouverte aux alternatives. La longueur est un objectif, pas un plafond :
ne jamais supprimer une preuve ou condition décisive pour y tenir.
Pas de logs complets ou historique lorsqu'un extrait suffit.

Astra travaille sur cette enveloppe, sans outil d'exploration ou d'exécution,
sans écriture ni délégation. Il peut rejeter le cadrage. Son livrable est une
décision avec conditions, interfaces/invariants utiles, alternatives/risques et
mesures nécessaires ; environ 80 lignes si cela suffit, sans forcer la longueur.
Pas de patch ni implémentation complète ; courts extraits d'interface autorisés.
La racine fait effectuer les mesures manquantes selon le routage sélectif, et ne
reconsulte que si elles changent la décision.

## Permissions

Conserver les restrictions de chaque rôle. Ne jamais utiliser `--yolo`,
`--dangerously-bypass-approvals-and-sandbox` ou élargir les permissions runtime
du parent pour consulter Astra. Les overrides parent peuvent prévaloir sur les
defaults enfants : si les restrictions d'architect ne tiennent plus, isoler la
décision dans une session adaptée plutôt que les contourner.
Après chaque réponse, vérifier dans la trace persistante le rôle, le modèle et
l'effort effectifs. Sans preuve `architect` + `gpt-6-astra` + `low`, écarter le
résultat comme non conforme et ne jamais annoncer une consultation ou une
consommation Astra.
