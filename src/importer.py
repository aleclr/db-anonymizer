import pandas as pd
import os
from sqlalchemy import create_engine, text

def import_tables_from_csv(config, input_dir):
    dialect = 'postgresql' if config['db_type'] == 'postgresql' else 'mysql+pymysql'
    url = f"{dialect}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

    print(f"Conectando ao banco de dados pela url: {url}")
    engine = create_engine(url)

    with engine.begin() as conn:
        if config['db_type'] == 'mysql':
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        elif config['db_type'] == 'postgresql':
            # Não é necessário desativar FK check no PostgreSQL
            pass

        for file in os.listdir(input_dir):
            if file.endswith(".csv"):
                table_name = file.replace(".csv", "")
                
                # 🚫 Pular tabela de logs
                if table_name == "anonymization_logs":
                    continue
                
                df = pd.read_csv(os.path.join(input_dir, file))

                print(f"Importing table: {table_name}")

                if config['db_type'] == 'postgresql':
                    conn.execute(text(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL;"))
                
                conn.execute(text(f"DELETE FROM {table_name}"))

                df.to_sql(table_name, conn, if_exists='append', index=False)

                if config['db_type'] == 'postgresql':
                    conn.execute(text(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL;"))

        if config['db_type'] == 'mysql':
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

    print("✅ Todas tabelas importadas com sucesso.")