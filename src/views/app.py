from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session
from src.controllers.usuario_controller import UsuarioController
from src.repository.produto_repository import ProdutoRepository
import os
from werkzeug.utils import secure_filename

from src.repository.usuario_repository import UsuarioRepository

# Define a pasta onde este arquivo está localizado
BASE_DIR = Path(__file__).parent

# Configura as pastas de templates e static
template_dir = str(BASE_DIR/ "templates")
static_dir = str(BASE_DIR/ "static")

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

# CONCEITO: Camada de Apresentação (Início das Rotas ‘Web’)
@app.route('/')
def index():
    # Busca produtos do seu banco de dados real
    produtos = produto_repo.listar_todos()
    return render_template('index.html', produtos=produtos)

@app.route('/produto/<int:id>')
def detalhes_produto(id):
    # Busca o produto específico no banco de dados usando o seu Repository
    produto_atual = produto_repo.buscar_por_id(id)

    if not produto_atual:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    return render_template('produto_detalhes.html', produto=produto_atual)

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

            # Caso ainda não tenha upload de foto, usamos uma imagem padrão
            session['usuario_foto'] = "/static/img/default-user.png"

            return redirect(url_for('index'))
        else:
            # Pega a mensagem de erro que o Controller gerou e exibe
            flash(resposta['mensagem'], 'danger')

    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Pega os dados do formulário HTML
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')
        data_nasc = request.form.get('data_nasc')

        # Chama a inteligência do Controller
        resposta, status_code = usuario_ctrl.registrar_usuario(
            nome, email, senha, cpf, telefone, endereco, data_nasc
        )

        if status_code == 201:
            flash(resposta['mensagem'], 'success')
            return redirect(url_for('login'))
        else:
            flash(resposta['mensagem'], 'danger')

    return render_template('cadastro.html')

@app.route('/perfil/foto', methods=['POST'])
def atualizar_foto():
    if 'foto' not in request.files:
        return redirect(url_for('perfil'))

    arquivo = request.files['foto']
    if arquivo.filename != '':
        filename = secure_filename(f"user_{session['usuario_id']}_{arquivo.filename}")
        caminho_salvar = os.path.join('src/views/static/uploads/usuarios', filename)
        arquivo.save(caminho_salvar)

        # Atualiza no Banco via UsuarioRepository
        caminho_db = f"static/uploads/usuarios/{filename}"
        usuario_repo.atualizar_foto(session['usuario_id'], caminho_db)

        # Atualiza a Sessão para o cabeçalho mudar
        session['usuario_id'] = caminho_db

    return redirect(url_for('perfil'))

if __name__ == '__main__':
    app.run(debug=True)