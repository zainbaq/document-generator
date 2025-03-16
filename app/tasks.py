import os
import json
import time
from .celery_worker import celery
from dotenv import load_dotenv
from app.services.document_generator import generate_document
from app.services.file_processor import process_context_files

# Load environment variables
load_dotenv()

# A simple in-memory store for task progress
# In production, you'd want to use Redis directly
task_progress = {}

@celery.task(bind=True)
def generate_document_task(self, template_text, info_text, context_files_content=None):
    """
    Celery task to generate a document in the background.
    
    Args:
        self: Celery task instance
        template_text (str): The document template text
        info_text (str): The original document text
        context_files_content (list): List of context file contents (optional)
        
    Returns:
        str: The generated document
    """
    # Initialize task state
    self.update_state(
        state='PROGRESS',
        meta={'current': 0, 'total': 100, 'status': 'Starting document generation...'}
    )
    
    task_progress[self.request.id] = {
        'current': 0,
        'total': 100,
        'status': 'Starting document generation...'
    }
    
    try:
        # Process context if provided
        context_chunks = None
        if context_files_content:
            self.update_state(
                state='PROGRESS',
                meta={'current': 10, 'total': 100, 'status': 'Processing context files...'}
            )
            task_progress[self.request.id]['current'] = 10
            task_progress[self.request.id]['status'] = 'Processing context files...'
            
            # Here you would need to implement a version of process_context_files
            # that works with the content directly rather than file objects
            # For simplicity, we'll assume no context files for now
            pass
        
        # Update progress to indicate summarization is starting
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Summarizing document...'}
        )
        task_progress[self.request.id]['current'] = 30
        task_progress[self.request.id]['status'] = 'Summarizing document...'
        
        # Generate the document
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Generating document...'}
        )
        task_progress[self.request.id]['current'] = 50
        task_progress[self.request.id]['status'] = 'Generating document...'
        
        # Import here to ensure Flask app context is available
        from app import create_app
        app = create_app()
        
        with app.app_context():
            final_document = generate_document(template_text, info_text, context_chunks)
        
        # Simulating processing time
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing document...'}
        )
        task_progress[self.request.id]['current'] = 90
        task_progress[self.request.id]['status'] = 'Finalizing document...'
        
        # Set final state
        task_progress[self.request.id] = {
            'current': 100,
            'total': 100,
            'status': 'Complete',
            'result': final_document
        }
        
        return {'status': 'Complete', 'result': final_document}
    
    except Exception as e:
        # Update state to indicate failure
        error_message = str(e)
        task_progress[self.request.id] = {
            'current': 100,
            'total': 100,
            'status': 'Error',
            'error': error_message
        }
        self.update_state(
            state='FAILURE',
            meta={'status': 'Error', 'error': error_message}
        )
        raise