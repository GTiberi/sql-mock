SELECT
    a.id AS account_id,
    a.customer_id,
    a.account_type,
    a.opened_date,
    a.status
FROM accounts a
WHERE a.status = 'active'
  AND a.opened_date < '2026-03-01'
ORDER BY a.opened_date, a.id;

