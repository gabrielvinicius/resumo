import re

def youtube_id(url):
    """
    Extrai o ID de um URL do YouTube
    Padrões suportados:
    - https://www.youtube.com/watch?v=ID
    - https://youtu.be/ID
    - https://www.youtube.com/embed/ID
    """
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
        r'^https?://youtu\.be/([\w-]+)',
        r'^https?://(?:www\.)?youtube\.com/embed/([\w-]+)'
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match and match.group(1):
            return match.group(1)
    return None


def format_time(seconds):
    """Formata segundos para MM:SS"""
    if seconds is None:
        return "00:00"
    seconds = float(seconds)
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def youtube_embed(url, width=560, height=315):
    """Gera código de embed para vídeos do YouTube"""
    video_id = youtube_id(url)
    if video_id:
        return f'<iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    return None

def is_youtube_url(url):
    youtube_pattern = re.compile(r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)')
    return bool(youtube_pattern.match(url)) if url else False

__all__ = ['youtube_id', 'format_time', 'youtube_embed','is_youtube_url']