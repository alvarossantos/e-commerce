from dotenv import load_dotenv
import psycopg2
import os

from psycopg2._psycopg import cursor

load_dotenv()

class BancoDeDados:
    def __init__(self):
        self.config = {
            "db_name": os.getenv("DB_NAME"),
            "db_user": os.getenv("DB_USER"),
            "db_password": os.getenv("DB_PASSWORD"),
            "db_host": os.getenv("DB_HOST"),
            "db_port": os.getenv("DB_PORT")
        }

    # Entrar/Conectar no banco
    def __enter__(self):
        self.conn = psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()
        return self.cursor

    # Sair/Fechar conexão ao banco
    def __exit__(self, exc_type, exc_val, exc_tb):
        # O Python preenche 'exc_type' se houver algum erro/exceção
        if exc_type is None:
            # Não aconteceu erro? Salva
            self.conn.commit()
        else:
            # Aconteceu erro? Cancela tudo para não sujar o banco
            self.conn.rollback()

        # Fecha a conexão
        self.cursor.close()
        self.conn.close()