# app/routes/video.py
import os
import re
from uuid import uuid1
import imageio
import moviepy.editor as mp
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Video
from pytube import YouTube

# from app.utils import allowed_file

video_bp = Blueprint('video', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_video_permission(video):
    """Verifica se o usuário tem permissão para acessar o vídeo."""
    return video and video.user_id == current_user.id


@video_bp.route('/dashboard')
@login_required
def dashboard():
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template('video/dashboard.html', videos=videos)


@video_bp.route('/upload', methods=['POST'])
@login_required
def upload():
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

        new_video = save_video_file(file, title)
        db.session.add(new_video)
        db.session.commit()

        flash('Video uploaded successfully', 'success')
        return redirect(url_for('video.view', video_id=new_video.id))

    else:
        youtube_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&.*)?$')
        youtube_link = request.form.get('youtube_link')
        if bool(youtube_pattern.match(youtube_link)):
            title = request.form.get('title')
            # Processar o link do YouTube e salvar os dados relevantes, se necessário
            # Exemplo:
            new_video = process_youtube_link(youtube_link, title)
            db.session.add(new_video)
            db.session.commit()

            flash('Video uploaded successfully', 'success')
            return redirect(url_for('video.view', video_id=new_video.id))
        else:
            flash('Insira um link valido do Youtube', 'danger')
            return redirect(url_for('video.dashboard'))


@video_bp.route('/view/<int:video_id>')
@login_required
def view(video_id):
    video = Video.query.get(video_id)

    if not check_video_permission(video):
        flash('Video not found or you do not have permission to view it', 'danger')
        return redirect(url_for('video.dashboard'))

    return render_template('video/view_video.html', video=video)


@video_bp.route('/download/<int:video_id>')
@login_required
def download(video_id):
    video = Video.query.get(video_id)

    if not check_video_permission(video):
        flash('Video not found or you do not have permission to download it', 'danger')
        return redirect(url_for('video.dashboard'))

    return send_file(os.path.join('..', video.video_path), as_attachment=True)


@video_bp.route('/thumbnail/<int:video_id>')
@login_required
def thumbnail(video_id):
    video = Video.query.get(video_id)
    if not check_video_permission(video):
        flash('Video not found or you do not have permission to download it', 'danger')
        return redirect(url_for('video.dashboard'))
    return send_file(os.path.join('..', video.thumbnail_path), as_attachment=True)


def save_video_file(file, title):
    # Lógica para salvar o arquivo de vídeo e obter seu caminho
    # Exemplo:
    filename = str(uuid1()) + '.mp4'
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    video_info = imageio.get_reader(file_path).get_meta_data()

    file_size = os.path.getsize(file_path)

    video = mp.VideoFileClip(file_path)
    duration = video.duration

    thumbnail_filename = f'{filename}_thumbnail.jpg'
    thumbnail_path = os.path.join(UPLOAD_FOLDER, thumbnail_filename)
    video.save_frame(thumbnail_path, t=(duration / 2))

    fps = video_info.get('fps')
    codec = video_info['codec']

    audio = video.audio
    audio_filename = str(uuid1()) + '.wav'
    audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
    audio.write_audiofile(audio_path, fps=16000, codec='pcm_s16le')

    new_video = Video(title=title, video_path=file_path, file_size=file_size, duration=duration,
                      thumbnail_path=thumbnail_path, user_id=current_user.id, fps=fps, codec=codec,
                      audio_path=audio_path)

    # video_path = '/path/to/video/file.mp4'
    return new_video


def process_youtube_link(youtube_link, title):
    # Lógica para processar o link do YouTube e obter o caminho do vídeo
    # Exemplo:
    yt = YouTube(youtube_link)
    filename = str(uuid1()) + '.mp3'
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(output_path=UPLOAD_FOLDER, filename=filename)
    # video_path = 'https://www.youtube.com/watch?v=video_id'
    thumbnail_url = yt.thumbnail_url
    duration = yt.length
    new_video = Video(title=title, video_path=youtube_link, duration=duration,
                      thumbnail_path=thumbnail_url, user_id=current_user.id, audio_path=file_path)
    return new_video
