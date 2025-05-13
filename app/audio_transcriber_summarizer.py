from transformers import pipeline
from optimum.intel import OVModelForSpeechSeq2Seq
from transformers import WhisperProcessor
import torch

# Caminho do modelo OpenVINO otimizado (pode baixar via huggingface hub ou converter)
model_id = "openai/whisper-large-v3"

# Carrega processador e modelo com suporte a OpenVINO/XPU
processor = WhisperProcessor.from_pretrained(model_id)
model = OVModelForSpeechSeq2Seq.from_pretrained(model_id, export=True, device="xpu")

# Pipeline com o modelo carregado em XPU
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    return_timestamps=True
)

# Transcrição do áudio
result = pipe("seu_audio.wav")

print("Transcrição:")
print(result["text"])
