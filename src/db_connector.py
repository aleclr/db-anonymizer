from sqlalchemy import create_engine

def get_connection(config):
    dialect = 'postgresql' if config['db_type'] == 'postgresql' else 'mysql+pymysql'
    url = f"{dialect}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    return create_engine(url)