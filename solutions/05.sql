WITH buckets AS (
    SELECT
        CASE
            WHEN amount < 50 THEN 'small'
            WHEN amount <= 200 THEN 'medium'
            ELSE 'large'
        END AS amount_bucket,
        amount
    FROM transactions
)
SELECT
    amount_bucket,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM buckets
GROUP BY amount_bucket
ORDER BY CASE amount_bucket
    WHEN 'small' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'large' THEN 3
END;

