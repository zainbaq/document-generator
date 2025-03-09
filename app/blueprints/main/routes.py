import io
from flask import render_template, request, redirect, url_for, flash, session, send_file, current_app
from werkzeug.utils import secure_filename

from . import main_bp
from app.services.file_processor import read_uploaded_file, process_context_files
from app.services.document_generator import generate_document, generate_docx, generate_pdf

@main_bp.route('/')
def index():
    """Render the homepage with the file upload form."""
    return render_template('index.html')

@main_bp.route('/generate', methods=['POST'])
def generate():
    """
    Handle file uploads, including optional additional context documents.
    Process and parse the files, generate the final document, and render the result.
    """
    if 'template_file' not in request.files or 'info_file' not in request.files:
        flash("Both template and information files are required.")
        return redirect(request.url)

    template_file = request.files['template_file']
    info_file = request.files['info_file']

    if template_file.filename == "" or info_file.filename == "":
        flash("Please select both a template file and an information file.")
        return redirect(url_for('main.index'))

    try:
        template_text = read_uploaded_file(template_file)
        info_text = read_uploaded_file(info_file)
    except Exception as e:
        flash(f"Error reading files: {str(e)}")
        return redirect(url_for('main.index'))

    # Process additional context documents if provided
    context_files = request.files.getlist('context_files')
    retrieved_docs = process_context_files(context_files, template_text)
    
    # Generate the final document using the provided files and any retrieved context
    final_document = generate_document(template_text, info_text, context_chunks=retrieved_docs)

    # Store the generated document in session for download
    session['final_document'] = final_document
    return render_template('result.html', document=final_document)

@main_bp.route('/download')
def download():
    """
    Download the generated document as either a DOCX file or a PDF file.
    """
    filetype = request.args.get('filetype', 'docx').lower()
    final_document = session.get('final_document')
    if not final_document:
        flash("No document available for download.")
        return redirect(url_for('main.index'))
    
    if filetype == 'docx':
        file_data = generate_docx(final_document)
        return send_file(file_data, as_attachment=True, download_name="generated_document.docx", 
                         mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    elif filetype == 'pdf':
        file_data = generate_pdf(final_document)
        return send_file(file_data, as_attachment=True, download_name="generated_document.pdf", 
                         mimetype="application/pdf")
    else:
        flash("Invalid file type requested.")
        return redirect(url_for('main.index'))