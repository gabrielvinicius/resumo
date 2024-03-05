# transcription.py
import whisper


def transcribe_video_audio(video_path):
    model = whisper.load_model("base")
    # Realiza a transcrição usando Whisper
    transcription = model.transcribe(video_path)

    return transcription.get('text')
