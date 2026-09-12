# Instructions projet — routage

Priorités : préserver la qualité et la pertinence du résultat, puis réduire le
coût total, puis le délai, avec quota Astra limité.
La racine utilise `quota-orchestrator` lorsqu'une délégation ou un choix de
palier est utile. Une courte inspection initiale est autorisée avant ce choix.
Une petite tâche locale ou consultation documentaire à une seule source reste
à Sol lorsque le coût de coordination dépasserait l'économie attendue,
validation comprise. Un lot déterministe borné ou une implémentation locale
au contrat explicite reste aussi à Sol ; déléguer à `runner` ou `builder`
seulement si le travail est assez long ou indépendant pour amortir la
coordination. Toute recherche documentaire comportant plusieurs
questions ou plusieurs sources passe par `researcher` ; la racine charge
`quota-orchestrator`, crée effectivement ce sous-agent, puis attend son
identifiant actif. Elle ne fait pas elle-même la recherche et n'appelle jamais
`wait` sans enfant actif. Le seuil se décide avant la première recherche : une
seule requête sur une seule source reste à Sol ; dès qu'une deuxième requête,
une deuxième source ou une deuxième question devient nécessaire, il arrête et
crée `researcher`. Une recherche déjà étendue ne se requalifie pas après coup
en consultation ponctuelle.
Toute recherche locale demandant d'établir une cause en traçant des appelants
ou un flux à travers plusieurs fichiers ou modules passe de même par `scout`.
La racine peut seulement inspecter assez pour borner la mission ; elle charge
`quota-orchestrator`, crée effectivement `scout`, vérifie son identifiant actif
et l'attend au lieu de réaliser elle-même l'exploration.

Le périmètre confié à un enfant lui est réservé jusqu'à sa réponse : la racine
n'y lit plus, n'y cherche plus et n'y fige ni plan ni diagnostic. Elle attend,
ou travaille sur un périmètre disjoint annoncé dans la ligne de triage, ou pose
à l'utilisateur une question que la réponse attendue ne peut pas changer. Si
elle constate qu'elle sait déjà conclure sans l'enfant, elle l'interrompt au
lieu de payer deux fois le même travail.

Un run de mesure avec `Complete = false` a exactement le statut
`non observable` : ne jamais utiliser ni citer ses tokens ou durées dans une
comparaison ou recommandation économique. Comparer au moins deux runs complets,
sinon conclure qu'aucune comparaison économique n'est possible.

Les sous-agents déjà mandatés suivent leur mission et leur rôle : ils ne
chargent pas le skill d'orchestration, ne refont pas le triage et ne délèguent
pas à leur tour. Ils remontent les décisions nécessaires à la racine.

La racine délègue à un modèle moins coûteux lorsque la mission est assez
définie pour préserver qualité et pertinence, et que l'économie attendue
amortit le cadrage, le contexte, l'intégration et les éventuelles reprises.
Cela reste valable si Sol sait faire lui-même et doit attendre le résultat.
Elle peut aussi déléguer pour une capacité de raisonnement supérieure ou un
travail indépendant utile en parallèle. Elle annonce brièvement le bénéfice
attendu ; ni la taille du lot ni le parallélisme ne suffisent à eux seuls.
Une incertitude décisive sur la capacité du modèle à remplir la mission impose
de garder le raisonnement concerné à Sol ou de consulter le rôle adapté.

Les rôles nommés portent leurs modèles et leurs efforts. Leur `sandbox_mode`
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
Astra ne fait ni exploration, ni commandes, ni écriture, ni délégation.
Après la réponse, vérifier dans la trace persistante le rôle, le modèle et
l'effort effectifs. Sans preuve `architect` + `gpt-6-astra` + `low`, écarter le
résultat comme non conforme et ne jamais annoncer une consultation ou une
consommation Astra.
