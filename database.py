import os

import psycopg2
import redis
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

rd = redis.Redis.from_url(os.getenv("REDIS_URL"))
engine = create_engine(os.getenv("DB_CONNECTION_URL"))
ormMetaData = MetaData()
ormMetaData.reflect(bind=engine)
Session = sessionmaker(bind=engine)


def getSession():
    with Session.begin() as session:
        yield session


# -----------------------------------------------------------
def getCursorForPGDB():
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        # TODO: check if we can simply yield conn.cursor and if it automatically closes it
        cursor = conn.cursor()
        yield cursor
    # TODO: Add more specific exceptions
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
