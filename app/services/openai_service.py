import os
from openai import OpenAI
from flask import current_app

def get_openai_client():
    """
    Create and return an initialized OpenAI client.
    
    Returns:
        OpenAI: An initialized OpenAI client.
    """
    # Get API key from environment (via Flask config)
    api_key = current_app.config.get('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("The OpenAI API key is not set.")
    
    return OpenAI(api_key=api_key)

def get_prompts():
    """
    Get the prompts from the application configuration.
    
    Returns:
        dict: The loaded prompts.
    """
    prompts = current_app.config.get('PROMPTS')
    if not prompts:
        raise ValueError("Prompts not loaded in application configuration.")
    return prompts

def generate_completion(messages, model="gpt-4o", temperature=0.5, max_tokens=4096):
    """
    Generate a completion using OpenAI's chat completion API.
    
    Args:
        messages (list): List of message dictionaries (role and content).
        model (str): The model to use for completion.
        temperature (float): Controls randomness (0 to 1).
        max_tokens (int): Maximum number of tokens to generate.
        
    Returns:
        str: The generated content.
        
    Raises:
        Exception: If an error occurs during the API call.
    """
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"Error generating completion: {e}")
        raise