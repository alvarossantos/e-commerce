from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from src.controllers.usuario_controller import UsuarioController
from src.repository.produto_repository import ProdutoRepository

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

# CONCEITO: Camada de Apresentação (Início das Rotas ‘Web’)
@app.route('/')
def index():
    # Busca produtos do seu banco de dados real
    produtos = produto_repo.listar_todos()
    return render_template('index.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        # Usa a lógica de autenticação já pronta!
        usuario = usuario_ctrl.fazer_login(email, senha)
        if usuario:
            return redirect(url_for('index'))
        flash('E-mail ou senha incorretos!', 'danger')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)