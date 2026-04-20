from src.repository.pedido_repository import PedidoRepository
from src.services.email_service import EmailService


class VendaService:
    def __init__(self):
        self.pedido_repo = PedidoRepository()

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
