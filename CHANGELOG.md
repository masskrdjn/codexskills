# Historique des évolutions

La version courante est définie dans le manifeste du plugin. Voir
[CONTRIBUTING.md](CONTRIBUTING.md) pour les règles de version et de maintenance.
Les fixtures conservent les anciennes sources ; cet historique ne reconstitue
pas les changements des versions précédentes.

## 0.9.0 — 2026-10-26 (préparée localement, non publiée)

- Ajout de GPT-6.1 Terra avec `visual_operator` pour les missions visuelles et
  parcours d'interface bornés, et `writer` pour la rédaction et la synthèse
  de faits établis.
- Raisonnement `medium` par défaut, sélection d'efforts supérieurs selon la
  difficulté et leur application effective par le runtime. Sources officielles,
  tarifs datés et limites documentés ; aucun gain économique projet démontré.
- Routage et copies distribuées actualisés ; migration depuis `0.8.5` avec
  sauvegardes, conservation des personnalisations et tests de régression.
- Guide de maintenance, règle obligatoire de version dans les consignes du
  dépôt et contrôles de cohérence de distribution.
- La proposition intermédiaire `0.8.6`, non publiée, est regroupée dans cette
  évolution mineure. Publication et chargement des profils dans une nouvelle
  conversation restent distincts de la préparation locale.
