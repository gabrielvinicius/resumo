# app/routes/video.py
import os
from uuid import uuid1
import imageio
import moviepy.editor as mp
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Video, Summary
from app.summarization import BartTextSummarizer, T5TextSummarizer, GPT2TextSummarizer, XLNetTextSummarizer
from app.transcription import transcribe_video_audio
from app.summarization.nltk import summarize_nltk
from app.summarization.bert import TextSummarizer
from app.summarization.spacy import summarize_spacy
from app.summarization.tfidf import summarize_tfidf
from app.audio_transcriber_summarizer import SpeechTranscriberWithSummarization
from app.speech_to_text import SpeechTranscriber

video_bp = Blueprint('video', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@video_bp.route('/dashboard')
@login_required
def dashboard():
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template('video/dashboard.html', videos=videos)


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

        if file and allowed_file(file.filename):
            filename = str(uuid1()) + '.mp4'
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            video_info = imageio.get_reader(file_path).get_meta_data()

            # Obtenha o tamanho do arquivo
            file_size = os.path.getsize(file_path)

            # Obtenha a duração do vídeo
            video = mp.VideoFileClip(file_path)
            duration = video.duration

            # Crie uma miniatura do vídeo
            thumbnail_filename = f'{filename}_thumbnail.jpg'
            thumbnail_path = os.path.join(UPLOAD_FOLDER, thumbnail_filename)
            video.save_frame(thumbnail_path, t=(duration / 2))  # Salva o quadro no meio do vídeo como miniatura

            # Obtenha o fps, size, nframes, codec e bitrate do vídeo
            fps = video_info.get('fps')
            # size = video_info['source_size']

            codec = video_info['codec']

            new_video = Video(title=request.form['title'], video_path=file_path, file_size=file_size, duration=duration,
                              thumbnail_path=thumbnail_path, user_id=current_user.id,
                              fps=fps, codec=codec)
            db.session.add(new_video)
            db.session.commit()

            flash('Video uploaded successfully', 'success')
            return redirect(url_for('video.dashboard'))
        else:
            flash('Invalid file format. Please upload a valid video file.', 'danger')
            return redirect(request.url)

    return render_template('video/upload.html')


@video_bp.route('/view/<int:video_id>')
@login_required
def view(video_id):
    video = Video.query.get(video_id)

    if not video or video.user_id != current_user.id:
        flash('Video not found or you do not have permission to view it', 'danger')
        return redirect(url_for('video.dashboard'))

    return render_template('video/view_video.html', video=video)


@video_bp.route('/transcribe/<int:video_id>')
@login_required
def transcribe(video_id):
    video = Video.query.get(video_id)

    if not video or video.user_id != current_user.id:
        flash('Video not found or you do not have permission to transcribe it', 'danger')
        return redirect(url_for('video.dashboard'))

    # Verifica se o arquivo de áudio já foi transcribido
    # if video.transcription:
    # flash('Audio already transcribed', 'info')
    # return redirect(url_for('video.dashboard'))

    # Extrai e transcreve o áudio do vídeo
    # transcription = transcribe_video_audio(video.video_path)
    transcriber = SpeechTranscriberWithSummarization()
    # transcriber = SpeechTranscriber()
    transcription = transcriber.transcribe(video.video_path)
    # Atualiza o modelo de vídeo com a transcrição
    video.transcription = transcription
    db.session.commit()

    flash('Transcription completed successfully', 'success')
    return redirect(url_for('video.summarize', video_id=video.id, library_id=2))


@video_bp.route('/summarize/<int:video_id>/<int:library_id>')
@login_required
def summarize(video_id, library_id):
    video = Video.query.get(video_id)

    if not video or video.user_id != current_user.id:
        flash('Video not found or you do not have permission to summarize it', 'danger')
        return redirect(url_for('video.dashboard'))

    summarizer = T5TextSummarizer()
    summary_content = summarizer.summarize(video.transcription)

    new_summary = Summary(content=summary_content, library_id=library_id, video_id=video.id)
    db.session.add(new_summary)
    db.session.commit()

    flash('Summarization completed successfully', 'success')
    return redirect(url_for('video.view', video_id=video.id))
