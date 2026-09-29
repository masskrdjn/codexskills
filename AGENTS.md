# Instructions projet — routage

Priorités : préserver la qualité et la pertinence du résultat, puis réduire le
coût total, puis le délai, avec quota Astra limité.
La racine utilise `quota-orchestrator` lorsqu'une délégation ou un choix de
palier est utile. Avant ce choix, seul un triage borné et non causal est
autorisé : inventorier les fichiers ou symboles pertinents sans suivre les
appelants, ouvrir plusieurs implémentations ni tester des hypothèses.
Le modèle racine choisi par l'utilisateur reste prioritaire. Une petite tâche
locale ou consultation documentaire à une seule source reste à la racine
lorsque le coût de coordination dépasserait l'économie attendue,
validation comprise. Un lot déterministe borné ou une implémentation locale
au contrat explicite reste aussi à la racine ; déléguer à `runner` ou `builder`
seulement si le travail est assez long ou indépendant pour amortir la
coordination. Toute recherche documentaire comportant plusieurs
questions ou plusieurs sources passe par `researcher` ; la racine charge
`quota-orchestrator`, crée effectivement ce sous-agent, puis attend son
identifiant actif. Elle ne fait pas elle-même la recherche et n'appelle jamais
`wait` sans enfant actif. Le seuil se décide avant la première recherche : une
seule requête sur une seule source reste à la racine ; dès qu'une deuxième requête,
une deuxième source ou une deuxième question devient nécessaire, il arrête et
crée `researcher`. Une recherche déjà étendue ne se requalifie pas après coup
en consultation ponctuelle.
Le routage d'une recherche de cause est décidé avant toute exploration du
code. La racine conserve la recherche seulement si, à partir des informations
déjà disponibles, la vérification est localisée à un point d'entrée connu et
peut être effectuée par une lecture directe ou une commande déterministe
bornée. Elle crée immédiatement `scout` si le point d'entrée doit être
découvert, s'il faut suivre des appelants, des données ou un état entre
plusieurs composants, si plusieurs hypothèses causales doivent être
départagées, ou si la demande porte explicitement sur un flux transversal.
Pour décider, elle peut uniquement inventorier les fichiers ou symboles
pertinents ; elle ne commence pas l'enquête. Avant le lancement, elle nomme la
question confiée, le travail qu'elle n'effectuera pas et la preuve qui arrêtera
le scout, puis vérifie son identifiant actif et l'attend.

Les rôles définissent les missions, restrictions et livrables; choisir
séparément le modèle et l'effort selon l'ambiguïté, les interactions, les
contradictions, la validation et les conséquences d'une erreur. D'abord
identifier les couples capables de satisfaire la qualité; parmi ces admissibles,
comparer les tokens du travail complet, puis coût monétaire et délai séparément.
GPT-6 Luna, GPT-6 Sol, GPT-5.6 Sol, GPT-6.1 Sol et GPT-6 Astra sont à comparer.
Sol 6 et 5.6 sont des candidats ordinaires avec les mêmes exigences que 6.1,
sans justification supplémentaire liée à leur ancienneté. Les valeurs TOML
sont des secours provisoires, pas une preuve d'optimalité ou d'économie.
Le plancher utilisateur Luna est high, y compris runner et générique; xhigh et
max restent candidats selon la tâche, sans max automatique ni obligation
d'épuiser tous les efforts inférieurs avant de comparer. Les niveaux d'effort
ne sont pas équivalents entre modèles. La grille de quota-orchestrator est
une hypothèse de politique; aucune économie n'est mesurée par cette révision.
Les variantes scout_complex et researcher_complex sont des facilités de runtime,
pas un classement obligatoire. Les petites tâches restent à la racine par défaut.

Le strategist prépare un plan sur contexte déjà rassemblé, sans exploration,
commande, écriture ni délégation; ne pas l'interposer devant une implémentation
déjà spécifiée. Le builder implémente et valide son périmètre. Astra passe
uniquement par architect pour une décision structurante ou difficile que sa
capacité supplémentaire justifie; son effort est choisi selon cette décision,
pas systématiquement low. Conserver son budget et ses restrictions.
Annoncer rôle, modèle, effort, justification et signal de requalification.
Si le runtime verrouille le profil, utiliser un profil dédié disponible
préservant son contrat et ses restrictions; sinon garder la mission à la
racine et signaler le choix non exécutable. Ne jamais prétendre qu'un override
non appliqué a été utilisé. Le modèle racine choisi par l'utilisateur reste
prioritaire. Une information manquante exige une collecte ciblée, pas une
augmentation automatique de l'effort. Seule la racine requalifie les missions.

Une délégation économique doit remplacer du travail racine, pas seulement
ajouter un exécutant moins coûteux. La ligne de triage nomme le livrable
exclusif de l'enfant, le travail abandonné par la racine, la condition d'arrêt
et la raison pour laquelle l'économie attendue amortit toute la coordination.
À défaut, le travail reste à la racine. Après le retour, une vérification
ponctuelle est permise, mais la racine ne refait pas l'exploration.

Le périmètre confié à un enfant lui est réservé jusqu'à sa réponse : la racine
n'y lit plus, n'y cherche plus et n'y fige ni plan ni diagnostic. Elle attend,
ou travaille sur un périmètre disjoint annoncé dans la ligne de triage, ou pose
à l'utilisateur une question que la réponse attendue ne peut pas changer. Si
elle constate qu'elle sait déjà conclure sans l'enfant, elle l'interrompt au
lieu de payer deux fois le même travail.

Mesurer contexte, raisonnement, réponses, échanges d'outils, coordination,
validation, corrections et reprises, racine, enfants et reviewers inclus.
Ne pas ajouter Reasoning à Output ni Cached à Input lorsque ces compteurs
sont déjà inclus. Séparer tokens, coût monétaire, délai, qualité et taux de
succès; inclure succès et échecs complets sans biais de survivants.
Un run `Complete = false` a exactement le statut `non observable` : ne jamais
utiliser ses tokens ou durées dans les ratios ou recommandations économiques.
Comparer les mêmes tâches, critères, contextes et outils, apparier les runs
complets et randomiser l'ordre; publier froid et chaud séparément. Deux runs
complets non appariés ne permettent pas de conclusion économique; une
comparaison exploratoire requiert au moins deux paires par tâche/scénario.
Le seuil de cinq paires pour une délégation locale économique reste applicable.

Les sous-agents déjà mandatés suivent leur mission et leur rôle : ils ne
chargent pas le skill d'orchestration, ne refont pas le triage et ne délèguent
pas à leur tour. Ils remontent les décisions nécessaires à la racine.

La racine délègue à un modèle moins coûteux lorsque la mission est assez
définie pour préserver qualité et pertinence, et que l'économie attendue
amortit le cadrage, le contexte, l'intégration et les éventuelles reprises.
La capacité de la racine à faire elle-même le travail n'interdit pas une
délégation substitutive, mais ne justifie jamais une exécution additive.
Elle peut aussi déléguer pour une capacité de raisonnement supérieure ou un
travail indépendant utile en parallèle. Elle annonce brièvement le bénéfice
attendu ; ni la taille du lot ni le parallélisme ne suffisent à eux seuls.
Une incertitude décisive sur la capacité du modèle à remplir la mission impose
de garder le raisonnement concerné à la racine ou de consulter le rôle adapté.

Une tâche locale bornée reste à la racine par défaut. Sa promotion vers un
sous-agent pour motif économique exige au moins cinq paires de runs complets,
comparables et randomisés montrant un gain en cache froid, tous agents et
reviewers inclus. Les résultats en cache chaud sont publiés séparément. Une
délégation reste possible pour un besoin explicite de capacité, de qualité ou
de délai, mais elle n'est alors pas présentée comme une économie démontrée.

Ne pas demander de revue indépendante par défaut. Une seule revue ciblée est
autorisée pour la sécurité, la perte de données, une migration irréversible,
un contrat public, une contradiction non résolue ou l'absence de test fiable
sur un comportement critique. Une analyse en lecture seule, une proposition
ou un changement déterministe à faible risque dont la validation ciblée passe
ne déclenche pas de revue supplémentaire. Les consommations `guardian_review`
non déclenchées par le projet sont mesurées séparément et incluses dans le coût
total, sans être présentées comme un levier directement contrôlable.

Les profils nommés portent des modèles et efforts de secours. Leur `sandbox_mode`
n'est pas appliqué : le bac à sable du parent prévaut, ne pas compter sur un
rôle pour restreindre un sous-agent. Ne pas laisser deux agents
d'implémentation éditer les mêmes fichiers.

Conserver dans les transmissions les critères d'acceptation, faits établis,
hypothèses, inconnues et validations déjà faites. Une hypothèse d'un expert ne
devient pas un fait dans la synthèse. Les instructions de l'utilisateur priment.

## Lancement

Ne jamais lancer l'orchestrateur sous `--yolo`,
`--dangerously-bypass-approvals-and-sandbox`, ni avec une permission runtime
accordée via `/permissions` qui élargirait le bac à sable.

Les overrides runtime du parent sont réappliqués aux sous-agents et prévalent
sur leurs valeurs par défaut. Si les permissions du parent annulent les
restrictions d'`architect`, ne pas le consulter dans cette session ; isoler la
décision dans une session aux permissions adaptées.
Lorsqu'ils sont lancés comme sous-agents, `strategist` et `architect` ne font
ni exploration, ni commandes, ni écriture, ni délégation.
Après la réponse, vérifier dans la trace persistante le rôle, le modèle et
l'effort effectifs. Sans preuve `architect` + `gpt-6-astra` + effort annoncé, écarter le
résultat comme non conforme et ne jamais annoncer une consultation ou une
consommation Astra.
