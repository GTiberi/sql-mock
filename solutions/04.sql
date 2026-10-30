SELECT
    c.id AS customer_id,
    c.name AS customer_name,
    ROUND(
        COALESCE(
            SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END),
            0
        ),
        2
    ) AS total_debits
FROM customers c
LEFT JOIN accounts a ON a.customer_id = c.id
LEFT JOIN transactions t ON t.account_id = a.id
GROUP BY c.id, c.name
ORDER BY total_debits DESC, customer_id;

