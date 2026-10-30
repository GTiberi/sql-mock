---
case: 11
title: "Cumul signe par compte"
expected_columns: account_id, transaction_date, transaction_id, signed_running_total
---
# Cumul signe par compte

Imagine que ton boss t'envoie ce ticket.

## Niveau

Avance.

## Le contexte du ticket

Ton equipe support veut suivre la tendance des mouvements de chaque compte sans
recalculer le cumul dans Python.

## Ce que je te demanderais

Pour chaque transaction, calcule le cumul signe du compte: un credit ajoute
son montant et un debit le soustrait. Le cumul doit respecter la date et, en
cas d'egalite de date, l'identifiant de transaction.

## Ce que j'attends de toi

Retourne `account_id`, `transaction_date`, `transaction_id` et
`signed_running_total`, arrondi a deux decimales.
Trie par `account_id`, date, puis `transaction_id`.

<details>
<summary>Hints</summary>

Transforme d'abord chaque ligne en montant signe avec un `CASE`.

Une fonction fenetree `SUM(...) OVER (...)` peut garder toutes les lignes tout
en calculant un cumul.

</details>

## Mes questions de suivi

- Pourquoi `GROUP BY account_id` ne peut-il pas produire ce resultat detaille?
- Pourquoi ajouter `transaction_id` dans l'ordre de la fenetre?

