# transcription.py
from moviepy.editor import VideoFileClip
import whisper
from models import db, Video, Summary

def transcribe_video_audio(video_id):
    # Recupera o vídeo do banco de dados
    video = Video.query.get(video_id)

    if not video:
        raise ValueError(f"Video with ID {video_id} not found")

    # Carrega o vídeo usando MoviePy
    video_clip = VideoFileClip(video.file_path)

    # Obtém o áudio do vídeo
    audio = video_clip.audio
    model = whisper.load_model("base")
    # Realiza a transcrição usando Whisper
    transcription = model.predict(audio)

    # Salva a transcrição no banco de dados
    video.transcription = transcription
    db.session.commit()

    return transcription

