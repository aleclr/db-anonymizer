import os
import csv
import datetime
from sqlalchemy import text

def init_logger(log_dir):
    os.makedirs(log_dir, exist_ok=True)

def log_to_csv(log_dir, log_entries):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"anonymization_log_{timestamp}.csv")

    with open(log_path, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "table", "column", "mask_function", "row_count"])
        writer.writeheader()
        for entry in log_entries:
            writer.writerow(entry)

def create_logging_table_if_enabled(config, conn):
    if config.get("log_to_database"):
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS anonymization_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(100),
                column_name VARCHAR(100),
                mask_function VARCHAR(100),
                row_count INT,
                run_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''))

def log_to_database(conn, log_entries):
    if not log_entries:
        return
    for entry in log_entries:
        conn.execute(text('''
            INSERT INTO anonymization_logs (table_name, column_name, mask_function, row_count, run_timestamp)
            VALUES (:table_name, :column_name, :mask_function, :row_count, :timestamp)
        '''), {
            "table_name": entry["table"],
            "column_name": entry["column"],
            "mask_function": entry["mask_function"],
            "row_count": entry["row_count"],
            "timestamp": entry["timestamp"]
        })
