from src.database.conexao import BancoDeDados


class PedidoRepository:
    def criar_pedido(self, usuario_id, endereco_id, valor_total, carrinho,produto_repo):
        """
        Cria um pedido completo (cabeçalho e itens) em uma única transação.
        Isso garante que, se houver erro ao salvar um item, o pedido não seja criado.
        """
        # Query 1: Cria o cabeçalho do pedido
        # Simplificado: status 'pendente' e o valor 0 são automáticos
        sql_pedido = """
            INSERT INTO pedidos (usuario_id, endereco_id, valor_total)
            VALUES (%s, %s, %s)
            RETURNING id; 
        """

        # Query 2: Insere os itens vinculados ao pedido
        sql_item = """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade,preco_unitario)
            VALUES (%s, %s, %s, %s);
        """

        with BancoDeDados() as cursor:
            # 1. Executa a criação do pedido e recupera o ID gerado
            cursor.execute(sql_pedido, (usuario_id, endereco_id, valor_total))
            pedido_id = cursor.fetchone()[0]

            # 2. Percorre o carrinho para inserir cada item
            for produto_id_str, quantidade in carrinho.items():
                produto_id = int(produto_id_str)
                # Buscamos o preço real do produto para evitar fraude no frontend
                produto = produto_repo.buscar_por_id(produto_id)

                cursor.execute(sql_item, (pedido_id, produto_id, quantidade, produto.preco))

            return pedido_id

    def inserir_item(self, pedido_id, produto_id, quantidade, preco_unitario):
        """
        Insere um produto como item em um pedido existente.

        Args:
            pedido_id (int): O 'ID' do pedido onde o item será adicionado.
            produto_id (int): O 'ID' do produto a ser inserido no pedido.
            quantidade (int): A quantidade do produto a ser adicionada.
            preco_unitario (float): O preço unitário do produto no momento da compra.
                                             Se None, cria uma nova conexão.

        Returns:
            None
        """
        # Inseri um produto no pedido
        sql = """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s);
        """

        with BancoDeDados() as cursor:
            cursor.execute(sql, (pedido_id, produto_id, quantidade, preco_unitario))

    def mudar_status(self, pedido_id, novo_status):
        """
        Atualiza o status de um pedido existente.

        Args:
            pedido_id (int): O 'ID' do pedido a ser atualizado.
            novo_status (str): O novo status do pedido. Valores válidos:
                              'pendente', 'pago', 'enviado', 'entregue', 'cancelado'.

        Returns:
            None
        """
        sql = "UPDATE pedidos SET status = %s WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (novo_status, pedido_id))

    def atualizar_total(self, pedido_id, valor_total):
        """
        Atualiza o valor total de um pedido.

        Args:
            pedido_id (int): O 'ID' do pedido a ser atualizado.
            valor_total (float): O novo valor total do pedido.

        Returns:
            None
        """
        sql = "UPDATE pedidos SET valor_total = %s WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (valor_total, pedido_id))

    def buscar_produtos_em_pedidos_cancelados(self):
        """
        Busca todos os produtos que apareceram em pedidos cancelados, com quantidade e data do pedido.

        Returns:
            list of dict: Cada dicionário contém:
                - produto (str): Nome do produto.
                - quantidade (int): Quantidade do produto no pedido cancelado.
                - data (datetime): Data de criação do pedido cancelado.
        """
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
        """
        Cancela pedidos pendentes que estão há mais de 48 horas sem atualização.

        Returns:
            int: Número de pedidos que foram cancelados.
        """
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
        """
        Busca pedidos pendentes que estão há mais de 12 horas e ainda não receberam o próximo alerta.
        O cálculo do intervalo considera o número de alertas já enviados (máximo de 3).

        Returns:
            list of dict: Cada dicionário contém:
                - pedido_id (int): ID do pedido.
                - cliente_nome (str): Nome do cliente.
                - cliente_email (str): Email do cliente.
                - total_alertas (int): Número de alertas já enviados para este pedido.
        """
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
        """
        Incrementa o contador de alertas enviados para um pedido.

        Args:
            pedido_id (int): O 'ID' do pedido cujo contador de alertas será incrementado.

        Returns:
            None
        """
        sql = "UPDATE pedidos SET alertas_enviados = alertas_enviados + 1 WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql , (pedido_id,))

    def listar_por_usuario(self, usuario_id):
        """
        Busca todos os cabeçalhos de pedido de um usuário específico.
        """
        sql = """
            SELECT id, data_criacao, status, valor_total
            FROM pedidos
            WHERE usuario_id = %s
            ORDER BY data_criacao DESC;
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchall()

    def listar_itens_por_pedido(self, pedido_id):
        """
        Busca os itens de um pedido, trazendo o nome e a foto do produto (JOIN)
        """
        sql = """
            SELECT p.id, p.nome, p.url_imagem, ip.quantidade, ip.preco_unitario
            FROM itens_pedido ip
            JOIN produtos p ON ip.produto_id = p.id
            WHERE ip.pedido_id = %s;
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql, (pedido_id,))
            return cursor.fetchall()