import os
import pandas as pd
from data_anonymizer import anonymize

def anonymize_csv_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(input_dir, file))

            # Regra exemplo: mascarar todos os valores
            # Aqui você pode definir regras mais complexas conforme necessário
            rules = {col: {"type": "mask", "value": "***"} for col in df.columns}

            anon_df = anonymize(df, rules)
            anon_df.to_csv(os.path.join(output_dir, file), index=False)
            print(f"Anonymized: {file}")