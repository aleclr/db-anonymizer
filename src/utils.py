import yaml

def load_yaml_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def sanitize_column_name(col):
    return col.strip().replace(" ", "_").lower()