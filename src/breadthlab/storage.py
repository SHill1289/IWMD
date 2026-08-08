from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from .config import DB_PATH


TABLES = [
    "prices",
    "constituents",
    "benchmark",
    "security_features",
    "daily_breadth",
]


def connect(path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def _table_exists(
    con: duckdb.DuckDBPyConnection,
    name: str,
) -> bool:
    result = con.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = ?
        """,
        [name],
    ).fetchone()

    return bool(result[0])


def hydrate_from_parquet_if_needed(path: Path = DB_PATH) -> bool:
    """
    Rebuild the local DuckDB database from persistent Parquet files
    when the database is empty.

    Returns True when hydration occurred.
    """

    parquet_dir = path.parent / "parquet"

    if not parquet_dir.exists():
        return False

    con = connect(path)

    try:
        has_data = False

        for name in TABLES:
            if _table_exists(con, name):
                count = con.execute(
                    f"SELECT COUNT(*) FROM {name}"
                ).fetchone()[0]

                if count > 0:
                    has_data = True
                    break

        if has_data:
            return False

        loaded_any = False

        for name in TABLES:
            parquet_file = parquet_dir / f"{name}.parquet"

            if not parquet_file.exists():
                continue

            safe_path = str(parquet_file).replace("\\", "/").replace("'", "''")

            con.execute(
                f"""
                CREATE OR REPLACE TABLE {name}
                AS
                SELECT *
                FROM read_parquet('{safe_path}')
                """
            )

            loaded_any = True

        return loaded_any

    finally:
        con.close()


def replace_table(
    name: str,
    df: pd.DataFrame,
    path: Path = DB_PATH,
) -> None:
    if name not in TABLES:
        raise ValueError(f"Unsupported table: {name}")

    con = connect(path)

    try:
        con.register("incoming_df", df)

        con.execute(
            f"""
            CREATE OR REPLACE TABLE {name}
            AS
            SELECT *
            FROM incoming_df
            """
        )

    finally:
        con.close()


def read_table(
    name: str,
    path: Path = DB_PATH,
) -> pd.DataFrame:
    if name not in TABLES:
        raise ValueError(f"Unsupported table: {name}")

    hydrate_from_parquet_if_needed(path)

    con = connect(path)

    try:
        if not _table_exists(con, name):
            return pd.DataFrame()

        return con.execute(
            f"SELECT * FROM {name} ORDER BY 1"
        ).df()

    finally:
        con.close()


def database_status(path: Path = DB_PATH) -> dict[str, int]:
    hydrate_from_parquet_if_needed(path)

    con = connect(path)

    status: dict[str, int] = {}

    try:
        for name in TABLES:
            if _table_exists(con, name):
                status[name] = con.execute(
                    f"SELECT COUNT(*) FROM {name}"
                ).fetchone()[0]
            else:
                status[name] = 0

    finally:
        con.close()

    return status
