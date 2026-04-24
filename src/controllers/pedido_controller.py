# ========================================================================================
# CONCEITO DE ARQUITETURA LÓGICA: CAMADA DE NEGÓCIOS / APLICAÇÃO (Business Layer)
# Papel do Controller: Atua como o "maestro" do sistema. Ele recebe as requisições
# enviadas pela Camada de Apresentação (Views), processa as regras de negócio orquestrando
# as Models e os Services, e decide o que será enviado para a Camada de Dados (Repository).
# Essa separação garante que a regra de negócio não fique misturada com o HTML ou com o SQL.
# ========================================================================================

from src.repository.pedido_repository import PedidoRepository
from src.repository.produto_repository import ProdutoRepository
from src.models.produto_model import ProdutoModel


class PedidoController:
    def __init__(self):
        self.pedido_repo = PedidoRepository()
        self.produto_repo = ProdutoRepository()

    def finalizar_venda(self, usuario_id, endereco_id, carrinho):
        """
        Orquestra a finalização da venda.
        Calcula o total consultando o banco (para evitar fraudes) e delega a gravação.
        """
        # 1. Calcular o valor total com os preços reais do banco
        valor_total = 0
        for produto_id_str, qtd in carrinho.items():
            produto_atual = self.produto_repo.buscar_por_id(int(produto_id_str))
            if produto_atual:
                valor_total += produto_atual.preco * qtd

        # 2. Chama a função real do repositório, passando todas as informações que ele exige
        id_pedido = self.pedido_repo.criar_pedido(
            usuario_id=usuario_id,
            endereco_id=endereco_id,
            valor_total=valor_total,
            carrinho=carrinho,
            produto_repo=self.produto_repo
        )

        return id_pedido

    def validar_e_finalizar(self, usuario_id, itens_vinda_da_tela):
        """
        Regra de Negócio: Verifica se o preço mudou enquanto o cliente estava no checkout.
        """
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
            }, 409  # Status de conflito HTTP

        # 4. Se não houver alteração, o sistema seguiria para finalizar a venda
        # (Lógica simplificada para a validação)
        return {"status": "sucesso", "mensagem": "Preços validados."}, 200