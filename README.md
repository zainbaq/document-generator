# Document Generation Tool

A Python Flask-based tool that leverages OpenAI's GPT to generate documents. The tool takes two inputs—a template document and an original document—then uses a summarization process to extract the most relevant information and fills in the template accordingly. It supports various file formats including plain text (`.txt`, `.md`), Word documents (`.docx`), and PDFs (`.pdf`).

## Features

- **Multi-Format File Upload:** Accepts text, DOCX, and PDF files.
- **Context Optimization:** Summarizes the original document with reference to the template to reduce token usage.
- **Customizable Document Generation:** Uses a detailed prompt to instruct GPT to fill in the template precisely.
- **Environment-Safe API Keys:** Manages sensitive API keys using a `.env` file.
- **Flask Web Interface:** Simple web interface for file uploads and displaying generated documents.

## Prerequisites

- **Python 3.8+**
- **OpenAI API Key:** Sign up at [OpenAI](https://openai.com) and obtain an API key.
- **Virtual Environment:** Recommended to create an isolated Python environment.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/zainbaq/document-generator.git
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
    ```

    Important: Ensure your .env file is listed in .gitignore to prevent sensitive information from being committed.

## Usage

    Run the Application:

    ```bash
    python app.py
    ```

    The Flask development server should start, typically accessible at http://127.0.0.1:5000.

    Access the Web Interface:

    Open your browser and navigate to http://127.0.0.1:5000. You will see a form where you can upload your template and document files.

    Upload Files & Generate Document:
        Template File: Use a file that defines the structure of your final document.
        Document File: Use a file containing the content that needs to be summarized and inserted into the template.
        After uploading, click the "Generate Document" button. The tool will:
            Read and parse the files.
            Summarize the document content with reference to the template.
            Generate a final document by filling in the template.
        The generated document will be displayed on the results page.

## Project Structure

```bash
document-generation-tool/
├── app.py                # Main Flask application
├── prompts.json          # JSON file with detailed prompts for GPT
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (ignored by Git)
├── README.md             # This file
├── templates/
│   ├── index.html        # Upload form
│   └── result.html       # Display generated document
└── static/
    └── css/
        └── style.css     # Basic styling for the web interface
```

## Sample Files

Sample Template File (sample_template.txt)

```bash
Title: [Document Title]
Introduction:
  - Overview: [Insert brief overview here]
  - Purpose: [Insert purpose here]
Body:
  - Details: [Insert detailed information here]
Conclusion:
  - Summary: [Insert summary here]
```

## Sample Document File (sample_document.txt)

```bash
The document discusses the benefits of renewable energy. It begins by outlining various renewable energy sources such as solar, wind, and hydro power, emphasizing their potential to provide sustainable energy solutions. The purpose of the document is to inform readers about both the environmental and economic benefits of adopting renewable energy. In the detailed section, the document explains how renewable energy can lead to reduced greenhouse gas emissions, improved air quality, and long-term cost savings. Finally, the conclusion summarizes that transitioning to renewable energy is essential for ensuring a sustainable future.
```

## Troubleshooting

    OpenAI API Issues:
        Ensure your .env file is correctly set up with your valid OpenAI API key.
        Update the OpenAI Python package to the latest version using pip install --upgrade openai.

    File Format Errors:
        Verify that your uploaded files are in one of the supported formats: .txt, .md, .docx, or .pdf.

    ChatCompletion Errors:
        If you encounter errors related to the openai.ChatCompletion.create method, check that your messages are structured correctly as a flat list of dictionaries (system and user messages).

## License

This project is licensed under the MIT License.

## Acknowledgments

    Thanks to OpenAI for their powerful language models.
    Thanks to the developers and maintainers of Flask, python-docx, PyPDF2, and python-dotenv.
    Special thanks to the community for inspiring this project.


