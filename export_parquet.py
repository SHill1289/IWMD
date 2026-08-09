from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "breadth.duckdb"
OUT_DIR = ROOT / "data" / "parquet"

OUT_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB_PATH), read_only=True)

tables = [
    "prices",
    "constituents",
    "benchmark",
    "security_features",
    "daily_breadth",
]

for table in tables:
    out_file = OUT_DIR / f"{table}.parquet"
    print(f"Exporting {table} -> {out_file}")
    con.execute(
        f"COPY {table} TO '{out_file.as_posix()}' (FORMAT PARQUET)"
    )

con.close()

print("Done.")