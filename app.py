import json
import os
import io
from flask import Flask, request, render_template, redirect, url_for, flash
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Import LangChain modules for text splitting and summarization.
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.llms import OpenAI as LCOpenAI

# =============================================================================
# Load Environment Variables
# =============================================================================
load_dotenv()

# =============================================================================
# Initialize Flask App
# =============================================================================
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# =============================================================================
# Initialize OpenAI Client (Original Client)
# =============================================================================
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
if not client.api_key:
    raise ValueError("The OpenAI API key is not set. Please set it in the .env file.")

# =============================================================================
# Load GPT Prompt Configuration
# =============================================================================
with open('prompts.json', 'r') as file:
    prompts = json.load(file)

generate_document_prompt = prompts.get('generate_document_from_template_prompt')
if not generate_document_prompt:
    raise ValueError("The generate_document_from_template_prompt is not defined in prompts.json.")

# =============================================================================
# Utility Function: Read Uploaded File
# =============================================================================
def read_uploaded_file(uploaded_file):
    """
    Read the uploaded file and extract text based on its file type.
    Supports .txt, .md, .docx, and .pdf files.
    """
    filename = secure_filename(uploaded_file.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.txt', '.md']:
        return uploaded_file.read().decode('utf-8')
    elif ext == '.docx':
        from docx import Document
        doc = Document(uploaded_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
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
    else:
        return uploaded_file.read().decode('utf-8')

# =============================================================================
# Function: Summarize Document (Updated with LangChain and Document Conversion)
# =============================================================================
def summarize_document(document_text, template_text):
    """
    Summarize the given document text with reference to the template.
    If the document is long, use LangChain's text splitter and summarization chain to
    generate a concise summary; otherwise, use the standard summarization prompt.
    
    Args:
        document_text (str): The full text of the original document.
        template_text (str): The template text used for context.
    
    Returns:
        str: A summary of the document.
    """
    # Define a threshold (in characters) above which we consider the document "long"
    LONG_DOC_THRESHOLD = 3000
    
    if len(document_text) > LONG_DOC_THRESHOLD:
        # Import necessary modules for text splitting and document conversion.
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.docstore.document import Document
        
        # Split the long document into smaller chunks.
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(document_text)
        
        # Convert each text chunk into a Document object.
        docs = [Document(page_content=t) for t in texts]
        
        # Use the chat-based LLM wrapper for LangChain.
        from langchain.chat_models import ChatOpenAI
        llm = ChatOpenAI(temperature=0.5, model="gpt-4o")
        
        # Load a summarization chain (map_reduce is a good choice for long documents).
        from langchain.chains.summarize import load_summarize_chain
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        
        # Process each document chunk individually to avoid passing a list of prompts.
        partial_summaries = []
        for doc in docs:
            # Each call receives a single Document wrapped in a list.
            summary = chain.run([doc])
            partial_summaries.append(summary)
        
        # Combine the partial summaries into a single summary.
        long_summary = "\n".join(partial_summaries)
        document_text = long_summary

    # Proceed with the original summarization method using a custom prompt.
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
    messages = [
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
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error summarizing document: {e}")
        # In case of an error, fallback to using the (possibly long) document text.
        return document_text


# =============================================================================
# Function: Generate Document (Unchanged)
# =============================================================================
def generate_document(template_text, info_text):
    """
    Generate a document by combining the template with a summary of the original information text.
    
    Uses the new ChatCompletion interface with system and user messages.
    """
    summarized_info = summarize_document(info_text, template_text)
    
    system_prompt = generate_document_prompt  # Detailed instructions from prompts.json.
    user_prompt = (
        f"Template:\n{template_text}\n\n"
        f"Original Document Summary:\n{summarized_info}"
    )
    messages = [
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
        generated_document = response.choices[0].message.content
    except Exception as e:
        generated_document = f"An error occurred while generating the document: {str(e)}"
    
    return generated_document

# =============================================================================
# Route: Index Page
# =============================================================================
@app.route('/')
def index():
    """
    Render the homepage with the file upload form.
    
    Returns:
        Rendered HTML of the index page.
    """
    return render_template('index.html')

# =============================================================================
# Route: Document Generation
# =============================================================================
@app.route('/generate', methods=['POST'])
def generate():
    """
    Handle file uploads, process and parse the files (supporting .txt, .md, .docx, .pdf),
    summarize the original document with reference to the template, generate the final document,
    and render the result.
    
    Returns:
        Rendered HTML of the result page with the generated document.
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

    final_document = generate_document(template_text, info_text)
    return render_template('result.html', document=final_document)

# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == '__main__':
    # In production, replace Flask's built-in server with a production WSGI server.
    app.run(debug=True)
