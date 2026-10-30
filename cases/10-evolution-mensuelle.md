---
case: 10
title: "Evolution mensuelle des debits"
expected_columns: branch_id, transaction_month, total_debits, previous_month_debits, variation
---
# Evolution mensuelle des debits

Imagine que ton boss t'envoie ce ticket.

## Niveau

Avance.

## Le contexte du ticket

Ton equipe de pilotage veut voir comment les debits changent d'un mois a
l'autre dans chaque succursale.

## Ce que je te demanderais

Pour chaque succursale et chaque mois de janvier a mai 2026, affiche le total
des debits, le total du mois precedent et la variation courante moins
precedente. Le premier mois d'une succursale a `NULL` pour le mois precedent
et la variation.

## Ce que j'attends de toi

Retourne `branch_id`, `transaction_month`, `total_debits`,
`previous_month_debits` et `variation`, arrondis a deux decimales sauf les
`NULL`.
Trie par succursale, puis mois.

<details>
<summary>Hints</summary>

`LAG()` lit la ligne precedente dans une partition.

Cree une grille complete succursale-mois avant `LAG`, sinon un mois absent
decalera la comparaison.

</details>

## Mes questions de suivi

- Pourquoi faut-il remplacer les mois sans transaction par zero avant `LAG`?
- Comment calculerais-tu une variation en pourcentage en evitant une division
  par zero?

