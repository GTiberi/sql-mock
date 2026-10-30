# sql-mock-entrevue

J'ai monte ce petit kit pour toi, pour que tu puisses pratiquer une entrevue
technique SQL avec des use cases qui ressemblent a de vraies demandes de data.

Tu connais deja `JOIN` et `GROUP BY`, alors je t'amene tranquillement vers les
CTE, les dates et les window functions.

Tout est fictif: Banque Fictive, clients inventes, comptes inventes.
Zero serveur de base de donnees, zero pip, zero npm, zero drama.

## Quick start

Clone le repo, ouvre un terminal dans le dossier, puis lance ces trois
commandes:

```bash
python3 setup_db.py
python3 check.py --list
python3 check.py 01 mon-reponse.sql
```

Le fichier `practice.db` est genere localement et est volontairement ignore
par Git.

Pour verifier tous les tests du kit, lance:

```bash
python3 -m unittest discover -s tests -v
```

## Le modele de donnees

J'ai mis le schema complet dans [`data/schema.sql`](data/schema.sql).
Lis-le avant ton premier case, ca vaut cinq minutes bien investies.

Quatre tables, et tout se tient par des cles entieres:

| Table | Cle primaire | Cles etrangeres | Colonnes utiles |
|---|---|---|---|
| `branches` | `id` | aucune | `name`, `city`, `region` |
| `customers` | `id` | `branch_id` -> `branches.id` | `name`, `city`, `birth_date`, `signup_date` |
| `accounts` | `id` | `customer_id` -> `customers.id`, `branch_id` -> `branches.id` | `account_type`, `opened_date`, `closed_date`, `status` |
| `transactions` | `id` | `account_id` -> `accounts.id` | `transaction_date`, `transaction_type`, `amount`, `category`, `external_reference`, `created_at` |

Le chemin de join normal que je veux que tu aies en tete est:

```sql
transactions t
  JOIN accounts a   ON a.id = t.account_id
  JOIN customers c  ON c.id = a.customer_id
  JOIN branches b   ON b.id = a.branch_id
```

Quelques details qui changent tes reponses, alors lis-les deux fois:

- Un compte a sa propre `branch_id`, qui n'est pas toujours celle de son
  client. Pour un total par succursale, passe par `accounts`, pas par
  `customers`.
- `accounts.status` vaut `active`, `closed` ou `suspended`, et `closed_date`
  est `NULL` tant que le compte est ouvert.
- Un client peut n'avoir aucun compte, et un compte peut n'avoir aucune
  transaction. C'est exactement la ou tes `LEFT JOIN` comptent.
- `transactions.amount` est toujours positif. Le sens vient de
  `transaction_type`, qui vaut `credit` ou `debit`.
- `transactions.category` peut etre `NULL`, et `external_reference` contient
  quelques doublons volontaires.
- Toutes les dates sont du texte ISO `YYYY-MM-DD`, donc elles se comparent et
  se trient correctement. Les transactions couvrent 2026-01-01 a 2026-05-31.

## Comment je veux que tu pratiques

1. Lis un ticket dans `cases/`.
2. Ecris ta reponse dans un fichier comme `mon-reponse.sql`.
3. Lance `python3 check.py 03 mon-reponse.sql`.
4. Si ca fail, lis le feedback et ouvre le hint seulement apres un vrai
   premier essai.
5. Ne regarde `solutions/` qu'apres t'etre explique ton approche a voix haute,
   ou apres me l'avoir expliquee.

Les aliases de colonnes sont acceptes par le checker.
Tes resultats doivent quand meme avoir les bonnes colonnes dans le bon ordre et
les bonnes lignes.

Tout execute avec SQLite ici, mais le moteur de ton entrevue est inconnu.
[`DIALECTES.md`](DIALECTES.md) liste les equivalences par moteur et les
endroits ou mes solutions du repo changeraient.

### Ce que le checker ne peut pas attraper

Le checker compare tes lignes avec celles de la solution, donc une erreur qui
produit exactement le meme resultat passe pareil.
Je te les liste au complet, parce qu'elles comptent quand meme en entrevue:

- Case 01, oublier le deuxieme critere de tri: les ex aequo sortent dans le
  bon ordre ici, mais rien ne te le garantit sur un autre moteur.
- Cases 02 et 04, grouper sans toutes les colonnes non agregees: SQLite
  l'accepte, SQL Server et Oracle le refusent. PostgreSQL l'accepte seulement
  parce que le `GROUP BY` contient deja la cle primaire de la table d'ou vient
  le nom; ne compte pas la-dessus des que la colonne vient d'ailleurs.
- Case 06, mettre une fonction sur la colonne dans le `WHERE`: meme resultat,
  mais tu perds l'index.
- Cases 04, 05, 06, 07, 08, 10 et 11, oublier `ROUND(..., 2)` sur un montant:
  les montants du seed sont deja au cent pres, donc la somme donne la meme
  valeur au cent pres avec ou sans l'arrondi et le checker ne voit aucune
  difference.
  Ce qui reste est du bruit de flottant: nul pour le case 05, au plus
  0.00000000003 pour les cases 06 et 08.
  Une somme de flottants n'est pas garantie exacte, meme quand elle tombe pile
  comme ici.
  Les tickets le demandent pareil, alors ecris-le.
  Case 13 fait exception: son `retention_rate` vient d'une division, donc le
  checker refuse bel et bien la version non arrondie.
- Case 08, joindre la grille sur le nom de succursale: les noms sont uniques
  dans ce jeu de donnees, donc ca marche par chance.
- Case 11, enlever `transaction_id` de l'`ORDER BY` de la fenetre: SQLite
  departage les ex aequo par rowid et retombe sur la bonne reponse.
- Case 13, oublier le filtre janvier-mai: toutes les transactions du seed sont
  deja dans cette periode.
- Case 14, `UNION` au lieu de `UNION ALL`: les quatre libelles sont
  differents, donc le dedoublonnage ne jette rien.
- Case 14, enlever `closed_date IS NOT NULL`: une comparaison avec `NULL`
  n'est jamais vraie, donc ces lignes tombent de toute facon.

Tous les autres pieges de mes sections "Les pieges que je veux que tu
surveilles" sont rejoues par les tests du kit, qui exigent que le checker les
refuse.

## Plan de study jusqu'a mercredi 2026-11-04

### Jeudi 29 octobre

Warm-up tranquille: cases 01 a 04.
Revise `WHERE` versus `HAVING`, `INNER JOIN` versus `LEFT JOIN` et `NULL`.

### Vendredi 30 octobre

Cases 05 a 07.
Pratique les `CASE`, les mois avec des bornes de dates et les sous-requetes.

### Samedi 31 octobre

Cases 08 a 10.
Fais les CTE et les fenetres sur papier avant de run le SQL.

### Dimanche 1er novembre

Cases 11 a 14.
Focus sur cumul, dedup, cohortes et data quality.

### Lundi 2 novembre

Refais les cases ou tu as utilise la solution.
Ensuite, reponds aux questions dans `THEORIE.md` sans lire les reponses.

### Mardi 3 novembre

Fais le mock de `MOCK.md` en 45 minutes.
Je poserai les follow-ups et je ne te sauverai pas trop vite.

### Mercredi 4 novembre

Pas de gros cram session.
Relis les patterns, respire, et rappelle-toi de dire tes assumptions.

## Interview-day tips

- Commence par reformuler la demande et les colonnes attendues.
- Dis clairement comment tu traites les `NULL`, les doublons et les dates
  limites.
- Fais une version simple, puis ameliore-la avec une CTE si ca rend le
  raisonnement plus clair.
- Sanity-check le nombre de lignes avant de parler de performance.
- Si tu bloques, pense out loud: le raisonnement compte beaucoup.

YEEE, you got this.
Un ticket a la fois, on ne pelletera pas par en avant sans regarder les
conditions du `JOIN` lol.
