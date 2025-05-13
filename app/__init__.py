# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from config import Config
import dotenv
dotenv.load_dotenv()

# Inicializa extensões sem app para usar o padrão factory
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
celery = Celery()


def create_app(config_class=Config):
    """Factory de aplicação Flask com padrão mais seguro"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configurações de segurança para Redis/Celery
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config.update(
        CELERY={
            'broker_url': redis_url,
            'result_backend': redis_url,
            'task_serializer': 'json',
            'result_serializer': 'json',
            'accept_content': ['json'],
            'result_expires': 3600,
            'task_track_started': True,
            'task_time_limit': 600,
            'task_soft_time_limit': 300,
            'broker_connection_retry_on_startup': True
        }
    )

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'

    # Configura Celery
    configure_celery(app)

    # Registra filtros de template
    register_template_filters(app)

    # Registra blueprints
    register_blueprints(app)

    return app


def configure_celery(app):
    """Configuração segura do Celery com contexto de aplicação"""
    celery.conf.update(app.config['CELERY'])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.set_default()

    # Importa tarefas após a configuração
    from app import tasks  # noqa


def register_template_filters(app):
    """Registra filtros personalizados de template"""
    from app.utils import filters

    filters_to_register = [
        ('youtube_id', filters.youtube_id),
        ('format_time', filters.format_time),
        ('youtube_embed', filters.youtube_embed),
        ('is_youtube_url', filters.is_youtube_url)
    ]

    for name, filter_func in filters_to_register:
        app.template_filter(name)(filter_func)


def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    from app.routes import (
        auth,
        video,
        main_bp,
        summarization,
        transcription,
        tasks as tasks_bp
    )

    blueprints = [
        auth.auth_bp,
        video.video_bp,
        main_bp,
        summarization.summarization_bp,
        transcription.transcription_bp,
        tasks_bp.task_bp
    ]

    for bp in blueprints:
        app.register_blueprint(bp)


# Cria a aplicação Flask
flask_app = create_app()