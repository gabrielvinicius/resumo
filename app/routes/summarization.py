# app/routes/summarization.py
from io import BytesIO


from flask import Blueprint, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.tasks import summarization_task
from app import db
from app.models import Transcription, Summary
from app.summarization import TFIDFSummarizer

summarization_bp = Blueprint('summarization', __name__)


def check_transcription_permission(transcription):
    """Verifica se o usuário tem permissão para acessar a transcrição."""
    return transcription and transcription.video.user_id == current_user.id


@summarization_bp.route('/summarize/<int:transcription_id>')
@login_required
async def summarize(transcription_id):
    transcription = Transcription.query.get(transcription_id)

    if not check_transcription_permission(transcription):
        flash('Transcription not found or you do not have permission to summarize it', 'danger')
        return redirect(url_for('main.dashboard'))

    task = summarization_task.delay(transcription_id)
    flash(f'Processo de Sumarização iniciado: {task.id}', 'success')
    return redirect(url_for('video.view', video_id=transcription.video.id))


@summarization_bp.route('/summarize/download/<int:summary_id>')
@login_required
async def download_summary(summary_id):
    summary = Summary.query.get(summary_id)
    if not summary:
        flash('Summary not found', 'danger')
        return redirect(url_for('main.dashboard'))

    return send_file(path_or_file=BytesIO(summary.text.encode('utf-8')), mimetype='text/plain',
                     as_attachment=True, download_name='summary.txt')
