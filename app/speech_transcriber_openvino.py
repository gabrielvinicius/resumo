import os
import time

import torchaudio
from transformers import WhisperProcessor, pipeline, AutoProcessor
from optimum.intel import OVModelForSpeechSeq2Seq
from openvino import Core
import librosa


class SpeechTranscriber:
    def __init__(self, model_name='openai/whisper-large-v3-turbo', export_dir="whisper_openvino"):
        self.export_dir = export_dir
        self.model_name = model_name

        print("🔍 Detectando dispositivo OpenVINO...")
        self.device = self._detect_device()
        print(f"✔️ Dispositivo selecionado: {self.device}")

        print("📦 Verificando modelo exportado...")
        self._export_model_if_needed()

        print("📥 Carregando modelo e processador...")
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = OVModelForSpeechSeq2Seq.from_pretrained(self.export_dir, device=self.device)
        self.model.config.forced_decoder_ids = None

        self.model = OVModelForSpeechSeq2Seq.from_pretrained(str(self.export_dir), device=self.device)
        self.processor = AutoProcessor.from_pretrained(str(self.export_dir))

        self.model.config.forced_decoder_ids = None

        if hasattr(self.model, 'generation_config'):
            if hasattr(self.model.generation_config, 'forced_decoder_ids'):
                self.model.generation_config.forced_decoder_ids = None

        print("⚙️ Criando pipeline de transcrição...")
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            return_timestamps=True
        )
        print("✅ Pipeline pronto.")

    def _detect_device(self):
        try:
            core = Core()
            devices = core.available_devices
            if any("GPU" in d for d in devices):
                return "GPU"
            return "CPU"
        except Exception as e:
            print(f"⚠️ Erro ao detectar dispositivos OpenVINO: {e}")
            return "CPU"

    def _export_model_if_needed(self):
        if not os.path.exists(self.export_dir):
            print("📤 Exportando modelo para OpenVINO...")
            from subprocess import run
            run([
                "optimum-cli", "export", "openvino",
                "--model", self.model_name,
                "--task", "automatic-speech-recognition",
                self.export_dir
            ], check=True)
        else:
            print("🆗 Modelo já exportado.")

    def transcribe(self, audio_path: str):
        print("🎙️ Iniciando transcrição...")
        start_time = time.time()
        # audio_url = str(audio_path)
        waveform, sr = librosa.load(audio_path, sr=16000)
        predicted_ids = self.model.generate(waveform)
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        print(transcription)
        result = self.pipe(waveform)

        language_code = result.get("language", "en")
        language_name = self._language_map().get(language_code, "unknown")

        end_time = time.time()
        processing_time = end_time - start_time

        print("📝 Transcrição concluída.")
        return result["text"], processing_time, language_name

    @staticmethod
    def _language_map():
        return {
            "en": "english", "pt": "portuguese", "es": "spanish", "fr": "french",
            "de": "german", "it": "italian", "zh": "chinese", "ja": "japanese",
            "ko": "korean", "ru": "russian", "ar": "arabic", "tr": "turkish",
            "hi": "hindi", "id": "indonesian", "uk": "ukrainian", "pl": "polish",
            "nl": "dutch", "sv": "swedish", "fi": "finnish", "cs": "czech",
            "ro": "romanian", "da": "danish", "he": "hebrew", "el": "greek",
            "th": "thai", "vi": "vietnamese", "bn": "bengali", "ta": "tamil",
            "te": "telugu", "fa": "persian", "ur": "urdu", "no": "norwegian",
            "hu": "hungarian", "ml": "malayalam", "sl": "slovenian", "sr": "serbian",
            "lt": "lithuanian", "bg": "bulgarian", "sk": "slovak", "et": "estonian",
            # Adicione mais conforme necessário...
        }
