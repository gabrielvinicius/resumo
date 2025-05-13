# app/routes/transcription.py
from io import BytesIO

from flask import Blueprint, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.tasks import transcription_task, summarization_task
from app.models import Video, Transcription

# from app.transcription import SpeechTranscriber

# from app.faster_whisper import SpeechTranscriber

transcription_bp = Blueprint('transcription', __name__)


def check_video_permission(video_id):
    """Verifica se o usuário tem permissão para acessar o vídeo."""
    video = Video.query.get(video_id)
    return video and video.user_id == current_user.id


@transcription_bp.route('/transcribe/<int:video_id>')
@login_required
async def transcribe(video_id):
    if not check_video_permission(video_id):
        flash('Video not found or you do not have permission to transcribe it', 'danger')
        return redirect(url_for('main.dashboard'))
    task = transcription_task.delay(video_id)

    flash(f'Processo de Transcrição iniciado: {task.id}', 'success')
    # Redireciona para a rota de visualização do vídeo
    return redirect(url_for('video.view', video_id=video_id))


@transcription_bp.route('/transcribe/download/<int:transcription_id>')
@login_required
def download(transcription_id):
    transcription = Transcription.query.get(transcription_id)
    if not transcription:
        flash('Transcription not found', 'danger')
        return redirect(url_for('main.dashboard'))

    return send_file(path_or_file=BytesIO(transcription.text.encode('utf-8')), mimetype='text/plain',
                     as_attachment=True, download_name='summary.txt')
