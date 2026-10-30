SELECT
    SUBSTR(transaction_date, 1, 7) AS transaction_month,
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM transactions
WHERE transaction_date >= '2026-01-01'
  AND transaction_date < '2026-06-01'
GROUP BY SUBSTR(transaction_date, 1, 7), transaction_type
ORDER BY transaction_month,
    CASE transaction_type WHEN 'credit' THEN 1 ELSE 2 END;

