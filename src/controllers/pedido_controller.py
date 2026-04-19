from src.repository.pedido_repository import PedidoRepository
from src.repository.produto_repository import ProdutoRepository
from src.models.produto_model import ProdutoModel


class PedidoController:
    def __init__(self):
        self.pedido_repo = PedidoRepository()
        self.produto_repo = ProdutoRepository()
        self.produto_db = ProdutoModel()

    def finalizar_venda(self, usuario_id, itens_do_carrinho):
        id_pedido = self.pedido_repo.criar(usuario_id)

        for item in itens_do_carrinho:
            # Buscamos o preço MAIS ATUAL do banco no momento do fechamento
            produto_atual = self.produto_repo.buscar_por_id(item['produto_id'])
            preco_no_fechamento = produto_atual.preco

            # Gravamos o preço que buscamos AGORA, não o que estava no carrinho antes
            self.pedido_repo.inserir_item(id_pedido, item['produto_id'], item['qtd'], preco_no_fechamento)

    def validar_e_finalizar(self, usuario_id, itens_vinda_da_tela):
        itens_com_preco_alterado = []

        for item in itens_vinda_da_tela:
            # 1. Buscamos o preço atualizado no banco
            produto_db = self.produto_repo.buscar_por_id(item['id'])

            # 2. Comparamos com o preço que o usuário viu na tela
            if produto_db.preco != item['preco_visualizado']:
                itens_com_preco_alterado.append({
                    "nome": produto_db.nome,
                    "preco_antigo": item['preco_visualizado'],
                    "preco_novo": produto_db.preco
                })

        # 3. Decisão do Controller
        if itens_com_preco_alterado:
            # Se houve mudança, paramos o processo e devolvemos os detalhes
            return {
                "status": "aviso",
                "mensagem": "Alguns preços mudaram desde que você adicionou ao carrinho.",
                "alteracoes": itens_com_preco_alterado
            }, 409 # Status de conflito

        # 4. Se não houver alteração, segue para a criação do pedido...