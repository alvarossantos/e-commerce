import bcrypt


class Seguranca:
    # Os métodos estáticos (pertencem à classe, não ao objeto)

    # Transforma a senha do usuário em um hash (chave)
    @staticmethod
    def gerar_hash(senha_plana: str) -> str:
        # 1. Converte a senha_plana para bytes usando o encode
        senha_bytes = senha_plana.encode('utf-8')

        # 2. Gera o salt (é como uma chave aleatória)
        salt = bcrypt.gensalt()

        # 3. Gera o hash usando o bcrypt.hashpw(senha_bytes, salt)
        hash_bytes = bcrypt.hashpw(senha_bytes, salt)

        # 4. Converte de volta para string para salvar no banco
        return hash_bytes.decode('utf-8')

    # Verifica se o hash de login é igual ao hash do banco
    @staticmethod
    def verificar_senha(senha_plana: str, hash_salvo: str) -> bool:
        # O bcrypt tem a função pronta de comparar, bcrypt.checkpw
        # Compara e retorna um booleano
        return bcrypt.checkpw(
            senha_plana.encode('utf-8'),
            hash_salvo.encode('utf-8')
        )