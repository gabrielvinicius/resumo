# app/routes/video.py
import os
from uuid import uuid1
import imageio
import moviepy.editor as mp
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Video
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
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('video.dashboard'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('video.dashboard'))

    if not allowed_file(file.filename):
        flash('Invalid file format. Please upload a valid video file.', 'danger')
        return redirect(url_for('video.dashboard'))

    if file:
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

        new_video = Video(title=request.form['title'], video_path=file_path, file_size=file_size, duration=duration,
                          thumbnail_path=thumbnail_path, user_id=current_user.id, fps=fps, codec=codec)
        db.session.add(new_video)
        db.session.commit()

        flash('Video uploaded successfully', 'success')
        return redirect(url_for('video.view', video_id=new_video.id))

    flash('Upload failed', 'danger')
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
