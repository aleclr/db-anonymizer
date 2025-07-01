import argparse
from src.utils import load_yaml_config
from src.db_connector import get_connection
from src.exporter import export_tables
from src.anonymizer import anonymize_csv_files
from src.importer import import_tables_from_csv

def main(step):
    config = load_yaml_config("config/db_config.yaml")
    conn = get_connection(config)

    if step == "export":
        export_tables(conn, "csv_exports")
    elif step == "anonymize":
        anonymize_csv_files("csv_exports", "csv_anonymized")
    elif step == "import":
        import_tables_from_csv(config, "csv_anonymized")
    elif step == "all":
        export_tables(conn, "csv_exports")
        anonymize_csv_files("csv_exports", "csv_anonymized")
        import_tables_from_csv(config, "csv_anonymized")
    else:
        print("Unknown step. Use: export, anonymize, import, all")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=str, required=True, help="Step to run: export, anonymize, import, all")
    args = parser.parse_args()
    main(args.step)