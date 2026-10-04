---
name: quota-orchestrator
description: Protocole pour choisir un modèle ou un effort hors des profils, une variante _complex, strategist, une consultation architect, une revue indépendante ou une mesure de coût. Ne pas lire pour une tâche locale ni pour déléguer à scout, researcher, runner ou builder standard : AGENTS.md suffit. Jamais dans un sous-agent déjà mandaté.
---

# Routage sélectif

## Activation

Le triage courant et la délégation à un profil standard sont décrits dans
AGENTS.md, chargé par l'hôte : ne pas lire ce skill pour eux. Le lire seulement
pour un choix de modèle ou d'effort hors des profils, une variante `_complex`,
`strategist`, une consultation `architect`, une revue indépendante, une mesure
ou comparaison de coûts, ou une situation qu'AGENTS.md ne tranche pas. Chaque
lecture coûte plusieurs milliers de tokens d'entrée, relus à chaque requête
suivante. Ne jamais l'activer depuis un sous-agent déjà mandaté.

## Objectif et périmètre

Préserver la qualité et la pertinence du résultat, puis réduire le coût total,
puis le délai, sous contrainte de quota Astra. Ne pas abaisser les critères
d'acceptation, omettre une vérification nécessaire ou simplifier la demande
pour rendre un modèle moins coûteux utilisable.
Comparer le coût du travail complet : pour chaque réponse, les tokens de chaque
type (entrée non cachée, entrée cachée, écritures de cache, sortie y compris
raisonnement) × le tarif API du modèle, racine, enfants et reviewers inclus,
puis le délai. Plus de tokens sur un palier moins cher est un bon échange tant
que la qualité tient : le nombre de tokens n'est pas le critère. Sans mesure
comparable, annoncer un bénéfice attendu, pas démontré. Un run `Complete = false`
a exactement le statut `non observable`; ses tokens et durées sont exclus des
comparaisons.

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
| Point d'entrée inconnu, traçage transversal ou hypothèses causales concurrentes, avec une exploration assez large pour dépasser la coordination (environ huit fichiers ou 60 Ko ; mesuré rentable pour un audit en lecture seule) | `scout` ; sinon racine |
| Revue bornée assez large (plusieurs axes, même seuil) pour amortir la coordination | `scout`, mode revue bornée ; sinon racine |
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

La racine crée immédiatement `scout` si, au-delà du seuil d'exploration
ci-dessus, le point d'entrée doit être découvert, s'il faut suivre des
appelants, des données ou un état entre plusieurs composants, si plusieurs
hypothèses causales doivent être départagées, ou si la demande porte
explicitement sur un flux transversal. Sous le seuil, la coordination coûte
plus que l'exploration et la racine la conserve. Pour décider, elle
peut seulement inventorier les fichiers ou symboles pertinents. Elle n'ouvre
pas plusieurs implémentations, ne suit pas les appelants et ne commence pas à
tester les hypothèses avant le routage. Avant le lancement, elle nomme la
question confiée, le travail qu'elle n'effectuera pas et la preuve qui arrêtera
le scout. Elle assigne le mode (enquête causale par défaut, ou revue bornée) et
choisit `scout` (Luna) ; `scout_complex` seulement selon la règle de coût.

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
parallélisme ou le seul prix par token ne suffisent pas : le gain se compte sur
le coût complet, coordination comprise.

Après le retour, la racine intègre le résultat sans refaire l'exploration. Lire
le résultat et le diff, et faire les contrôles ciblés nécessaires à l'acceptation,
est permis : ce sont des tokens d'entrée, bien moins chers que produire le
travail. Seule une refaite (nouveau raisonnement, nouvelle exploration,
réécriture) annule la substitution et se compte comme une reprise.

Une tâche locale bornée reste à la racine par défaut. Sa promotion vers un
sous-agent pour motif économique exige au moins cinq paires de runs complets,
comparables et randomisés montrant un gain de coût en cache froid, tous agents
et reviewers inclus. Les résultats en cache chaud sont publiés séparément : ils
peuvent justifier une optimisation de répétition, mais pas la promotion
générale d'une catégorie de tâches. Une délégation reste possible sans preuve
économique pour un besoin explicite de capacité, de qualité ou de délai ; elle
est alors annoncée comme telle et non comme une économie.

Choisir le rôle selon la mission et ses restrictions, puis le couple modèle/effort
selon la capacité puis le coût complet, lorsque la coordination est amortie.
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
| GPT-6 Luna | Travail circonscrit; `high`, `xhigh` et `max` sont candidats, y compris pour une implémentation ou un cadrage bien définis | Plancher utilisateur `high`, dans les rôles comme dans le générique. Environ 20× moins chère que Sol 6.1 par token : voir la règle de coût. |
| GPT-6 Sol | Candidat ordinaire pour les missions techniques et les interactions complexes, indépendamment du rôle | Même exigence de qualité et même protocole comparatif que Sol 6.1, sans preuve liée à son ancienneté ; mêmes tarifs que 6.1 sauf le cache, 2× plus cher. |
| GPT-5.6 Sol | Candidat ordinaire pour le raisonnement, le cadrage et les autres missions qu'il peut remplir | Même exigence que les autres Sol; ni exception de compatibilité ni inférieur présumé ; tarif 2× celui de 6.1 (promotionnel, voir règle de coût). |
| GPT-6.1 Sol | Candidat transversal pour l'implémentation, la recherche et les décisions | Sa nouveauté ne prouve ni moins de tokens ni un remplacement optimal des autres Sol. |
| GPT-6 Astra | Consultation `architect` lorsque la capacité supplémentaire répond à une difficulté identifiée | Quota et restrictions architect; pas d'exploration, commande, écriture ni délégation. 5× le tarif de 6.1 (10× en cache), 100× Luna. |

Vérifier les modèles et efforts réellement disponibles dans le runtime.
La disponibilité API ne prouve pas leur disponibilité dans Codex. Les noms
d'effort ne sont pas équivalents entre modèles : Luna `xhigh` ne signifie pas
Sol `medium`, ni Sol `xhigh` Astra `low`.

## Choisir la capacité, puis le coût

Le couple modèle/effort dépend de l'ambiguïté du contrat, des dépendances et
interactions, des contradictions, de la validation et des conséquences d'une
erreur. La longueur du lot, le nombre de fichiers et le rôle ne suffisent pas.
Une information manquante appelle une collecte ciblée, pas automatiquement
plus d'effort. Cette qualification n'autorise pas l'exploration avant le routage.

1. **Capacité** : identifier les couples admissibles qui peuvent satisfaire
   les mêmes critères de qualité et de pertinence, avec une validation adaptée
   aux conséquences d'une erreur. Écarter un couple pour une limite identifiée,
   pas pour son ancienneté ; le prix entre dans le coût, pas dans l'admissibilité.
   Une incertitude décisive reste explicite.
2. **Coût** : parmi les couples admissibles, comparer le coût du travail complet
   (tarifs ci-dessous), racine, enfants et reviewers inclus, puis le délai. Les
   tokens se rapportent sans arbitrer. Sans mesures comparables, le choix reste
   une hypothèse de politique, pas une économie démontrée ni un optimum.

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
candidature par la tâche puis mesurer la qualité et le coût complet.
Les secours Luna sont `high`, y compris runner et générique; ce choix provisoire
respecte le plancher utilisateur, sans établir que `high` est optimal.
Les modèles de secours existants restent en place; ni leurs valeurs TOML ni
leur exécution ne prouvent une économie. Les variantes scout_complex et
researcher_complex sont des facilités de runtime, pas un classement obligatoire :
la variante standard (Luna) est le défaut ; la complex (Sol 6.1 xhigh, 20× par
token et un raisonnement plus long) exige une capacité établie au cadrage ou une
limite constatée de la standard.

Au lancement, annoncer rôle, modèle exact, effort, faits justifiant le choix,
hypothèses, inconnues, validation attendue et signal de requalification.
Utiliser les overrides explicites et `fork_turns = "none"` seulement si le
runtime les autorise. S'il verrouille le profil, choisir un profil disponible
préservant le contrat et les restrictions; sinon garder la mission à la racine
et signaler le couple non exécutable. Un générique ne convient que si ces
garanties peuvent être conservées. Une consigne ne remplace pas un outil désactivé.
Ne jamais annoncer un override non appliqué. La consultation d'un sous-agent
Astra passe exclusivement par architect vérifiable. Le modèle et l'effort racine choisis par l'utilisateur
restent prioritaires; le plancher Luna concerne les sélections des sous-agents.

L'enfant remonte les faits qui invalident son choix initial; seule la racine
requalifie. Une difficulté d'exécution ne justifie pas automatiquement plus de
capacité. Réutiliser les preuves et validations pertinentes plutôt que refaire
le travail. Une difficulté conceptuelle décisive se remonte immédiatement.

### Tarifs API et règle de coût

Tarifs standard (entrée ≤ 272 K tokens), dollars par million de tokens, relevés
le 2026-10-03 sur https://developers.openai.com/api/docs/pricing (la page n'a pas
de version : rafraîchir avant toute comparaison datée autrement).

| Modèle | Entrée | Cachée | Écriture cache | Sortie (raisonnement inclus) | Sortie vs Luna |
|---|---|---|---|---|---|
| GPT-6 Luna | 0,10 | 0,01 | 0,125 | 0,50 | 1× |
| GPT-6 Sol | 2,00 | 0,20 | 2,50 | 10,00 | 20× |
| GPT-6.1 Sol | 2,00 | 0,10 | 2,50 | 10,00 | 20× |
| GPT-5.6 Sol | 4,00 | 0,40 | 5,00 | 20,00 | 40× |
| GPT-6 Astra | 10,00 | 1,00 | 12,50 | 50,00 | 100× |

Le tarif de GPT-5.6 Sol est promotionnel au moins jusqu'au 21 novembre 2026.
Au-delà de 272 K tokens d'entrée, une requête paie entrée, cache et écritures ×2
et sortie ×1,5 sur toute la requête. Fast ×2, Batch et Flex ×0,5 (Ultrafast ×6,
Astra seul) : comparer à niveau de service identique, les journaux ne l'indiquent
pas. Un jeton d'entrée est facturé non caché, caché ou en écriture de cache,
sans cumul.

Règle de coût : à capacité admissible égale, comparer Σ tokens × tarif, pas les
tokens. Luna reste moins chère que Sol 6.1 tant qu'elle consomme moins de 20×
(entrée, sortie) ou 10× (cache) ses tokens. Essayer un palier moins cher d'abord
est rentable si coût_bas + (1 − p) × coût_haut < coût_haut, soit p > coût_bas /
coût_haut, p étant la probabilité que le palier bas suffise et que son
insuffisance soit détectée avant livraison : sans critères vérifiables (contrat
de retour), une erreur non détectée ne se rattrape pas et ce calcul ne
s'applique pas. Escalader sur une limite de capacité identifiée, pas par
précaution. Sol 6 (cache 2×) et Sol 5.6 (2× le tarif de 6.1, 4× en cache) ne
gagnent que par une consommation moindre mesurée : moins de la moitié des tokens
de 6.1 pour 5.6, à qualité égale. Garder le contexte racine sous 272 K est un
bénéfice de la délégation ; un fork complet repart sans cache vers un autre
modèle et peut franchir le seuil. Astra reste une contrainte de quota en plus du
coût.

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
sur ce dépôt. Les tarifs API fondent le calcul du coût ; ni eux ni les résultats
d'évaluations externes n'établissent une économie du projet, qui reste à
mesurer; le plancher Luna high est une préférence utilisateur distincte des
exemples documentaires. La grille reste une hypothèse
à valider, pas une recommandation comparative prouvée par ces sources.

## Mesurer le coût sans confondre tokens, prix et qualité

Aucune économie n'est mesurée par cette révision.
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
Les écritures de cache sont un troisième type d'entrée, facturé à part. Vérifier
ces inclusions dans la source des compteurs avant tout calcul.

Le critère est le coût en dollars API par résultat accepté : somme, sur les
réponses, des tokens de chaque type × le tarif daté du modèle (majorations de
contexte long et de niveau de service comprises), succès, échecs et relances
inclus ; par run complet si aucun verdict de qualité n'existe. Rapporter
séparément tokens totaux et ventilés, délai, qualité et taux de succès. Les
crédits Codex ne sont pas des dollars API : le tarif API sert de proxy pour un
abonnement, le quota Astra restant une contrainte séparée. Inclure les succès et les échecs complets,
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

<!-- contract:mission -->
Le message autonome contient les seuls éléments utiles ; une mission simple tient
en quelques phrases, aucun fichier ni format JSON n'est obligatoire :
- type de mission, périmètre exclusif, condition d'arrêt et décisions à remonter ;
- objectif et critères identifiés (acceptation de l'utilisateur) ;
- contraintes, dont les permissions ;
- état analysé (commit et modifications locales pertinentes), s'il est déjà connu
  de la racine : ne pas lancer de commande pour l'obtenir ;
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
le contrôle nécessaire.

<!-- contract:review -->
La revue indépendante reste conditionnelle : une seule revue ciblée est autorisée
si le changement touche à la sécurité ou à la perte de données, réalise une
migration irréversible, modifie un contrat public, laisse une contradiction non
résolue entre implémentation et validation, ou concerne un comportement critique
dépourvu de test fiable. Lorsqu'un de ces risques est effectivement touché, la
racine décide explicitement si ses contrôles suffisent ou si cette revue est
nécessaire. Aucun reviewer supplémentaire systématique ; une analyse en lecture
seule, une proposition ou un changement déterministe à faible risque dont la
validation ciblée passe ne déclenche pas de revue. Astra n'est pas le testeur
final et n'exécute pas cette revue.

Les consommations `guardian_review` non déclenchées par le projet sont
mesurées séparément et incluses dans le coût total. Elles ne sont pas
présentées comme un levier directement contrôlable par ces règles.

<!-- contract:scout-modes -->
Scout et scout_complex ont deux modes explicitement assignés ; sans assignation,
enquête causale :
- Enquête causale : arrêt à la première chaîne de preuves suffisante (point
  d'entrée, chemin pertinent, cause localisée, preuve par code, configuration,
  log ou test existant) ; ne pas chercher d'autres causes sauf contradiction
  factuelle ou demande explicite ; une mission porte sur une seule question,
  toute extension nécessite un nouveau triage par la racine.
- Revue bornée : arrêt après traitement de tous les axes assignés, avec les
  zones non vérifiées signalées. Trouver un premier bug ne termine pas la mission.
Les bornes de recherche existantes restent applicables ; leur atteinte produit
une limite explicite, jamais une conclusion implicite de conformité. Une revue
complexe ne requiert pas de contradictions déjà connues, mais une capacité Sol
établie.

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

Le sous-agent architect Astra travaille sur cette enveloppe, sans outil d'exploration ou d'exécution,
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

<!-- contract:execution -->
Les restrictions d'architect concernent le sous-agent consultant ; elles ne
limitent pas une racine Astra choisie par l'utilisateur. Le consultant reste sans
exploration, commande, écriture ni délégation, sur le seul contexte fourni.
Distinguer modèle annoncé, configuration et exécution attestée : utiliser les
métadonnées effectives lorsqu'elles sont accessibles (rôle, modèle, effort),
sinon indiquer « exécution non vérifiée ». La provenance des instructions
héritées ne prouve pas le modèle exécutant. Après chaque réponse, vérifier dans
la trace persistante le rôle architect, le modèle et l'effort effectifs ; sans
preuve effective architect + gpt-6-astra + effort annoncé, écarter le résultat
comme non conforme et ne jamais annoncer une consultation ou une consommation
Astra attestée.

## Contrat de mission et acceptation finale

<!-- contract:coverage -->
Le retour associe à chaque critère identifié un statut « vérifié », « échoué »
ou « non vérifié », avec sa preuve et l'état auquel elle s'applique.
Les findings gardent des identifiants stables et distinguent défaut confirmé,
risque et proposition d'amélioration. Les réserves et inconnues restent explicites.

<!-- contract:closure -->
La délégation transfère l'exécution, pas la responsabilité de clôture.
Après le retour, la racine rapproche les critères initiaux des résultats,
signale toute couverture manquante, examine le diff pertinent après une
implémentation et vérifie que les preuves correspondent à l'état final.
Elle effectue les contrôles ciblés nécessaires à l'acceptation sans recommencer
l'exploration de l'enfant : lire un diff coûte de l'entrée, seule une refaite
annule la substitution. Elle ne déclare le travail complet que si tous les
critères requis sont satisfaits ; sinon elle précise les limites ou le blocage.

<!-- contract:freshness -->
Toute modification ultérieure invalide les preuves qu'elle peut affecter.
Relancer uniquement les vérifications concernées et rapporter les changements
depuis la validation ; réutiliser les autres preuves si leur état est inchangé.

<!-- contract:completion -->
Builder et runner rapportent séparément la commande, le code de sortie mesuré,
le périmètre effectivement testé et une preuve d'achèvement propre au runner
de tests : résumé final, compteur attendu ou marqueur terminal adapté.
Rapporter les échecs, exclusions et vérifications non réalisées. Un code `0`
sans preuve suffisante donne « validation non établie » ; la racine apprécie la
suffisance de la preuve. Ne pas employer le statut économique `non observable`
pour cela ; aucun marqueur universel tel que `PASS` n'est imposé.
