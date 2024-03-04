# transcription.py
import whisper
from moviepy.editor import VideoFileClip
from app.models import db, Video
import numpy as np  # Importe a biblioteca NumPy

def transcribe_video_audio(video_id):
    # Recupera o vídeo do banco de dados
    video = Video.query.get(video_id)

    if not video:
        raise ValueError(f"Video with ID {video_id} not found")

    # Carrega o vídeo usando MoviePy
    video_clip = VideoFileClip(video.video_path)

    # Obtém o áudio do vídeo
    audio = video_clip.audio.to_soundarray()  # Converte o áudio para um array NumPy

    # Certifique-se de que o áudio seja um array NumPy
    if not isinstance(audio, np.ndarray):
        raise TypeError("Audio must be a NumPy array")

    model = whisper.load_model("base")
    # Realiza a transcrição usando Whisper
    transcription = model.transcribe(audio)

    # Salva a transcrição no banco de dados
    video.transcription = transcription
    db.session.commit()

    return transcription
