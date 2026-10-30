SELECT
    external_reference,
    COUNT(*) AS row_count,
    MIN(id) AS first_id,
    MAX(id) AS last_id
FROM transactions
GROUP BY external_reference
HAVING COUNT(*) > 1
ORDER BY row_count DESC, external_reference;

