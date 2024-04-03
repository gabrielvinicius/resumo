# app/routes/transcription.py
from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Video, Transcription
# from app.transcription import SpeechTranscriber
from app.faster_whisper import SpeechTranscriber

transcription_bp = Blueprint('transcription', __name__)


def check_video_permission(video):
    """Verifica se o usuário tem permissão para acessar o vídeo."""
    return video and video.user_id == current_user.id


@transcription_bp.route('/transcribe/<int:video_id>')
@login_required
def transcribe(video_id):
    video = Video.query.get(video_id)

    if not check_video_permission(video):
        flash('Video not found or you do not have permission to transcribe it', 'danger')
        return redirect(url_for('video.dashboard'))

    # Realiza a transcrição do vídeo
    transcriber = SpeechTranscriber()
    transcription_text, processing_time, language = transcriber.transcribe(video.audio_path)

    # Cria uma nova transcrição associada ao vídeo
    new_transcription = Transcription(text=transcription_text, video_id=video.id, processing_time=processing_time, language=language)
    db.session.add(new_transcription)
    db.session.commit()

    flash('Transcription completed successfully', 'success')

    # Redireciona para a rota de visualização do vídeo
    return redirect(url_for('video.view', video_id=video.id))
