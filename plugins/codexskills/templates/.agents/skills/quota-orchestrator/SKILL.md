---
name: quota-orchestrator
description: Appliquer automatiquement au début de chaque tâche racine pour décider si elle reste locale ou doit être déléguée à un profil spécialisé. Les petites tâches bornées restent directes. Ne pas appliquer dans un sous-agent déjà mandaté.
---

# Routage sélectif

## Activation automatique

Effectuer ce triage au début de chaque tâche racine sans attendre que
l'utilisateur nomme le skill ou le plugin. Pour une tâche locale bornée,
décider de la conserver à la racine puis poursuivre directement, sans imposer
de cérémonie visible. Ne jamais activer ce routage depuis un sous-agent déjà
mandaté.

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

Le routage est décidé avant toute exploration causale. Un triage borné peut
inventorier les fichiers ou symboles pertinents, mais ne suit pas les
appelants, n'ouvre pas plusieurs implémentations et ne teste pas d'hypothèse.
Ne pas compter les opérations pour déclencher une délégation.

| Situation | Chemin normal |
|---|---|
| Petit travail local, lot déterministe borné ou implémentation locale au contrat explicite | Racine : lecture, modification et validation |
| Point d'entrée connu et vérification directe ou commande déterministe bornée | Racine |
| Point d'entrée inconnu, traçage transversal ou hypothèses causales concurrentes | `scout` |
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

La racine crée immédiatement `scout` si le point d'entrée doit être découvert,
s'il faut suivre des appelants, des données ou un état entre plusieurs
composants, si plusieurs hypothèses causales doivent être départagées, ou si
la demande porte explicitement sur un flux transversal. Pour décider, elle
peut seulement inventorier les fichiers ou symboles pertinents. Elle n'ouvre
pas plusieurs implémentations, ne suit pas les appelants et ne commence pas à
tester les hypothèses avant le routage. Avant le lancement, elle nomme la
question confiée, le travail qu'elle n'effectuera pas et la preuve qui arrêtera
le scout.

## Porte de substitution

Une délégation économique doit remplacer du travail racine, pas seulement
ajouter un exécutant moins coûteux.

Avant le lancement, la ligne de triage indique :
1. le livrable exclusif de l'enfant ;
2. les lectures, recherches, raisonnements ou validations que la racine
   n'effectuera plus ;
3. la condition d'arrêt vérifiable ;
4. pourquoi l'économie attendue amortit le lancement, le contexte,
   l'intégration et la validation.

Sans réponse concrète aux quatre points, garder le travail à la racine. Le
parallélisme ou le prix inférieur du modèle ne suffisent pas.

Après le retour, la racine intègre le résultat sans refaire l'exploration. Une
vérification ponctuelle d'une preuve est permise ; relire tout le périmètre
annule la substitution et doit être compté comme une reprise.

Une tâche locale bornée reste à la racine par défaut. Sa promotion vers un
sous-agent pour motif économique exige au moins cinq paires de runs complets,
comparables et randomisés montrant un gain en cache froid, tous agents et
reviewers inclus. Les résultats en cache chaud sont publiés séparément : ils
peuvent justifier une optimisation de répétition, mais pas la promotion
générale d'une catégorie de tâches. Une délégation reste possible sans preuve
économique pour un besoin explicite de capacité, de qualité ou de délai ; elle
est alors annoncée comme telle et non comme une économie.

Choisir le rôle le moins coûteux capable de respecter les critères
d'acceptation sans perte de pertinence, lorsque la coordination est amortie.
La capacité de la racine à faire le travail elle-même n'interdit pas de déléguer.
Une petite modification risquée peut demander une revue indépendante ; le
nombre de fichiers ne détermine ni le niveau nécessaire ni la rentabilité.
Si une ambiguïté décisive dépasse le rôle choisi, la racine garde cet arbitrage et
ne transmet que la partie suffisamment définie ; ne pas déléguer à bas coût
en comptant sur une reprise systématique pour obtenir la qualité attendue.

Quand un choix de palier est utile, annoncer une ligne de triage après le
triage non causal et avant la délégation. Pour une simple lecture directe, ne pas
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
le contrôle nécessaire. Ne pas demander de revue indépendante par défaut. Une
seule revue ciblée est autorisée si le changement touche à la sécurité ou à la
perte de données, réalise une migration irréversible, modifie un contrat
public, laisse une contradiction non résolue entre implémentation et
validation, ou concerne un comportement critique dépourvu de test fiable. Une
analyse en lecture seule, une proposition ou un changement déterministe à
faible risque dont la validation ciblée passe ne déclenche pas de revue
supplémentaire. Astra n'est pas le testeur final et n'exécute pas cette revue.

Les consommations `guardian_review` non déclenchées par le projet sont
mesurées séparément et incluses dans le coût total. Elles ne sont pas
présentées comme un levier directement contrôlable par ces règles.

Pour `scout`, la condition d'arrêt normale est la première chaîne causale
suffisante comportant le point d'entrée, le chemin pertinent, la cause
localisée et une preuve par code, configuration, log ou test existant. Une
fois ces éléments obtenus, ne pas rechercher d'autres causes possibles sauf
contradiction factuelle ou demande explicite. Une mission porte normalement
sur une seule question causale ; toute extension nécessite un nouveau triage
par la racine.

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
