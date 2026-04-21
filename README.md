# 🛒 Plataforma de E-Commerce

Uma plataforma completa de e-commerce construída com Python, Flask e PostgreSQL. Este projeto implementa uma loja online completa com gerenciamento de usuários, catálogo de produtos, carrinho de compras, processamento de pedidos e muito mais.

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Esquema do Banco de Dados](#esquema-do-banco-de-dados)
- [Instalação](#instalação)
- [Uso](#uso)
- [Endpoints da API](#endpoints-da-api)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Visão Geral

Esta plataforma de e-commerce é uma aplicação web projetada para simular uma loja online. Ela segue a arquitetura MVC (Model-View-Controller) com separação clara de responsabilidades:

- **Models**: Lógica de negócio e entidades de dados
- **Views**: Templates HTML e camada de apresentação
- **Controllers**: Tratamento de requisições e orquestração de negócio
- **Repository**: Camada de acesso aos dados com consultas SQL
- **Services**: Integrações externas (email, gateways de pagamento)

## ✨ Funcionalidades

### Gerenciamento de Usuários
- Registro de usuários com validação (email, CPF, telefone, idade)
- Login/logout seguro com gerenciamento de sessões
- Hash de senhas usando bcrypt
- Gerenciamento de perfil (upload de foto, livro de endereços)
- Controle de acesso baseado em papéis (usuário/admin)

### Catálogo de Produtos
- Listagem de produtos com paginação
- Páginas detalhadas de produtos com imagens e descrições
- Categorização de produtos
- Busca e filtragem de produtos
- Sistema de avaliações e comentários

### Experiência de Compra
- Funcionalidade de carrinho de compras
- Lista de desejos/favoritos
- Processo de checkout seguro
- Histórico e rastreamento de pedidos
- Simulação de múltiplos métodos de pagamento

### Funcionalidades Admin
- Gerenciamento de produtos (operções CRUD)
- Controle de estoque
- Gerenciamento de pedidos
- Administração de usuários
- Relatórios de vendas e análises

### Características Técnicas
- Design de API RESTful
- Interface web responsiva
- Suporte para migrações de banco de dados
- Configuração de ambiente
- Tratamento de erros e logging
- Validação e sanitização de entradas

## 🏗️ Estrutura do Projeto

```
projeto-ecommerce/
├── main.py                  # Ponto de entrada da aplicação
├── database.sql             # Esquema do banco e dados de exemplo
├── requirements.txt         # Dependências Python
├── .env.example             # Modelo de variáveis de ambiente
├── README.md                # Este arquivo
├── estrutura                # Documentação da estrutura do projeto
├── src/
│   ├── controllers/         # Manipuladores de requisições HTTP
│   │   ├── usuario_controller.py
│   │   ├── produto_controller.py
│   │   ├── pedido_controller.py
│   │   └── seguranca.py
│   ├── models/              # Entidades de lógica de negócio
│   │   ├── usuario_model.py
│   │   ├── produto_model.py
│   │   └── estoque_model.py
│   ├── views/               # Camada de apresentação
│   │   ├── app.py           # Aplicação Flask
│   │   ├── templates/       # Templates HTML
│   │   │   ├── index.html
│   │   │   ├── produto_detalhes.html
│   │   │   ├── login.html
│   │   │   ├── cadastro.html
│   │   │   └── perfil.html
│   │   └── static/          # Arquivos estáticos
│   │       ├── img/
│   │       │   ├── produtos/
│   │       │   └── usuarios/
│   │       └── uploads/
│   ├── repository/          # Camada de acesso aos dados
│   │   ├── usuario_repository.py
│   │   ├── produto_repository.py
│   │   ├── pedido_repository.py
│   │   ├── endereco_repository.py
│   │   ├── estoque_repository.py
│   │   └── avaliacao_repository.py
│   ├── services/            # Serviços externos
│   │   ├── email_service.py
│   │   └── venda_service.py
│   └── database/            # Utilitários de banco de dados
│       └── conexao.py
└── venv/                    # Ambiente virtual
```

## 🗄️ Esquema do Banco de Dados

A plataforma utiliza PostgreSQL com as seguintes tabelas:

### Entidades Principais
- **usuarios**: Contas e perfis de usuários
- **enderecos**: Endereços dos usuários (relação um-para-muitos)
- **produtos**: Catálogo de produtos
- **estoque**: Gestão de inventário
- **avaliacoes**: Avaliações e comentários de produtos

### Entidades de Transação
- **pedidos**: Cabeçalhos dos pedidos
- **itens_pedido**: Itens dos pedidos

### Características Principais
- Suporte a UUID (comentado para futura migração)
- Atualização automática de timestamps
- Triggers para controle automático de estoque
- Integridade referencial com exclusão em cascata
- Índices para otimização de performance
- Dados de exemplo para testes imediatos

## 🔧 Instalação

### Pré-requisitos
- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

### Instruções de Configuração

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositório>
   cd e-commerce
   ```

2. **Crie o ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o ambiente**
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais do banco de dados
   ```

5. **Inicialize o banco de dados**
   ```bash
   # Crie o banco de dados
   createdb ecommerce
   
   # Aplique o esquema e dados de exemplo
   psql -d ecommerce -f database.sql
   ```

6. **Execute a aplicação**
   ```bash
   python src/views/app.py
   ```

7. **Acesse a aplicação**
   Abra seu navegador em: http://localhost:5000

## 🚀 Uso

### Contas Padrão
Após executar o script do banco de dados, você pode testar com:
- **Admin**: Use o formulário de registro para criar uma conta de administrador
- **Usuários Comuns**: Registre-se através da interface web

### Fluxos de Trabalho Principais

#### Navegando por Produtos
1. Visite a página inicial para ver produtos em destaque
2. Clique em qualquer produto para ver os detalhes
3. Leia as avaliações e verifique a disponibilidade

#### Registro de Usuário
1. Clique em "Cadastro" na navegação
2. Preencha os campos obrigatórios (nome, email, senha, CPF, etc.)
3. Envie o formulário e verifique o email para confirmação
4. Faça login com suas credenciais

#### Realizando uma Compra
1. Navegue pelos produtos e adicione ao carrinho
2. Revise o conteúdo do carrinho
3. Prossiga para o checkout
4. Preencha as informações de envio e pagamento
5. Confirme o pedido

#### Gerenciando o Perfil
1. Faça login em sua conta
2. Navegue até "Perfil"
3. Atualize a foto do perfil
4. Gerencie endereços
5. Visualize o histórico de pedidos

## 🔌 Endpoints da API

### Autenticação
- `POST /login` - Login do usuário
- `POST /cadastro` - Registro de novo usuário
- `GET /sair` - Logout do usuário

### Produtos
- `GET /` - Listar todos os produtos
- `GET /produto/<int:id>` - Obter detalhes de um produto
- `POST /produto/<int:id>/avaliar` - Enviar avaliação de produto

### Perfil do Usuário
- `GET /perfil` - Visualizar perfil do usuário
- `POST /perfil/foto` - Atualizar foto do perfil
- `POST /perfil/endereco` - Adicionar novo endereço

### Carrinho e Pedidos
- `GET /carrinho` - Visualizar carrinho de compras
- `GET /meus-pedidos` - Visualizar histórico de pedidos

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.14** - Linguagem de programação principal
- **Flask 2.3+** - Framework web
- **PostgreSQL** - Banco de dados relacional
- **PSQL** - Adaptador de banco de dados
- **Werkzeug** - Utilitários de segurança

### Frontend
- **HTML5** - Linguagem de marcação
- **CSS3** - Estilização
- **Bootstrap 5** - Framework de UI (via CDN)
- **JavaScript** - Interatividade do lado do cliente

### Ferramentas de Desenvolvimento
- **Git** - Controle de versão
- **Virtualenv** - Isolamento de ambiente
- **PSQL** - Gerenciamento de banco de dados
- **Flask Debug Toolbar** - Assistência para desenvolvimento

## 📦 Dependências

Veja `requirements.txt` para a lista completa:
- Flask
- psycopg2-binary
- python-dotenv
- Werkzeug
- bcrypt

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, siga estes passos:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/recurso-incrivel`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona recurso incrível'`)
4. Push para a branch (`git push origin feature/recurso-incrível`)
5. Abra um Pull Request

### Diretrizes de Desenvolvimento
- Siga os padrões PEP 8 de codificação
- Escreva mensagens de commit significativas
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário
- Mantenha compatibilidade com versões anteriores

## 🐛 Problemas Conhecidos

- Funcionalidade do carrinho está simulada (não totalmente implementada)
- Processamento de pagamento usa gateway mock
- Serviço de email requer configuração SMTP
- Painel administrativo precisa de implementação
- Validação de upload de imagens de produtos poderia ser melhorada

## 🔜 Melhorias Futuras

- [ ] Implementação completa do carrinho de compras
- [ ] Integração com gateways de pagamento (Stripe/PayPal)
- [ ] Painel administrativo com analytics
- [ ] Busca de produtos com filtros
- [ ] Funcionalidade de lista de desejos/salvar para depois
- [ ] Notificações por email para pedidos
- [ ] Geração de faturas em PDF
- [ ] Documentação da API RESTful (Swagger)
- [ ] Containerização com Docker
- [ ] Testes unitários e de integração
- [ ] Configuração de pipeline CI/CD

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Agradecimentos

- Comunidade open source pelo Flask e bibliotecas relacionadas
- Equipe do PostgreSQL pelo excelente sistema de banco de dados
- Contribuintes do Bootstrap pelo framework frontend
- Todos os contribuintes deste projeto

---

**Boa codificação!** Se você achar este projeto útil, considere dar uma estrela ⭐

Última atualização: Abril de 2026