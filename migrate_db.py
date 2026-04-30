import psycopg2
from psycopg2 import extensions
import os

# ================= CONFIG =================

# LOCAL (desenvolvimento)
DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "1234"
}

# PRODUÇÃO (Render + Neon)
DATABASE_URL = os.environ.get("DATABASE_URL")


# ================= CRIAR BANCO =================
def init_db():
    """Cria o banco de dados caso não exista (APENAS LOCAL)."""
    if DATABASE_URL:
        print("Ambiente de produção detectado. Pulando criação de banco.")
        return

    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="postgres"
        )
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'catalogo_filmes'"
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("CREATE DATABASE catalogo_filmes")
            print("Banco 'catalogo_filmes' criado!")
        else:
            print("Banco já existe.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar banco: {e}")


# ================= CONEXÃO =================
def get_conn():
    """Retorna conexão (local ou produção)."""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database="catalogo_filmes"
    )


# ================= CRIAR TABELA =================
def init_table():
    """Cria a tabela filmes."""
    try:
        conn = get_conn()
        cursor = conn.cursor()

        sql = """
        CREATE TABLE IF NOT EXISTS filmes (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            genero VARCHAR(100),
            ano VARCHAR(10),
            url_capa TEXT
        );
        """

        cursor.execute(sql)
        conn.commit()

        print("Tabela 'filmes' pronta!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar tabela: {e}")


# ================= RUN =================
if __name__ == "__main__":
    print("Iniciando migração...")

    init_db()      # só local
    init_table()   # local e produção

    print("Migração finalizada!")