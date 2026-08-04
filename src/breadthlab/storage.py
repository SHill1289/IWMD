from __future__ import annotations
from pathlib import Path
import duckdb
import pandas as pd
from .config import DB_PATH

TABLES = ["prices", "constituents", "benchmark", "security_features", "daily_breadth"]


def connect(path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(path))


def replace_table(name: str, df: pd.DataFrame, path: Path = DB_PATH) -> None:
    if name not in TABLES:
        raise ValueError(f"Unsupported table: {name}")
    con = connect(path)
    try:
        con.register("incoming_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM incoming_df")
    finally:
        con.close()


def read_table(name: str, path: Path = DB_PATH) -> pd.DataFrame:
    if name not in TABLES:
        raise ValueError(f"Unsupported table: {name}")
    con = connect(path)
    try:
        exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?", [name]
        ).fetchone()[0]
        if not exists:
            return pd.DataFrame()
        return con.execute(f"SELECT * FROM {name} ORDER BY 1").df()
    finally:
        con.close()


def database_status(path: Path = DB_PATH) -> dict[str, int]:
    con = connect(path)
    status: dict[str, int] = {}
    try:
        for name in TABLES:
            exists = con.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?", [name]
            ).fetchone()[0]
            status[name] = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] if exists else 0
    finally:
        con.close()
    return status
