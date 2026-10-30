---
case: 01
title: "Lister les comptes actifs"
expected_columns: account_id, customer_id, account_type, opened_date, status
---
# Lister les comptes actifs

Imagine que ton boss t'envoie ce ticket.

## Niveau

Warm-up.

## Le contexte du ticket

Ton boss du service des operations veut une liste rapide des comptes qui
peuvent encore etre utilises par les clients.

## Ce que je te demanderais

Retourne les comptes dont le `status` est `active` et qui ont ete ouverts avant
le 1er mars 2026.

## Ce que j'attends de toi

Retourne `account_id`, `customer_id`, `account_type`, `opened_date` et
`status`.
Trie par `opened_date` croissante, puis `account_id` croissant.

<details>
<summary>Hints</summary>

Filtre sur la table `accounts`, puis joins `customers` seulement si tu as
besoin de ses colonnes.

La date est stockee en texte ISO `YYYY-MM-DD`, donc une comparaison directe
fonctionne ici.

</details>

## Mes questions de suivi

- Que changerais-tu pour inclure les comptes ouverts le 1er mars?
- Pourquoi ne faut-il pas filtrer seulement sur `closed_date IS NULL`?

