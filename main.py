import argparse
from src.utils import load_yaml_config
from src.db_connector import get_connection
from src.exporter import export_tables
from src.anonymizer import anonymize_csv_files
from src.importer import import_tables_from_csv
from src.logger import init_logger, create_logging_table_if_enabled

def main(step):
    config = load_yaml_config("config/db_config.yaml")
    engine = get_connection(config)

    # Initialize logger directory
    init_logger(config.get("log_path", "logs"))

    # Optionally create logging table in DB
    create_logging_table_if_enabled(config, engine)
    
    with engine.connect() as conn:
        if step == "export":
            export_tables(conn, "csv_exports", config["db_type"], config["database"])
            engine.dispose()  # Close the connection after export
        elif step == "anonymize":
            anonymize_csv_files("csv_exports", "csv_anonymized", config=config, db_conn=conn)
        elif step == "import":
            import_tables_from_csv(config, "csv_anonymized")
        elif step == "all":
            export_tables(conn, "csv_exports", config["db_type"], config["database"])
            engine.dispose()  # Close the connection after export
            anonymize_csv_files("csv_exports", "csv_anonymized", config=config, db_conn=conn)
            import_tables_from_csv(config, "csv_anonymized")
        else:
            print("Argumento desconhecido. Use um destes: export, anonymize, import, all")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=str, required=True, help="Step to run: export, anonymize, import, all")
    args = parser.parse_args()
    main(args.step)