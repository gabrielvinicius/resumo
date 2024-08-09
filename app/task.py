from app import db
from app.models import Video, Summary, Transcription, Segment, Word
from app.transcription import SpeechTranscriber
from app.summarization import TFIDFSummarizer
from flask import flash
from celery import celery_app


@celery_app.task()
def transcription_task(video: Video):
    # Realiza a transcrição do vídeo
    transcriber = SpeechTranscriber()
    transcription_text, processing_time, language, segments = transcriber.transcribe(video.audio_path)

    # Cria uma nova transcrição associada ao vídeo
    new_transcription = Transcription(text=transcription_text, video_id=video.id, processing_time=processing_time,
                                      language=language)
    db.session.add(new_transcription)
    db.session.commit()

    for segment_data in segments:
        segment = Segment(start=segment_data.start, end=segment_data.end, text=segment_data.text,
                          transcription=new_transcription)
        db.session.add(segment)
        for word_text in segment_data.words:
            word = Word(text=word_text.word, segment=segment, start=word_text.start, end=word_text.end)
            db.session.add(word)

    db.session.commit()
    flash('Transcription completed successfully', 'success')


@celery_app.task()
def summarization_task(transcription: Transcription):
    summarizer = TFIDFSummarizer(language=transcription.language)
    # summarizerTopic = VideoTopicSummarizer(transcription)
    # print("Topicos:", summarizerTopic.identify_topic())
    summary_text, processing_time = summarizer.summarize(transcription.text)

    # Cria um novo resumo associado à transcrição
    new_summary = Summary(text=summary_text, transcription_id=transcription.id, processing_time=processing_time)
    db.session.add(new_summary)
    db.session.commit()

    flash('Summarization completed successfully', 'success')
