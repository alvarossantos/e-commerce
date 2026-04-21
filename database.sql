---
-- CONFIGURAÇÕES INICIAIS
---

-- Extensão opcional para suporte a UUID (caso queira trocar SERIAL por UUID no futuro)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

---
-- CRIAÇÃO DAS TABELAS (DDL)
---

-- Tabela de Usuários: Armazena as informações básicas de quem acessa o sistema
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,                   -- Identificador único autoincrementado
    nome VARCHAR(100) NOT NULL,              -- Nome completo do usuário
    email VARCHAR(150) UNIQUE NOT NULL,      -- Email único (usado para login)
    senha_hash TEXT NOT NULL,                -- Hash da senha (nunca salvar texto plano!)
    cpf VARCHAR(11) UNIQUE NOT NULL,        -- CPF (apenas números)
    data_nascimento DATE NOT NULL,           -- Data de nascimento (AAAA-MM-DD)
    telefone VARCHAR(15),                   -- Formatos como (11) 99999-9999
    url_foto TEXT DEFAULT '/static/img/usuarios/default.png',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Data de registro
    ativo BOOLEAN DEFAULT TRUE               -- Define se o usuário pode logar
);

-- Tabela de Endereços: Armazena os endereços de cada usuário
CREATE TABLE enderecos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    logradouro VARCHAR(255) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    bairro VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    cep CHAR(8) NOT NULL,
    complemento VARCHAR(100),
    principal BOOLEAN DEFAULT false,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Produtos: Cadastro do catálogo de itens
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    sku VARCHAR(50) UNIQUE,                          -- Código de estoque único
    preco DECIMAL(10, 2) NOT NULL CHECK (preco >= 0), -- Preço não pode ser negativo
    descricao TEXT,
    codigo_barras VARCHAR(13) UNIQUE,                -- Padrão EAN-13, por exemplo
    categoria VARCHAR(100),                          -- Classificação do item
    url_imagem TEXT DEFAULT '/static/img/produtos/placeholder.png',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Estoque: Controla a quantidade disponível de cada produto
CREATE TABLE estoque (
    produto_id INTEGER PRIMARY KEY REFERENCES produtos(id) ON DELETE CASCADE, -- 1:1 com produtos
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),            -- Não permite estoque negativo
    estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),                    -- Alerta para reposição
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pedidos: Cabeçalho das vendas realizadas
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id), -- Quem comprou
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Status controlado por CHECK para integridade dos dados
    status VARCHAR(20) DEFAULT 'pendente'
        CHECK (status IN ('pendente', 'pago', 'enviado', 'entregue', 'cancelado')),
    valor_total DECIMAL(10, 2) DEFAULT 0.00, -- Valor total do pedido (soma dos itens)
    alertas_enviados INTEGER DEFAULT 0
);

-- Tabela de Itens do Pedido: Relacionamento Muitos-para-Muitos entre Pedidos e Produtos
CREATE TABLE itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario DECIMAL(10, 2) NOT NULL,

    -- Impede que o mesmo produto seja inserido duas vezes como linhas separadas no mesmo pedido
    CONSTRAINT unique_produto_pedido UNIQUE (pedido_id, produto_id)
);

---
-- ÍNDICES (Otimização de busca)
---

CREATE INDEX idx_pedidos_usuario ON pedidos(usuario_id);     -- Acelera histórico de pedidos por usuário
CREATE INDEX idx_itens_pedido_pedido ON itens_pedido(pedido_id); -- Acelera listagem de itens de um pedido
CREATE INDEX idx_pedidos_status ON pedidos(status);         -- Acelera filtros por status (ex: "pedidos pendentes")

---
-- FUNÇÕES E TRIGGERS (Automação de Regras de Negócio)
---

-- 1. Atualizar automaticamente a data de 'atualizado_em' na tabela de produtos
CREATE OR REPLACE FUNCTION atualizar_data_modificacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER tg_atualizar_produtos_data
BEFORE UPDATE ON produtos
FOR EACH ROW EXECUTE PROCEDURE atualizar_data_modificacao();


-- 2. Baixar o estoque automaticamente quando um item for adicionado ao pedido
CREATE OR REPLACE FUNCTION baixar_estoque_apos_venda()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE estoque
    SET quantidade = quantidade - NEW.quantidade
    WHERE produto_id = NEW.produto_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_baixar_estoque_venda
AFTER INSERT ON itens_pedido
FOR EACH ROW EXECUTE PROCEDURE baixar_estoque_apos_venda();


-- 3. Devolver produtos ao estoque caso o pedido seja cancelado
CREATE OR REPLACE FUNCTION gerenciar_cancelamento_pedido()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se o status mudou especificamente de qualquer coisa para 'cancelado'
    IF (OLD.status <> 'cancelado' AND NEW.status = 'cancelado') THEN
        UPDATE estoque e
        SET quantidade = e.quantidade + ip.quantidade
        FROM itens_pedido ip
        WHERE ip.pedido_id = NEW.id AND e.produto_id = ip.produto_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_cancelamento_pedido_estoque
AFTER UPDATE ON pedidos
FOR EACH ROW EXECUTE PROCEDURE gerenciar_cancelamento_pedido();

-- 1. Inserindo os Produtos no Catálogo
INSERT INTO produtos (nome, sku, preco, descricao, codigo_barras, categoria) VALUES
('Processador AMD Ryzen 7 5800X', 'HW-AMD-5800X', 1850.00, 'Processador de alta performance com 8 núcleos e 16 threads, ideal para jogos pesados e renderização 3D.', '7301433127451', 'Hardware'),
('Placa de Vídeo NVIDIA RTX 4060 Ti', 'HW-NV-4060TI', 2799.90, 'Placa de vídeo com 8GB GDDR6, suporte a Ray Tracing e DLSS 3 para máximo desempenho.', '8435156489721', 'Hardware'),
('Placa Mãe Asus TUF Gaming B550M', 'HW-AS-B550M', 950.00, 'Placa mãe micro-ATX com excelente construção térmica e suporte a PCIe 4.0.', '4718017823561', 'Hardware'),
('Teclado Mecânico HyperX Alloy Origins', 'PER-HX-ALLOY', 450.00, 'Teclado mecânico com switches vermelhos (Lineares) e iluminação RGB customizável.', '7406172886032', 'Periféricos'),
('Mouse Gamer Logitech G Pro Wireless', 'PER-LG-GPRO', 580.00, 'Mouse sem fio ultraleve (80g) com sensor HERO 25K para e-sports.', '0978551421063', 'Periféricos'),
('Headset Gamer Cloud II Vermelho', 'PER-HX-CL2', 499.90, 'Fones de ouvido com som surround 7.1 virtual e almofadas de espuma memory foam.', '7406172356710', 'Periféricos'),
('Monitor LG UltraGear 24" 144Hz', 'MON-LG-24GN', 1100.00, 'Monitor IPS de 24 polegadas com tempo de resposta de 1ms e taxa de atualização de 144Hz.', '8806091325471', 'Monitores'),
('Monitor Dell 27" 4K USB-C', 'MON-DL-274K', 2850.00, 'Monitor focado em produtividade e design com resolução 4K e hub USB-C integrado.', '5397184512034', 'Monitores');

-- 2. Inserindo o Estoque (Assumindo que os IDs gerados acima foram de 1 a 8)
-- O campo 'estoque_minimo' é o que você configurou para dar alerta!
INSERT INTO estoque (produto_id, quantidade, estoque_minimo) VALUES
(1, 15, 5),   -- Ryzen 7 (15 em estoque)
(2, 8, 3),    -- RTX 4060 Ti (8 em estoque)
(3, 20, 5),   -- Placa Mãe B550M
(4, 50, 10),  -- Teclado HyperX
(5, 35, 10),  -- Mouse Logitech
(6, 40, 10),  -- Headset Cloud II
(7, 12, 4),   -- Monitor UltraGear
(8, 5, 2);    -- Monitor Dell 4K (Pouco estoque!)