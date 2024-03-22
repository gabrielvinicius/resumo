# app/faster_whisper.py
import os
from datetime import datetime
import time

from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel


class SpeechTranscriber:
    def __init__(self, model_size="large-v3"):
        self.model = WhisperModel(model_size, device="CPU", compute_type="int8")

    def transcribe(self, video_path):
        start_time = time.time()

        # Extrair áudio do arquivo de vídeo
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(video_dir, f"{video_name}.wav")
        # audio_path = os.path.join(video_dir, f"{video_name}.flac")
        video = VideoFileClip(video_path)
        audio = video.audio
        # audio.write_audiofile(audio_path, fps=16000)  # Especificando a taxa de amostragem como 16000 Hz
        audio.write_audiofile(audio_path, fps=16000, codec='pcm_s16le')

        # Transcrição do áudio extraído
        segments, info = self.model.transcribe(audio=audio_path, beam_size=5, vad_filter=True)
        # segments, info = self.model.transcribe(audio=video_path, beam_size=5, vad_filter=True)
        # segments = list(segments)
        text = "".join(segments)
        # for segment in segments:
          # text += segment.text

        # Remover o arquivo de áudio temporário após a transcrição
        # os.remove(audio_path)


        LANGUAGES = {
            "en": "english",
            "zh": "chinese",
            "de": "german",
            "es": "spanish",
            "ru": "russian",
            "ko": "korean",
            "fr": "french",
            "ja": "japanese",
            "pt": "portuguese",
            "tr": "turkish",
            "pl": "polish",
            "ca": "catalan",
            "nl": "dutch",
            "ar": "arabic",
            "sv": "swedish",
            "it": "italian",
            "id": "indonesian",
            "hi": "hindi",
            "fi": "finnish",
            "vi": "vietnamese",
            "he": "hebrew",
            "uk": "ukrainian",
            "el": "greek",
            "ms": "malay",
            "cs": "czech",
            "ro": "romanian",
            "da": "danish",
            "hu": "hungarian",
            "ta": "tamil",
            "no": "norwegian",
            "th": "thai",
            "ur": "urdu",
            "hr": "croatian",
            "bg": "bulgarian",
            "lt": "lithuanian",
            "la": "latin",
            "mi": "maori",
            "ml": "malayalam",
            "cy": "welsh",
            "sk": "slovak",
            "te": "telugu",
            "fa": "persian",
            "lv": "latvian",
            "bn": "bengali",
            "sr": "serbian",
            "az": "azerbaijani",
            "sl": "slovenian",
            "kn": "kannada",
            "et": "estonian",
            "mk": "macedonian",
            "br": "breton",
            "eu": "basque",
            "is": "icelandic",
            "hy": "armenian",
            "ne": "nepali",
            "mn": "mongolian",
            "bs": "bosnian",
            "kk": "kazakh",
            "sq": "albanian",
            "sw": "swahili",
            "gl": "galician",
            "mr": "marathi",
            "pa": "punjabi",
            "si": "sinhala",
            "km": "khmer",
            "sn": "shona",
            "yo": "yoruba",
            "so": "somali",
            "af": "afrikaans",
            "oc": "occitan",
            "ka": "georgian",
            "be": "belarusian",
            "tg": "tajik",
            "sd": "sindhi",
            "gu": "gujarati",
            "am": "amharic",
            "yi": "yiddish",
            "lo": "lao",
            "uz": "uzbek",
            "fo": "faroese",
            "ht": "haitian creole",
            "ps": "pashto",
            "tk": "turkmen",
            "nn": "nynorsk",
            "mt": "maltese",
            "sa": "sanskrit",
            "lb": "luxembourgish",
            "my": "myanmar",
            "bo": "tibetan",
            "tl": "tagalog",
            "mg": "malagasy",
            "as": "assamese",
            "tt": "tatar",
            "haw": "hawaiian",
            "ln": "lingala",
            "ha": "hausa",
            "ba": "bashkir",
            "jw": "javanese",
            "su": "sundanese",
            "yue": "cantonese",
        }
        end_time = time.time()
        processing_time = end_time - start_time
        return text, processing_time, LANGUAGES.get(info.language)
