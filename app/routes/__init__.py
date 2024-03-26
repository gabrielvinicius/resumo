# routes/__init__.py
from flask import Blueprint, redirect, url_for
from flask_login import current_user

from app.routes.auth import auth_bp
from app.routes.video import video_bp
from app.routes.transcription import transcription_bp
from app.routes.summarization import summarization_bp

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('video.dashboard'))
    else:
        return redirect(url_for('auth.login'))
