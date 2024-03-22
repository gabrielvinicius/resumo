import os
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip


class SpeechTranscriber:
    def __init__(self, model_size="large-v3"):
        # self.model = WhisperModel(model_size, device="CPU", compute_type="float32")
        self.model = WhisperModel(model_size, device="CPU", compute_type="int8")

    def transcribe(self, video_path):
        # Extrair áudio do arquivo de vídeo
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(video_dir, f"{video_name}.wav")
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path, fps=16000)  # Especificando a taxa de amostragem como 16000 Hz

        # Transcrição do áudio extraído
        segments, info = self.model.transcribe(audio=audio_path, beam_size=5)

        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        text = ""
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            text += segment.text
            # text.append(segment.text)

        # Remover o arquivo de áudio temporário após a transcrição
        # os.remove(audio_path)
        return text
