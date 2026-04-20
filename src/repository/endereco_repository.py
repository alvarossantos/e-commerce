from src.database.conexao import BancoDeDados


class EnderecoRepository:
    def criar(self, usuario_id, dados:dict):
        sql = """
            INSERT INTO endereco (usuario_id, logradouro, numero, bairro, cidade, estado, cep, complemento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        params = (
            usuario_id, dados['rua'], dados['numero'], dados['bairro'],
            dados['cidade'], dados['estado'], dados['cep'], dados.get('complemento')
        )
        with BancoDeDados() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()[0]

    def listar_por_usuario(self, usuario_id):
        sql = "SELECT * FROM enderecos WHERE usuario_id = %s ORDER BY criado_em DESC;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (usuario_id,))

            # Retorna a lista de tuplas/dicionários
            return cursor.fetchall()