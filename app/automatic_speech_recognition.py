import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class SpeechTranscriber:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-large-v2")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v2")

    def transcribe(self, video_path):
        """
        Transcribe speech from a video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            str: Transcribed text.
        """
        input_audio = self.processor(video_path, return_tensors="pt")
        input_features = input_audio.input_features
        generated_ids = self.model.generate(inputs=input_features)
        transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return transcription
