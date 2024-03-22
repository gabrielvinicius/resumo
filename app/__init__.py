# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config  # Importa a classe Config do arquivo no diretório raiz

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager()
login.init_app(app)
login.login_view = 'auth.login'


@login.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


from app.routes import auth, video, main_bp

# Importa os módulos de rotas

app.register_blueprint(auth.auth_bp)
app.register_blueprint(video.video_bp)
app.register_blueprint(main_bp)
