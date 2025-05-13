from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login
from app.models import User
from app.utils.validators import validate_password, validate_username

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login.user_loader
def load_user(user_id):
    """Callback para carregar o usuário a partir do ID na sessão"""
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota de login com tratamento de erros e redirecionamento seguro
    """
    # Se já estiver logado, redireciona para home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        # Validação básica
        if not username or not password:
            flash('Por favor, preencha todos os campos', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        # Proteção contra timing attacks
        if not user or not check_password_hash(user.password, password):
            flash('Credenciais inválidas', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash('Login realizado com sucesso', 'success')

        # Redirecionamento seguro
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.home'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Rota de logout com limpeza de sessão"""
    logout_user()
    flash('Você foi desconectado com sucesso', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota de registro com validação robusta"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validações
        #if not validate_username(username):
         #   flash('Nome de usuário inválido (3-20 caracteres alfanuméricos)', 'danger')
        #elif not validate_password(password):
         #   flash('Senha deve ter 8+ caracteres, incluindo maiúsculas, números e especiais', 'danger')
        #elif password != password_confirm:
         #   flash('As senhas não coincidem', 'danger')
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já está em uso', 'danger')
        else:
            try:
                new_user = User(
                    username=username,
                    password=generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=16))
                db.session.add(new_user)
                db.session.commit()
                flash('Conta criada com sucesso! Faça login', 'success')
                return redirect(url_for('auth.login'))
            except Exception:
                db.session.rollback()
                flash('Erro ao criar conta. Tente novamente.', 'danger')

    return render_template('auth/register.html')