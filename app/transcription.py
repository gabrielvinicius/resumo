# transcription.py
import whisper
from moviepy.editor import VideoFileClip
from app.models import db, Video
import numpy as np  # Importe a biblioteca NumPy
import os

def transcribe_video_audio(video_id):
    # Recupera o vídeo do banco de dados
    video = Video.query.get(video_id)

    if not video:
        raise ValueError(f"Video with ID {video_id} not found")

    # Carrega o vídeo usando MoviePy
    video_clip = VideoFileClip(video.video_path)


    # Salva o áudio do vídeo em um arquivo wav
    # Obtém o nome do arquivo do vídeo sem a extensão
    video_name = os.path.splitext(os.path.basename(video.video_path))[0]
    # Define o caminho do arquivo wav usando o mesmo nome do vídeo
    audio_path = os.path.join(os.path.dirname(video.video_path), video_name + ".wav")
    if not os.path.exists(audio_path):
        # Escreve o áudio em um arquivo wav usando o MoviePy
        video_clip.audio.write_audiofile(audio_path)

    model = whisper.load_model("base")
    # Realiza a transcrição usando Whisper
    transcription = model.transcribe(audio_path)

    # Salva a transcrição no banco de dados
    video.transcription = transcription['text']
    db.session.commit()

    return transcription
