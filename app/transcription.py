import os
import time

import torch
#import intel_extension_for_pytorch as ipex
import whisper
# from moviepy.editor import VideoFileClip


class SpeechTranscriber:
    def __init__(self, model_name='tiny'):
        print("Iniciando carregando o Modelo...")
        if torch.cuda.is_available():
            self.device = "cuda"
            self.torch_dtype = "float16"
        elif torch.xpu.is_available():
            self.device = "xpu"
            self.torch_dtype = "float16"
        else:
            self.device = "cpu"
            self.torch_dtype = "float32"

        print("O device foi "+self.device)
        # self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = whisper.load_model(name=model_name, device=self.device)
        #self.model = ipex.optimize(self.model)
        print("Modelo carregado")

    def transcribe(self, audio_path: str):
        print("Iniciando transcrição...")
        start_time = time.time()
        # video_dir = os.path.dirname(video_path)
        # video_name = os.path.splitext(os.path.basename(video_path))[0]
        # audio_path = os.path.join(video_dir, f"{video_name}.wav")
        # print("Extraindo áudio do vídeo...")
        # video = VideoFileClip(video_path)
        # audio = video.audio
        # audio.write_audiofile(audio_path, fps=16000, codec='pcm_s16le')
        # print("Transcrição do áudio...")
        result = self.model.transcribe(audio=audio_path, verbose=True, beam_size=5, word_timestamps=True)

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
        print("Transcrição concluída.")
        return result['text'], processing_time, LANGUAGES.get(result['language'])
