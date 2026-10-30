SELECT
    c.id AS customer_id,
    c.name AS customer_name,
    ROUND(SUM(t.amount), 2) AS total_debits
FROM customers c
JOIN accounts a ON a.customer_id = c.id
JOIN transactions t
  ON t.account_id = a.id
 AND t.transaction_type = 'debit'
GROUP BY c.id, c.name
HAVING SUM(t.amount) > (
    SELECT AVG(customer_total)
    FROM (
        SELECT SUM(t2.amount) AS customer_total
        FROM accounts a2
        JOIN transactions t2
          ON t2.account_id = a2.id
         AND t2.transaction_type = 'debit'
        GROUP BY a2.customer_id
    ) customer_totals
)
ORDER BY total_debits DESC, customer_id;

