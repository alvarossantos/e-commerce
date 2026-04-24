from src.repository.pedido_repository import PedidoRepository
from src.repository.produto_repository import ProdutoRepository
from src.services.email_service import EmailService


class VendaService:
    def __init__(self):
        self.pedido_repo = PedidoRepository()
        self.produto_repo = ProdutoRepository()

    def realizar_venda(self, usuario_id, carrinho, endereco_id):
        """
        Comanda a criação de um pedido: calcula o total e salva no banco.
        carrinho é um dicionário no formato {'id_produto': quantidade}
        """
        valor_total = 0

        # 1. Calcula o valor total seguro (direto do banco de dados, ignorando HTML)
        for produto_id_str, quantidade in carrinho.items():
            produto_id = int(produto_id_str)
            produto = self.produto_repo.buscar_por_id(produto_id)

            if not produto:
                raise ValueError(f"Produto ID {produto_id} não encontrado.")

            valor_total += (produto.preco * quantidade)

        # 2. Envia para o repositório criar o cabeçalho do pedido e os itens
        pedido_id = self.pedido_repo.criar_pedido(usuario_id, endereco_id, valor_total, carrinho, self.produto_repo)

        return pedido_id

    def processar_notificacao_e_cancelamento(self):
        # 1. Envia Alertas de 12h/24h/36h
        pedidos_para_avisar = self.pedido_repo.buscar_pendentes_para_notificacao()
        for p in pedidos_para_avisar:
            assunto = "Lembrete de Compra"
            if p['total_alertas'] == 2:
                assunto = "ÚLTIMO AVISO: Seu pedido será cancelado!"

            mensagem = f"Olá {p['cliente_nome']}, seu pedido #{p['pedido_id']} está aguardando pagamento..."
            sucesso = EmailService.enviar_email(p['cliente_email'], "Lembrete de Compra", mensagem)

            if sucesso:
                self.pedido_repo.incrementar_alerta(p['pedido_id'])

        # 2. Cancela os que passaram de 48h
        total_cancelados = self.pedido_repo.cancelar_pedidos_expirados()
        if total_cancelados > 0:
            print(f"Sucesso: {total_cancelados} pedidos expirados foram cancelados e o estoque devolvido.")
