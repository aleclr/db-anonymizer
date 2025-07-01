import os
import pandas as pd
import hashlib
import random
import string

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

def anonymize_csv_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    file = "clients.csv"
    file_path = os.path.join(input_dir, file)
    if not os.path.exists(file_path):
        print("clients.csv not found. Skipping anonymization.")
        return

    df = pd.read_csv(file_path)

    if 'name' in df.columns:
        df['name'] = df['name'].apply(mask_name)
    if 'email' in df.columns:
        df['email'] = df['email'].apply(mask_email)
    if 'cpf' in df.columns:
        df['cpf'] = df['cpf'].apply(mask_cpf)
    if 'phone' in df.columns:
        df['phone'] = df['phone'].apply(mask_phone)

    df.to_csv(os.path.join(output_dir, file), index=False)
    print(f"Anonymized: {file}")