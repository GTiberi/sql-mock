# Dialectes SQL

J'ai fait les solutions avec SQLite, mais ton entrevue peut utiliser un autre
moteur.
Quand on te donne le dialecte, dis-le a voix haute avant d'adapter la syntaxe.

| Besoin | SQLite | SQL Server | Oracle | PostgreSQL |
|---|---|---|---|---|
| Extraire un mois d'une date ISO | `SUBSTR(d, 1, 7)` | `SUBSTRING(d, 1, 7)` | `SUBSTR(d, 1, 7)` | `SUBSTRING(d, 1, 7)` ou `SUBSTR` |
| Extraire un mois d'un vrai type date | `strftime('%Y-%m', d)` | `CONVERT(char(7), d, 126)` ou `FORMAT(d, 'yyyy-MM')` | `TO_CHAR(d, 'YYYY-MM')` | `TO_CHAR(d, 'YYYY-MM')` ou `date_trunc` |
| Limiter les lignes | `LIMIT 10` | `TOP 10` ou `OFFSET ... FETCH` | `FETCH FIRST 10 ROWS ONLY` | `LIMIT 10` ou `FETCH FIRST` |
| Concatener | `a || b` | `a + b` ou `CONCAT` | `a || b` | `a || b` |
| Remplacer un NULL | `COALESCE`, `IFNULL` | `COALESCE`, `ISNULL` | `COALESCE`, `NVL` | `COALESCE` |
| Fenetres | `RANK`, `LAG`, `SUM OVER` | Oui | Oui | Oui |
| Alias de table | `accounts a` ou `accounts AS a` | `accounts a` ou `accounts AS a` | `accounts a`, jamais `AS` | `accounts a` ou `accounts AS a` |
| Arrondir une somme flottante | `ROUND(SUM(amount), 2)` | `ROUND(SUM(amount), 2)` | `ROUND(SUM(amount), 2)` | `ROUND(SUM(amount)::numeric, 2)` |

## Ce que tu dois adapter dans mes solutions

Les patterns de jointure, `GROUP BY`, `HAVING`, `CASE`, CTE et fonctions
fenetrees sont largement portables.

Voici les changements les plus probables:

- Mes solutions nomment leurs tables sans `AS` (`FROM accounts a`,
  `JOIN transactions t`), parce que Oracle refuse `accounts AS a` avec un
  ORA-00933 avant meme de regarder le reste de la requete.
  SQLite, SQL Server et PostgreSQL acceptent les deux formes, donc celle sans
  `AS` est la seule qui passe partout.
  Les alias de colonne gardent leur `AS`, qui lui est portable.
- Je ne nomme jamais une colonne de sortie ou une CTE avec un mot reserve.
  `rank` et `month` passent sur les quatre moteurs du tableau, mais pas `date`
  ni `user`: Oracle reserve les deux, SQL Server reserve `user`, et PostgreSQL
  accepte `user` comme alias de colonne mais le refuse comme nom de CTE.
  Le standard SQL reserve les quatre, et MySQL 8.0 reserve `RANK` pour de
  vrai: `AS rank` sans accents graves y est une erreur de syntaxe, pas un
  avertissement.
  C'est pour ca que ma solution 09 ecrit `account_rank` et que mes solutions
  06, 08 et 10 ecrivent `transaction_month`.
  Citer le nom marche aussi, mais la citation change d'un moteur a l'autre:
  `"rank"` sur SQLite, Oracle et PostgreSQL, `[rank]` sur SQL Server, et des
  accents graves sur MySQL.
  Un nom plus precis ne coute rien et t'evite ce choix en entrevue.
- Mes solutions 06, 08, 10 et 13 extraient le mois avec
  `SUBSTR(date, 1, 7)`, qui tourne tel quel sur SQLite, Oracle et PostgreSQL.
  Sur SQL Server, remplace `SUBSTR` par `SUBSTRING`, qui prend exactement les
  memes trois arguments.
- Mes solutions 08 et 10 fabriquent leur grille de mois avec des `SELECT`
  combines par `UNION ALL`, portable partout. Oracle demande en plus un
  `FROM dual` apres chaque `SELECT` de constantes.
- Mes solutions 01 et les autres filtres de dates utilisent des textes ISO,
  ce qui se compare correctement tant que la colonne reste en `YYYY-MM-DD`.
  Sur un vrai type `DATE`, aucune orthographe de literal ne se parse sur les
  quatre moteurs, et c'est justement la lecon a retenir.
  Le texte ISO entre quotes, `'2026-03-01'`, passe tel quel sur SQLite, qui
  garde ses dates en texte, et se convertit tout seul sur SQL Server et
  PostgreSQL.
  Oracle le convertit plutot selon `NLS_DATE_FORMAT`, souvent `DD-MON-RR`, et
  te sort un ORA-01861, donc ecris-y `DATE '2026-03-01'` ou
  `TO_DATE('2026-03-01', 'YYYY-MM-DD')`.
  Ne transporte pas `DATE '2026-03-01'` partout pour autant: ce literal
  standard existe sur Oracle et PostgreSQL, mais SQLite et SQL Server ne le
  connaissent pas et te repondent une erreur de syntaxe.
  N'enleve surtout pas les quotes non plus, parce que `2026-03-01` sans quotes
  est une soustraction d'entiers qui vaut 2022; SQLite l'accepte et te rend une
  reponse silencieusement fausse, PostgreSQL et Oracle te donnent une erreur de
  type.
  `CAST('2026-03-01' AS DATE)` n'est pas une porte de sortie non plus: sur
  SQLite ce type prend l'affinite numerique et rend 2026, la meme reponse
  silencieusement fausse.
- Mes solutions 07 et 14 nomment leur sous-requete du `FROM`
  (`) customer_totals`, `) duplicate_references`). SQLite, Oracle et
  PostgreSQL 16 tolerent une table derivee sans alias, mais SQL Server et
  PostgreSQL avant la version 16 refusent de la parser.
  Nomme toujours tes tables derivees, sans `AS` pour rester bon sur Oracle
  aussi.
- Mes solutions 06, 08, 10 et 13 repetent l'expression du mois dans leur
  `GROUP BY` au lieu de reutiliser l'alias du `SELECT`. SQLite et PostgreSQL
  acceptent l'alias, mais SQL Server et Oracle le refusent. Un alias dans
  le `ORDER BY` reste correct partout.
- Les montants vivent dans une colonne `REAL`, donc `ROUND(SUM(amount), 2)`
  tourne tel quel sur SQLite, SQL Server et Oracle. PostgreSQL n'a pas de
  `round(double precision, integer)`, alors ecris-y
  `ROUND(SUM(amount)::numeric, 2)`.

Ne memorise pas une fonction par coeur.
Dis plutot: "Je vais adapter l'extraction de mois au dialecte cible, mais la
logique d'agregation reste la meme."
