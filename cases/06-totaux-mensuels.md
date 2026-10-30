---
case: 06
title: "Totaux mensuels par type"
expected_columns: transaction_month, transaction_type, transaction_count, total_amount
---
# Totaux mensuels par type

Imagine que ton boss t'envoie ce ticket.

## Niveau

Intermediaire.

## Le contexte du ticket

Ton equipe reporting demande un resume mensuel des credits et des debits pour
les cinq premiers mois de 2026.

## Ce que je te demanderais

Agrege les transactions par mois calendaire et par `transaction_type`.
Un mois est identifie par `YYYY-MM`.

## Ce que j'attends de toi

Retourne `transaction_month`, `transaction_type`, `transaction_count` et
`total_amount`, arrondi a deux decimales.
Trie par mois croissant, puis `transaction_type` avec `credit` avant `debit`.

<details>
<summary>Hints</summary>

`SUBSTR(transaction_date, 1, 7)` fabrique le mois `YYYY-MM` a partir
d'une date ISO, et ca marche sur a peu pres tous les moteurs.

Ne groupe pas seulement par le numero de mois si la requete doit survivre a
un changement d'annee.

</details>

## Mes questions de suivi

- Comment ecrirais-tu cette extraction de mois en PostgreSQL?
- Pourquoi un filtre de date borne est-il souvent preferable a une fonction
  sur la colonne dans un `WHERE` indexe?

