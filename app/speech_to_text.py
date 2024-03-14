import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class SpeechTranscriber:
    def __init__(self, model_id="openai/whisper-large-v3"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=self.torch_dtype, use_safetensors=True)
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

    def transcribe(self, video_path):
        # script_directory = os.path.dirname(os.path.realpath(__file__))
        # video_path = os.path.join(script_directory, "..", "uploads", video_filename)

        print(f"Transcribing video at: {video_path}")

        result = self.pipe(video_path)
        transcribed_text = result["text"]

        return transcribed_text


if __name__ == "__main__":
    transcriber = SpeechTranscriber()
    video_filename = "seu_video.mp4"  # Substitua pelo nome real do seu vídeo
    transcription = transcriber.transcribe(video_filename)
    print("Transcrição do Áudio:")
    print(transcription)
