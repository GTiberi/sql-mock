---
case: 02
title: "Succursales avec assez de comptes actifs"
expected_columns: branch_id, branch_name, active_account_count
---
# Succursales avec assez de comptes actifs

Imagine que ton boss t'envoie ce ticket.

## Niveau

Warm-up plus.

## Le contexte du ticket

Ton boss veut savoir quelles succursales ont assez de volume pour recevoir
une nouvelle plage de support.

## Ce que je te demanderais

Compte les comptes `active` par succursale et garde seulement les succursales
qui ont au moins 20 comptes actifs.

## Ce que j'attends de toi

Retourne `branch_id`, `branch_name` et `active_account_count`.
Trie par nombre de comptes decroissant, puis `branch_id` croissant.

<details>
<summary>Hints</summary>

Pense a `GROUP BY` pour obtenir un total par succursale.

Le filtre sur un resultat d'agregation va dans `HAVING`, pas dans `WHERE`.

</details>

## Mes questions de suivi

- Pourquoi `COUNT(*)` et `COUNT(a.id)` ne sont-ils pas toujours equivalentes
  avec un `LEFT JOIN`?
- Comment retourner aussi les succursales a zero compte?

