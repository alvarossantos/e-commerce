# ========================================================================================
# CONCEITO DE ARQUITETURA LÓGICA: CAMADA DE ACESSO A DADOS (Data Access Layer)
# Papel do Repository: Isolar e centralizar toda a comunicação física com o banco de dados.
# Esta é a ÚNICA camada do sistema autorizada a conter código SQL (INSERT, SELECT, etc.)
# e a interagir com a biblioteca psycopg2. Isso permite que, se mudarmos o banco de dados
# no futuro (ex: para MySQL), apenas esta pasta precisará ser alterada.
# ========================================================================================


from src.database.conexao import BancoDeDados


class AvaliacaoRepository:
    def criar(self, produto_id, usuario_id, nota, comentario):
        sql = """
            INSERT INTO avaliacoes (produto_id, usuario_id, nota, comentario)
            VALUES (%s, %s, %s, %s)
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql, (produto_id, usuario_id, nota, comentario))

    def listar_por_produto(self, produto_id):
        # Traz a nota, o comentário e embute o NOME e a FOTO do usuário!
        sql = """
            SELECT a.nota, a.comentario, a.criado_em, u.nome, u.url_foto
            FROM avaliacoes a
            JOIN usuarios u ON a.usuario_id = u.id
            WHERE a.produto_id = %s
            ORDER BY a.criado_em DESC;
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql, (produto_id,))
            return cursor.fetchall()