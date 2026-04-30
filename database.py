import psycopg2
import os

def get_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1234",
        database="catalogo_filmes"
    )