# ========================================================================================
# CONCEITO DE ARQUITETURA LÓGICA: CAMADA DE ACESSO A DADOS (Data Access Layer)
# Papel do Repository: Isolar e centralizar toda a comunicação física com o banco de dados.
# Esta é a ÚNICA camada do sistema autorizada a conter código SQL (INSERT, SELECT, etc.)
# e a interagir com a biblioteca psycopg2. Isso permite que, se mudarmos o banco de dados
# no futuro (ex: para MySQL), apenas esta pasta precisará ser alterada.
# ========================================================================================


from src.database.conexao import BancoDeDados
from src.models.estoque_model import EstoqueModel
from src.models.produto_model import ProdutoModel


class EstoqueRepository:
    def buscar_produtos_em_alerta(self, produto: ProdutoModel, estoque: EstoqueModel):
        sql = """
            SELECT p.nome, e.quantidade, e.estoque_minimo
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