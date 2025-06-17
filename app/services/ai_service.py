"""
AI service for Vertex AI integration.
"""
import os
import logging
import vertexai
from vertexai.preview.generative_models import GenerativeModel

logger = logging.getLogger(__name__)

# Configuration
GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
GOOGLE_CLOUD_REGION = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')
DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'gemini-2.0-flash')


def initialize_vertex_ai():
  """Initialize Vertex AI with project configuration."""
  try:
    vertexai.init(
        project=GOOGLE_CLOUD_PROJECT_ID,
        location=GOOGLE_CLOUD_REGION)
    logger.info(
        f"Vertex AI initialized for project: {GOOGLE_CLOUD_PROJECT_ID}")
    return True
  except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {str(e)}")
    return False


def generate_llm_response(prompt: str, model_name: str = DEFAULT_MODEL) -> str:
  """Generate LLM response using Vertex AI Gemini model."""
  try:
    if not initialize_vertex_ai():
      return "Error: Failed to initialize Vertex AI"

    model = GenerativeModel(model_name)
    response = model.generate_content(prompt)

    if response and response.text:
      return response.text.strip()
    else:
      return "Unable to generate response - empty response from model"

  except Exception as e:
    logger.error(f"Error generating LLM response: {str(e)}")
    return f"Error generating response: {str(e)}"
