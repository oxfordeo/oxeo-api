import os

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# command line: psql -h hostname -p portNumber -U userName dbName -W
DB_USER = os.environ.get("PG_DB_USER")
DB_PW = os.environ.get("PG_DB_PW")
DB_HOST = os.environ.get("PG_DB_HOST")
DB_NAME = os.environ.get("PG_DB_NAME")


SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PW}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

try:
    engine.connect()
    print("success")
except SQLAlchemyError as err:
    print("error", err.__cause__)  # this will give what kind of error
