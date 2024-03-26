import os
import re
from uuid import uuid1

import requests
import youtube_dl


class VideoHandler:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def handle_upload(self, file):
        """
        Trata um vídeo carregado diretamente.
        """
        # Lógica de processamento de vídeo carregado
        filename = str(uuid1()) + '.mp4'
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path

    def handle_link(self, link):
        """
        Trata um vídeo fornecido como link.
        """
        if self.is_youtube_link(link):
            # Se for um link do YouTube, faça o download do áudio
            audio_file_path = self.download_youtube_audio(link)
            return audio_file_path
        else:
            # Caso contrário, faça o download do vídeo
            video_file_path = self.download_video(link)
            return video_file_path

    @staticmethod
    def is_youtube_link(link):
        """
        Verifica se o link fornecido é um link do YouTube.
        """
        youtube_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&.*)?$')
        return bool(youtube_pattern.match(link))

    def download_youtube_audio(self, youtube_link):
        """
        Faz o download do áudio de um vídeo do YouTube.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.upload_folder, '%(id)s.%(ext)s'),
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_link, download=False)
            video_id = info['id']
            audio_file_path = os.path.join(self.upload_folder, f'{video_id}.mp3')
            ydl.download([youtube_link])
        return audio_file_path

    def download_video(self, video_link):
        """
        Faz o download de um vídeo a partir de um link.
        """
        # Aqui você pode implementar a lógica para fazer o download do vídeo de um link normal
        # Por exemplo, usando a biblioteca requests para fazer o download do arquivo
        # e salvar no diretório de uploads
        video_file_path = os.path.join(self.upload_folder, 'video_from_link.mp4')
        response = requests.get(video_link)
        with open(video_file_path, 'wb') as f:
            f.write(response.content)
        return video_file_path

    def generate_youtube_embed_code(self, youtube_link):
        """
        Gera o código de incorporação (embed) de um vídeo do YouTube.
        """
        video_id = self.extract_youtube_video_id(youtube_link)
        if video_id:
            embed_code = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
            return embed_code
        else:
            return None

    @staticmethod
    def extract_youtube_video_id(youtube_link):
        """
        Extrai o ID do vídeo do YouTube a partir do link fornecido.
        """
        youtube_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)(?:&.*)?$')
        match = youtube_pattern.match(youtube_link)
        if match:
            return match.group(1)
        else:
            return None
