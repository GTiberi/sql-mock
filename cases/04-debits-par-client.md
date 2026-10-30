---
case: 04
title: "Total des debits par client"
expected_columns: customer_id, customer_name, total_debits
---
# Total des debits par client

Imagine que ton boss t'envoie ce ticket.

## Niveau

Intermediaire.

## Le contexte du ticket

Ton equipe marketing veut une vue de la valeur des sorties d'argent par
client, y compris les clients qui n'ont encore aucune transaction de debit.

## Ce que je te demanderais

Retourne tous les clients et le total de leurs transactions `debit`.
Un client sans debit doit afficher `0`, pas `NULL`.

## Ce que j'attends de toi

Retourne `customer_id`, `customer_name` et `total_debits`, arrondi a deux
decimales.
Trie par `total_debits` decroissant, puis `customer_id` croissant.

<details>
<summary>Hints</summary>

Garde `customers` du cote gauche de tes joins et utilise `COALESCE` autour de
ton `SUM`.

Mets la condition `transaction_type = 'debit'` dans le `JOIN` ou dans un
`CASE` d'agregation, sinon tu risques de perdre les clients sans debit.

</details>

## Mes questions de suivi

- Quelle difference entre `SUM(amount)` et
  `SUM(CASE WHEN ... THEN amount ELSE 0 END)` ici?
- Que se passe-t-il si le montant lui-meme peut etre `NULL`?

