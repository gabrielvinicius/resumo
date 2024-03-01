# app.py
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

db.init_app(app)

from routes import auth_bp, video_bp

app.register_blueprint(auth_bp)
app.register_blueprint(video_bp)

# Cria todas as tabelas se não existirem
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)