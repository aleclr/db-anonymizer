import pytest
import pandas as pd
from src.anonymizer import (
    mask_email, mask_name, mask_cpf, mask_phone, mask_string, mask_integer,
    mask_float, mask_date, mask_boolean, nullify, hash_value, load_rules,
    MASK_FUNCTIONS, anonymize_csv_files
)

# TESTES INDIVIDUAIS PARA CADA FUNÇÃO DE ANONIMIZAÇÃO

def test_mask_email():
    result = mask_email("user@example.com")
    assert result.startswith("masked_") and result.endswith("@example.com")

def test_mask_name():
    result = mask_name("John Doe")
    assert result.startswith("Name_") and len(result) == 10

def test_mask_cpf():
    result = mask_cpf("12345678901")
    assert len(result) == 11 and result.isdigit()

def test_mask_phone():
    result = mask_phone("11999999999")
    assert len(result) == 11 and result.isdigit()

def test_mask_string():
    result = mask_string("anything")
    assert len(result) == 8

def test_mask_integer():
    result = mask_integer(123)
    assert isinstance(result, int)

def test_mask_float():
    result = mask_float(123.45)
    assert isinstance(result, float)

def test_mask_date():
    result = mask_date("2023-01-01")
    assert str(result).startswith("20")

def test_mask_boolean():
    assert mask_boolean(True) in [True, False]

def test_nullify():
    assert pd.isna(nullify("anything"))

def test_hash_value():
    result = hash_value("secret")
    assert len(result) == 64
    
# TESTE PARA CARREGAMENTO E VALIDAÇÃO DE REGRAS

def test_load_rules_structure_and_validity(tmp_path):
    yaml_path = tmp_path / "rules.yaml"
    yaml_path.write_text("""
    users:
      email: mask_email
      password: hash_value
    orders:
      total: mask_float
    """)

    rules = load_rules(str(yaml_path))
    assert isinstance(rules, dict)

    for table, columns in rules.items():
        assert isinstance(table, str)
        assert isinstance(columns, dict)
        for column, rule in columns.items():
            assert isinstance(column, str)
            assert rule in MASK_FUNCTIONS
            
# TESTE PARA ANONIMIZAÇÃO DE ARQUIVOS CSV

def test_anonymize_csv_files(tmp_path):
    # Criando csv de teste
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    df = pd.DataFrame({
        "email": ["user@example.com"],
        "cpf": ["12345678901"]
    })
    df.to_csv(input_dir / "clients.csv", index=False)

    # Criando arquivo de regras
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("""
clients:
  email: mask_email
  cpf: mask_cpf
""")

    # Executando a função de anonimização
    anonymize_csv_files(str(input_dir), str(output_dir), rules_path=str(rules_file))

    # Checando o resultado
    output_df = pd.read_csv(output_dir / "clients.csv")
    assert output_df.shape == df.shape
    assert output_df["email"].iloc[0].startswith("masked_")
    assert output_df["cpf"].iloc[0] != "12345678901"