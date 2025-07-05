from openai import OpenAI
from dotenv import load_dotenv
import os
from config import DEFAULT_MODEL

load_dotenv()

def get_openai_client():
    """Create and return OpenAI client configured for OpenRouter"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    return client

def chat_completion(messages, model=None):
    """Simple wrapper for chat completion with centralized model config"""
    if model is None:
        model = DEFAULT_MODEL
        
    client = get_openai_client()
    
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    
    return completion.choices[0].message.content

# Test function
if __name__ == "__main__":
    test_messages = [
        {"role": "user", "content": "What is 2+2?"}
    ]
    
    try:
        response = chat_completion(test_messages)
        print(f"Test successful with model {DEFAULT_MODEL}: {response}")
    except Exception as e:
        print(f"Test failed: {e}") 