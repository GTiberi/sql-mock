# Theorie express

Je te donne ici les questions qui arrivent souvent juste apres un exercice.
Les reponses sont courtes volontairement, comme dans une vraie entrevue.

## Quand tu reponds WHERE versus HAVING

`WHERE` filtre les lignes avant le `GROUP BY`.
`HAVING` filtre les groupes apres l'agregation.

## Quand tu compares INNER JOIN versus LEFT JOIN

`INNER JOIN` garde seulement les correspondances des deux tables.
`LEFT JOIN` garde toutes les lignes de gauche et met `NULL` a droite quand il
n'y a pas de correspondance.

## Quand tu choisis UNION versus UNION ALL

`UNION` combine puis dedoublonne.
`UNION ALL` combine sans dedoublonner et est le choix normal quand chaque bloc
represente un evenement ou un controle different.

## Quand tu reponds COUNT(*) versus COUNT(colonne)

`COUNT(*)` compte les lignes.
`COUNT(colonne)` ignore les lignes ou cette colonne est `NULL`.

## Quand tu rencontres NULL

`NULL` veut dire valeur inconnue ou absente, pas zero et pas une chaine vide.
Tu utilises `IS NULL`, jamais `= NULL`.
`COALESCE` prend la premiere valeur non-NULL.

## Quand on te demande l'ordre logique d'execution

Une version courte est: `FROM` et joins, `WHERE`, `GROUP BY`, agregats,
`HAVING`, fenetres, `SELECT`, `ORDER BY`, puis `LIMIT`.
Le moteur peut optimiser le plan physique, mais cette logique t'aide a savoir
ou placer chaque filtre.

## Quand on te parle d'indexes

Un index aide surtout les recherches et joins sur des colonnes selectives.
Il coute de l'espace et ralentit les writes, donc tu indexes selon les vrais
patterns de requetes plutot que chaque colonne.

## Quand tu compares window function versus GROUP BY

`GROUP BY` reduit plusieurs lignes en une ligne par groupe.
Une window function garde les lignes detaillees et ajoute un calcul de
contexte, comme un rang, un cumul ou la ligne precedente.

## Quand tu choisis ROW_NUMBER, RANK, DENSE_RANK

`ROW_NUMBER` donne un numero unique, meme en cas d'egalite.
`RANK` conserve les egalites et saute des rangs.
`DENSE_RANK` conserve les egalites sans saut de rang.
