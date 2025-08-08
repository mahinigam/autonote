import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

class Config:
    # Security - Generate secure secret key if not provided
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # File upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    UPLOAD_EXTENSIONS = ['.txt', '.pdf', '.docx']
    UPLOAD_PATH = os.path.join(os.getcwd(), 'downloads')  # Use absolute path
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Security settings for production
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # AI Service Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Ensure downloads directory exists
    @classmethod
    def init_app(cls, app):
        os.makedirs(cls.UPLOAD_PATH, exist_ok=True)
        
        # Log AI service status
        if cls.GEMINI_API_KEY:
            print("Google Gemini API key configured")
        else:
            print("GEMINI_API_KEY not found - AI features will use fallback mode")
