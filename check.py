#!/usr/bin/env python3
"""Run a candidate answer and compare it with a case reference solution."""

from __future__ import annotations

import argparse
import math
import re
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from setup_db import DEFAULT_DB, build_database


ROOT = Path(__file__).resolve().parent
CASE_DIR = ROOT / "cases"
SOLUTION_DIR = ROOT / "solutions"
COMPARISON_DIGITS = 6


@dataclass
class CaseConfig:
    case_id: str
    title: str
    expected_columns: list[str]
    hint: str


@dataclass
class CheckResult:
    ok: bool
    message: str


def find_case(case_id: str) -> Path | None:
    normalized = str(case_id).zfill(2)
    matches = sorted(CASE_DIR.glob(f"{normalized}-*.md"))
    return matches[0] if matches else None


def parse_case(case_path: Path) -> CaseConfig:
    text = case_path.read_text(encoding="utf-8")
    blocks = text.split("---\n", 2)
    frontmatter: dict[str, str] = {}
    if text.startswith("---\n") and len(blocks) == 3:
        for line in blocks[1].splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                value = value.strip()
                if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                frontmatter[key.strip()] = value
    columns = [
        item.strip()
        for item in frontmatter.get("expected_columns", "").split(",")
        if item.strip()
    ]
    hint_match = re.search(r"<summary>Hints</summary>(.*?)</details>", text, re.DOTALL)
    missing = [key for key in ("case", "title") if not frontmatter.get(key)]
    if not columns:
        missing.append("expected_columns")
    if hint_match is None:
        missing.append("la section <summary>Hints</summary>")
    if missing:
        raise ValueError(
            f"{case_path.name} est mal forme, il manque {', '.join(missing)}."
        )
    return CaseConfig(
        case_id=frontmatter["case"],
        title=frontmatter["title"],
        expected_columns=columns,
        hint=" ".join(hint_match.group(1).split()),
    )


def list_cases() -> None:
    for case_path in sorted(CASE_DIR.glob("[0-9][0-9]-*.md")):
        config = parse_case(case_path)
        print(f"{config.case_id}: {config.title}")


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.resolve()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def execute_query(connection: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple[Any, ...]]]:
    cursor = connection.execute(sql.strip())
    columns = [description[0] for description in cursor.description or []]
    return columns, cursor.fetchall()


def normalize_value(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, COMPARISON_DIGITS)
    return value


def values_equal(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(
            float(left), float(right), rel_tol=0.0, abs_tol=10 ** (-COMPARISON_DIGITS)
        )
    return left == right


def row_equal(left: tuple[Any, ...], right: tuple[Any, ...]) -> bool:
    return len(left) == len(right) and all(
        values_equal(a, b) for a, b in zip(left, right)
    )


def row_key(row: tuple[Any, ...]) -> tuple[Any, ...]:
    return tuple(normalize_value(value) for value in row)


def format_row(row: tuple[Any, ...]) -> str:
    return "(" + ", ".join("NULL" if value is None else str(value) for value in row) + ")"


def compare_results(
    candidate_rows: list[tuple[Any, ...]],
    reference_rows: list[tuple[Any, ...]],
) -> tuple[bool, str]:
    if len(candidate_rows) != len(reference_rows):
        candidate_counter = Counter(row_key(row) for row in candidate_rows)
        reference_counter = Counter(row_key(row) for row in reference_rows)
        missing = list((reference_counter - candidate_counter).elements())[:3]
        extra = list((candidate_counter - reference_counter).elements())[:3]
        details = [
            f"row-count diff: expected {len(reference_rows)}, got {len(candidate_rows)}"
        ]
        if missing:
            details.append("missing: " + ", ".join(format_row(row) for row in missing))
        if extra:
            details.append("extra: " + ", ".join(format_row(row) for row in extra))
        return False, "; ".join(details)

    for index, (candidate, reference) in enumerate(
        zip(candidate_rows, reference_rows), start=1
    ):
        if not row_equal(candidate, reference):
            return (
                False,
                f"row {index} differs: expected {format_row(reference)}, "
                f"got {format_row(candidate)}",
            )
    return True, "all rows match in the required order"


def check_case(case_id: str, answer_path: Path, db_path: Path = DEFAULT_DB) -> CheckResult:
    case_path = find_case(case_id)
    if case_path is None:
        return CheckResult(
            False,
            f"la case {case_id} n'existe pas dans le kit. "
            "Fais `python3 check.py --list` pour voir les numeros disponibles.",
        )
    config = parse_case(case_path)
    reference_path = SOLUTION_DIR / f"{config.case_id}.sql"
    if not answer_path.exists():
        return CheckResult(False, f"Answer file not found: {answer_path}")
    if not reference_path.exists():
        return CheckResult(False, f"Reference solution not found: {reference_path}")
    if not db_path.exists():
        build_database(db_path)

    try:
        answer_sql = answer_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return CheckResult(
            False,
            f"{answer_path.name} n'est pas encode en UTF-8. "
            "Re-sauvegarde ton fichier en UTF-8 dans ton editeur, puis relance.",
        )
    except OSError as error:
        return CheckResult(False, f"Could not read {answer_path.name}: {error}")

    try:
        reference_sql = reference_path.read_text(encoding="utf-8")
    except OSError as error:
        return CheckResult(False, f"Could not read {reference_path.name}: {error}")

    connection = connect_readonly(db_path)
    try:
        try:
            _, reference_rows = execute_query(connection, reference_sql)
        except (sqlite3.Error, sqlite3.Warning) as error:
            return CheckResult(
                False,
                f"la solution de reference {reference_path.name} n'a pas pu tourner "
                f"sur {db_path.name}: {error}. Ta reponse n'est pas en cause: "
                f"efface {db_path.name} et refais `python3 setup_db.py`.",
            )
        try:
            candidate_columns, candidate_rows = execute_query(connection, answer_sql)
        except (sqlite3.Error, sqlite3.Warning) as error:
            return CheckResult(
                False,
                f"SQL error in {answer_path.name}: {error}. "
                "Check table names, commas, JOIN conditions and date syntax.",
            )
    finally:
        connection.close()

    if len(candidate_columns) != len(config.expected_columns):
        return CheckResult(
            False,
            f"expected {len(config.expected_columns)} output columns "
            f"({', '.join(config.expected_columns)}), got {len(candidate_columns)}",
        )
    ok, detail = compare_results(candidate_rows, reference_rows)
    if ok:
        aliases = "Column aliases are okay; "
        return CheckResult(True, f"Correct! {aliases}{detail}.")
    return CheckResult(False, f"{detail}. Hint: {config.hint}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", help="case number, such as 03")
    parser.add_argument("answer", nargs="?", help="path to your answer SQL file")
    parser.add_argument("--list", action="store_true", help="list all cases")
    args = parser.parse_args()
    if not args.list and (not args.case or not args.answer):
        parser.error("provide CASE and ANSWER, or use --list")
    try:
        if args.list:
            list_cases()
            return 0
        result = check_case(args.case, Path(args.answer))
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Pas encore: le kit n'a pas pu lire ses propres fichiers: {error}")
        return 1
    prefix = "YEEE" if result.ok else "Pas encore"
    print(f"{prefix}: {result.message}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
