---
case: 08
title: "Net mensuel par succursale"
expected_columns: branch_id, branch_name, transaction_month, total_credits, total_debits, net
---
# Net mensuel par succursale

Imagine que ton boss t'envoie ce ticket.

## Niveau

Avance.

## Le contexte du ticket

Ton boss suit les flux entrants et sortants par succursale pendant la
periode janvier a mai 2026.

## Ce que je te demanderais

Pour chaque succursale et chaque mois de cette periode, calcule les credits,
les debits et le net (`credits - debits`). Les valeurs absentes doivent etre
affichees a zero.

## Ce que j'attends de toi

Retourne `branch_id`, `branch_name`, `transaction_month`, `total_credits`,
`total_debits` et `net`, arrondis a deux decimales.
Trie par `branch_id`, puis mois croissant.

<details>
<summary>Hints</summary>

Une CTE peut rendre l'agregation mensuelle plus lisible.

Pour garantir les mois a zero, construis une petite liste des mois et combine
la avec les succursales avant le `LEFT JOIN`.

</details>

## Mes questions de suivi

- Quelle serait la difference entre `CROSS JOIN` et `INNER JOIN` dans la grille
  succursale-mois?
- Comment eviterais-tu de compter deux fois une transaction apres plusieurs
  joins?

