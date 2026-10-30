WITH checks AS (
    SELECT
        'transactions_after_closure' AS check_name,
        COUNT(*) AS issue_count
    FROM transactions t
    JOIN accounts a ON a.id = t.account_id
    WHERE a.closed_date IS NOT NULL
      AND t.transaction_date > a.closed_date

    UNION ALL

    SELECT
        'duplicate_references',
        COUNT(*)
    FROM (
        SELECT external_reference
        FROM transactions
        GROUP BY external_reference
        HAVING COUNT(*) > 1
    ) duplicate_references

    UNION ALL

    SELECT 'missing_categories', COUNT(*)
    FROM transactions
    WHERE category IS NULL

    UNION ALL

    SELECT 'invalid_amounts', COUNT(*)
    FROM transactions
    WHERE amount <= 0
)
SELECT check_name, issue_count
FROM checks
ORDER BY CASE check_name
    WHEN 'transactions_after_closure' THEN 1
    WHEN 'duplicate_references' THEN 2
    WHEN 'missing_categories' THEN 3
    WHEN 'invalid_amounts' THEN 4
END;

