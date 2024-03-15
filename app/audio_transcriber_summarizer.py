import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSpeechSeq2Seq, pipeline


class SpeechTranscriberWithSummarization:
    def __init__(self, model_id_transcription="openai/whisper-large-v3", model_id_summarization="t5-small"):
        # Inicializa o modelo de transcrição
        self.transcription_model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id_transcription)
        self.transcription_tokenizer = AutoTokenizer.from_pretrained(model_id_transcription)
        self.transcription_pipe = pipeline(
            "automatic-speech-recognition",
            model=self.transcription_model,
            tokenizer=self.transcription_tokenizer,
            # feature_extractor=self.transcription_tokenizer.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        # Inicializa o modelo de sumarização
        self.summarization_model = AutoModelForSeq2SeqLM.from_pretrained(model_id_summarization)
        self.summarization_tokenizer = AutoTokenizer.from_pretrained(model_id_summarization)

    def transcribe(self, video_path):
        # Código para transcrição... (mantido igual ao exemplo anterior)
        transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
        result = transcriber(video_path)
        # transcribed_text = "Texto de exemplo transcrito."

        return result["text"]

    def summarize(self, text):
        # Obtém os tokens da transcrição
        transcription_tokens = self.transcription_tokenizer(text, return_tensors="pt", padding=True)

        # Gera a representação oculta usando o modelo de transcrição
        with torch.no_grad():
            transcription_hidden = self.transcription_model(**transcription_tokens).last_hidden_state

        # Utiliza o modelo de sumarização para gerar a sumarização
        summarization_tokens = self.summarization_model.generate(transcription_hidden)
        summarization_text = self.summarization_tokenizer.decode(summarization_tokens[0], skip_special_tokens=True)

        return summarization_text


if __name__ == "__main__":
    transcriber_with_summarization = SpeechTranscriberWithSummarization()
    video_filename = "seu_video.mp4"  # Substitua pelo nome real do seu vídeo
    transcribed_text = transcriber_with_summarization.transcribe(video_filename)
    summarization = transcriber_with_summarization.summarize(transcribed_text)

    print("Texto Transcrito:")
    print(transcribed_text)
    print("\nSumarização:")
    print(summarization)
