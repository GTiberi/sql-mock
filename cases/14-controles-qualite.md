---
case: 14
title: "Rapport de controles de qualite"
expected_columns: check_name, issue_count
---
# Rapport de controles de qualite

Imagine que ton boss t'envoie ce ticket.

## Niveau

Challenge final.

## Le contexte du ticket

Avant que tu livres le reporting, la data quality veut un petit rapport
reproductible avec quatre controles independants.

## Ce que je te demanderais

Retourne une ligne par controle:

- `transactions_after_closure`: transactions dont la date depasse la date
  de fermeture du compte;
- `duplicate_references`: groupes de references externes qui apparaissent
  plus d'une fois;
- `missing_categories`: transactions dont la categorie est `NULL`;
- `invalid_amounts`: transactions dont le montant est nul ou negatif.

## Ce que j'attends de toi

Retourne `check_name` et `issue_count`, dans l'ordre exact ci-dessus. Tous les
controles doivent etre presents, meme si le compte est zero.

<details>
<summary>Hints</summary>

Des petits `SELECT` combines avec `UNION ALL` donnent une ligne par controle.

Pour compter les references dupliquees, compte les groupes produits par une
sous-requete avec `HAVING`, pas le nombre de lignes dupliquees.

</details>

## Mes questions de suivi

- Comment distinguer une categorie inconnue legitime d'une vraie anomalie?
- Pourquoi ce rapport devrait-il etre suivi par des tests de donnees et pas
  seulement par un test de code?

