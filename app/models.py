# models.py
from flask_login import UserMixin
from app import db
from datetime import datetime
# from flask_security import UserMixin


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.String(20), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    # active = db.Column(db.Boolean(), default=True)
    videos = db.relationship('Video', backref='user', lazy=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    transcription = db.Column(db.Text, nullable=True)
    video_path = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # Tamanho do arquivo em bytes
    # duration = db.Column(db.Integer, nullable=True)  # Duração do vídeo em segundos
    fps = db.Column(db.Float, nullable=True)
    size = db.Column(db.String(20), nullable=True)
    duration = db.Column(db.Float, nullable=True)
    nframes = db.Column(db.Integer, nullable=True)
    codec = db.Column(db.String(20), nullable=True)
    bitrate = db.Column(db.Integer, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Data em que o vídeo foi adicionado
    codec_info = db.Column(db.String(100), nullable=True)  # Informações do codec do vídeo
    thumbnail_path = db.Column(db.String(255), nullable=True)  # Caminho para a miniatura do vídeo
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    summaries = db.relationship('Summary', backref='video', lazy=True)


class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=True)  # Relaciona a Summary com a Library
    library = db.relationship('Library', backref='summaries', lazy=True)
