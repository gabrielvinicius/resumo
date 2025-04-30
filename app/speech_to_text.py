import time
from pathlib import Path

import torch
import torchaudio
from transformers import pipeline

class SpeechTranscriber:
    def __init__(self, model_size="base"):
        self.device = "xpu" if torch.xpu.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "xpu" else torch.float32

        # Inicializa pipeline com suporte a timestamps
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=f"openai/whisper-{model_size}",
            return_timestamps=True,
            device=0 if self.device == "xpu" else -1
        )

    def transcribe(self, audio_path):
        start_time = time.time()
        torchaudio.set_audio_backend("ffmpeg")
        path = Path(audio_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        path_str = path.as_posix()  # barras “/” funcionam em qualquer SO

        # audio_url = str(audio_path)
        waveform, sr = torchaudio.load(path_str)
        waveform = torchaudio.functional.resample(waveform, orig_freq=sr, new_freq=16000)
        waveform = waveform.mean(dim=0).numpy()  # Para pipe: precisa array, não tensor

        result = self.pipe({
            "array": waveform,
            "sampling_rate": 16000
        })

        transcription = result["text"]
        timestamps = result.get("chunks", [])
        processing_time = time.time() - start_time

        return transcription, processing_time, timestamps
