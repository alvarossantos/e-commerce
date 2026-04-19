class EstoqueModel:
    def __init__(self, produto_id, quantidade, estoque_minimo, ultima_atualizacao=None):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.estoque_minimo = estoque_minimo
        self.ultima_atualizacao = ultima_atualizacao

        if self.quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        if self.estoque_minimo < 0:
            raise ValueError("O estoque mínimo não pode ser negativo.")

    def precisa_repor(self):
        """Retorna True se a quantidade atual for menor ou igual ao mínimo"""
        return self.quantidade <= self.estoque_minimo
