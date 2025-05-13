#app\tasks
from app import celery, db
#from flask import current_app
from app.models import Video, Transcription, Segment, Summary
from uuid import uuid1
import os
#from pathlib import Path
from moviepy import VideoFileClip
import imageio
from pytubefix import YouTube
from app.faster_whisper import SpeechTranscriber
from app.summarization import TFIDFSummarizer


@celery.task(bind=True)
def process_youtube_link(self, youtube_link, title, current_user_id):
    try:
        yt = YouTube(youtube_link)
        filename = str(uuid1()) + '.mp3'
        file_path = os.path.join('uploads', filename)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path='uploads', filename=filename)

        new_video = Video(
            title=title,
            video_path=youtube_link,
            duration=yt.length,
            thumbnail_path=yt.thumbnail_url,
            user_id=current_user_id,
            audio_path=file_path
        )

        db.session.add(new_video)
        db.session.commit()

        transcription_task.delay(new_video.id)

        return {'status': 'SUCCESS', 'video_id': new_video.id}

    except Exception as e:
        db.session.rollback()
        self.retry(exc=e, countdown=60, max_retries=3)
        return {'status': 'FAILURE', 'error': str(e)}

@celery.task(bind=True, name='app.save_video_file')
def save_video_file(self, file_path, title, filename, current_user_id):
    try:
        video_info = imageio.get_reader(file_path).get_meta_data()
        file_size = os.path.getsize(file_path)

        video = VideoFileClip(file_path)
        duration = video.duration

        thumbnail_filename = f'{filename}_thumbnail.jpg'
        thumbnail_path = os.path.join('uploads', thumbnail_filename)
        video.save_frame(thumbnail_path, t=(duration / 2))

        audio_filename = str(uuid1()) + '.wav'
        audio_path = os.path.join('uploads', audio_filename)
        video.audio.write_audiofile(audio_path, fps=16000, codec='pcm_s16le')

        new_video = Video(
            title=title,
            video_path=file_path,
            file_size=file_size,
            duration=duration,
            thumbnail_path=thumbnail_path,
            user_id=current_user_id,
            fps=video_info.get('fps'),
            codec=video_info['codec'],
            audio_path=audio_path
        )

        db.session.add(new_video)
        db.session.commit()

        # Inicia a tarefa de transcrição
        transcription_task.delay(new_video.id)

        return {
            'status': 'SUCCESS',
            'video_id': new_video.id,
            'message': 'Video file processed successfully'
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        self.retry(exc=e, countdown=60, max_retries=3)
        return {
            'status': 'FAILURE',
            'error': str(e),
            'message': 'Failed to process video file'
        }


@celery.task(bind=True, name='app.transcription_task')
def transcription_task(self, video_id):
    try:
        video = Video.query.get(video_id)
        transcriber = SpeechTranscriber()
        transcription_text, processing_time, language, segments = transcriber.transcribe(audio_path=video.audio_path)

        new_transcription = Transcription(
            text=transcription_text,
            video_id=video.id,
            processing_time=processing_time,
            language=language
        )
        db.session.add(new_transcription)
        db.session.commit()

        for segment_data in segments:
            segment = Segment(
                start=segment_data.start,
                end=segment_data.end,
                text=segment_data.text,
                transcription=new_transcription
            )
            db.session.add(segment)

        db.session.commit()

        # Inicia a tarefa de sumarização
        summarization_task.delay(new_transcription.id)

        return {
            'status': 'SUCCESS',
            'transcription_id': new_transcription.id
        }

    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return {
            'status': 'FAILURE',
            'error': str(e)
        }


@celery.task(bind=True, name='app.summarization_task')
def summarization_task(self, transcription_id):
    try:
        transcription = Transcription.query.get(transcription_id)
        summarizer = TFIDFSummarizer(language=transcription.language)
        summary_text, processing_time = summarizer.summarize(transcription.text)

        new_summary = Summary(
            text=summary_text,
            transcription_id=transcription.id,
            processing_time=processing_time
        )
        db.session.add(new_summary)
        db.session.commit()

        return {
            'status': 'SUCCESS',
            'summary_id': new_summary.id
        }

    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return {
            'status': 'FAILURE',
            'error': str(e)
        }