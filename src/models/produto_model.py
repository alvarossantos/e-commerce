class ProdutoModel:
    def __init__(self, nome, sku, preco, descricao, codigo_barras, categoria, criado_em, id=None):
        self.id = id
        self.nome = nome
        self.sku = sku
        self.verificar_valor(preco)
        self.descricao = descricao
        self.codigo_barras = codigo_barras
        self.categoria = categoria
        self.criado_em = criado_em

    def verificar_valor(self, preco):
        if preco <= 0:
            raise ValueError("O valor unitário deve ser maior que zero.")
