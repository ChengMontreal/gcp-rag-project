# src/chatbot/lib/llms.py

from langchain_google_vertexai import ChatVertexAI
# CORRECTED IMPORT: Absolute path from the project root
from chatbot.config import REGION

def get_llm(streaming: bool = False, streaming_handler=None):
    """Initializes the ChatVertexAI model."""
    
    model_name = "gemini-2.5-flash"
    
    # Add streaming capabilities if requested
    if streaming:
        return ChatVertexAI(
            location=REGION,
            model_name=model_name,
            streaming=True,
            callbacks=[streaming_handler]
        )
    
    return ChatVertexAI(
        location=REGION,
        model_name=model_name
    )