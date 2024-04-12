# routes/__init__.py
from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user, login_required

from app.models import Video
from app.routes.auth import auth_bp
from app.routes.video import video_bp
from app.routes.transcription import transcription_bp
from app.routes.summarization import summarization_bp

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template('video/dashboard.html', videos=videos)
