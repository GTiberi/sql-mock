from __future__ import annotations

import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import NamedTuple

import check
from setup_db import build_database


ROOT = Path(__file__).resolve().parents[1]


class Answer(NamedTuple):
    case: str
    label: str
    sql: str
    detail: str = ""


MONTHS_AND_DEBITS = """WITH transaction_month AS (
    SELECT '2026-01' AS transaction_month
    UNION ALL SELECT '2026-02'
    UNION ALL SELECT '2026-03'
    UNION ALL SELECT '2026-04'
    UNION ALL SELECT '2026-05'
),
grid AS (
    SELECT b.id AS branch_id, m.transaction_month
    FROM branches b
    CROSS JOIN transaction_month m
),
debits AS (
    SELECT
        a.branch_id,
        SUBSTR(t.transaction_date, 1, 7) AS transaction_month,
        SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) AS total_debits
    FROM accounts a
    JOIN transactions t ON t.account_id = a.id
    WHERE t.transaction_date >= '2026-01-01'
      AND t.transaction_date < '2026-06-01'
    GROUP BY a.branch_id, SUBSTR(t.transaction_date, 1, 7)
),
complete AS (
    SELECT
        g.branch_id,
        g.transaction_month,
        ROUND(COALESCE(d.total_debits, 0), 2) AS total_debits
    FROM grid g
    LEFT JOIN debits d
      ON d.branch_id = g.branch_id
     AND d.transaction_month = g.transaction_month
)"""

ACCOUNT_TOTALS = """WITH account_totals AS (
    SELECT
        a.branch_id,
        a.id AS account_id,
        a.customer_id,
        COUNT(t.id) AS transaction_count
    FROM accounts a
    LEFT JOIN transactions t ON t.account_id = a.id
    GROUP BY a.branch_id, a.id, a.customer_id
)"""

DENSE_RANK_ANSWER = ACCOUNT_TOTALS + """,
classes AS (
    SELECT
        branch_id,
        account_id,
        customer_id,
        transaction_count,
        DENSE_RANK() OVER (
            PARTITION BY branch_id
            ORDER BY transaction_count DESC
        ) AS account_rank
    FROM account_totals
)
SELECT branch_id, account_id, customer_id, transaction_count, account_rank
FROM classes
WHERE account_rank <= 2
ORDER BY branch_id, account_rank, account_id;"""

COHORTS_AND_SIZES = """WITH cohorts AS (
    SELECT id AS customer_id, SUBSTR(signup_date, 1, 7) AS cohort_month
    FROM customers
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM cohorts
    GROUP BY cohort_month
)"""


REJECTED_ON_RESULTS: tuple[Answer, ...] = (
    Answer(
        "01",
        "aucun filtre sur le status ni sur la date",
        """
        SELECT id, customer_id, account_type, opened_date, status
        FROM accounts
        ORDER BY id;
        """,
        "row-count diff",
    ),
    Answer(
        "01",
        "01.md: borne <= '2026-03-01' au lieu de <",
        """
        SELECT a.id AS account_id, a.customer_id, a.account_type,
               a.opened_date, a.status
        FROM accounts a
        WHERE a.status = 'active'
          AND a.opened_date <= '2026-03-01'
        ORDER BY a.opened_date, a.id;
        """,
        "row-count diff",
    ),
    Answer(
        "02",
        "02.md: trier le nom au lieu du volume",
        """
        SELECT b.id AS branch_id, b.name AS branch_name,
               COUNT(a.id) AS active_account_count
        FROM branches b
        JOIN accounts a
          ON a.branch_id = b.id
         AND a.status = 'active'
        GROUP BY b.id, b.name
        HAVING COUNT(a.id) >= 20
        ORDER BY branch_name;
        """,
        "row 1 differs",
    ),
    Answer(
        "02",
        "02.md: oublier le HAVING",
        """
        SELECT b.id AS branch_id, b.name AS branch_name,
               COUNT(a.id) AS active_account_count
        FROM branches b
        JOIN accounts a
          ON a.branch_id = b.id
         AND a.status = 'active'
        GROUP BY b.id, b.name
        ORDER BY active_account_count DESC, branch_id;
        """,
        "row-count diff",
    ),
    Answer(
        "03",
        "03.md: INNER JOIN au lieu de LEFT JOIN",
        """
        SELECT c.id, c.name
        FROM customers c
        JOIN accounts a ON a.customer_id = c.id
        ORDER BY c.id;
        """,
        "row-count diff",
    ),
    Answer(
        "03",
        "03.md: tester une colonne client contre NULL",
        """
        SELECT c.id AS customer_id, c.name AS customer_name
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.id
        WHERE c.id IS NULL
        ORDER BY c.id;
        """,
        "row-count diff",
    ),
    Answer(
        "03",
        "03.md: ne garder que les comptes actifs dans l'anti-join",
        """
        SELECT c.id AS customer_id, c.name AS customer_name
        FROM customers c
        LEFT JOIN accounts a
          ON a.customer_id = c.id
         AND a.status = 'active'
        WHERE a.id IS NULL
        ORDER BY c.id;
        """,
        "row-count diff",
    ),
    Answer(
        "04",
        "04.md: filtre debit dans le WHERE",
        """
        SELECT c.id AS customer_id, c.name AS customer_name,
               ROUND(COALESCE(SUM(t.amount), 0), 2) AS total_debits
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.id
        LEFT JOIN transactions t ON t.account_id = a.id
        WHERE t.transaction_type = 'debit'
        GROUP BY c.id, c.name
        ORDER BY total_debits DESC, customer_id;
        """,
        "row-count diff",
    ),
    Answer(
        "04",
        "04.md: retourner NULL au lieu de zero",
        """
        SELECT c.id AS customer_id, c.name AS customer_name,
               ROUND(SUM(t.amount), 2) AS total_debits
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.id
        LEFT JOIN transactions t
          ON t.account_id = a.id
         AND t.transaction_type = 'debit'
        GROUP BY c.id, c.name
        ORDER BY total_debits DESC, customer_id;
        """,
        "NULL",
    ),
    Answer(
        "05",
        "05.md: amount <= 50 dans le bucket small",
        """
        WITH buckets AS (
            SELECT
                CASE
                    WHEN amount <= 50 THEN 'small'
                    WHEN amount <= 200 THEN 'medium'
                    ELSE 'large'
                END AS amount_bucket,
                amount
            FROM transactions
        )
        SELECT amount_bucket, COUNT(*) AS transaction_count,
               ROUND(SUM(amount), 2) AS total_amount
        FROM buckets
        GROUP BY amount_bucket
        ORDER BY CASE amount_bucket
            WHEN 'small' THEN 1 WHEN 'medium' THEN 2 WHEN 'large' THEN 3
        END;
        """,
        "small",
    ),
    Answer(
        "05",
        "cases/05: medium < 200 et large >= 200",
        """
        WITH buckets AS (
            SELECT
                CASE
                    WHEN amount < 50 THEN 'small'
                    WHEN amount < 200 THEN 'medium'
                    ELSE 'large'
                END AS amount_bucket,
                amount
            FROM transactions
        )
        SELECT amount_bucket, COUNT(*) AS transaction_count,
               ROUND(SUM(amount), 2) AS total_amount
        FROM buckets
        GROUP BY amount_bucket
        ORDER BY CASE amount_bucket
            WHEN 'small' THEN 1 WHEN 'medium' THEN 2 WHEN 'large' THEN 3
        END;
        """,
        "medium",
    ),
    Answer(
        "05",
        "05.md: oublier le GROUP BY de l'expression calculee",
        """
        SELECT
            CASE
                WHEN amount < 50 THEN 'small'
                WHEN amount <= 200 THEN 'medium'
                ELSE 'large'
            END AS amount_bucket,
            COUNT(*) AS transaction_count,
            ROUND(SUM(amount), 2) AS total_amount
        FROM transactions;
        """,
        "row-count diff",
    ),
    Answer(
        "05",
        "05.md: trier les tranches alphabetiquement",
        """
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
        SELECT amount_bucket, COUNT(*) AS transaction_count,
               ROUND(SUM(amount), 2) AS total_amount
        FROM buckets
        GROUP BY amount_bucket
        ORDER BY amount_bucket;
        """,
        "row 1 differs",
    ),
    Answer(
        "06",
        "06.md: grouper par mois sans l'annee",
        """
        SELECT SUBSTR(transaction_date, 6, 2) AS transaction_month, transaction_type,
               COUNT(*) AS transaction_count, ROUND(SUM(amount), 2) AS total_amount
        FROM transactions
        WHERE transaction_date >= '2026-01-01'
          AND transaction_date < '2026-06-01'
        GROUP BY SUBSTR(transaction_date, 6, 2), transaction_type
        ORDER BY transaction_month, CASE transaction_type WHEN 'credit' THEN 1 ELSE 2 END;
        """,
        "row 1 differs",
    ),
    Answer(
        "07",
        "07.md: moyenne des montants ligne par ligne",
        """
        SELECT c.id AS customer_id, c.name AS customer_name,
               ROUND(SUM(t.amount), 2) AS total_debits
        FROM customers c
        JOIN accounts a ON a.customer_id = c.id
        JOIN transactions t
          ON t.account_id = a.id
         AND t.transaction_type = 'debit'
        GROUP BY c.id, c.name
        HAVING SUM(t.amount) > (
            SELECT AVG(amount) FROM transactions WHERE transaction_type = 'debit'
        )
        ORDER BY total_debits DESC, customer_id;
        """,
        "row-count diff",
    ),
    Answer(
        "07",
        "07.md: inclure les clients sans debit dans la moyenne",
        """
        SELECT c.id AS customer_id, c.name AS customer_name,
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
                SELECT COALESCE(SUM(CASE WHEN t2.transaction_type = 'debit'
                                         THEN t2.amount ELSE 0 END), 0) AS customer_total
                FROM customers c2
                LEFT JOIN accounts a2 ON a2.customer_id = c2.id
                LEFT JOIN transactions t2 ON t2.account_id = a2.id
                GROUP BY c2.id
            ) customer_totals
        )
        ORDER BY total_debits DESC, customer_id;
        """,
        "row-count diff",
    ),
    Answer(
        "07",
        "07.md: comparer dans le WHERE avant d'agreger",
        """
        SELECT c.id AS customer_id, c.name AS customer_name,
               ROUND(SUM(t.amount), 2) AS total_debits
        FROM customers c
        JOIN accounts a ON a.customer_id = c.id
        JOIN transactions t
          ON t.account_id = a.id
         AND t.transaction_type = 'debit'
        WHERE t.amount > (
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
        GROUP BY c.id, c.name
        ORDER BY total_debits DESC, customer_id;
        """,
        "row-count diff",
    ),
    Answer(
        "08",
        "08.md: garder seulement les mois presents dans transactions",
        """
        SELECT
            a.branch_id,
            b.name AS branch_name,
            SUBSTR(t.transaction_date, 1, 7) AS transaction_month,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit'
                           THEN t.amount ELSE 0 END), 2) AS total_credits,
            ROUND(SUM(CASE WHEN t.transaction_type = 'debit'
                           THEN t.amount ELSE 0 END), 2) AS total_debits,
            ROUND(SUM(CASE WHEN t.transaction_type = 'credit'
                           THEN t.amount ELSE -t.amount END), 2) AS net
        FROM accounts a
        JOIN branches b ON b.id = a.branch_id
        JOIN transactions t ON t.account_id = a.id
        WHERE t.transaction_date >= '2026-01-01'
          AND t.transaction_date < '2026-06-01'
        GROUP BY a.branch_id, b.name, transaction_month
        ORDER BY a.branch_id, transaction_month;
        """,
        "row-count diff",
    ),
    Answer(
        "08",
        "08.md: additionner les debits au lieu de les soustraire",
        """
        WITH transaction_month AS (
            SELECT '2026-01' AS transaction_month
            UNION ALL SELECT '2026-02'
            UNION ALL SELECT '2026-03'
            UNION ALL SELECT '2026-04'
            UNION ALL SELECT '2026-05'
        ),
        grid AS (
            SELECT b.id AS branch_id, b.name AS branch_name, m.transaction_month
            FROM branches b
            CROSS JOIN transaction_month m
        ),
        flows AS (
            SELECT
                a.branch_id,
                SUBSTR(t.transaction_date, 1, 7) AS transaction_month,
                SUM(CASE WHEN t.transaction_type = 'credit'
                         THEN t.amount ELSE 0 END) AS credits,
                SUM(CASE WHEN t.transaction_type = 'debit'
                         THEN t.amount ELSE 0 END) AS debits
            FROM accounts a
            JOIN transactions t ON t.account_id = a.id
            WHERE t.transaction_date >= '2026-01-01'
              AND t.transaction_date < '2026-06-01'
            GROUP BY a.branch_id, SUBSTR(t.transaction_date, 1, 7)
        )
        SELECT
            g.branch_id,
            g.branch_name,
            g.transaction_month,
            ROUND(COALESCE(f.credits, 0), 2) AS total_credits,
            ROUND(COALESCE(f.debits, 0), 2) AS total_debits,
            ROUND(COALESCE(f.credits, 0) + COALESCE(f.debits, 0), 2) AS net
        FROM grid g
        LEFT JOIN flows f
          ON f.branch_id = g.branch_id
         AND f.transaction_month = g.transaction_month
        ORDER BY g.branch_id, g.transaction_month;
        """,
        "row 1 differs",
    ),
    Answer(
        "09",
        "09.md: ROW_NUMBER() supprime les ex aequo",
        ACCOUNT_TOTALS + """,
        classes AS (
            SELECT branch_id, account_id, customer_id, transaction_count,
                   ROW_NUMBER() OVER (
                       PARTITION BY branch_id ORDER BY transaction_count DESC
                   ) AS account_rank
            FROM account_totals
        )
        SELECT branch_id, account_id, customer_id, transaction_count, account_rank
        FROM classes
        WHERE account_rank <= 2
        ORDER BY branch_id, account_rank, account_id;
        """,
        "row-count diff",
    ),
    Answer(
        "09",
        "09.md: classer tous les comptes sans PARTITION BY",
        ACCOUNT_TOTALS + """,
        classes AS (
            SELECT branch_id, account_id, customer_id, transaction_count,
                   RANK() OVER (ORDER BY transaction_count DESC) AS account_rank
            FROM account_totals
        )
        SELECT branch_id, account_id, customer_id, transaction_count, account_rank
        FROM classes
        WHERE account_rank <= 2
        ORDER BY branch_id, account_rank, account_id;
        """,
        "row-count diff",
    ),
    Answer(
        "09",
        "09.md: grouper par client au lieu de compte",
        """
        WITH customer_totals AS (
            SELECT a.branch_id, MIN(a.id) AS account_id, a.customer_id,
                   COUNT(t.id) AS transaction_count
            FROM accounts a
            LEFT JOIN transactions t ON t.account_id = a.id
            GROUP BY a.branch_id, a.customer_id
        ),
        classes AS (
            SELECT branch_id, account_id, customer_id, transaction_count,
                   RANK() OVER (
                       PARTITION BY branch_id ORDER BY transaction_count DESC
                   ) AS account_rank
            FROM customer_totals
        )
        SELECT branch_id, account_id, customer_id, transaction_count, account_rank
        FROM classes
        WHERE account_rank <= 2
        ORDER BY branch_id, account_rank, account_id;
        """,
        "row-count diff",
    ),
    Answer(
        "09",
        "09.md: DENSE_RANK ne donne pas le meme resultat",
        DENSE_RANK_ANSWER,
        "row-count diff",
    ),
    Answer(
        "10",
        "10.md: appliquer LAG avant de completer les mois",
        """
        WITH debits AS (
            SELECT
                a.branch_id,
                SUBSTR(t.transaction_date, 1, 7) AS transaction_month,
                SUM(CASE WHEN t.transaction_type = 'debit'
                         THEN t.amount ELSE 0 END) AS total_debits
            FROM accounts a
            JOIN transactions t ON t.account_id = a.id
            WHERE t.transaction_date >= '2026-01-01'
              AND t.transaction_date < '2026-06-01'
            GROUP BY a.branch_id, transaction_month
        )
        SELECT
            branch_id,
            transaction_month,
            ROUND(total_debits, 2) AS total_debits,
            ROUND(LAG(total_debits) OVER (
                PARTITION BY branch_id ORDER BY transaction_month
            ), 2) AS previous_month_debits,
            ROUND(total_debits - LAG(total_debits) OVER (
                PARTITION BY branch_id ORDER BY transaction_month
            ), 2) AS variation
        FROM debits
        ORDER BY branch_id, transaction_month;
        """,
        "row-count diff",
    ),
    Answer(
        "10",
        "10.md: remplacer le premier NULL par zero",
        MONTHS_AND_DEBITS + """,
        with_previous AS (
            SELECT branch_id, transaction_month, total_debits,
                   COALESCE(LAG(total_debits) OVER (
                       PARTITION BY branch_id ORDER BY transaction_month
                   ), 0) AS previous_month_debits
            FROM complete
        )
        SELECT branch_id, transaction_month, total_debits, previous_month_debits,
               ROUND(total_debits - previous_month_debits, 2) AS variation
        FROM with_previous
        ORDER BY branch_id, transaction_month;
        """,
        "NULL",
    ),
    Answer(
        "11",
        "11.md: GROUP BY account_id supprime le detail",
        """
        SELECT t.account_id, MAX(t.transaction_date) AS transaction_date,
               MAX(t.id) AS transaction_id,
               ROUND(SUM(CASE WHEN t.transaction_type = 'credit'
                              THEN t.amount ELSE -t.amount END), 2) AS signed_running_total
        FROM transactions t
        GROUP BY t.account_id
        ORDER BY t.account_id;
        """,
        "row-count diff",
    ),
    Answer(
        "11",
        "11.md: soustraire aussi les credits",
        """
        SELECT t.account_id, t.transaction_date, t.id AS transaction_id,
               ROUND(SUM(-t.amount) OVER (
                   PARTITION BY t.account_id
                   ORDER BY t.transaction_date, t.id
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ), 2) AS signed_running_total
        FROM transactions t
        ORDER BY t.account_id, t.transaction_date, t.id;
        """,
        "differs",
    ),
    Answer(
        "12",
        "12.md: un DISTINCT qui masque le probleme",
        """
        SELECT external_reference, COUNT(DISTINCT external_reference) AS row_count,
               MIN(id) AS first_id, MAX(id) AS last_id
        FROM transactions
        GROUP BY external_reference
        HAVING COUNT(DISTINCT external_reference) > 1
        ORDER BY row_count DESC, external_reference;
        """,
        "row-count diff",
    ),
    Answer(
        "12",
        "12.md: dedupliquer sur le montant",
        """
        SELECT MIN(external_reference) AS external_reference, COUNT(*) AS row_count,
               MIN(id) AS first_id, MAX(id) AS last_id
        FROM transactions
        GROUP BY amount
        HAVING COUNT(*) > 1
        ORDER BY row_count DESC, external_reference;
        """,
        "row-count diff",
    ),
    Answer(
        "13",
        "13.md: COUNT(*) au lieu de COUNT(DISTINCT customer_id)",
        COHORTS_AND_SIZES + """
        SELECT coh.cohort_month, SUBSTR(t.transaction_date, 1, 7) AS activity_month,
               cohort_sizes.cohort_customers, COUNT(*) AS active_customers,
               ROUND(100.0 * COUNT(*) / cohort_sizes.cohort_customers, 2) AS retention_rate
        FROM transactions t
        JOIN accounts a ON a.id = t.account_id
        JOIN cohorts coh ON coh.customer_id = a.customer_id
        JOIN cohort_sizes ON cohort_sizes.cohort_month = coh.cohort_month
        WHERE t.transaction_date >= '2026-01-01'
          AND t.transaction_date < '2026-06-01'
          AND SUBSTR(t.transaction_date, 1, 7) >= coh.cohort_month
        GROUP BY coh.cohort_month, SUBSTR(t.transaction_date, 1, 7),
                 cohort_sizes.cohort_customers
        ORDER BY coh.cohort_month, activity_month;
        """,
        "differs",
    ),
    Answer(
        "13",
        "13.md: cohorte basee sur la premiere transaction",
        """
        WITH cohorts AS (
            SELECT a.customer_id, MIN(SUBSTR(t.transaction_date, 1, 7)) AS cohort_month
            FROM accounts a
            JOIN transactions t ON t.account_id = a.id
            GROUP BY a.customer_id
        ),
        cohort_sizes AS (
            SELECT cohort_month, COUNT(*) AS cohort_customers
            FROM cohorts
            GROUP BY cohort_month
        ),
        activity AS (
            SELECT c.id AS customer_id, SUBSTR(t.transaction_date, 1, 7) AS activity_month
            FROM customers c
            JOIN accounts a ON a.customer_id = c.id
            JOIN transactions t ON t.account_id = a.id
            WHERE t.transaction_date >= '2026-01-01'
              AND t.transaction_date < '2026-06-01'
            GROUP BY c.id, SUBSTR(t.transaction_date, 1, 7)
        )
        SELECT coh.cohort_month, act.activity_month, cohort_sizes.cohort_customers,
               COUNT(DISTINCT act.customer_id) AS active_customers,
               ROUND(100.0 * COUNT(DISTINCT act.customer_id) / cohort_sizes.cohort_customers,
                     2) AS retention_rate
        FROM activity act
        JOIN cohorts coh ON coh.customer_id = act.customer_id
        JOIN cohort_sizes ON cohort_sizes.cohort_month = coh.cohort_month
        WHERE act.activity_month >= coh.cohort_month
        GROUP BY coh.cohort_month, act.activity_month, cohort_sizes.cohort_customers
        ORDER BY coh.cohort_month, act.activity_month;
        """,
        "row-count diff",
    ),
    Answer(
        "14",
        "12.md: compter les lignes dupliquees au lieu des groupes",
        """
        WITH checks AS (
            SELECT 'transactions_after_closure' AS check_name, COUNT(*) AS issue_count
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            WHERE a.closed_date IS NOT NULL
              AND t.transaction_date > a.closed_date

            UNION ALL

            SELECT 'duplicate_references', COUNT(*)
            FROM transactions
            WHERE external_reference IN (
                SELECT external_reference
                FROM transactions
                GROUP BY external_reference
                HAVING COUNT(*) > 1
            )

            UNION ALL

            SELECT 'missing_categories', COUNT(*)
            FROM transactions WHERE category IS NULL

            UNION ALL

            SELECT 'invalid_amounts', COUNT(*)
            FROM transactions WHERE amount <= 0
        )
        SELECT check_name, issue_count
        FROM checks
        ORDER BY CASE check_name
            WHEN 'transactions_after_closure' THEN 1
            WHEN 'duplicate_references' THEN 2
            WHEN 'missing_categories' THEN 3
            WHEN 'invalid_amounts' THEN 4
        END;
        """,
        "differs",
    ),
    Answer(
        "14",
        "14.md: sous-requete de doublons sans son HAVING",
        """
        WITH checks AS (
            SELECT 'transactions_after_closure' AS check_name, COUNT(*) AS issue_count
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            WHERE a.closed_date IS NOT NULL
              AND t.transaction_date > a.closed_date

            UNION ALL

            SELECT 'duplicate_references', COUNT(*)
            FROM (
                SELECT external_reference
                FROM transactions
                GROUP BY external_reference
            ) duplicate_references

            UNION ALL

            SELECT 'missing_categories', COUNT(*)
            FROM transactions WHERE category IS NULL

            UNION ALL

            SELECT 'invalid_amounts', COUNT(*)
            FROM transactions WHERE amount <= 0
        )
        SELECT check_name, issue_count
        FROM checks
        ORDER BY CASE check_name
            WHEN 'transactions_after_closure' THEN 1
            WHEN 'duplicate_references' THEN 2
            WHEN 'missing_categories' THEN 3
            WHEN 'invalid_amounts' THEN 4
        END;
        """,
        "differs",
    ),
    Answer(
        "13",
        "13.md: oublier d'arrondir le taux de retention",
        """
        WITH cohorts AS (
            SELECT id AS customer_id, SUBSTR(signup_date, 1, 7) AS cohort_month
            FROM customers
        ),
        cohort_sizes AS (
            SELECT cohort_month, COUNT(*) AS cohort_customers
            FROM cohorts
            GROUP BY cohort_month
        ),
        activity AS (
            SELECT c.id AS customer_id, SUBSTR(t.transaction_date, 1, 7) AS activity_month
            FROM customers c
            JOIN accounts a ON a.customer_id = c.id
            JOIN transactions t ON t.account_id = a.id
            WHERE t.transaction_date >= '2026-01-01'
              AND t.transaction_date < '2026-06-01'
            GROUP BY c.id, SUBSTR(t.transaction_date, 1, 7)
        )
        SELECT
            coh.cohort_month,
            act.activity_month,
            cohort_sizes.cohort_customers,
            COUNT(DISTINCT act.customer_id) AS active_customers,
            100.0 * COUNT(DISTINCT act.customer_id) / cohort_sizes.cohort_customers
                AS retention_rate
        FROM activity act
        JOIN cohorts coh ON coh.customer_id = act.customer_id
        JOIN cohort_sizes ON cohort_sizes.cohort_month = coh.cohort_month
        WHERE act.activity_month >= coh.cohort_month
        GROUP BY coh.cohort_month, act.activity_month, cohort_sizes.cohort_customers
        ORDER BY coh.cohort_month, act.activity_month;
        """,
        "differs",
    ),
)


REJECTED_WITH_SQL_ERROR: tuple[Answer, ...] = (
    Answer(
        "01",
        "deux requetes dans le meme fichier",
        """
        SELECT 1;
        SELECT 2;
        """,
    ),
    Answer(
        "02",
        "02.md: COUNT(a.id) >= 20 dans le WHERE",
        """
        SELECT b.id AS branch_id, b.name AS branch_name,
               COUNT(a.id) AS active_account_count
        FROM branches b
        JOIN accounts a
          ON a.branch_id = b.id
         AND a.status = 'active'
        WHERE COUNT(a.id) >= 20
        GROUP BY b.id, b.name
        ORDER BY active_account_count DESC, branch_id;
        """,
    ),
    Answer(
        "10",
        "10.md: reutiliser un alias du meme SELECT",
        MONTHS_AND_DEBITS + """
        SELECT branch_id, transaction_month, total_debits,
               LAG(total_debits) OVER (
                   PARTITION BY branch_id ORDER BY transaction_month
               ) AS previous_month_debits,
               ROUND(total_debits - previous_month_debits, 2) AS variation
        FROM complete
        ORDER BY branch_id, transaction_month;
        """,
    ),
)


ACCEPTED_ALTERNATIVES: tuple[Answer, ...] = (
    Answer(
        "02",
        "02.md: LEFT JOIN avec le status dans le ON",
        """
        SELECT b.id AS branch_id, b.name AS branch_name,
               COUNT(a.id) AS active_account_count
        FROM branches b
        LEFT JOIN accounts a
          ON a.branch_id = b.id
         AND a.status = 'active'
        GROUP BY b.id, b.name
        HAVING COUNT(a.id) >= 20
        ORDER BY active_account_count DESC, branch_id;
        """,
    ),
    Answer(
        "03",
        "03.md: NOT EXISTS au lieu de l'anti-join",
        """
        SELECT c.id AS customer_id, c.name AS customer_name
        FROM customers c
        WHERE NOT EXISTS (
            SELECT 1 FROM accounts a WHERE a.customer_id = c.id
        )
        ORDER BY c.id;
        """,
    ),
    Answer(
        "04",
        "04.md: condition dans le ON puis COALESCE(SUM(...), 0)",
        """
        SELECT c.id AS customer_id, c.name AS customer_name,
               ROUND(COALESCE(SUM(t.amount), 0), 2) AS total_debits
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.id
        LEFT JOIN transactions t
          ON t.account_id = a.id
         AND t.transaction_type = 'debit'
        GROUP BY c.id, c.name
        ORDER BY total_debits DESC, customer_id;
        """,
    ),
    Answer(
        "05",
        "05.md: le CASE repete dans le SELECT et le GROUP BY",
        """
        SELECT
            CASE
                WHEN amount < 50 THEN 'small'
                WHEN amount <= 200 THEN 'medium'
                ELSE 'large'
            END AS amount_bucket,
            COUNT(*) AS transaction_count,
            ROUND(SUM(amount), 2) AS total_amount
        FROM transactions
        GROUP BY
            CASE
                WHEN amount < 50 THEN 'small'
                WHEN amount <= 200 THEN 'medium'
                ELSE 'large'
            END
        ORDER BY CASE
            WHEN amount < 50 THEN 1
            WHEN amount <= 200 THEN 2
            ELSE 3
        END;
        """,
    ),
    Answer(
        "07",
        "07.md: deux CTE, customer_totals et average_total",
        """
        WITH customer_totals AS (
            SELECT a.customer_id, SUM(t.amount) AS customer_total
            FROM accounts a
            JOIN transactions t
              ON t.account_id = a.id
             AND t.transaction_type = 'debit'
            GROUP BY a.customer_id
        ),
        average_total AS (
            SELECT AVG(customer_total) AS average_customer_total FROM customer_totals
        )
        SELECT c.id AS customer_id, c.name AS customer_name,
               ROUND(tc.customer_total, 2) AS total_debits
        FROM customer_totals tc
        JOIN customers c ON c.id = tc.customer_id
        CROSS JOIN average_total m
        WHERE tc.customer_total > m.average_customer_total
        ORDER BY total_debits DESC, customer_id;
        """,
    ),
    Answer(
        "11",
        "11.md: une CTE signed_amount avant la fenetre",
        """
        WITH movements AS (
            SELECT account_id, transaction_date, id AS transaction_id,
                   CASE WHEN transaction_type = 'credit' THEN amount
                        ELSE -amount END AS signed_amount
            FROM transactions
        )
        SELECT account_id, transaction_date, transaction_id,
               ROUND(SUM(signed_amount) OVER (
                   PARTITION BY account_id
                   ORDER BY transaction_date, transaction_id
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ), 2) AS signed_running_total
        FROM movements
        ORDER BY account_id, transaction_date, transaction_id;
        """,
    ),
)


class SqlKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.temp_dir.name) / "practice.db"
        build_database(cls.db_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def run_answer(self, answer: Answer) -> check.CheckResult:
        path = Path(self.temp_dir.name) / f"answer-{answer.case}.sql"
        path.write_text(answer.sql, encoding="utf-8")
        return check.check_case(answer.case, path, self.db_path)

    def query(self, sql: str) -> list[tuple]:
        connection = check.connect_readonly(self.db_path)
        try:
            return connection.execute(sql.strip().rstrip(";")).fetchall()
        finally:
            connection.close()

    def test_every_reference_solution_is_accepted(self) -> None:
        for solution_path in sorted((ROOT / "solutions").glob("[0-9][0-9].sql")):
            with self.subTest(case=solution_path.stem):
                result = check.check_case(
                    solution_path.stem, solution_path, self.db_path
                )
                self.assertTrue(result.ok, result.message)

    def test_documented_mistakes_are_rejected_on_results(self) -> None:
        for answer in REJECTED_ON_RESULTS:
            with self.subTest(case=answer.case, mistake=answer.label):
                self.assertTrue(answer.detail, "expected detail is required here")
                result = self.run_answer(answer)
                self.assertFalse(result.ok, result.message)
                self.assertNotIn("SQL error", result.message)
                self.assertIn(answer.detail, result.message)

    def test_documented_mistakes_are_rejected_with_a_sql_error(self) -> None:
        for answer in REJECTED_WITH_SQL_ERROR:
            with self.subTest(case=answer.case, mistake=answer.label):
                result = self.run_answer(answer)
                self.assertFalse(result.ok, result.message)
                self.assertIn("SQL error", result.message)

    def test_documented_alternatives_are_accepted(self) -> None:
        for answer in ACCEPTED_ALTERNATIVES:
            with self.subTest(case=answer.case, alternative=answer.label):
                result = self.run_answer(answer)
                self.assertTrue(result.ok, result.message)

    def test_an_unknown_case_number_stays_friendly(self) -> None:
        completed = subprocess.run(
            [sys.executable, "check.py", "99", "solutions/01.sql"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stderr)
        self.assertIn("Pas encore: la case 99 n'existe pas", completed.stdout)

    @unittest.skipUnless(os.name == "posix", "needs a POSIX shell and symlinks")
    def test_the_recovery_command_runs_on_a_python3_only_machine(self) -> None:
        completed = subprocess.run(
            [sys.executable, "check.py", "99", "solutions/01.sql"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        printed = re.search(r"`([^`]+)`", completed.stdout)
        self.assertIsNotNone(printed, completed.stdout)
        command = printed.group(1)

        bin_dir = Path(self.temp_dir.name) / "python3-only-bin"
        bin_dir.mkdir()
        os.symlink(sys.executable, bin_dir / "python3")

        recovery = subprocess.run(
            command,
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            env={"PATH": str(bin_dir)},
        )
        self.assertEqual(0, recovery.returncode, recovery.stderr)
        self.assertIn("01", recovery.stdout)
        self.assertIn("14", recovery.stdout)

    def test_an_answer_file_that_is_not_utf8_blames_the_answer_file(self) -> None:
        path = Path(self.temp_dir.name) / "answer-cp1252.sql"
        path.write_bytes("-- Premi\u00e8re tentative\nSELECT 1;".encode("cp1252"))
        result = check.check_case("01", path, self.db_path)
        self.assertFalse(result.ok)
        self.assertIn("answer-cp1252.sql", result.message)
        self.assertIn("UTF-8", result.message)

    def test_a_database_without_the_kit_tables_blames_the_kit(self) -> None:
        empty_db = Path(self.temp_dir.name) / "sans-tables.db"
        connection = sqlite3.connect(empty_db)
        try:
            connection.execute("CREATE TABLE inutile (x INTEGER)")
            connection.commit()
        finally:
            connection.close()
        answer = Path(self.temp_dir.name) / "answer-valide.sql"
        answer.write_text("SELECT 1, 2, 3, 4, 5;", encoding="utf-8")
        result = check.check_case("01", answer, empty_db)
        self.assertFalse(result.ok)
        self.assertIn("01.sql", result.message)
        self.assertIn("setup_db.py", result.message)
        self.assertNotIn("answer-valide.sql", result.message)

    def test_a_case_file_without_frontmatter_names_the_file(self) -> None:
        broken = Path(self.temp_dir.name) / "99-casse.md"
        broken.write_text(
            "# Pas de frontmatter\n\n<summary>Hints</summary>\nrien\n</details>\n",
            encoding="utf-8",
        )
        with self.assertRaises(ValueError) as raised:
            check.parse_case(broken)
        self.assertIn("99-casse.md", str(raised.exception))
        for key in ("case", "title", "expected_columns"):
            self.assertIn(key, str(raised.exception))

    def test_a_case_file_without_hints_names_the_file(self) -> None:
        broken = Path(self.temp_dir.name) / "98-sans-hints.md"
        broken.write_text(
            '---\ncase: 98\ntitle: "Sans hints"\nexpected_columns: a\n---\n# Sans hints\n',
            encoding="utf-8",
        )
        with self.assertRaises(ValueError) as raised:
            check.parse_case(broken)
        self.assertIn("98-sans-hints.md", str(raised.exception))
        self.assertIn("Hints", str(raised.exception))

    def test_every_shipped_case_file_parses_strictly(self) -> None:
        case_paths = sorted((ROOT / "cases").glob("[0-9][0-9]-*.md"))
        self.assertTrue(case_paths)
        for case_path in case_paths:
            with self.subTest(case=case_path.stem):
                config = check.parse_case(case_path)
                self.assertEqual(case_path.stem[:2], config.case_id)
                self.assertTrue(config.title)
                self.assertTrue(config.expected_columns)
                self.assertTrue(config.hint)

    def test_seed_pins_both_bucket_boundaries_of_case_05(self) -> None:
        small_medium, medium_large = self.query(
            """
            SELECT SUM(CASE WHEN amount = 50.0 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN amount = 200.0 THEN 1 ELSE 0 END)
            FROM transactions
            """
        )[0]
        self.assertGreater(small_medium, 0)
        self.assertGreater(medium_large, 0)

    def test_case_09_notes_match_the_data(self) -> None:
        reference = (ROOT / "solutions" / "09.sql").read_text(encoding="utf-8")
        self.assertEqual(22, len(self.query(reference)))
        self.assertEqual(31, len(self.query(DENSE_RANK_ANSWER)))
        self.assertEqual(
            [(38, 6)],
            self.query(
                """
                SELECT transaction_count, COUNT(*)
                FROM (
                    SELECT COUNT(t.id) AS transaction_count
                    FROM accounts a
                    LEFT JOIN transactions t ON t.account_id = a.id
                    WHERE a.branch_id = 1
                    GROUP BY a.id
                )
                GROUP BY transaction_count
                ORDER BY transaction_count DESC
                LIMIT 1
                """
            ),
        )


if __name__ == "__main__":
    unittest.main()
