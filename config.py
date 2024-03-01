# config.py
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://summary:summary@45.33.198.3/summarization'
    SQLALCHEMY_TRACK_MODIFICATIONS = False