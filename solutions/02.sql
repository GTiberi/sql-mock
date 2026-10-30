SELECT
    b.id AS branch_id,
    b.name AS branch_name,
    COUNT(a.id) AS active_account_count
FROM branches b
JOIN accounts a
  ON a.branch_id = b.id
 AND a.status = 'active'
GROUP BY b.id, b.name
HAVING COUNT(a.id) >= 20
ORDER BY active_account_count DESC, branch_id;

