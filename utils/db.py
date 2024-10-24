import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")


connection_pool = pool.SimpleConnectionPool(1, 20, dsn=DATABASE_URL)
