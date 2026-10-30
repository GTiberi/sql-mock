---
case: 03
title: "Trouver les clients sans compte"
expected_columns: customer_id, customer_name
---
# Trouver les clients sans compte

Imagine que ton boss t'envoie ce ticket.

## Niveau

Intermediaire.

## Le contexte du ticket

Une campagne d'accueil vise les clients qui ont un profil, mais aucun compte
bancaire dans notre inventaire.

## Ce que je te demanderais

Retourne tous les clients qui n'ont aucun compte, ferme ou actif.

## Ce que j'attends de toi

Retourne `customer_id` et `customer_name`.
Trie par `customer_id` croissant.

<details>
<summary>Hints</summary>

Commence par `customers`, puis fais un `LEFT JOIN` vers `accounts`.

Un anti-join classique verifie ensuite que la cle de la table jointe est
`NULL`.

</details>

## Mes questions de suivi

- Pourquoi un `INNER JOIN` ferait-il disparaitre la reponse?
- Quelle autre strategie avec `NOT EXISTS` pourrais-tu utiliser?

