from celery import Celery

# Configuração do Celery
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # URL do broker (use Redis, RabbitMQ, etc.)
    backend='redis://localhost:6379/0',  # Backend para resultados (SQLite neste exemplo)
)

# Configuração de tarefas do Celery
celery_app.conf.update(
    result_expires=3600,  # Resultados expiram em 1 hora
)
