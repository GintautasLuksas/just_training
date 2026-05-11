from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

def insert_dataframe_to_postgres(df: pd.DataFrame, table_name: str):
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")

    assert user and password and host and port and dbname, "Missing one or more DB env vars"

    print(f"Connecting to DB {dbname} at {host}:{port} as {user}")

    try:
        db_url = URL.create(
            "postgresql+pg8000",
            username=user,
            password=password,
            host=host,
            port=int(port),
            database=dbname,
        )
        engine = create_engine(db_url)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Inserted {len(df)} rows into '{table_name}'")
    except Exception as e:
        print(f"Error inserting dataframe to postgres: {e}")
        raise
