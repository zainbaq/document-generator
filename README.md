# Document Generation Tool

A Python Flask-based tool that leverages OpenAI's GPT to generate documents. The tool takes two inputs—a template document and an original document—then uses a summarization process to extract the most relevant information and fills in the template accordingly. It supports various file formats including plain text (`.txt`, `.md`), Word documents (`.docx`), and PDFs (`.pdf`).

## Features

- **Multi-Format File Upload:** Accepts text, DOCX, and PDF files.
- **Context Optimization:** Summarizes the original document with reference to the template to reduce token usage.
- **Customizable Document Generation:** Uses a detailed prompt to instruct GPT to fill in the template precisely.
- **Environment-Safe API Keys:** Manages sensitive API keys using a `.env` file.
- **Flask Web Interface:** Simple web interface for file uploads and displaying generated documents.
- **RESTful API:** Provides API endpoints for programmatic document generation.
- **Modular Architecture:** Organized with blueprints and service modules for better maintainability.

## Project Structure

```
document-generator/
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
├── run.py                  # Application entry point
├── requirements.txt        # Project dependencies
├── app/                    # Main application package
│   ├── __init__.py         # Application factory
│   ├── config.py           # Configuration settings
│   ├── prompts.json        # JSON file with detailed prompts
│   ├── blueprints/         # Blueprint modules
│   │   ├── __init__.py     
│   │   ├── main/           # Main web interface blueprint
│   │   │   ├── __init__.py # Blueprint initialization
│   │   │   └── routes.py   # Web routes
│   │   └── api/            # API blueprint
│   │       ├── __init__.py # Blueprint initialization
│   │       └── routes.py   # API endpoints
│   ├── services/           # Service modules
│   │   ├── __init__.py     
│   │   ├── document_generator.py # Document generation service
│   │   ├── file_processor.py     # File processing service
│   │   └── openai_service.py     # OpenAI integration service
│   ├── static/             # Static assets
│   │   └── css/
│   │       └── style.css
│   └── templates/          # HTML templates
│       ├── index.html
│       └── result.html
└── examples/               # Example usage scripts
    └── api_usage.py        # API usage example
```

## Prerequisites

- **Python 3.8+**
- **OpenAI API Key:** Sign up at [OpenAI](https://openai.com) and obtain an API key.
- **Virtual Environment:** Recommended to create an isolated Python environment.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/document-generator.git
   cd document-generator
   ```

2. **Create and Activate a Virtual Environment:**

    ***On Windows:***

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

    ***On macOS/Linux:***

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables:**

    Create a .env file in the root directory:

    ```bash
    touch .env
    ```

    ***Add your OpenAI API key to the .env file:***

    ```bash
    OPENAI_API_KEY=your_actual_api_key_here
    SECRET_KEY=your_secret_key_for_flask_sessions
    FLASK_CONFIG=development  # Options: development, testing, production
    ```

## Usage

### Running the Web Application

1. **Start the Flask Development Server:**

    ```bash
    python run.py
    ```

2. **Access the Web Interface:**

    Open your browser and navigate to http://127.0.0.1:5000. You will see a form where you can upload your template and document files.

3. **Upload Files & Generate Document:**
    - Template File: Use a file that defines the structure of your final document.
    - Document File: Use a file containing the content that needs to be summarized and inserted into the template.
    - After uploading, click the "Generate Document" button.
    - The generated document will be displayed on the results page.

### Using the API

The application provides a RESTful API for programmatic document generation:

#### Generate Document Endpoint

**POST /api/generate**

You can use this endpoint in two ways:

1. **JSON Payload:**

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_text": "Your template content here",
    "document_text": "Your document content here",
    "output_format": "text"
  }'
```

2. **Multipart Form Data with File Uploads:**

```bash
curl -X POST http://localhost:5000/api/generate \
  -F "template_file=@/path/to/template.txt" \
  -F "info_file=@/path/to/document.txt" \
  -F "output_format=text"
```

Available output formats:
- `text`: Returns JSON with the generated document text
- `docx`: Returns a DOCX file download
- `pdf`: Returns a PDF file download

#### Health Check Endpoint

**GET /api/health**

```bash
curl http://localhost:5000/api/health
```

## Application Configuration

The application supports multiple environment configurations:

- **Development**: Default configuration with debug mode enabled.
- **Testing**: For running automated tests.
- **Production**: Optimized for production deployment with debugging disabled.

You can switch between configurations by setting the `FLASK_CONFIG` environment variable in your `.env` file or by passing it directly to the application when running.

## Extending the Application

### Adding New Blueprints

To add a new feature module:

1. Create a new directory in `app/blueprints/`
2. Add `__init__.py` with blueprint definition
3. Add `routes.py` with route handlers
4. Register the blueprint in `app/__init__.py`

### Adding New Services

To add a new service:

1. Create a new Python module in `app/services/`
2. Import and use the service in your blueprint or other services

## Troubleshooting

- **OpenAI API Issues:**
    Ensure your .env file is correctly set up with your valid OpenAI API key.
    Update the OpenAI Python package to the latest version using pip install --upgrade openai.

- **File Format Errors:**
    Verify that your uploaded files are in one of the supported formats: .txt, .md, .docx, or .pdf.

- **API Connection Issues:**
    Check that you're using the correct endpoint URL and request format when making API calls.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Thanks to OpenAI for their powerful language models.
- Thanks to the developers and maintainers of Flask, python-docx, PyPDF2, and python-dotenv.
- Special thanks to the community for inspiring this project.