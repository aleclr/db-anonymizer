import pandas as pd
import os
# from src.utils import sanitize_column_name
from sqlalchemy import text

def export_tables(conn, output_dir, db_type, database_name):
    os.makedirs(output_dir, exist_ok=True)

    if db_type == 'postgresql':
        query = text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    elif db_type == 'mysql':
        query = text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{database_name}';")
    else:
        raise ValueError("Unsupported database type")

    result = conn.execute(query)
    tables = [row[0] for row in result]

    for table_name in tables:
        
        if table_name == "anonymization_logs":
            continue
        
        df = pd.read_sql_table(table_name, conn)
        df.to_csv(os.path.join(output_dir, f"{table_name}.csv"), index=False)
        print(f"Exported: {table_name}")