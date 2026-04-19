from src.database.conexao import BancoDeDados


class PedidoRepository:
    def criar(self, usuario_id):
        # Cria o pedido inicial (cabeçalho)
        sql = "INSERT INTO pedidos (usuario_id, status, valor_total) VALUES (%s, 'pendente', %s) RETURNING id;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchone()[0]

    def inserir_item(self, pedido_id, produto_id, quantidade, preco_unitario, cursor_externo=None):
        # Inseri um produto no pedido
        sql = """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s);
        """
        params = (pedido_id, produto_id, quantidade, preco_unitario)

        if cursor_externo:
            cursor_externo.execute(sql, params)
        else:
            with BancoDeDados() as cursor:
                cursor.execute(sql, params)

    def mudar_status(self, pedido_id, novo_status):
        sql = "UPDATE pedidos SET status = %s WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (novo_status, pedido_id))