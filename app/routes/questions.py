"""
Questions search routes.
"""
import logging
from flask import Blueprint, jsonify, request
from app.services.questions_service import generate_interview_questions
from app.services.exceptions import ServiceError

logger = logging.getLogger(__name__)

# Create Blueprint
questions_bp = Blueprint('questions', __name__)


def _json_error(message, status_code):
  """Creates a JSON error response."""
  return jsonify({
      'error': message,
      'success': False
  }), status_code


@questions_bp.route('/questions', methods=['POST'])
def generate_questions_endpoint():
  """
  Generates interview questions based on a job object.

  Expected JSON payload:
  {
      "job": {
          "title": "Senior Python Developer",
          "description": "...",
          "skills": ["Python", "Django", "AWS"]
      }
  }
  """
  if not request.is_json:
    return _json_error('Request must be JSON', 400)

  data = request.get_json()
  job = data.get('job')

  if not job:
    return _json_error('Job object is required in request body', 400)

  try:
    result = generate_interview_questions(job)

    response_data = {
        'success': True,
        **result
    }

    logger.info(
        f"Successfully generated {result['total']} questions for job: '{result['job_title']}'")
    return jsonify(response_data)

  except ServiceError as e:
    logger.error(f"Service error in questions endpoint: {str(e)}")
    return _json_error(str(e), e.status_code)
  except Exception as e:
    logger.error(f"Unexpected error in questions endpoint: {str(e)}")
    return _json_error(f'Internal server error: {str(e)}', 500)
