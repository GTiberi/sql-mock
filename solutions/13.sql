WITH cohorts AS (
    SELECT
        id AS customer_id,
        SUBSTR(signup_date, 1, 7) AS cohort_month
    FROM customers
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM cohorts
    GROUP BY cohort_month
),
activity AS (
    SELECT
        c.id AS customer_id,
        SUBSTR(t.transaction_date, 1, 7) AS activity_month
    FROM customers c
    JOIN accounts a ON a.customer_id = c.id
    JOIN transactions t ON t.account_id = a.id
    WHERE t.transaction_date >= '2026-01-01'
      AND t.transaction_date < '2026-06-01'
    GROUP BY c.id, SUBSTR(t.transaction_date, 1, 7)
)
SELECT
    coh.cohort_month,
    act.activity_month,
    cohort_sizes.cohort_customers,
    COUNT(DISTINCT act.customer_id) AS active_customers,
    ROUND(
        100.0 * COUNT(DISTINCT act.customer_id) / cohort_sizes.cohort_customers,
        2
    ) AS retention_rate
FROM activity act
JOIN cohorts coh ON coh.customer_id = act.customer_id
JOIN cohort_sizes ON cohort_sizes.cohort_month = coh.cohort_month
WHERE act.activity_month >= coh.cohort_month
GROUP BY coh.cohort_month, act.activity_month, cohort_sizes.cohort_customers
ORDER BY coh.cohort_month, act.activity_month;

