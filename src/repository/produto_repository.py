from src.database.conexao import BancoDeDados
from src.models.produto_model import ProdutoModel


class ProdutoRepository:
    def criar(self, produto: ProdutoModel, cursor_externo=None):
        """
        Cria um novo produto no banco de dados.

        Args:
            produto (ProdutoModel): Objeto contendo todos os dados do produto a ser criado.
                                   Deve incluir nome, sku, preco, descricao, codigo_barras e categoria.
            cursor_externo (cursor, opcional): Cursor de banco de dados externo para uso em transações.
                                              Se None, cria uma nova conexão.

        Returns:
            int: O 'ID' do novo produto gerado pelo banco de dados.
        """
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
        """
        Lista todos os produtos cadastrados no banco de dados, ordenados por data de criação (mais recente primeiro).

        Returns:
            list of ProdutoModel: Lista contendo todos os produtos encontrados.
                                 Retorna lista vazia se nenhum produto estiver cadastrado.
        """
        sql = """
            SELECT nome, sku, preco, descricao, codigo_barras, categoria, criado_em, url_imagem, id
            FROM produtos 
            ORDER BY criado_em DESC;
        """
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
                    url_imagem=row[7],
                    id=row[8]
                ))
        return produtos

    def buscar_por_categoria(self, categoria):
        """
        Busca todos os produtos pertencentes a uma determinada categoria.

        Args:
            categoria (str): Nome da categoria a ser filtrada.

        Returns:
            list of ProdutoModel: Lista de produtos que pertencem à categoria especificada.
                                 Retorna lista vazia se nenhum produto for encontrado.
        """
        sql = """
            SELECT nome, sku, preco, descricao, codigo_barras, categoria, criado_em, url_imagem, id
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
                    url_imagem=row[7],
                    id=row[8]
                ))
        return produtos

    def buscar_por_id(self, id):
        """
        Busca um produto pelo seu ID no banco de dados.

        Args:
            id (int): ID do produto a ser buscado.

        Returns:
            ProdutoModel: Objeto contendo todos os dados do produto se encontrado.
                         Retorna None se nenhum produto com esse ID existir.
        """
        sql = """
            SELECT nome, sku, preco, descricao, codigo_barras, categoria, criado_em, url_imagem
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
                    url_imagem=row[7],
                    id=id # Passando o ID para o construtor
                )

            # Caso não encontre nada, retorna None
            return None