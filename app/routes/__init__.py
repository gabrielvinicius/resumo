# routes/__init__.py
from flask import Blueprint, redirect, url_for

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('video.dashboard'))
    else:
        return redirect(url_for('auth.login'))


# Cria um Blueprint chamado 'video' e associa-o ao pacote 'routes'
video_bp = Blueprint('video', __name__)

# Importa as rotas relacionadas a vídeos
from .video import *

# Cria um Blueprint chamado 'auth' e associa-o ao pacote 'routes'
auth_bp = Blueprint('auth', __name__)

# Importa as rotas relacionadas à autenticação
from .auth import *
