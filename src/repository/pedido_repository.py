from src.database.conexao import BancoDeDados


class PedidoRepository:
    def criar(self, usuario_id, valor_total):
        # Cria o pedido inicial (cabeçalho)
        # Simplificado: status 'pendente' e o valor 0 são automáticos
        sql = "INSERT INTO pedidos (usuario_id) VALUES (%s) RETURNING id;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchone()[0]

    def inserir_item(self, pedido_id, produto_id, quantidade, preco_unitario, cursor_externo=None):
        # Inseri um produto no pedido
        sql = """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s);
        """

        with BancoDeDados() as cursor:
            cursor.execute(sql, (pedido_id, produto_id, quantidade, preco_unitario))

    def mudar_status(self, pedido_id, novo_status):
        sql = "UPDATE pedidos SET status = %s WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (novo_status, pedido_id))

    def atualizar_total(self, pedido_id, valor_total):
        sql = "UPDATE pedidos SET valor_total = %s WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (valor_total, pedido_id))

    def buscar_produtos_em_pedidos_cancelados(self):
        sql = """
            SELECT p.nome, ip.quantidade, ped.data_criacao
            FROM produtos p
            JOIN itens_pedido ip ON p.id = ip.produto_id
            JOIN pedidos ped ON ped.id = ip.pedido_id
            WHERE ped.status = 'cancelado'
            ORDER BY ped.data_criacao DESC;
        """

        cancelados = []
        with BancoDeDados() as cursor:
            cursor.execute(sql)
            for row in cursor.fetchall():
                cancelados.append({
                    "produto": row[0],
                    "quantidade": row[1],
                    "data": row[2]
                })
        return cancelados

    def cancelar_pedidos_expirados(self):
        # Seleciona pedidos pendentes com mais de 48 horas
        sql = """
            UPDATE pedidos
            SET status = 'cancelado'
            WHERE status = 'pendente'
            AND data_criacao < NOW() - INTERVAL '48 hours';
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql)
            return cursor.rowcount # Retorna quantos pedidos foram cancelados

    def buscar_pendentes_para_notificacao(self):
        # Busca pedidos criados há mais de 12h que ainda não receberam o próximo alerta
        sql = """
            SELECT p.id, u.nome, u.email, p.alertas_enviados, p.data_criacao
            FROM pedidos p
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.status = 'pendente'
            AND p.alertas_enviados < 3 -- Limitamos a 3 avisos antes do cancelamento do pedido
            AND p.data_criacao < NOW() - (INTERVAL '12 hours' * (p.alertas_enviados + 1));
        """
        notificacoes = []
        with BancoDeDados() as cursor:
            cursor.execute(sql)
            for row in cursor.fetchall():
                notificacoes.append({
                    "pedido_id": row[0],
                    "cliente_nome": row[1],
                    "cliente_email": row[2],
                    "total_alertas": row[3]
                })
        return notificacoes

    def incrementar_alerta(self, pedido_id):
        sql = "UPDATE pedidos SET alertas_enviados = alertas_enviados + 1 WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql , (pedido_id,))