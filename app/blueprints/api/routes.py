import io
import os
import json
from flask import request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from . import api_bp
from app.services.file_processor import read_file_content, process_context_files
from app.services.document_generator import generate_document, generate_docx, generate_pdf

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        "status": "ok", 
        "message": "API is operational",
        "version": "1.0.0"
    })

@api_bp.route('/generate', methods=['POST'])
def generate_document_api():
    """
    API endpoint to generate a document from template and content files.
    
    Expected JSON payload:
    {
        "template_text": "Text content of the template",
        "document_text": "Text content of the document to extract info from",
        "output_format": "text|docx|pdf" (optional, defaults to "text")
    }
    
    Or multipart form data with:
    - template_file: File upload for the template
    - info_file: File upload for the document
    - context_files: (Optional) Additional context files
    - output_format: (Optional) "text", "docx", or "pdf"
    
    Returns:
    - JSON response with generated document text or
    - File download for docx/pdf formats
    """
    output_format = request.form.get('output_format', 'text')
    if output_format not in ['text', 'docx', 'pdf']:
        return jsonify({"error": "Invalid output format. Must be 'text', 'docx', or 'pdf'"}), 400
    
    # Handle JSON payload
    if request.is_json:
        data = request.get_json()
        if not data.get('template_text') or not data.get('document_text'):
            return jsonify({"error": "Both template_text and document_text are required"}), 400
        
        template_text = data.get('template_text')
        document_text = data.get('document_text')
        output_format = data.get('output_format', 'text')
        
        # Generate document
        try:
            result = generate_document(template_text, document_text)
            
            if output_format == 'text':
                return jsonify({"result": result})
            elif output_format == 'docx':
                docx_data = generate_docx(result)
                return send_file_response(docx_data, 'generated_document.docx', 
                                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            elif output_format == 'pdf':
                pdf_data = generate_pdf(result)
                return send_file_response(pdf_data, 'generated_document.pdf', 'application/pdf')
        except Exception as e:
            current_app.logger.error(f"Error generating document: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Handle form data with file uploads
    else:
        if 'template_file' not in request.files or 'info_file' not in request.files:
            return jsonify({"error": "Both template_file and info_file are required"}), 400
        
        template_file = request.files['template_file']
        info_file = request.files['info_file']
        
        if template_file.filename == "" or info_file.filename == "":
            return jsonify({"error": "Both template and information files must be selected"}), 400
        
        try:
            template_text = read_file_content(template_file)
            info_text = read_file_content(info_file)
            
            # Process additional context documents if provided
            context_files = request.files.getlist('context_files')
            retrieved_docs = process_context_files(context_files, template_text)
            
            # Generate document
            result = generate_document(template_text, info_text, context_chunks=retrieved_docs)
            
            if output_format == 'text':
                return jsonify({"result": result})
            elif output_format == 'docx':
                docx_data = generate_docx(result)
                return send_file_response(docx_data, 'generated_document.docx', 
                                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            elif output_format == 'pdf':
                pdf_data = generate_pdf(result)
                return send_file_response(pdf_data, 'generated_document.pdf', 'application/pdf')
        except Exception as e:
            current_app.logger.error(f"Error processing files: {str(e)}")
            return jsonify({"error": str(e)}), 500

def send_file_response(file_data, filename, mimetype):
    """Helper function to send file as response from the API."""
    return send_file(
        file_data,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )