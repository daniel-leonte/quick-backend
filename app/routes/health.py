"""
Health check routes.
"""
import os
import logging
from flask import Blueprint, jsonify
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from models import get_db

logger = logging.getLogger(__name__)

# Create Blueprint
health_bp = Blueprint('health', __name__)

# Configuration from environment variables
GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
GOOGLE_CLOUD_REGION = os.environ.get('GOOGLE_CLOUD_REGION', 'us-central1')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'job_postings_db')
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


@health_bp.route('/health', methods=['GET'])
def health_check():
  """Health check endpoint."""
  mongo_status = 'connected'
  try:
    get_db()
  except Exception:
    mongo_status = 'failed'

  vertex_initialized = initialize_vertex_ai()

  health_status = {
      'status': 'healthy' if vertex_initialized and mongo_status == 'connected' else 'unhealthy',
      'vertex_ai': 'connected' if vertex_initialized else 'failed',
      'mongodb': mongo_status,
      'project_id': GOOGLE_CLOUD_PROJECT_ID,
      'region': GOOGLE_CLOUD_REGION}

  status_code = 200 if health_status['status'] == 'healthy' else 503

  return jsonify(health_status), status_code


@health_bp.route('/models', methods=['GET'])
def get_available_models():
  """Get list of available Vertex AI models."""
  available_models = [
      'gemini-2.0-flash',
      'gemini-1.5-pro',
      'gemini-1.5-flash'
  ]

  return jsonify({
      'success': True,
      'available_models': available_models,
      'default_model': DEFAULT_MODEL
  })


@health_bp.route('/config', methods=['GET'])
def get_config():
  """Get current configuration information."""
  mongodb_uri = os.environ.get('MONGODB_URI')
  return jsonify({
      'project_id': GOOGLE_CLOUD_PROJECT_ID,
      'region': GOOGLE_CLOUD_REGION,
      'mongodb_configured': bool(mongodb_uri),
      'database_name': DATABASE_NAME
  })
