WITH transaction_month AS (
    SELECT '2026-01' AS transaction_month
    UNION ALL SELECT '2026-02'
    UNION ALL SELECT '2026-03'
    UNION ALL SELECT '2026-04'
    UNION ALL SELECT '2026-05'
),
grid AS (
    SELECT b.id AS branch_id, m.transaction_month
    FROM branches b
    CROSS JOIN transaction_month m
),
debits AS (
    SELECT
        a.branch_id,
        SUBSTR(t.transaction_date, 1, 7) AS transaction_month,
        SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) AS total_debits
    FROM accounts a
    JOIN transactions t ON t.account_id = a.id
    WHERE t.transaction_date >= '2026-01-01'
      AND t.transaction_date < '2026-06-01'
    GROUP BY a.branch_id, SUBSTR(t.transaction_date, 1, 7)
),
complete AS (
    SELECT
        g.branch_id,
        g.transaction_month,
        ROUND(COALESCE(d.total_debits, 0), 2) AS total_debits
    FROM grid g
    LEFT JOIN debits d
      ON d.branch_id = g.branch_id
     AND d.transaction_month = g.transaction_month
),
with_previous AS (
    SELECT
        branch_id,
        transaction_month,
        total_debits,
        LAG(total_debits) OVER (
            PARTITION BY branch_id
            ORDER BY transaction_month
        ) AS previous_month_debits
    FROM complete
)
SELECT
    branch_id,
    transaction_month,
    total_debits,
    previous_month_debits,
    ROUND(total_debits - previous_month_debits, 2) AS variation
FROM with_previous
ORDER BY branch_id, transaction_month;

