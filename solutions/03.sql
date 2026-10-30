SELECT
    c.id AS customer_id,
    c.name AS customer_name
FROM customers c
LEFT JOIN accounts a ON a.customer_id = c.id
WHERE a.id IS NULL
ORDER BY c.id;

