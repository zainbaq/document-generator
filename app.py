import json
import os
import io
from flask import Flask, request, render_template, redirect, url_for, flash
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing error messages

# Set your OpenAI API key from the environment
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)
if not client.api_key:
    raise ValueError("The OpenAI API key is not set. Please set it in the .env file.")

# Load the prompt from the JSON file
with open('prompts.json', 'r') as file:
    prompts = json.load(file)

generate_document_prompt = prompts.get('generate_document_from_template_prompt')
if not generate_document_prompt:
    raise ValueError("The generate_document_from_template_prompt is not defined in prompts.json.")

def read_uploaded_file(uploaded_file):
    """
    Read the uploaded file and extract text depending on its file type.
    Supports .txt, .md, .docx, and .pdf files.
    """
    filename = secure_filename(uploaded_file.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    # For text-based files
    if ext in ['.txt', '.md']:
        return uploaded_file.read().decode('utf-8')
    
    # For DOCX files
    elif ext == '.docx':
        from docx import Document
        doc = Document(uploaded_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    
    # For PDF files
    elif ext == '.pdf':
        import PyPDF2
        uploaded_file.seek(0)
        reader = PyPDF2.PdfReader(uploaded_file)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
    
    # Fallback to reading as text
    else:
        return uploaded_file.read().decode('utf-8')

def summarize_document(document_text, template_text):
    """
    Summarize the given document text with reference to the template.
    Only keep the information relevant to the sections and requirements in the template.
    Uses the new ChatCompletion interface with a system and user message.
    """
    system_prompt = (
        "You are an expert summarizer. Given the following template and document, "
        "generate a concise summary that includes only the information relevant to filling in the template. "
        "Provide the summary as bullet points."
    )
    user_prompt = (
        f"Template:\n{template_text}\n\n"
        f"Document:\n{document_text}\n\n"
        "Summary (bullet points):"
    )
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            temperature=0.5,
            max_tokens=500
        )
        print('Summary')
        print(response.choices[0].message.content)
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error summarizing document: {e}")
        # In case of error, fallback to using the original document text
        return document_text

def generate_document(template_text, info_text):
    """
    Generate a document by combining the template and a summary of the original information text.
    Uses the new ChatCompletion interface with system and user messages.
    """
    # Summarize the original document (with reference to the template)
    summarized_info = summarize_document(info_text, template_text)
    
    system_prompt = generate_document_prompt  # Your detailed instructions
    user_prompt = (
        f"Template:\n{template_text}\n\n"
        f"Original Document Summary:\n{summarized_info}"
    )
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    try:
        response = client.chat.completions.create(
            messages=messages[0],
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4096
        )
        print('Generation')
        print(response.choices[0].message.content)
        generated_document = response.choices[0].message.content
    except Exception as e:
        generated_document = f"An error occurred while generating the document: {str(e)}"
    
    return generated_document

@app.route('/')
def index():
    """
    Render the homepage with the file upload form.
    """
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    Handle file uploads, read and parse the files (supporting .txt, .md, .docx, .pdf),
    summarize the original document with reference to the template, generate the final document, and render the result.
    """
    if 'template_file' not in request.files or 'info_file' not in request.files:
        flash("Both files are required.")
        return redirect(request.url)

    template_file = request.files['template_file']
    info_file = request.files['info_file']

    if template_file.filename == "" or info_file.filename == "":
        flash("Please select both a template file and an information file.")
        return redirect(url_for('index'))

    try:
        template_text = read_uploaded_file(template_file)
        info_text = read_uploaded_file(info_file)
    except Exception as e:
        flash(f"Error reading files: {str(e)}")
        return redirect(url_for('index'))

    # Generate the final document using the summarized information
    final_document = generate_document(template_text, info_text)

    return render_template('result.html', document=final_document)

if __name__ == '__main__':
    app.run(debug=True)
