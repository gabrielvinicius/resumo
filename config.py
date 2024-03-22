# config.py


class Config:
    SECRET_KEY = 'gv060793'  # Defina uma chave secreta forte para segurança
    SQLALCHEMY_DATABASE_URI = 'mysql://summary:summary@45.33.198.3/summarization'  # Use SQLite como banco de dados por padrão
    UPLOAD_FOLDER = 'uploads'  # Diretório para upload de vídeos
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}  # Extensões permitidas para upload de vídeos
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # Limite de tamanho para upload de arquivos (1024MB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://summary:summary@45.33.198.3/summarization'  # Substitua pelos detalhes do seu banco de dados MySQL
    # Outras configurações específicas para produção


class DevelopmentConfig(Config):
    DEBUG = True
    # Outras configurações específicas para desenvolvimento
