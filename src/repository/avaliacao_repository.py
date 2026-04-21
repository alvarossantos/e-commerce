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