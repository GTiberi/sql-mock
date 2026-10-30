SELECT
    t.account_id,
    t.transaction_date,
    t.id AS transaction_id,
    ROUND(
        SUM(
            CASE
                WHEN t.transaction_type = 'credit' THEN t.amount
                ELSE -t.amount
            END
        ) OVER (
            PARTITION BY t.account_id
            ORDER BY t.transaction_date, t.id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS signed_running_total
FROM transactions t
ORDER BY t.account_id, t.transaction_date, t.id;

