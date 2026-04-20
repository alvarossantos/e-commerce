from src.database.conexao import BancoDeDados
from src.models.produto_model import ProdutoModel


class ProdutoRepository:
    def criar(self, produto: ProdutoModel, cursor_externo=None):
        sql = """
            INSERT INTO produtos (nome, sku, preco, descricao, codigo_barras, categoria)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            produto.nome,
            produto.sku,
            produto.preco,
            produto.descricao,
            produto.codigo_barras,
            produto.categoria
        )

        with BancoDeDados() as cursor:
            cursor.execute(sql, params)
            novo_id = cursor.fetchone()
            return novo_id[0]

    def listar_todos(self):
        sql = """SELECT nome, sku, preco, descricao, codigo_barras, categoria, criado_em, id "
               "FROM produtos "
               "ORDER BY criado_em DESC;"""
        produtos = []
        with BancoDeDados() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                produtos.append(ProdutoModel(
                    nome=row[0],
                    sku=row[1],
                    preco=row[2],
                    descricao=row[3],
                    codigo_barras=row[4],
                    categoria=row[5],
                    criado_em=row[6],
                    id=row[7]
                ))
        return produtos

    def buscar_por_categoria(self, categoria):
        sql = """
            SELECT nome, sku, preco, descricao, codigo_barras, categoria, criado_em, id
            FROM produtos
            WHERE categoria = %s;
        """
        produtos = []
        with BancoDeDados() as cursor:
            cursor.execute(sql, (categoria,))
            rows = cursor.fetchall()
            for row in  rows:
                produtos.append(ProdutoModel(
                    nome=row[0],
                    sku=row[1],
                    preco=row[2],
                    descricao=row[3],
                    codigo_barras=row[4],
                    categoria=row[5],
                    criado_em=row[6],
                    id=row[7]
                ))
        return produtos

    def buscar_por_id(self, id):
        sql = """
            SELECT nome, sku, preco, descricao, codigo_barras, categoria, criado_em
            FROM produtos
            WHERE id = %s;
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql, (id,))
            # Atribuímos o resultado da consulta à variável 'row'
            row = cursor.fetchone()

            if row:
                # Retorna um dicionário com os dados mapeados
                return ProdutoModel(
                    nome=row[0],
                    sku=row[1],
                    preco=row[2],
                    descricao=row[3],
                    codigo_barras=row[4],
                    categoria=row[5],
                    criado_em=row[6],
                    id=id # Passando o ID para o construtor
                )

            # Caso não encontre nada, retorna None
            return None