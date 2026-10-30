#!/usr/bin/env python3
"""Build the deterministic fictional bank database used by the exercises."""

from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "data" / "schema.sql"
DEFAULT_DB = ROOT / "practice.db"
SEED = 20261029
FIRST_DAY = date(2026, 1, 1)
LAST_DAY = date(2026, 5, 31)
NEW_BRANCH_ID = 5
NEW_BRANCH_OPENING = date(2026, 3, 1)
SMALL_BUCKET_LIMIT = 50.00
MEDIUM_BUCKET_LIMIT = 200.00


def iso_day(value: date) -> str:
    return value.isoformat()


def random_day(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def build_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    rng = random.Random(SEED)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA.read_text(encoding="utf-8"))

    branches = [
        (1, "Centre-ville", "Montreal", "Quebec"),
        (2, "Vieux-Port", "Quebec", "Quebec"),
        (3, "Riviere-des-Prairies", "Laval", "Quebec"),
        (4, "Jardin-des-Neiges", "Sherbrooke", "Quebec"),
        (5, "Lac-des-Pins", "Gatineau", "Outaouais"),
    ]
    connection.executemany(
        "INSERT INTO branches (id, name, city, region) VALUES (?, ?, ?, ?)",
        branches,
    )

    first_names = [
        "Ariane", "Benoit", "Camille", "Diane", "Eli", "Fatima", "Gabriel",
        "Hugo", "Ines", "Jade", "Karim", "Lea", "Malik", "Nadia", "Olivier",
        "Paul", "Rania", "Samuel", "Tania", "Victor",
    ]
    last_names = [
        "Beaulieu", "Caron", "Desjardins", "Fortin", "Gagnon", "Hebert",
        "Lachance", "Morin", "Nguyen", "Pelletier", "Roy", "Simard",
        "Tremblay", "Vaillancourt",
    ]
    cities = ["Montreal", "Quebec", "Laval", "Sherbrooke", "Gatineau"]
    customers = []
    for customer_id in range(1, 241):
        birth = random_day(rng, date(1960, 1, 1), date(2004, 12, 31))
        branch_id = (
            NEW_BRANCH_ID if customer_id % 20 == 0 else rng.randint(1, NEW_BRANCH_ID - 1)
        )
        signup_start = (
            NEW_BRANCH_OPENING if branch_id == NEW_BRANCH_ID else date(2025, 7, 1)
        )
        signup = random_day(rng, signup_start, date(2026, 4, 30))
        name = f"{rng.choice(first_names)} {rng.choice(last_names)}"
        customers.append(
            (customer_id, name, rng.choice(cities), iso_day(birth), iso_day(signup), branch_id)
        )
    connection.executemany(
        """
        INSERT INTO customers
            (id, name, city, birth_date, signup_date, branch_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        customers,
    )

    accounts = []
    account_id = 1
    account_meta: dict[int, tuple[int, str | None, str]] = {}
    for customer_id, _, _, _, _, customer_branch in customers:
        if customer_id % 9 == 0:
            continue
        account_count = 1 + (1 if customer_id % 11 in (0, 1, 2) else 0)
        for account_number in range(account_count):
            branch_id = (
                customer_branch
                if account_number == 0
                else rng.randint(1, NEW_BRANCH_ID - 1)
            )
            opened_start = (
                NEW_BRANCH_OPENING if branch_id == NEW_BRANCH_ID else date(2025, 8, 1)
            )
            opened = random_day(rng, opened_start, date(2026, 3, 31))
            is_closed = customer_id % 13 == 0 and account_number == 0
            if is_closed:
                closed = opened + timedelta(days=rng.randint(40, 130))
                status = "closed"
                closed_text = iso_day(closed)
            else:
                closed_text = None
                status = "suspended" if customer_id % 23 == 0 else "active"
            account_type = ["checking", "savings", "student"][
                (customer_id + account_number) % 3
            ]
            accounts.append(
                (
                    account_id,
                    customer_id,
                    branch_id,
                    account_type,
                    iso_day(opened),
                    closed_text,
                    status,
                )
            )
            account_meta[account_id] = (customer_id, closed_text, iso_day(opened))
            account_id += 1
    connection.executemany(
        """
        INSERT INTO accounts
            (id, customer_id, branch_id, account_type, opened_date,
             closed_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        accounts,
    )

    categories = [
        "groceries",
        "rent",
        "transport",
        "salary",
        "entertainment",
        "fees",
        "other",
        None,
    ]
    transactions = []
    transaction_id = 1
    for account_id, (customer_id, closed_text, opened_text) in account_meta.items():
        opened = date.fromisoformat(opened_text)
        lower = max(FIRST_DAY, opened)
        upper = LAST_DAY
        if closed_text:
            upper = min(upper, date.fromisoformat(closed_text))
        if lower > upper:
            continue
        transaction_count = 22 + (customer_id % 17)
        for _ in range(transaction_count):
            tx_day = random_day(rng, lower, upper)
            is_credit = rng.random() < 0.31
            tx_type = "credit" if is_credit else "debit"
            if is_credit:
                amount = round(rng.choice([1200, 1500, 1800, 2200, 2500]) + rng.uniform(0, 80), 2)
                category = "salary" if rng.random() < 0.7 else rng.choice(categories[:-1])
            else:
                amount = round(rng.uniform(8, 520), 2)
                if transaction_id % 199 == 0:
                    amount = SMALL_BUCKET_LIMIT
                elif transaction_id % 211 == 0:
                    amount = MEDIUM_BUCKET_LIMIT
                category = rng.choice(categories)
            reference = f"EXT-{transaction_id:06d}"
            transactions.append(
                (
                    transaction_id,
                    account_id,
                    iso_day(tx_day),
                    tx_type,
                    amount,
                    category,
                    f"{tx_type.title()} transaction",
                    reference,
                    iso_day(tx_day) + "T12:00:00",
                )
            )
            transaction_id += 1

    # A controlled data-quality issue: one transaction arrived after closure.
    closed_account = next(
        (account_id for account_id, (_, closed, _) in account_meta.items() if closed),
        None,
    )
    if closed_account is not None:
        _, closed_text, _ = account_meta[closed_account]
        assert closed_text is not None
        bad_day = date.fromisoformat(closed_text) + timedelta(days=2)
        transactions.append(
            (
                transaction_id,
                closed_account,
                iso_day(bad_day),
                "debit",
                42.00,
                None,
                "Transaction to review",
                f"EXT-{transaction_id:06d}",
                iso_day(bad_day) + "T12:00:00",
            )
        )
        transaction_id += 1

    connection.executemany(
        """
        INSERT INTO transactions
            (id, account_id, transaction_date, transaction_type, amount,
             category, description, external_reference, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        transactions,
    )

    # Intentional duplicate business events for the dedup exercise.
    duplicate_source_ids = [17, 211, 503, 877, 1299, 1711, 2303]
    duplicate_rows = []
    for source_id in duplicate_source_ids:
        row = connection.execute(
            """
            SELECT account_id, transaction_date, transaction_type, amount,
                   category, description, external_reference
            FROM transactions
            WHERE id = ?
            """,
            (source_id,),
        ).fetchone()
        if row is None:
            continue
        duplicate_rows.append((transaction_id, *row, iso_day(LAST_DAY) + "T23:00:00"))
        transaction_id += 1
    connection.executemany(
        """
        INSERT INTO transactions
            (id, account_id, transaction_date, transaction_type, amount,
             category, description, external_reference, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        duplicate_rows,
    )

    connection.commit()
    connection.close()


def main() -> None:
    build_database(DEFAULT_DB)
    print(f"Database ready: {DEFAULT_DB}")


if __name__ == "__main__":
    main()
