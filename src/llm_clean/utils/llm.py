import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_chat_model(model_id: str, temperature: float = 0.0):
    """
    Returns a LangChain ChatOpenAI instance configured for OpenRouter.
    
    Args:
        model_id (str): The model identifier (e.g., 'openai/gpt-4o').
        temperature (float): The sampling temperature. Defaults to 0.0.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set.")
        
    return ChatOpenAI(
        model=model_id,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature
    )
