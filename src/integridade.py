import pandas as pd
import os
from sqlalchemy import text

def update_foreign_keys(engine, pk_mappings, fk_mapping, output_dir):
    for (ref_table, ref_column), fk_list in fk_mapping.items():
        # Pular tabelas que não possuem mapeamento de PK
        if ref_table not in pk_mappings or ref_column not in pk_mappings[ref_table]:
            continue

        mapping = pk_mappings[ref_table][ref_column]

        for fk_table, fk_column in fk_list:
            csv_path = os.path.join(output_dir, f"{fk_table}.csv")
            if not os.path.exists(csv_path):
                print(f"⚠️  Skipping FK update for {fk_table}.{fk_column}: file not found")
                continue

            df = pd.read_csv(csv_path)
            if fk_column not in df.columns:
                print(f"⚠️  Column {fk_column} not in {fk_table}.csv")
                continue

            df[fk_column] = df[fk_column].map(mapping).fillna(df[fk_column])  # fallback
            df.to_csv(csv_path, index=False)
            print(f"✅ Updated foreign keys in {fk_table}.{fk_column} referencing {ref_table}.{ref_column}")