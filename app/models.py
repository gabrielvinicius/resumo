# app/models.py
import re
from datetime import datetime
from pytube import YouTube
from flask_login import UserMixin
from flask import url_for

from app import db


# from flask_security import UserMixin


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    version = db.Column(db.String(20), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    videos = db.relationship('Video', backref='user', lazy=True)


class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    processing_time = db.Column(db.Float, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(50), nullable=True)
    # Adiciona relação com Summary (um para muitos)
    summaries = db.relationship('Summary', backref='transcription', lazy=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    video_path = db.Column(db.String(255), nullable=True)
    audio_path = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Float, nullable=True)
    thumbnail_path = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    codec = db.Column(db.String(20), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Data em que o vídeo foi adicionado
    fps = db.Column(db.Float, nullable=True)
    transcription = db.relationship('Transcription', backref='video', uselist=False)

    def get_video_embed_html(self):
        youtube_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&.*)?$')
        if bool(youtube_pattern.match(self.video_path)):
            yt = YouTube(self.video_path)
            return yt.embed_html
        else:
            return (f'<video controls height="360" width="640"><source src="'
                    f'{url_for("video.download", video_id=self.id)}" type="video/mp4">'
                    f'Seu navegador não suporta a tag de vídeo.</video>')

    def get_thumbnail_html(self):
        youtube_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&.*)?$')
        if bool(youtube_pattern.match(self.video_path)):
            yt = YouTube(self.video_path)
            return '<img src="' + yt.thumbnail_url + '" alt="Thumbnail" class="card-img-top">'
        else:
            return '<img src="' + url_for('video.thumbnail',
                                          video_id=self.id) + '" alt="Thumbnail" class="card-img-top">'


class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float, nullable=False)
    # Adicione outras colunas conforme necessário
