import os
import whisper
from moviepy.editor import VideoFileClip


class SpeechTranscriber:
    def __init__(self, model_name='large-v3'):
        self.model = whisper.load_model(name=model_name, device="cpu")

    def transcribe(self, video_path):
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(video_dir, f"{video_name}.wav")
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path, fps=16000)
        model = whisper.load_model("base")
        result = model.transcribe(audio_path,verbose=None)
        return result.text
