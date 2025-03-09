import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create app instance with the specified configuration
app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config.get('HOST', '127.0.0.1'), port=app.config.get('PORT', 5000))