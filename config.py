import os

class Config:
    """Configuration settings for the application"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
    
    # Database settings
    DATABASE_PATH = 'data/documents.db'
    
    # NLP settings
    SPACY_MODEL = 'en_core_web_sm'
    SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'
    
    # Quiz settings
    QUIZ_QUESTIONS_DEFAULT = 5
    
    # Summarization settings
    SUMMARY_RATIO = 0.3  # 30% of original length