# app/routes/summarization.py
from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Transcription, Summary
from app.summarization import TFIDFSummarizer
from app.summarization import VideoTopicSummarizer

summarization_bp = Blueprint('summarization', __name__)


def check_transcription_permission(transcription):
    """Verifica se o usuário tem permissão para acessar a transcrição."""
    return transcription and transcription.video.user_id == current_user.id


@summarization_bp.route('/summarize/<int:transcription_id>')
@login_required
def summarize(transcription_id):
    transcription = Transcription.query.get(transcription_id)

    if not check_transcription_permission(transcription):
        flash('Transcription not found or you do not have permission to summarize it', 'danger')
        return redirect(url_for('video.dashboard'))

    # Realiza a sumarização do texto da transcrição
    summarizer = TFIDFSummarizer(language=transcription.language)
    # summarizerTopic = VideoTopicSummarizer(transcription)
    # print("Topicos:", summarizerTopic.identify_topic())
    summary_text, processing_time = summarizer.summarize(transcription.text)

    # Cria um novo resumo associado à transcrição
    new_summary = Summary(text=summary_text, transcription_id=transcription.id, processing_time=processing_time)
    db.session.add(new_summary)
    db.session.commit()

    flash('Summarization completed successfully', 'success')
    return redirect(url_for('video.view', video_id=transcription.video.id))
