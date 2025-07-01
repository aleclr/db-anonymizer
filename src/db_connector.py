import psycopg2
import mysql.connector
# from src.utils import load_yaml_config

def get_connection(config):
    if config["db_type"] == "postgresql":
        return psycopg2.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            dbname=config["database"]
        )
    elif config["db_type"] == "mysql":
        return mysql.connector.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
    else:
        raise ValueError("Unsupported database type")