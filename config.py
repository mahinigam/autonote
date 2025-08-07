import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-change-me')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    UPLOAD_EXTENSIONS = ['.txt', '.pdf', '.docx', '.png', '.jpg', '.jpeg']
    UPLOAD_PATH = os.path.join(os.getcwd(), 'downloads')  # Use absolute path
    
    # API configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Security settings for production
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ensure downloads directory exists
    @classmethod
    def init_app(cls, app):
        os.makedirs(cls.UPLOAD_PATH, exist_ok=True)
