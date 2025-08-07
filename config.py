import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey-change-in-production')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    UPLOAD_EXTENSIONS = ['.txt', '.pdf', '.docx', '.png', '.jpg', '.jpeg']
    UPLOAD_PATH = 'downloads'
    
    # OpenAI API configuration (optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Flask-Limiter configuration
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Security settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
