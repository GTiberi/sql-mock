---
case: 12
title: "Detecter les references externes dupliquees"
expected_columns: external_reference, row_count, first_id, last_id
---
# Detecter les references externes dupliquees

Imagine que ton boss t'envoie ce ticket.

## Niveau

Avance plus.

## Le contexte du ticket

Une integration a peut-etre rejoue quelques evenements. La data quality veut
les references externes qui apparaissent plusieurs fois.

## Ce que je te demanderais

Retourne chaque `external_reference` qui apparait plus d'une fois, avec le
nombre de lignes, le plus petit id et le plus grand id.

## Ce que j'attends de toi

Retourne `external_reference`, `row_count`, `first_id` et `last_id`.
Trie par `row_count` decroissant, puis reference croissante.

<details>
<summary>Hints</summary>

Le regroupement se fait par reference, et le filtre sur le compte se fait avec
`HAVING COUNT(*) > 1`.

`MIN(id)` et `MAX(id)` montrent l'etendue de la duplication.

</details>

## Mes questions de suivi

- Comment garderais-tu une seule ligne canonique par reference?
- Pourquoi ne faut-il pas dedoublonner sur le montant seulement?

