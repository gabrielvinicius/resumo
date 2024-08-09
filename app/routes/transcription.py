# app/routes/transcription.py
from io import BytesIO


from flask import Blueprint, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.task import transcription_task, summarization_task
from app.models import Video, Transcription, Segment, Word

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
        return redirect(url_for('main.dashboard'))
    task = transcription_task.delay(Video)
    # Realiza a transcrição do vídeo
    # transcriber = SpeechTranscriber()
    # transcription_text, processing_time, language, segments = transcriber.transcribe(video.audio_path)

    # Cria uma nova transcrição associada ao vídeo
    # new_transcription = Transcription(text=transcription_text, video_id=video.id, processing_time=processing_time,
       #                               language=language)
    # db.session.add(new_transcription)
    # db.session.commit()

    # for segment_data in segments:
        # segment = Segment(start=segment_data.start, end=segment_data.end, text=segment_data.text,
          #                transcription=new_transcription)
        # db.session.add(segment)
        # for word_text in segment_data.words:
         #   word = Word(text=word_text.word, segment=segment, start=word_text.start, end=word_text.end)
         #  db.session.add(word)

    # db.session.commit()

    flash(f'Processo de Transcrição iniciado: {task.id}', 'success')
    # Redireciona para a rota de visualização do vídeo
    return redirect(url_for('video.view', video_id=video.id))


@transcription_bp.route('/transcribe/download/<int:transcription_id>')
@login_required
def download_transcribe(transcription_id):
    transcription = Transcription.query.get(transcription_id)
    if not transcription:
        flash('Transcription not found', 'danger')
        return redirect(url_for('main.dashboard'))

    return send_file(path_or_file=BytesIO(transcription.text.encode('utf-8')), mimetype='text/plain',
                     as_attachment=True, download_name='summary.txt')
