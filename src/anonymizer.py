import os
import pandas as pd
import hashlib
import random
import string
import yaml
import numpy as np
from datetime import datetime, timedelta
from src.logger import log_to_csv, log_to_database
from sqlalchemy import inspect
from src.utils import get_foreign_key_mappings


def mask_email(email):
    if pd.isna(email):
        return email
    return "masked_" + hashlib.md5(email.encode()).hexdigest()[:10] + "@example.com"

def mask_name(name):
    if pd.isna(name):
        return name
    return "Name_" + ''.join(random.choices(string.ascii_uppercase, k=5))

def mask_cpf(cpf):
    if pd.isna(cpf):
        return cpf
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def mask_phone(phone):
    if pd.isna(phone):
        return phone
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def mask_string(value):
    if pd.isna(value):
        return value
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def mask_integer(value):
    if pd.isna(value):
        return value
    return random.randint(1000, 999999)

def mask_float(value):
    if pd.isna(value):
        return value
    return round(random.uniform(1000.0, 99999.9), 2)

def mask_date(value):
    if pd.isna(value):
        return value
    try:
        base_date = pd.to_datetime(value)
        random_days = random.randint(-365, 365)
        return (base_date + timedelta(days=random_days)).date()
    except:
        return value

def mask_boolean(value):
    if pd.isna(value):
        return value
    return random.choice([True, False])

def nullify(value):
    return np.nan

def hash_value(value):
    if pd.isna(value):
        return value
    return hashlib.sha256(str(value).encode()).hexdigest()

def mask_id_generator():
    counter = random.randint(1000, 9999)

    def mask_id(_):
        nonlocal counter
        counter += 1
        return counter

    return mask_id

MASK_FUNCTIONS = {
    'mask_email': mask_email,
    'mask_name': mask_name,
    'mask_cpf': mask_cpf,
    'mask_phone': mask_phone,
    'mask_string': mask_string,
    'mask_integer': mask_integer,
    'mask_float': mask_float,
    'mask_date': mask_date,
    'mask_boolean': mask_boolean,
    'nullify': nullify,
    'hash_value': hash_value,
    'id': mask_id_generator()  # Geração de IDs sequenciais
}

def load_rules(config_path="config/anonymization_rules.yaml"):
    if not os.path.exists(config_path):
        print("Anonymization rules not found. Skipping anonymization.")
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
    

def anonymize_csv_files(input_dir, output_dir, rules_path="config/anonymization_rules.yaml", config=None, db_conn=None):
    os.makedirs(output_dir, exist_ok=True)
    rules = load_rules(rules_path)
    log_entries = []
    pk_mappings = {}
    
    inspector = inspect(db_conn) if db_conn else None
    fk_mapping = get_foreign_key_mappings(db_conn, config["db_type"], config["database"])

    for file in os.listdir(input_dir):
        if not file.endswith(".csv"):
            continue

        table_name = file.replace(".csv", "")
        df = pd.read_csv(os.path.join(input_dir, file))

        if table_name in rules:
            table_pk = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            table_mapping = {}  # Objeto para armazenar mapeamentos de PK

            for column, rule in rules[table_name].items():
                if column in df.columns and rule in MASK_FUNCTIONS:
                    original_values = df[column].dropna().unique()
                    original_count = df[column].notna().sum()

                    # Mapeamento para chaves primárias
                    if column in table_pk:
                        mapping = {}
                        for value in original_values:
                            new_value = MASK_FUNCTIONS[rule](value)
                            mapping[value] = new_value
                        df[column] = df[column].map(mapping)
                        table_mapping[column] = mapping
                    else:
                        df[column] = df[column].apply(MASK_FUNCTIONS[rule])

                    log_entries.append({
                        "timestamp": datetime.now().isoformat(),
                        "table": table_name,
                        "column": column,
                        "mask_function": rule,
                        "row_count": int(original_count)
                    })

            if table_mapping:
                pk_mappings[table_name] = table_mapping  # Armazenar mapeamentos de PK

        df.to_csv(os.path.join(output_dir, file), index=False)

    # Sempre criar o log em csv
    if config:
        log_to_csv(config.get("log_path", "logs"), log_entries)

    # Criar tabela de logs no banco de dados se habilitada
    if config and config.get("log_to_database") and db_conn:
        from src.logger import log_to_database
        log_to_database(db_conn, log_entries)
        db_conn.commit()
    
    return pk_mappings