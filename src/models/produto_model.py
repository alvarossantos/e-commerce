# ========================================================================================
# CONCEITO DE ARQUITETURA LÓGICA: CAMADA DE NEGÓCIOS / DOMÍNIO (Business Layer)
# Papel da Model: Representa as entidades centrais e as regras estritas do negócio.
# É aqui que ocorrem as validações puras (ex: verificar se um CPF é válido ou se o
# preço é negativo). A Model é "cega" em relação ao banco de dados e à interface web;
# ela apenas garante a integridade da informação antes de ser persistida.
# ========================================================================================


class ProdutoModel:
    def __init__(self, nome, sku, preco, descricao, codigo_barras, categoria, url_imagem, criado_em=None, id=None):
        self.id = id
        self.nome = nome
        self.sku = sku
        self.verificar_valor(preco)
        self.descricao = descricao
        self.codigo_barras = codigo_barras
        self.categoria = categoria
        self.url_imagem = url_imagem
        self.criado_em = criado_em

    def verificar_valor(self, preco):
        if preco <= 0:
            raise ValueError("O valor unitário deve ser maior que zero.")

        self.preco = preco
