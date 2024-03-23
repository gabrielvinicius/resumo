import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence


class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, audio):
        try:
            return self.recognizer.recognize_google(audio).capitalize()
        except sr.RequestError as e:
            print("Google Speech Recognition service request failed:", str(e))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
        return ""

    def split_audio_on_silence(self, audio):
        return split_on_silence(audio,
                                min_silence_len=500,
                                silence_thresh=audio.dBFS - 14,
                                keep_silence=500)

    def process_audio_chunks(self, chunks):
        transcribed_text = []
        for i, chunk in enumerate(chunks, start=1):
            chunk_filename = f"chunk{i}.wav"
            chunk.export(chunk_filename, format="wav")
            text = self.transcribe_audio(chunk)
            if text:
                print(chunk_filename, ":", text)
                transcribed_text.append(text + ".")
        return " ".join(transcribed_text)

    def transcribe_large_audio(self, audio_path):
        with AudioSegment.from_file(audio_path) as sound:
            chunks = self.split_audio_on_silence(sound)

        folder_name = "audio-chunks"
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        transcribed_text = self.process_audio_chunks(chunks)
        return transcribed_text


# Exemplo de uso:
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    transcribed_text = transcriber.transcribe_large_audio("audio_file.wav")
    print("Transcribed Text:")
    print(transcribed_text)
