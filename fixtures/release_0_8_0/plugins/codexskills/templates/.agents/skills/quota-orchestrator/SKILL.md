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
Comparer les tokens du travail complet, puis le coût monétaire et le délai
séparément, selon le protocole de mesure ci-dessous. Sans mesure comparable,
annoncer un bénéfice attendu, pas démontré. Un run `Complete = false` a exactement
le statut `non observable`; ses tokens et durées sont exclus des comparaisons.

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
| Cadrage complexe, décomposition ou arbitrage intermédiaire sur contexte assemblé | `strategist` |
| Intégration finale et décision de routage | Racine |
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

Choisir le rôle selon la mission et ses restrictions, puis le couple modèle/effort
selon la capacité et les tokens complets, lorsque la coordination est amortie.
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

## Cadrage Strategist

Le rôle `strategist` intervient uniquement lorsque le contexte utile est déjà
assemblé mais que le quoi-faire reste trop ambigu pour `builder`. Il prépare
une décision ou un plan : missions, ordre, dépendances, contrats, critères
d'acceptation, alternatives et conditions de révision. Il n'explore pas,
n'exécute rien, n'écrit rien et ne lance aucun agent ; la racine conserve
l'orchestration effective et l'intégration.

Ne pas rendre ce passage obligatoire. Une implémentation dont le contrat est
explicite va directement à `builder`. Une mesure ciblée va au rôle approprié
plutôt qu'à `strategist`. Le strategist ne fait pas de revue après coup et
n'escalade vers `architect` que si une décision structurante, difficile à
corriger ou encore contradictoire nécessite réellement Astra.

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
Après chaque réponse, vérifier dans la trace persistante le rôle architect, le modèle et
l'effort effectifs. Sans preuve `architect` + `gpt-6-astra` + effort annoncé, écarter le
résultat comme non conforme et ne jamais annoncer une consultation ou une
consommation Astra.
