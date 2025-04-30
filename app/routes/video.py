# app/routes/video.py
import os
import re
from uuid import uuid1

#import imageio
#import moviepy.editor as mp
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from pytube import YouTube

from app import db
from app.models import Video
from app.task import process_youtube_link, save_video_file

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
async def upload():

    title = request.form.get('title')
    upload_type = request.form.get('upload_type')
    if upload_type == 'file':
        file = request.files['file']
        # Salvar o arquivo de vídeo e obter seu caminho
        # Exemplo:
        if not allowed_file(file.filename):
            flash('Invalid file format. Please upload a valid video file.', 'danger')
            return redirect(url_for('video.dashboard'))

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('video.dashboard'))

        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('video.dashboard'))
        filename = str(uuid1()) + '.mp4'
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        task = save_video_file.delay(file_path, title, filename, current_user.id)

    else:
        youtube_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&.*)?$')
        youtube_link = request.form.get('youtube_link')
        if bool(youtube_pattern.match(youtube_link)):
            title = request.form.get('title')
            # Processar o link do YouTube e salvar os dados relevantes, se necessário
            # Exemplo:
            task = process_youtube_link.delay(youtube_link, title, current_user.id)
        else:
            flash('Insira um link valido do Youtube', 'danger')
            return redirect(url_for('main.dashboard'))

    flash(f'Upload concluído, iniciando o processo de processamento, id: {task.id}', 'success')
    return redirect(url_for('main.dashboard'))


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
