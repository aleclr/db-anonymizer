import argparse
import os
import pandas as pd
from src.utils import load_yaml_config, get_foreign_key_mappings
from src.db_connector import get_connection
from src.exporter import export_tables
from src.anonymizer import anonymize_csv_files
from src.importer import import_tables_from_csv
from src.logger import init_logger, create_logging_table_if_enabled
from src.integridade import update_foreign_keys

def main(step):
    config = load_yaml_config("config/db_config.yaml")
    engine = get_connection(config)

    # Inicializa o logger
    init_logger(config.get("log_path", "logs"))

    # Cria a tabela de logs no banco de dados se habilitado
    create_logging_table_if_enabled(config, engine)
    
    with engine.connect() as conn:
        if step == "export":
            export_tables(conn, "csv_exports", config["db_type"], config["database"])
            engine.dispose()  # Fechar a conexão após exportação
            
        elif step == "anonymize":
            pk_mappings = anonymize_csv_files("csv_exports", "csv_anonymized", config=config, db_conn=conn)
            fk_mapping = get_foreign_key_mappings(conn, config["db_type"], config["database"])
            update_foreign_keys(conn, pk_mappings, fk_mapping, output_dir="csv_anonymized")
            engine.dispose()  # Fechar a conexão após anonimização
            
        elif step == "import":
            print("\n📋 Aqui está uma preview dos campos anonimizados:")
            for file in os.listdir("csv_anonymized"):
                if file.endswith(".csv"):
                    print(f"\n🔹 {file}")
                    df = pd.read_csv(os.path.join("csv_anonymized", file))
                    print(df.head(3))

            confirm = input("\nVoce deseja importar essas tabelas para o banco? (yes/no): ").strip().lower()
            if confirm == "yes":
                import_tables_from_csv(config, "csv_anonymized")
            else:
                print("❌ Import cancelado pelo usuário.")
            import_tables_from_csv(config, "csv_anonymized")
            
        elif step == "all":
            export_tables(conn, "csv_exports", config["db_type"], config["database"])
            pk_mappings = anonymize_csv_files("csv_exports", "csv_anonymized", config=config, db_conn=conn)
            
            fk_mapping = get_foreign_key_mappings(conn, config["db_type"], config["database"])
            update_foreign_keys(conn, pk_mappings, fk_mapping, output_dir="csv_anonymized")
            
            print("\n📋 Aqui está uma preview dos campos anonimizados:")
            for file in os.listdir("csv_anonymized"):
                if file.endswith(".csv"):
                    print(f"\n🔹 {file}")
                    df = pd.read_csv(os.path.join("csv_anonymized", file))
                    print(df.head(3))

            confirm = input("\nVoce deseja importar essas tabelas para o banco? (yes/no): ").strip().lower()
            if confirm == "yes":
                import_tables_from_csv(config, "csv_anonymized")
            else:
                print("❌ Import cancelado pelo usuário.")
                
        else:
            print("Argumento desconhecido. Use um destes: export, anonymize, import, all")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=str, required=True, help="Step to run: export, anonymize, import, all")
    args = parser.parse_args()
    main(args.step)