import yaml
from sqlalchemy import text

def load_yaml_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def sanitize_column_name(col):
    return col.strip().replace(" ", "_").lower()

# Método para obter os mapeamentos de chaves estrangeiras
def get_foreign_key_mappings(conn, db_type, db_name):
    if db_type == "postgresql":
        query = text("""
            SELECT
                tc.table_name AS foreign_table,
                kcu.column_name AS foreign_column,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM
                information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public';
        """)
    elif db_type == "mysql":
        query = text(f"""
            SELECT
                TABLE_NAME AS foreign_table,
                COLUMN_NAME AS foreign_column,
                REFERENCED_TABLE_NAME AS referenced_table,
                REFERENCED_COLUMN_NAME AS referenced_column
            FROM
                information_schema.KEY_COLUMN_USAGE
            WHERE
                REFERENCED_TABLE_NAME IS NOT NULL
                AND TABLE_SCHEMA = '{db_name}';
        """)
    else:
        raise ValueError("Unsupported database type")

    results = conn.execute(query).mappings()

    # Estrutura: {(referenced_table, referenced_column): [(foreign_table, foreign_column), ...]}
    mapping = {}
    for row in results:
        key = (row["referenced_table"], row["referenced_column"])
        value = (row["foreign_table"], row["foreign_column"])
        mapping.setdefault(key, []).append(value)
        
    return mapping