---
case: 05
title: "Bucketiser les montants de transaction"
expected_columns: amount_bucket, transaction_count, total_amount
---
# Bucketiser les montants de transaction

Imagine que ton boss t'envoie ce ticket.

## Niveau

Intermediaire.

## Le contexte du ticket

Ton equipe produit veut comprendre la taille des mouvements dans le compte
courant.

## Ce que je te demanderais

Classe chaque transaction dans une tranche:

- `small` si le montant est strictement inferieur a 50;
- `medium` si le montant est de 50 a 200 inclusivement;
- `large` si le montant est strictement superieur a 200.

Retourne le nombre de transactions et leur montant total par tranche.

## Ce que j'attends de toi

Retourne `amount_bucket`, `transaction_count` et `total_amount`.
Trie dans l'ordre `small`, `medium`, `large`.

<details>
<summary>Hints</summary>

Un `CASE` est utile pour produire une categorie calculee.

L'ordre alphabetique ne donnera pas forcement l'ordre business demande:
ajoute un deuxieme `CASE` dans `ORDER BY` si necessaire.

</details>

## Mes questions de suivi

- Comment traiterais-tu un montant `NULL`?
- Comment ferais-tu des tranches parametrees par une table de reference?

