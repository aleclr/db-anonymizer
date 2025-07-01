import pandas as pd
import os
from src.utils import sanitize_column_name

def export_tables(conn, output_dir, db_type, db_name):
    cursor = conn.cursor()

    if db_type == "postgresql":
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    elif db_type == "mysql":
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}';")
    else:
        raise ValueError("Unsupported database type for export")

    tables = cursor.fetchall()

    os.makedirs(output_dir, exist_ok=True)

    for (table_name,) in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df.columns = [sanitize_column_name(c) for c in df.columns]
        df.to_csv(os.path.join(output_dir, f"{table_name}.csv"), index=False)
        print(f"Exported: {table_name}")