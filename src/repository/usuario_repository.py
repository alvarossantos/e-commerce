# ========================================================================================
# CONCEITO DE ARQUITETURA LÓGICA: CAMADA DE ACESSO A DADOS (Data Access Layer)
# Papel do Repository: Isolar e centralizar toda a comunicação física com o banco de dados.
# Esta é a ÚNICA camada do sistema autorizada a conter código SQL (INSERT, SELECT, etc.)
# e a interagir com a biblioteca psycopg2. Isso permite que, se mudarmos o banco de dados
# no futuro (ex: para MySQL), apenas esta pasta precisará ser alterada.
# ========================================================================================


from src.database.conexao import BancoDeDados
from src.models.usuario_model import UsuarioModel


class UsuarioRepository:
    def criar(self, usuario: UsuarioModel):
        """
        Cria um novo usuário no banco de dados.

        Args:
            usuario (UsuarioModel): Objeto contendo todos os dados do usuário a ser criado.
                                   Deve incluir nome, email, senha_hash, cpf, telefone,
                                   endereco e data_nascimento.

        Returns:
            int: O 'ID' do novo usuário gerado pelo banco de dados.
                 Também atualiza o atributo 'id' do objeto usuario passado como parâmetro.
        """
        sql = """
            INSERT INTO usuarios (nome, email, senha_hash, cpf, data_nascimento, telefone)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            usuario.nome,
            usuario.email,
            usuario.senha_hash,
            usuario.cpf,
            usuario.data_nascimento,
            usuario.telefone
        )

        with BancoDeDados() as cursor:
            cursor.execute(sql, params)
            # Atualizamos o ID do próprio objeto para que o restante do sistema saiba qual é
            novo_id = cursor.fetchone()[0]
            return novo_id

    def buscar_por_email(self, email: str):
        """
        Busca um usuário pelo seu email no banco de dados.

        Args:
            email (str): Email do usuário a ser buscado (deve ser único no sistema).

        Returns:
            UsuarioModel: Objeto contendo todos os dados do usuário se encontrado.
                         Retorna None se nenhum usuário com esse email existir.
        """
        sql = """
            SELECT id, nome, email, senha_hash, cpf, data_nascimento, telefone, criado_em, ativo, is_admin
            FROM usuarios
            WHERE email = %s;
        """
        with BancoDeDados() as cursor:
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            if row:
                # Reconstruindo o objeto com os dados vindos do banco
                return UsuarioModel(
                    id=row[0],
                    nome=row[1],
                    email=row[2],
                    senha_hash=row[3],
                    cpf=row[4],
                    data_nascimento=str(row[5]),
                    telefone=row[6],
                    criado_em=row[7],
                    ativo=row[8],
                    is_admin=row[9]
                )
            return None

    def atualizar_foto(self, usuario_id, caminho_foto):
        sql = "UPDATE usuarios SET url_foto = %s WHERE id = %s;"
        with BancoDeDados() as cursor:
            cursor.execute(sql, (caminho_foto, usuario_id))
