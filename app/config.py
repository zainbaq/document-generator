import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    HOST = '127.0.0.1'
    PORT = 5000


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    # Use a separate upload folder for testing
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_uploads')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Use stronger session key in production
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    # Production server can bind to 0.0.0.0 for public access if needed
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}