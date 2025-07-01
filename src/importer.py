import pandas as pd
import os
from sqlalchemy import create_engine, text

def import_tables_from_csv(config, input_dir):
    dialect = 'postgresql' if config['db_type'] == 'postgresql' else 'mysql+pymysql'
    url = f"{dialect}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    print(f"Connecting to database: {url}")

    engine = create_engine(url)

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            table_name = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(input_dir, file))
            with engine.begin() as conn:
                if config['db_type'] == 'postgresql':
                    conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                elif config['db_type'] == 'mysql':
                    conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                else:
                    raise ValueError("Unsupported DB type for TRUNCATE")
                df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Imported: {table_name}")