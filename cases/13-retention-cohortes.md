---
case: 13
title: "Retention par cohorte d'inscription"
expected_columns: cohort_month, activity_month, cohort_customers, active_customers, retention_rate
---
# Retention par cohorte d'inscription

Imagine que ton boss t'envoie ce ticket.

## Niveau

Challenge.

## Le contexte du ticket

Ton equipe produit veut savoir si les clients inscrits dans une meme periode
continuent de faire des transactions.

## Ce que je te demanderais

Forme une cohorte avec le mois de `signup_date`. Pour chaque cohorte et
mois d'activite entre janvier et mai 2026, compte les clients de la cohorte,
les clients ayant au moins une transaction, puis le taux de retention en
pourcentage. Ignore une activite avant le mois d'inscription.

## Ce que j'attends de toi

Retourne `cohort_month`, `activity_month`, `cohort_customers`,
`active_customers` et `retention_rate`, arrondi a deux decimales.
Trie par cohorte, puis mois d'activite.

<details>
<summary>Hints</summary>

Precalcule l'activite au niveau client-mois pour eviter de compter plusieurs
transactions du meme client.

Une CTE pour la taille des cohortes et une autre pour l'activite rendent la
jointure finale plus simple.

</details>

## Mes questions de suivi

- Quel effet aurait `COUNT(*)` au lieu de `COUNT(DISTINCT customer_id)`?
- Comment calculerais-tu le mois 0, mois 1, mois 2 plutot que des dates
  `YYYY-MM`?

