---
case: 07
title: "Clients au-dessus de la moyenne des debits"
expected_columns: customer_id, customer_name, total_debits
---
# Clients au-dessus de la moyenne des debits

Imagine que ton boss t'envoie ce ticket.

## Niveau

Intermediaire plus.

## Le contexte du ticket

Ta collegue analyste veut cibler les clients dont les debits cumules depassent
la moyenne des clients qui ont au moins un debit.

## Ce que je te demanderais

Retourne les clients dont le total de debits est strictement superieur a la
moyenne des totaux de debits par client. Les clients sans debit ne font pas
partie de la moyenne.

## Ce que j'attends de toi

Retourne `customer_id`, `customer_name` et `total_debits`, arrondi a deux
decimales.
Trie par `total_debits` decroissant, puis `customer_id` croissant.

<details>
<summary>Hints</summary>

Calcule d'abord un total par client, puis calcule la moyenne de cette
sous-requete.

La moyenne est une moyenne des totaux clients, pas la moyenne de toutes les
lignes de transaction.

</details>

## Mes questions de suivi

- Pourquoi ne faut-il pas comparer chaque ligne de transaction a la moyenne?
- Comment inclure les clients sans debit avec un total de zero, tout en les
  excluant automatiquement du resultat final?

