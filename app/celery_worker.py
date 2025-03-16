from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def make_celery(app_name=__name__):
    """
    Create a Celery instance with the given app name.
    
    Args:
        app_name (str): The name of the application.
        
    Returns:
        Celery: A configured Celery instance.
    """
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url,
        include=['app.tasks']
    )
    
    # Configure Celery
    celery.conf.update(
        result_expires=3600,  # Results expire after 1 hour
        task_acks_late=True,  # Tasks acknowledged after execution
        task_time_limit=600,  # 10 minutes timeout
        worker_prefetch_multiplier=1  # Prefetch one task at a time
    )
    
    return celery

# Create the Celery instance
celery = make_celery()

# If executing as script, start worker
if __name__ == '__main__':
    celery.start()