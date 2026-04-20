from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

class BancoDeDados:
    def __init__(self):
        self.config = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
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