WITH account_totals AS (
    SELECT
        a.branch_id,
        a.id AS account_id,
        a.customer_id,
        COUNT(t.id) AS transaction_count
    FROM accounts a
    LEFT JOIN transactions t ON t.account_id = a.id
    GROUP BY a.branch_id, a.id, a.customer_id
),
classes AS (
    SELECT
        branch_id,
        account_id,
        customer_id,
        transaction_count,
        RANK() OVER (
            PARTITION BY branch_id
            ORDER BY transaction_count DESC
        ) AS account_rank
    FROM account_totals
)
SELECT
    branch_id,
    account_id,
    customer_id,
    transaction_count,
    account_rank
FROM classes
WHERE account_rank <= 2
ORDER BY branch_id, account_rank, account_id;

