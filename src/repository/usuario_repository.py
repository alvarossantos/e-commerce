from src.database.conexao import BancoDeDados
from src.models.usuario_model import UsuarioModel


class UsuarioRepository:
    def criar(self, usuario: UsuarioModel):
        sql = """
            INSERT INTO usuarios (nome, email, senha_hash, cpf, telefone, endereco, data_nascimento)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            usuario.nome,
            usuario.email,
            usuario.senha_hash,
            usuario.cpf,
            usuario.telefone,
            usuario.endereco,
            usuario.data_nascimento
        )

        with BancoDeDados() as cursor:
            cursor.execute(sql, params)
            # Atualizamos o ID do próprio objeto para que o restante do sistema saiba qual é
            novo_id = cursor.fetchone()[0]
            return novo_id

    def buscar_por_email(self, email: str):
        sql = """
            SELECT id, nome, email, senha_hash, ativo, data_nascimento, cpf, telefone, endereco, criado_em
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
                    ativo=row[4],
                    data_nascimento=str(row[5]),
                    cpf=row[6],
                    telefone=row[7],
                    endereco=row[8],
                    criado_em=row[9]
                )
            return None
