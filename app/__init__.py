import os
import json
from flask import Flask
from .config import config

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Verify OpenAI API key
    if not app.config['OPENAI_API_KEY']:
        app.logger.warning("The OpenAI API key is not set. Please set it in the .env file.")
    
    # Load prompts
    app.config['PROMPTS'] = load_prompts()
    
    # Register blueprints
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def load_prompts():
    """Load prompts from JSON file."""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts.json'), 'r') as file:
            prompts = json.load(file)
        
        # Validate required prompts
        required_prompts = [
            'generate_document_from_template_prompt',
            'summarize_document_prompt'
        ]
        
        for prompt in required_prompts:
            if not prompts.get(prompt):
                raise ValueError(f"The {prompt} is not defined in prompts.json.")
                
        return prompts
    except Exception as e:
        raise ValueError(f"Error loading prompts: {str(e)}")