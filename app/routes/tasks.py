from flask import Blueprint, jsonify
#from app.task import process_youtube_link, save_video_file

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/task/status/<task_id>')
def task_status(task_id):
    from celery.result import AsyncResult
    from app import celery

    # Verifica ambas as tarefas possíveis
    task = AsyncResult(task_id, app=celery)

    response = {
        'status': task.state,
        'task_id': task_id
    }

    if task.state == 'SUCCESS':
        response['result'] = task.result
    elif task.state == 'FAILURE':
        response['error'] = str(task.result)

    return jsonify(response)