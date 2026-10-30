WITH transaction_month AS (
    SELECT '2026-01' AS transaction_month
    UNION ALL SELECT '2026-02'
    UNION ALL SELECT '2026-03'
    UNION ALL SELECT '2026-04'
    UNION ALL SELECT '2026-05'
),
grid AS (
    SELECT b.id AS branch_id, b.name AS branch_name, m.transaction_month
    FROM branches b
    CROSS JOIN transaction_month m
),
flows AS (
    SELECT
        a.branch_id,
        SUBSTR(t.transaction_date, 1, 7) AS transaction_month,
        SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END) AS credits,
        SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) AS debits
    FROM accounts a
    JOIN transactions t ON t.account_id = a.id
    WHERE t.transaction_date >= '2026-01-01'
      AND t.transaction_date < '2026-06-01'
    GROUP BY a.branch_id, SUBSTR(t.transaction_date, 1, 7)
)
SELECT
    g.branch_id,
    g.branch_name,
    g.transaction_month,
    ROUND(COALESCE(f.credits, 0), 2) AS total_credits,
    ROUND(COALESCE(f.debits, 0), 2) AS total_debits,
    ROUND(COALESCE(f.credits, 0) - COALESCE(f.debits, 0), 2) AS net
FROM grid g
LEFT JOIN flows f
  ON f.branch_id = g.branch_id
 AND f.transaction_month = g.transaction_month
ORDER BY g.branch_id, g.transaction_month;

