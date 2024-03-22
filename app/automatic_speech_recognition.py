import torch
from transformers import WhisperForConditionalGeneration, WhisperTokenizerFast


class SpeechTranscriber:
    def __init__(self):
        self.processor = WhisperTokenizerFast.from_pretrained("openai/whisper-large-v3")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3")

    def transcribe(self, video_path):
        """
        Transcribe speech from a video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            str: Transcribed text.
        """
        with torch.no_grad(), torch.cuda.amp.autocast():
            input_audio = self.processor(video_path, return_tensors="pt")
            input_features = input_audio.input_features
            generated_ids = self.model.generate(inputs=input_features)
            transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return transcription
