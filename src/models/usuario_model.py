import re
from datetime import datetime


class UsuarioModel:
    def __init__(self, nome, email, senha_hash, ativo, data_nascimento, cpf, telefone, endereco, id=None, criado_em=None):
        self.id = id
        self.nome = nome
        self.verificar_email(email)
        self.senha_hash = senha_hash
        self.verificar_cpf(cpf)
        self.verificar_idade(data_nascimento)
        self.verificar_telefone(telefone)
        self.endereco = endereco
        self.criado_em = criado_em
        self.ativo = ativo

    def verificar_email(self, email):
        if "@" in email:
            self.email = email
        else:
            raise ValueError(f"Email inválido, não possui '@': {email}")

    def verificar_cpf(self, cpf):
        if cpf.isdigit() and len(cpf) == 11:
            self.cpf = cpf
        else:
            raise ValueError(f"CPF inválido, somente números são aceitos e deve ter 11 digitos.")

    def verificar_telefone(self, telefone):
        # Remove caracteres não numéricos
        telefone = re.sub('[^0-9]', '', telefone)

        # Regex para telefone brasileiro (DDD 2 dígitos + 9 dígitos começando com 9)
        padrao = r'^([0-9]{2})9[0-9]{8}$'
        aceito = bool(re.match(padrao, telefone))
        if aceito:
            print(f"Telefone válido: {telefone}")
            self.telefone = telefone
        else:
            raise ValueError(f"Telefone inválido: {telefone}")

    def verificar_idade(self, data_nascimento):
        data_nasc = datetime.strptime(data_nascimento, '%Y-%m-%d')
        data_atual = datetime.now()

        # Calcula idade em anos
        idade = data_atual.year - data_nasc.year

        # Ajusta a idade se o aniversário do ano atual ainda não aconteceu
        if (data_atual.month, data_atual.day) < (data_nasc.month, data_nasc.day):
            idade -= 1

        # Verificação de maioridade
        if idade >= 18:
            print(f"O usuário tem {idade} anos.")
            self.data_nascimento = data_nascimento
        else:
            raise ValueError(f"O usuário tem {idade} anos, não pode realizar compra.")