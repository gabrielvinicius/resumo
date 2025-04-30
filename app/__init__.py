# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config  # Importa a classe Config do arquivo no diretório raiz
from celery import Celery, Task


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


flask_app = Flask(__name__)
flask_app.config.from_object(Config)
flask_app.config.from_mapping(
    CELERY=dict(
        #broker_url="redis://localhost",
        #result_backend="redis://localhost",
        broker_url="redis://45.33.198.3",
        result_backend="redis://45.33.198.3",
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(flask_app)
db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)

login = LoginManager()
login.init_app(flask_app)
login.login_view = 'auth.login'

from app.routes import auth, video, main_bp, summarization, transcription

# Importa os módulos de rotas

flask_app.register_blueprint(auth.auth_bp)
flask_app.register_blueprint(video.video_bp)
flask_app.register_blueprint(main_bp)
flask_app.register_blueprint(summarization.summarization_bp)
flask_app.register_blueprint(transcription.transcription_bp)
