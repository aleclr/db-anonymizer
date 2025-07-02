import os
import pandas as pd
import hashlib
import random
import string
import yaml

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

MASK_FUNCTIONS = {
    'mask_email': mask_email,
    'mask_name': mask_name,
    'mask_cpf': mask_cpf,
    'mask_phone': mask_phone
}

def load_rules(config_path="config/anonymization_rules.yaml"):
    if not os.path.exists(config_path):
        print("Anonymization rules not found. Skipping anonymization.")
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
    


def anonymize_csv_files(input_dir, output_dir, rules_path="config/anonymization_rules.yaml"):
    os.makedirs(output_dir, exist_ok=True)
    rules = load_rules(rules_path)

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            table_name = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(input_dir, file))

            # Normalize column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            table_rules = rules.get(table_name, {})
            for column, rule in table_rules.items():
                if column in df.columns and rule in MASK_FUNCTIONS:
                    df[column] = df[column].apply(MASK_FUNCTIONS[rule])

            df.to_csv(os.path.join(output_dir, file), index=False)
            print(f"Anonymized: {file}")