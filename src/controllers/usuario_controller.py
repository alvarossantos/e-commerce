# ========================================================================================
# CONCEITO DE ARQUITETURA LÓGICA: CAMADA DE NEGÓCIOS / APLICAÇÃO (Business Layer)
# Papel do Controller: Atua como o "maestro" do sistema. Ele recebe as requisições
# enviadas pela Camada de Apresentação (Views), processa as regras de negócio orquestrando
# as Models e os Services, e decide o que será enviado para a Camada de Dados (Repository).
# Essa separação garante que a regra de negócio não fique misturada com o HTML ou com o SQL.
# ========================================================================================

from src.models.usuario_model import UsuarioModel
from src.repository.usuario_repository import UsuarioRepository
from src.controllers.seguranca import Seguranca

class UsuarioController:
    def __init__(self):
        self.repository = UsuarioRepository()

    def registrar_usuario(self, nome, email, senha_pura, cpf, telefone, data_nascimento):
        try:
            # 1. Preparar a senha (usando a classe Seguranca)
            senha_hash = Seguranca.gerar_hash(senha_pura)

            # 2. Tentar criar o objeto (Vai disparar validações do Model)
            novo_usuario = UsuarioModel(
                nome=nome,
                email=email,
                senha_hash=senha_hash,
                ativo=True,
                data_nascimento=data_nascimento,
                cpf=cpf,
                telefone=telefone
            )

            # 3. Tenta salvar no banco via Repository
            self.repository.criar(novo_usuario)

            return {"status": "sucesso", "mensagem": "Usuário criado!", "id": novo_usuario}, 201
        except ValueError as e:
            # Erro veio das verificações do MODEL (idade, email, cpf e telefone)
            return {"status": "erro", "mensagem": str(e)}, 400

        except Exception as e:
            # Captura os erros de validação do Model (CPF inválido, Senha fraca, etc)
            print(f"Erro fatal: {e}")
            return {"status": "erro", "mensagem": "Erro interno ao criar conta."}, 500

    def fazer_login(self, email, senha_pura):
        # Busca o usuário
        usuario = self.repository.buscar_por_email(email)

        # Se o objeto usuario é None, ele não existe no banco
        if usuario is None:
            return {"status": "erro", "mensagem": "E-mail ou senha incorretos."}, 401

        # Se chegou aqui, o usuario existe. Testar a sua senha
        senha_valida = Seguranca.verificar_senha(senha_pura, usuario.senha_hash)

        if senha_valida:
            # Login com sucesso!
            return {
                "status": "sucesso",
                "mensagem": f"Bem-vindo, {usuario.nome}!",
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "is_admin": usuario.is_admin
                }
            }, 200
        else:
            # Senha errada
            return {"status": "erro", "mensagem": "Senha incorreta."}, 401