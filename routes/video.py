# routes/video.py
import os
import hashlib
import speech_recognition as sr
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_uploads import UploadNotAllowed
from werkzeug.utils import secure_filename
from models import db, User, Video, Summary

video_bp = Blueprint('video', __name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}  # Adicione formatos de áudio permitidos


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@video_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        try:
            videos.save(file, name="video", extension=None)
        except UploadNotAllowed:
            flash('Invalid file type. Allowed types: mp4, avi, mkv, mov', 'danger')
            return redirect(request.url)

        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)
        filename = secure_filename(file_hash + '.' + file.filename.rsplit('.', 1)[1].lower())
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        new_video = Video(user_id=current_user.id, title=request.form['title'], file_path=file_path)
        db.session.add(new_video)
        db.session.commit()

        flash('Video uploaded successfully', 'success')

        # Redireciona para a rota de transcrição com o ID do vídeo
        return redirect(url_for('video.transcribe', video_id=new_video.id))

    return render_template('video/upload.html', current_user=current_user)
