import os
from uuid import uuid1
import moviepy.editor as mp
import imageio
from pytubefix import YouTube

from app import db
from app.models import Video, Summary, Transcription, Segment
# from app.transcription import SpeechTranscriber
from app.faster_whisper import SpeechTranscriber

from app.summarization import TFIDFSummarizer
from celery import shared_task



UPLOAD_FOLDER = 'uploads'


@shared_task(ignore_result=False)
def transcription_task(video_id):
    # Realiza a transcrição do vídeo
    video = db.session.get(Video, video_id)
    print(video.audio_path)
    # video = Video.query.get(video_id)
    transcriber = SpeechTranscriber()
    # print(video.audio_path)
    transcription_text, processing_time, language, segments = transcriber.transcribe(audio_path=video.audio_path)

    # Cria uma nova transcrição associada ao vídeo
    new_transcription = Transcription(text=transcription_text, video_id=video.id, processing_time=processing_time,
                                      language=language)
    db.session.add(new_transcription)
    db.session.commit()

    for segment_data in segments:
        segment = Segment(start=segment_data.start, end=segment_data.end, text=segment_data.text,
                          transcription=new_transcription)
        db.session.add(segment)
        # for word_text in segment_data.words:
        #    word = Word(text=word_text.word, segment=segment, start=word_text.start, end=word_text.end)
        #    db.session.add(word)

    db.session.commit()
    summarization_task.delay(new_transcription.id)
    # flash('Transcription completed successfully', 'success')


@shared_task(ignore_result=False, serializer="json")
def summarization_task(transcription_id):
    transcription = db.session.get(Transcription, transcription_id)
    summarizer = TFIDFSummarizer(language=transcription.language)
    # summarizerTopic = VideoTopicSummarizer(transcription)
    # print("Topicos:", summarizerTopic.identify_topic())
    summary_text, processing_time = summarizer.summarize(transcription.text)

    # Cria um novo resumo associado à transcrição
    new_summary = Summary(text=summary_text, transcription_id=transcription.id, processing_time=processing_time)
    db.session.add(new_summary)
    db.session.commit()

    # flash('Summarization completed successfully', 'success')


@shared_task(ignore_result=False)
def process_youtube_link(youtube_link, title, current_user_id):
    # Lógica para processar o link do YouTube e obter o caminho do vídeo
    # Exemplo:
    yt = YouTube(youtube_link)
    filename = str(uuid1()) + '.mp3'
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(output_path=UPLOAD_FOLDER, filename=filename)
    # video_path = 'https://www.youtube.com/watch?v=video_id'
    thumbnail_url = yt.thumbnail_url
    duration = yt.length
    new_video = Video(title=title, video_path=youtube_link, duration=duration,
                      thumbnail_path=thumbnail_url, user_id=current_user_id, audio_path=file_path)
    db.session.add(new_video)
    db.session.commit()
    transcription_task.delay(new_video.id)
    # return new_video


@shared_task(ignore_result=False)
def save_video_file(file_path, title, filename, current_user_id):
    # Lógica para salvar o arquivo de vídeo e obter seu caminho
    # Exemplo:

    video_info = imageio.get_reader(file_path).get_meta_data()

    file_size = os.path.getsize(file_path)

    video = mp.VideoFileClip(file_path)
    duration = video.duration

    thumbnail_filename = f'{filename}_thumbnail.jpg'
    thumbnail_path = os.path.join(UPLOAD_FOLDER, thumbnail_filename)
    video.save_frame(thumbnail_path, t=(duration / 2))

    fps = video_info.get('fps')
    codec = video_info['codec']

    audio = video.audio
    audio_filename = str(uuid1()) + '.wav'
    audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
    audio.write_audiofile(audio_path, fps=16000, codec='pcm_s16le')

    new_video = Video(title=title, video_path=file_path, file_size=file_size, duration=duration,
                      thumbnail_path=thumbnail_path, user_id=current_user_id, fps=fps, codec=codec,
                      audio_path=audio_path)

    # video_path = '/path/to/video/file.mp4'
    db.session.add(new_video)
    db.session.commit()
    transcription_task.delay(new_video.id)
    # return new_video
