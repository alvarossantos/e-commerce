from src.database.conexao import BancoDeDados
from src.models.estoque_model import EstoqueModel
from src.models.produto_model import ProdutoModel


class EstoqueRepository:
    def buscar_produtos_em_alerta(self, produto: ProdutoModel, estoque: EstoqueModel):
        sql = """
            SELECT p.nome, e.quantidade
            FROM produtos p
            JOIN estoque e ON p.id = e.produto_id
            WHERE e.quantidade <= e.estoque_minimo 
       """
        alertas = []
        with BancoDeDados() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                alertas.append({
                    "produto": row[0],
                    "quantidade_atual": row[1],
                    "minimo_esperado": row[2]
                })
        return alertas