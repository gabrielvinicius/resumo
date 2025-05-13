from flask import Blueprint, redirect, url_for, render_template, send_from_directory
from flask_login import current_user, login_required

from app.models import Video
from app.routes.auth import auth_bp
from app.routes.video import video_bp
from app.routes.transcription import transcription_bp
from app.routes.summarization import summarization_bp

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Rota raiz que redireciona para home ou login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
@login_required
def home():
    """Página principal do usuário autenticado"""
    videos = Video.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Video.created_at.desc()
    ).all()
    return render_template('video/dashboard.html', videos=videos)

@main_bp.route('/static/js/<path:filename>')
def serve_js(filename):
    """Serve arquivos JavaScript estáticos"""
    return send_from_directory('static/js', filename)

# Depreciação da rota /dashboard (mantida para compatibilidade)
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Rota legada - redireciona para a nova home"""
    return redirect(url_for('main.home'))