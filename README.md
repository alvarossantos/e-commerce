# NexStore — Plataforma de E-Commerce

Loja online completa construída com Python, Flask e PostgreSQL. Arquitetura MVC com camada de Repository separada, templates modernos com tema dark e animações CSS, e banco de dados robusto com triggers automáticos de estoque.

## Sumário
- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Esquema do Banco de Dados](#esquema-do-banco-de-dados)
- [Templates HTML — Interface Redesenhada](#templates-html--interface-redesenhada)
- [Instalação](#instalação)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Endpoints da API](#endpoints-da-api)
- [Tecnologias](#tecnologias)
- [Roadmap](#roadmap)

## Visão Geral
O NexStore é uma plataforma de e-commerce focada em hardware e periféricos. O projeto segue a arquitetura de **Repository Pattern**, separando claramente as responsabilidades entre cada camada:
- **Views (`app.py` + templates):** Rotas centralizadas no Flask, renderização Jinja2 e gerenciamento de sessões.
- **Controllers:** Orquestração das requisições HTTP e regras de negócio.
- **Models:** Entidades de dados e validações estruturais.
- **Repository:** Consultas SQL puro e acesso isolado ao banco de dados PostgreSQL.
- **Services:** Lógicas de negócio transversais (ex: transição de status de vendas).

## Funcionalidades

### Gerenciamento de Usuários
- Registro com validação completa (nome, e-mail único, CPF único, data de nascimento).
- Login e logout com gerenciamento de sessão Flask.
- Hash de senhas com bcrypt — senhas nunca armazenadas em texto plano.
- Perfil do usuário com upload de foto local, múltiplos endereços e histórico de pedidos.

### Painel Administrativo
- **Controle de Acesso (RBAC):** Rotas blindadas via Decorators customizados (`@admin_required`) para acesso exclusivo da administração.
- CRUD completo de produtos (criar, editar, excluir) via interface web, com upload inteligente de imagens (arquivo local ou URL).
- Gestão de pedidos com conciliação manual (Pendente ➔ Em Análise ➔ Pago ➔ Enviado).

### Experiência de Compra e Catálogo
- **Carrinho de Compras Otimizado:** Gerenciamento de estado rápido via Sessão do Flask (`session`), eliminando sobrecarga e consultas desnecessárias no banco de dados para itens não finalizados.
- Checkout seguro com seleção de endereço de entrega.
- Máquina de estados de pedidos (pendente → em_analise → pago → enviado → entregue → cancelado).
- Controle automático de estoque via triggers nativos do PostgreSQL.
- Sistema de avaliações (1–5 estrelas).
- Proteção CSRF em todos os formulários via Flask-WTF + CSRFProtect.

## Estrutura do Projeto
```text
e-commerce/
├── database.sql                  # Esquema completo do banco + triggers
├── requirements.txt              # Dependências Python
├── .env.example                  # Modelo de variáveis de ambiente
├── README.md                     # Este arquivo
└── src/
    ├── views/                    # Camada de Apresentação (Frontend)
    │   ├── app.py                # Ponto de entrada e centralizador de rotas
    │   ├── templates/            # Telas Jinja2 (Base, Admin, Cliente, etc.)
    │   └── static/               # CSS, JS e Uploads (Imagens locais)
    ├── controllers/              # Processamento de Requisições
    │   ├── usuario_controller.py 
    │   └── pedido_controller.py  
    ├── models/                   # Entidades de Dados
    │   ├── usuario_model.py      
    │   ├── produto_model.py      
    │   └── estoque_model.py      
    ├── repository/               # Consultas SQL Isoladas
    │   ├── usuario_repository.py
    │   ├── produto_repository.py
    │   ├── pedido_repository.py
    │   ├── endereco_repository.py
    │   ├── estoque_repository.py
    │   └── avaliacao_repository.py
    ├── services/                 # Regras de Negócio e Integrações
    │   ├── email_service.py      
    │   └── venda_service.py      
    └── database/
        └── conexao.py            # Pool de conexões com PostgreSQL
```

## Esquema do Banco de Dados
O banco utiliza PostgreSQL com tabelas relacionais robustas, índices de performance e **Triggers Automáticos**:

### Triggers PLpgSQL
1. `tg_atualizar_produtos_data`: Atualiza o timestamp `atualizado_em` automaticamente.
2. `tg_baixar_estoque_venda`: Desconta o estoque de forma atômica ao inserir um novo `item_pedido`.
3. `tg_cancelamento_pedido_estoque`: Devolve o produto ao estoque se o pedido for cancelado.

## Templates HTML — Interface Redesenhada
Todos os templates utilizam um design system próprio, herdando de `base.html`:
- **Design System Dark Mode:** Cores de fundo `#0a0a0f`, cards `#16161f` e destaque laranja `#ff6b2b`.
- **Componentes:** Navbar com glassmorphism, Flash Messages animadas, botões reutilizáveis e dropzones dinâmicas para uploads.
- **Tipografia:** Syne (display) e Space Grotesk (corpo do texto).

## Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/e-commerce.git](https://github.com/SEU_USUARIO/e-commerce.git)
   cd e-commerce
   ```
2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   # Linux/Mac:
   source venv/bin/activate       
   # Windows:
   venv\Scripts\activate          
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o ambiente copiando o `.env.example` para `.env` e inserindo suas credenciais.
5. Crie o banco de dados no PostgreSQL e execute o `database.sql` para gerar o esquema e os dados de exemplo.
6. Inicie o servidor:
   ```bash
   python src/views/app.py
   ```

## Variáveis de Ambiente (`.env`)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

SECRET_KEY=sua_chave_secreta_aqui
```

## Endpoints da API (Principais Rotas em `app.py`)
- **Autenticação:** `/login`, `/cadastro`, `/sair`
- **Catálogo:** `/`, `/produto/<id>`, `/produto/<id>/avaliar`
- **Usuário:** `/perfil`, `/perfil/foto`, `/perfil/endereco`
- **Fluxo de Compra:** `/carrinho`, `/checkout`, `/pagamento/<pedido_id>`, `/meus-pedidos`
- **Painel Admin:** `/admin`, `/admin/produtos`, `/admin/pedidos`

## Tecnologias
- **Backend:** Python 3, Flask, psycopg2-binary
- **Segurança:** Flask-WTF (Proteção CSRF), bcrypt (Hash de senhas), Werkzeug (Sanitização de arquivos)
- **Banco de Dados:** PostgreSQL 12+
- **Frontend:** HTML5, CSS3, JavaScript ES6, Bootstrap 5.3

## Roadmap

**Já implementado ✅**
- [x] Carrinho de compras rápido via Sessão (`session['carrinho']`).
- [x] Proteção severa de formulários contra CSRF com Flask-WTF.
- [x] Painel administrativo blindado com Decorators (CRUD e Gestão Logística).
- [x] Lógica atômica de estoque através de Triggers SQL.
- [x] Templates em Dark Mode com Design System moderno (NexStore UI).
- [x] Upload inteligente de imagens locais (arquivos físicos e URL).

**Próximos passos 🚀**
- [ ] Implementação do Flask Blueprints para divisão modular de rotas.
- [ ] Integração de Notificações por e-mail em mudanças de status do pedido.
- [ ] Integração com Gateway de Pagamento real (ex: Mercado Pago SDK).
- [ ] Geração de Faturas/Recibos em PDF.
