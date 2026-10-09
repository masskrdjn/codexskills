# Instructions projet — routage

Priorités : préserver la qualité et la pertinence du résultat, puis réduire le
coût total, puis le délai, avec quota Astra limité. Le coût s'entend en dollars
API (tokens de chaque type × tarif du modèle), pas en nombre de tokens : plus de
tokens sur un palier moins cher est un bon échange à qualité égale. Le modèle
racine choisi par l'utilisateur reste prioritaire, comme ses instructions.

## Triage, avant toute exploration

Une demande locale précise (renommage, modification, validation ou lecture
nommés) se fait directement, sans inventaire ni triage : une première commande
qui groupe les recherches indépendantes, l'action, puis la validation demandée ;
une vérification de plus seulement si elle apporte un fait nouveau. L'inventaire
borné ne sert qu'à décider d'une délégation : lister ou compter les fichiers et
symboles pertinents, sans suivre d'appelants, ouvrir plusieurs implémentations
ni tester d'hypothèse.

Reste à la racine, sans annonce et sans lire le skill : petite tâche locale, lot
déterministe borné (validation, renommage), implémentation locale au contrat
explicite, consultation documentaire à une seule source, recherche de cause dont
le point d'entrée est connu et la vérification directe.
Le travail confié doit amortir la coordination de chaque enfant, y compris les
requêtes racine à tarif complet.

Même modèle et même effort que la racine : rester à la racine, quel que soit
le rôle ou le motif. Cette règle prime sur tout routage.

Déléguer seulement dans ces cas :
- `scout` (Luna ; `scout_complex` seulement pour une capacité Sol établie au
  cadrage) : point d'entrée à découvrir ou chaîne à tracer entre composants, avec
  une exploration confiée assez large pour dépasser la coordination (environ huit
  fichiers ou 60 Ko de source à lire ; mesuré rentable pour un audit en lecture
  seule) et une réponse qui tient en quelques lignes `chemin:ligne`.
- `researcher` : toute recherche documentaire à plusieurs questions ou sources.
  Le seuil se décide avant la première recherche : dès qu'une deuxième requête,
  source ou question devient nécessaire, arrêter et créer `researcher`, puis
  attendre son identifiant actif ; ne pas requalifier après coup en consultation
  ponctuelle.
- `runner` : validation assez longue et indépendante ; `builder` : implémentation
  substantielle ou indépendante, validation ciblée comprise.

## Protocole de délégation

1. Avant la création, une ligne de triage : rôle, modèle, effort, livrable
   exclusif de l'enfant, travail que la racine n'effectuera plus, preuve d'arrêt,
   raison pour laquelle l'économie dépasse la coordination, signal de
   requalification. À défaut, garder le travail à la racine.
2. Transmission autonome et courte, `fork_turns = "none"` : question, périmètre,
   preuve d'arrêt, format de retour, faits établis séparés des hypothèses et
   inconnues. Ne pas recopier ces instructions : l'enfant les charge déjà.
3. Après la création, l'identifiant retourné suffit : pas de `list_agents`, un
   seul `wait_agent` avec `timeout_ms` d'au moins 300000 (il revient dès que
   l'enfant répond ; chaque appel de plus est une requête racine à tarif
   complet), relancé seulement après dépassement, pas de `send_message` de
   pilotage, jamais d'attente sans enfant actif. Le périmètre confié est réservé
   à l'enfant : la racine n'y lit plus, n'y cherche plus et n'y fige ni plan ni
   diagnostic. Si elle sait déjà conclure sans lui, `interrupt_agent`.
4. Acceptation : lire le rapport et ne vérifier que les preuves `chemin:ligne`
   citées (quelques lectures courtes). Relire des fichiers entiers ou explorer
   au-delà est une refaite : la substitution est annulée. Pour un audit
   exhaustif, vérifier que la liste des fichiers avec preuve couvre tout
   l'ensemble (un comptage) : un fichier absent ou « non vérifié » n'est pas
   conforme.
5. Une hypothèse d'un enfant ne devient pas un fait dans la synthèse. Seule la
   racine requalifie une mission.

## Le skill `quota-orchestrator`

Le lire seulement pour choisir un modèle ou un effort hors des profils, une
variante `_complex`, `strategist`, une consultation `architect`, une revue
indépendante, une mesure ou comparaison de coûts, ou une situation que ces
règles ne tranchent pas. Jamais pour une tâche locale ni pour déléguer à un
profil standard.

## Règles permanentes

- Les profils nommés portent leurs modèles et efforts de secours, non une preuve
  d'optimalité ; leur `sandbox_mode` n'est pas appliqué : le bac à sable du
  parent prévaut. Ne pas laisser deux agents d'implémentation éditer les mêmes
  fichiers. Ne jamais prétendre qu'un override non appliqué a été utilisé.
- Revue indépendante : jamais par défaut ; une seule revue ciblée pour la
  sécurité, la perte de données, une migration irréversible, un contrat public,
  une contradiction non résolue ou un comportement critique sans test fiable.
- Une délégation pour un besoin explicite de capacité, de qualité ou de délai
  reste possible ; elle est annoncée comme telle, pas comme une économie.
- Une information manquante appelle une collecte ciblée, pas plus d'effort.
- Sans mesure comparable, annoncer un gain attendu, pas démontré. Un run
  `Complete = false` est `non observable` : jamais dans une comparaison ou une
  recommandation économique. Promouvoir une tâche locale vers un sous-agent pour
  motif économique exige au moins cinq paires de runs complets, comparables et
  randomisés, en cache froid (cache chaud publié séparément).
- Un sous-agent déjà mandaté suit sa mission et son rôle : il ne lit pas le
  skill, ne refait pas le triage, ne délègue pas et remonte les décisions.
- Ne jamais lancer l'orchestrateur sous `--yolo` ni
  `--dangerously-bypass-approvals-and-sandbox`, ni élargir ses permissions
  runtime.
