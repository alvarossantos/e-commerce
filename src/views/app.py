from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session
from src.controllers.usuario_controller import UsuarioController
from src.repository.avaliacao_repository import AvaliacaoRepository
from src.repository.endereco_repository import EnderecoRepository
from src.repository.pedido_repository import PedidoRepository
from src.repository.produto_repository import ProdutoRepository
from src.services.venda_service import VendaService
from src.repository.usuario_repository import UsuarioRepository
from src.models.produto_model import ProdutoModel
import os

from werkzeug.utils import secure_filename
from functools import wraps

# Define a pasta onde este arquivo está localizado
BASE_DIR = Path(__file__).parent

# Configura as pastas de templates e static
template_dir = str(BASE_DIR/ "templates")
static_dir = str(BASE_DIR/ "static")

# Configuração para upload de produtos
UPLOAD_PRODUTOS_DIR = os.path.join('src/views/static/uploads/produtos')
os.makedirs(UPLOAD_PRODUTOS_DIR, exist_ok=True)

app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir)

# Teste para ver se os caminhos estão corretos
print(f"Buscando templates em: {template_dir}")

app.secret_key = 'sua_chave_secreta_aqui' # Necessário para mensagens de erro/sucesso

# Instanciando seus componentes existentes
produto_repo = ProdutoRepository()
usuario_ctrl = UsuarioController()
usuario_repo = UsuarioRepository()
endereco_repo = EnderecoRepository()
avaliacao_repo = AvaliacaoRepository()
venda_service = VendaService()
pedido_repo = PedidoRepository()


# PROTEÇÃO DE ROTAS (DECORATOR PARA ADMIN)
def admin_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        # Se não estiver logado ou o is_admin for falso/nulo, bloqueia
        if 'usuario_id' not in session or not session.get('is_admin'):
            flash('Acesso negado. Área restrita a administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorator_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    # Puxa todos os pedidos da loja
    pedidos = pedido_repo.listar_todos()
    return render_template('admin_pedidos.html', pedidos=pedidos)

@app.route('/admin/pedidos/<int:pedido_id>/status', methods=['POST'])
@admin_required
def admin_alterar_status_pedido(pedido_id):
    # Recebe o novo status que o admin escolheu no formulário
    novo_status = request.form.get('status')

    if novo_status in ['pendente', 'pago', 'enviado', 'entregue', 'cancelado']:
        pedido_repo.mudar_status(pedido_id, novo_status)
        flash(f'Estado do pedido #{pedido_id} alterado para {novo_status.upper()}.', 'success')
    else:
        flash('Estado inválido.', 'danger')

    return redirect(url_for('admin_pedidos'))

@app.route('/admin/produtos')
@admin_required
def admin_produtos():
    produtos = produto_repo.listar_todos()
    return render_template('admin_produtos.html', produtos=produtos)

@app.route('/admin/produtos/novo', methods=['GET', 'POST'])
@admin_required
def admin_produto_novo():
    if request.method == 'POST':
        # 1. Tentar pegar o arquivo local
        caminho_final_imagem = request.form.get('url_imagem')

        if 'foto_local' in request.files:
            arquivo = request.files['foto_local']
            if arquivo.filename != '':
                # Cria um nome seguro
                sku = request.form.get('sku', 'sem_sku')
                filename = secure_filename(f"prod_{sku}_{arquivo.filename}")
                caminho_salvar = os.path.join(UPLOAD_PRODUTOS_DIR, filename)

                # Guarda localmente
                arquivo.save(caminho_salvar)

                # Atualiza a variavel com o caminho relativo para a Base da Dados
                caminho_final_imagem = f"/static/uploads/produtos/{filename}"

        # 2. Criar o modelo
        preco_str = request.form.get('preco')

        # Criando o objeto com argumentos nomeados (mais seguro)
        novo_p = ProdutoModel(
            nome=request.form.get('nome'),
            sku=request.form.get('sku'),
            preco=float(preco_str) if preco_str else 0.0,
            descricao=request.form.get('descricao'),
            codigo_barras=request.form.get('codigo_barras'),
            categoria=request.form.get('categoria'),
            url_imagem=caminho_final_imagem
            # criado_em e id ficam como None automaticamente
        )

        produto_repo.criar(novo_p)
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))

    return render_template('admin_produtos_form.html', produto=None)

@app.route('/admin/produtos/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_produto_editar(id):
    produto = produto_repo.buscar_por_id(id)
    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.sku = request.form.get('sku')
        preco_str = request.form.get('preco')
        produto.preco = float(preco_str) if preco_str else 0.0
        produto.descricao = request.form.get('descricao')
        produto.codigo_barras = request.form.get('codigo_barras')
        produto.categoria = request.form.get('categoria')
        produto.url_imagem = request.form.get('url_imagem')

        # --- LÓGICA DE UPLOAD NA EDIÇÃO ---
        # Se ele preencheu o campo de URL, usamos isso
        nova_url = request.form.get('url_imagem')
        if nova_url:
            produto.url_imagem = nova_url

        # Se ele enviou um novo ficheiro, o ficheiro tem prioridade
        if 'foto_local' in request.files:
            arquivo = request.files['foto_local']
            if arquivo.filename != '':
                filename = secure_filename(f"prod_{produto.sku}_{arquivo.filename}")
                caminho_salvar = os.path.join(UPLOAD_PRODUTOS_DIR, filename)
                arquivo.save(caminho_salvar)
                produto.url_imagem = f"/static/uploads/produtos/{filename}"

        produto_repo.atualizar(id, produto)
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))

    return render_template('admin_produtos_form.html', produto=produto)

@app.route('/admin/produtos/excluir/<int:id>', methods=['POST'])
@admin_required
def admin_produto_excluir(id):
    try:
        produto_repo.deletar(id)
        flash('Produto removido do catálogo.', 'success')
    except Exception:
        flash('Erro: Este produto possui pedidos vinculados e não pode ser removido.', 'danger')

    return redirect(url_for('admin_produtos'))


# CONCEITO: Camada de Apresentação (Início das Rotas ‘Web’)
@app.route('/')
def index():
    # Captura os dados da Query String (ex: /?busca=mouse&categoria=Hardware)
    busca = request.args.get('busca')
    categoria = request.args.get('categoria')

    # Chama a nossa função flexível
    produtos = produto_repo.listar_todos(busca=busca, categoria=categoria)

    return render_template('index.html', produtos=produtos, busca=busca, categoria=categoria)

@app.route('/produto/<int:id>')
def detalhes_produto(id):
    # Busca o produto específico no banco de dados usando o seu Repository
    produto_atual = produto_repo.buscar_por_id(id)
    if not produto_atual:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    # Busca os comentários deste produto específico
    comentarios = avaliacao_repo.listar_por_produto(id)

    # Passamos os comentários para o HTML
    return render_template('produto_detalhes.html', produto=produto_atual, comentarios=comentarios)

@app.route('/produto/<int:id>/avaliar', methods=['POST'])
def avaliar_produto(id):
    # Proteção: Só quem está logado pode comentar
    if 'usuario_id' not in session:
        flash('Faça login para avaliar o produto.', 'warning')
        return redirect(url_for('login'))

    nota = request.form.get('nota')
    comentario = request.form.get('comentario')

    # Salva no banco
    avaliacao_repo.criar(id, session['usuario_id'], nota, comentario)
    flash('Avaliação enviada com sucesso!', 'success')

    return redirect(url_for('detalhes_produto', id=id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Desempacota a resposta do Controller
        resposta, status_code = usuario_ctrl.fazer_login(email, senha)

        if status_code == 200:
            # SUCESSO: Guardamos os dados na sessão
            # Supondo que a 'resposta' contenha os dados do usuário
            session['usuario_id'] = resposta['usuario']['id']
            session['usuario_nome'] = resposta['usuario']['nome']
            session['is_admin'] = resposta['usuario']['is_admin']

            # Caso ainda não tenha upload de foto, usamos uma imagem padrão
            session['usuario_foto'] = "/static/img/usuarios/default-user.png"

            return redirect(url_for('index'))
        else:
            # Pega a mensagem de erro que o Controller gerou e exibe
            flash(resposta['mensagem'], 'danger')

    return render_template('login.html')

@app.route('/sair')
def logout():
    """
    Rota para encerrar a sessão do usuário.
    Limpa o cookie de sessão e redireciona para a página inicial.
    :return:
    """
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Pega os dados do formulário HTML
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')
        data_nascimento = request.form.get('data_nascimento')

        # Chama a inteligência do Controller
        resposta, status_code = usuario_ctrl.registrar_usuario(
            nome, email, senha, cpf, telefone, data_nascimento
        )

        if status_code == 201:
            flash(resposta['mensagem'], 'success')
            return redirect(url_for('login'))
        else:
            flash(resposta['mensagem'], 'danger')

    return render_template('cadastro.html')

@app.route('/perfil')
def perfil():
    # Proteção de Rota: Só entra quem está logado
    if 'usuario_id' not in session:
        flash('Faça login para acessar seu perfil.', 'warning')
        return redirect(url_for('login'))

    # Busca os endereços cadastrados deste usuário
    lista_enderecos = endereco_repo.listar_por_usuario(session['usuario_id'])

    return render_template('perfil.html', enderecos=lista_enderecos)

@app.route('/perfil/foto', methods=['POST'])
def atualizar_foto():
    if 'foto' not in request.files:
        return redirect(url_for('perfil'))

    arquivo = request.files['foto']
    if arquivo.filename != '':
        filename = secure_filename(f"user_{session['usuario_id']}_{arquivo.filename}")
        caminho_salvar = os.path.join('src/views/static/uploads/usuarios', filename)

        # Garante que a pasta existe antes de tentar salvar a foto de perfil
        os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)

        arquivo.save(caminho_salvar)

        # Atualiza no Banco via UsuarioRepository
        caminho_db = f"/static/uploads/usuarios/{filename}"
        usuario_repo.atualizar_foto(session['usuario_id'], caminho_db)

        # Atualiza a Sessão para o cabeçalho mudar
        session['usuario_foto'] = caminho_db

    return redirect(url_for('perfil'))


@app.route('/perfil/endereco', methods=['POST'])
def novo_endereco():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Coleta os dados do Model de Endereço
    dados_endereco = {
        'cep': request.form.get('cep'),
        'rua': request.form.get('rua'),
        'numero': request.form.get('numero'),
        'bairro': request.form.get('bairro'),
        'complemento': request.form.get('complemento'),
        'cidade': request.form.get('cidade'),
        'estado': request.form.get('estado')
    }

    try:
        # Usa o repositório para salvar no banco
        endereco_repo.criar(session['usuario_id'], dados_endereco)
        flash('Endereço cadastrado com sucesso!', 'success')
    except Exception as e:
        print(f"Erro ao salvar endereço: {e}")
        flash('Erro ao cadastrar endereço.', 'danger')

    return redirect(url_for('perfil'))

@app.route('/carrinho/adicionar/<int:id>', methods=['POST'])
def adicionar_carrinho(id):
    quantidade = int(request.form.get('quantidade', 1))

    # Inicializa o carrinho na sessão se não existir
    if 'carrinho' not in session:
        session['carrinho'] = {}

    carrinho = session['carrinho']

    # Se o produto já está lá, soma a quantidade; se não, cria
    id_str = str(id)
    if id_str in carrinho:
        carrinho[id_str] += quantidade
    else:
        carrinho[id_str] = quantidade

    session['carrinho'] = carrinho # Notifica o Flask da mudança
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    itens_carrinho = []
    total_geral = 0

    carrinho_session = session.get('carrinho', {})

    # Buscamos os detalhes reais de cada produto no banco
    for id_produto, qtd in carrinho_session.items():
        produto = produto_repo.buscar_por_id(int(id_produto))
        if produto:
            subtotal = produto.preco * qtd
            total_geral += subtotal
            itens_carrinho.append({
                'produto': produto,
                'quantidade': qtd,
                'subtotal': subtotal
            })

    return render_template('carrinho.html', itens=itens_carrinho, total=total_geral)

@app.route('/carrinho/remover/<int:id>')
def remover_item_carrinho(id):
    carrinho = session.get('carrinho', {})
    id_str = str(id)
    if id_str in carrinho:
        del carrinho[id_str]
        session['carrinho'] = carrinho
        flash('Item removido.', 'info')
    return redirect(url_for('carrinho'))

@app.route('/pagamento/<int:pedido_id>')
def pagamento(pedido_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    # Reutilizamos a busca de pedidos do usuário para garantir que ele só pague os dele
    pedidos = pedido_repo.listar_por_usuario(session['usuario_id'])
    pedido_atual = next((p for p in pedidos if p[0] == pedido_id), None)

    # Se o pedido não for dele, não existir ou já estiver pago, bloqueia
    if not pedido_atual or pedido_atual[2] != 'pendente':
        flash('Pedido inválido ou já pago.', 'warning')
        return redirect(url_for('meus_pedidos'))

    # Passamos os dados do pedido (id, data, status, valor) para o HTML
    return render_template('pagamento.html', pedido=pedido_atual)

@app.route('/pagamento/processar/<int:pedido_id>', methods=['POST'])
def processar_pagamento(pedido_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    metodo = request.form.get('metodo_pagamento', 'N/A')

    # -------------------------------------------------------------
    # É AQUI QUE A MÁGICA (SIMULAÇÃO) ACONTECE!
    # Numa aplicação real, enviaríamos os dados do cartão para a API aqui.
    # Como é simulação, apenas assumimos sucesso imediato e mudamos o status.
    # -------------------------------------------------------------

    try:
        pedido_repo.mudar_status(pedido_id, 'em_analise')
        flash(f'Pagamento via {metodo} aprovado com sucesso! Obrigado pela sua compra!')
    except Exception as e:
        flash('Erro ao processar pagamento.', 'danger')

    return redirect(url_for('meus_pedidos'))

@app.route('/meus-pedidos')
def meus_pedidos():
    # Proteção: Só logados entram
    if 'usuario_id' not in session:
        flash('Faça login para ver seu histórico de pedidos.', 'warning')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    # Busca os pedidos "crus" do banco de dados
    pedidos_brutos = pedido_repo.listar_por_usuario(usuario_id)

    # Monntar uma lista limpa e organizada
    pedidos_completos = []

    if pedidos_brutos:
        for ped in pedidos_brutos:
            # Para cada pedido, busca os produtos que estão dentro dele
            itens = pedido_repo.listar_itens_por_pedido(ped[0])

            pedidos_completos.append({
                'id': ped[0],
                'data': ped[1],
                'status': ped[2],
                'total': ped[3],
                'itens': itens
            })

    return render_template('meus_pedidos.html', pedidos=pedidos_completos)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # 1. Proteção: Só logados entram
    if 'usuario_id' not in session:
        flash('Faça login para finalizar a compra.', 'warning')
        return redirect(url_for('login'))

    carrinho = session.get('carrinho', {})

    # 2. Proteção: Carrinho vazio não finaliza
    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('carrinho'))

    # Se o utilizador clicou em "Confirmar Pedido" (POST)
    if request.method == 'POST':
        endereco_id = request.form.get('endereco_id')

        if not endereco_id:
            flash('Por favor, selecione um endereço de entrega.', 'danger')
            return redirect(url_for('checkout'))

        try:
            # Aqui chamamos o seu Service Pattern para orquestrar a venda no banco de dados!
            # Ele deve receber o ID do cliente, o dicionário do carrinho e o ID do endereço
            venda_service.realizar_venda(session['usuario_id'], carrinho, endereco_id)

            # Esvazia o carrinho da sessão após o sucesso
            session.pop('carrinho', None)

            flash('🎉 Pedido realizado com sucesso! Verifique seus pedidos.', 'success')
            return redirect(url_for('meus_pedidos'))

        except Exception as e:
            # Se algo falhar (ex: falta de estoque), o banco de dados faz o ROLLBACK automático
            print(f"Erro no checkout: {e}")
            flash(f'Erro ao processar o pedido: {str(e)}', 'danger')
            return redirect(url_for('checkout'))

    # Se for apenas para visualizar a página (GET)
    enderecos = endereco_repo.listar_por_usuario(session['usuario_id'])

    # Calcula o total para exibir na tela
    total = 0
    for id_produto, qtd in carrinho.items():
        produto = produto_repo.buscar_por_id(int(id_produto))
        if produto:
            total += produto.preco * qtd

    return render_template('checkout.html', enderecos=enderecos, total=total)

@app.context_processor
def utility_processor():
    def contagem_carrinho():
        carrinho = session.get('carrinho', {})
        return sum(carrinho.values()) # Soma todas as quantidades
    return dict(total_itens=contagem_carrinho())

if __name__ == '__main__':
    app.run(debug=True)