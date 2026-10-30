# Mock interview SQL - 45 minutes

On va se faire un mock ensemble avant mercredi.
Voici comment ca va marcher: je te pose les demandes comme dans une entrevue,
je te laisse penser out loud, puis je te donne un feedback concret.

## Structure

| Temps | Activite |
|---|---|
| 0-5 min | Warm-up, clarifier le schema et les assumptions |
| 5-12 min | Case 01, filtre et tri |
| 12-20 min | Case 03, anti-join et NULL |
| 20-28 min | Case 07, agregation et sous-requete |
| 28-36 min | Case 09, top-N avec ties |
| 36-42 min | Case 10 ou 11, fenetre |
| 42-45 min | Feedback, score, deux points a pratiquer |

Tu peux ouvrir le schema, mais ne regarde pas les solutions.
Le modele est resume dans la section "Le modele de donnees" du `README.md`, et
le schema complet est dans `data/schema.sql`.
Je veux surtout que tu penses out loud au lieu de me donner la query
directement.

## Questions a poser a voix haute

### Case 01 - Comptes actifs

Je te demanderai: "On veut les comptes actifs ouverts avant le 1er mars.
Quelles colonnes et quel ordre tu retournerais?"

Follow-up: "Le 1er mars est-il inclus?"

### Case 03 - Clients sans compte

Je te demanderai: "Trouve les clients qui n'ont aucun compte, meme pas un
compte ferme."

Follow-up: "Pourquoi ton `LEFT JOIN` ne doit pas devenir un `INNER JOIN`?"

### Case 07 - Au-dessus de la moyenne

Je te demanderai: "Trouve les clients dont les debits depassent la moyenne des
totaux clients."

Follow-up: "Ta moyenne est-elle par transaction ou par client?"

### Case 09 - Top comptes

Je te demanderai: "Retourne les rangs 1 et 2 par succursale, en gardant les
ties."

Follow-up: "Pourquoi `ROW_NUMBER` n'est-il pas le meilleur choix ici?"

### Case 10 - Mois precedent

Je te demanderai: "Compare les debits de chaque mois a ceux du mois precedent."

Follow-up: "Que fais-tu quand un mois n'a aucune transaction?"

### Case 11 - Cumul

Je te demanderai: "Calcule un montant signe cumulatif par compte."

Follow-up: "Que fais-tu si deux transactions ont la meme date?"

## A quoi ressemble une bonne reponse

Je veux que tu reformules la demande avant de coder.

Je regarderai si tu identifies la table de depart, les cles de join et le
grain attendu.

Je veux t'entendre annoncer le traitement des `NULL`, des doublons et des
bornes de date.

Je te demanderai de verifier le nombre de lignes et quelques resultats avant
de declarer la requete correcte.

Je regarderai si tu sais expliquer pourquoi `RANK`, `LAG` ou une CTE est
utilisee, sans simplement reciter une syntaxe.

## Rubrique simple

Je te donnerai 0, 1 ou 2 points dans chaque categorie:

| Categorie | 0 | 1 | 2 |
|---|---|---|---|
| Comprend le besoin | part dans le code | clarifie apres aide | reformule proprement |
| Joins | mauvais grain ou mauvais type | corrige avec indice | choisit et justifie |
| Agregations | compte faux | bonne idee, details fragiles | grain et `HAVING` justes |
| NULL et doublons | oublis | reconnait apres follow-up | anticipe |
| Fenetres et dates | bloque | pattern avec aide | explique partition et ordre |
| Communication | silence ou guess | explique partiellement | assumptions et sanity-check |

Un score de 9 sur 12 sera deja un bon signal pour ton niveau intermediaire.
Le plus important sera de noter les deux patterns a revoir, pas de faire un
verdict dramatique.

## Si tu ne peux pas executer le code

Je te demanderai de penser a voix haute.

Je te ferai ecrire le grain de chaque CTE et les colonnes finales.

Je te demanderai de me construire un mini exemple avec deux clients, un
`NULL` et un doublon.

Je te ferai verbaliser les lignes qui doivent survivre a un `LEFT JOIN`.

YEEE, le but est de pratiquer le raisonnement, pas de gagner un concours de
typing SQL lol.
