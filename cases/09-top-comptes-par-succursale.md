---
case: 09
title: "Top comptes par succursale"
expected_columns: branch_id, account_id, customer_id, transaction_count, account_rank
---
# Top comptes par succursale

Imagine que ton boss t'envoie ce ticket.

## Niveau

Avance.

## Le contexte du ticket

Chaque succursale veut identifier ses comptes les plus actifs pour inviter
leurs clients a une session de conseil.

## Ce que je te demanderais

Compte les transactions par compte et retourne les comptes de rang 1 ou 2
dans leur succursale. Les egalites doivent etre conservees: si plusieurs
comptes sont ex aequo au rang 2, retourne-les tous.

## Ce que j'attends de toi

Retourne `branch_id`, `account_id`, `customer_id`, `transaction_count` et
`account_rank`.
Trie par succursale, rang, puis compte.

<details>
<summary>Hints</summary>

Agrege d'abord au niveau du compte, puis applique `RANK()` avec une partition
par succursale.

`ROW_NUMBER()` coupe les egalites. Ici, le mot important est "ex aequo".

</details>

## Mes questions de suivi

- Quand utiliserais-tu `DENSE_RANK` au lieu de `RANK`?
- Que se passe-t-il avec un `LEFT JOIN` si un compte n'a aucune transaction?

