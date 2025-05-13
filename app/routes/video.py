# app/routes/video.py
import os
#import re
from pathlib import Path
from uuid import uuid1

#import imageio
#import moviepy.editor as mp
from flask import Blueprint, current_app,render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
#from pytube import YouTube
from werkzeug.utils import secure_filename

from app import db
from app.models import Video
from app.tasks import process_youtube_link, save_video_file

# from app.utils import allowed_file

video_bp = Blueprint('video', __name__)


ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_video_permission(video):
    """Verifica se o usuário tem permissão para acessar o vídeo."""
    return video and video.user_id == current_user.id


@video_bp.route('/video/upload', methods=['POST'])
@login_required
def upload():
    title = request.form.get('title')
    upload_type = request.form.get('upload_type')

    try:
        if upload_type == 'file':
            file = request.files['file']
            filename = secure_filename(str(uuid1()) + Path(file.filename).suffix)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            task = save_video_file.delay(
                file_path=file_path,
                title=title,
                filename=filename,
                current_user_id=current_user.id
            )
        else:
            youtube_link = request.form.get('youtube_link')
            task = process_youtube_link.delay(
                youtube_link=youtube_link,
                title=title,
                current_user_id=current_user.id
            )

        return jsonify({'task_id': task.id}), 202

    except Exception as e:
        current_app.logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@video_bp.route('/video/view/<int:video_id>')
@login_required
async def view(video_id):
    video = Video.query.get(video_id)

    if not check_video_permission(video):
        flash('Video not found or you do not have permission to view it', 'danger')
        return redirect(url_for('main.dashboard'))

    # return render_template('video/view_video.html', video=video)
    return render_template('video/video.html', video=video)


@video_bp.route('/video/download/<int:video_id>')
@login_required
async def download(video_id):
    video = Video.query.get(video_id)

    if not check_video_permission(video):
        flash('Video not found or you do not have permission to download it', 'danger')
        return redirect(url_for('main.dashboard'))

    return send_file(os.path.join('..', video.video_path), as_attachment=True)


@video_bp.route('/video/thumbnail/<int:video_id>')
@login_required
def thumbnail(video_id):
    video = Video.query.get(video_id)
    if not check_video_permission(video):
        flash('Video not found or you do not have permission to download it', 'danger')
        return redirect(url_for('main.dashboard'))
    return send_file(os.path.join('..', video.thumbnail_path), as_attachment=True)


@video_bp.route('/video/delete/<int:video_id>', methods=['POST'])
@login_required
async def delete(video_id):
    video = Video.query.get(video_id)
    if not check_video_permission(video):
        flash('Video not found or you do not have permission to delete it', 'danger')
        return redirect(url_for('main.dashboard'))

    # Remove todas as revisões associadas ao vídeo
    # Summary.query.filter_by(video_id=video.id).delete()

    # Remove todas as transcrições associadas ao vídeo
    # Transcription.query.filter_by(video_id=video.id).delete()
    # Excluir arquivos de áudio e vídeo, se existirem
    if video.audio_path and os.path.exists(video.audio_path):
        os.remove(video.audio_path)
    if video.video_path and os.path.exists(video.video_path):
        os.remove(video.video_path)
    # Remove o vídeo
    db.session.delete(video)
    db.session.commit()

    flash('Video deleted successfully', 'success')
    return redirect(url_for('main.dashboard'))

@video_bp.route('/videos/list')
@login_required
def list_videos():
    videos = Video.query.filter_by(user_id=current_user.id).order_by(Video.date_added.desc()).all()
    return render_template('partials/video_list.html', videos=videos)