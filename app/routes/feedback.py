"""
Feedback routes.
"""
import logging
from flask import Blueprint, jsonify, request
from app.services.feedback_service import generate_feedback_for_answers
from app.services.exceptions import ServiceError

logger = logging.getLogger(__name__)

# Create Blueprint
feedback_bp = Blueprint('feedback', __name__)


def _json_error(message, status_code):
  """Creates a JSON error response."""
  return jsonify({
      'error': message,
      'success': False
  }), status_code


@feedback_bp.route('/feedback', methods=['POST'])
def generate_feedback_endpoint():
  """
  Generates feedback on interview answers.

  Expected JSON payload:
  {
      "job": {
          "title": "Senior Python Developer",
          "description": "...",
          "skills": ["Python", "Django", "AWS"]
      },
      "questions": [
          { "question": "...", "answer": "..." },
          { "question": "...", "answer": "..." }
      ]
  }
  """
  if not request.is_json:
    return _json_error('Request must be JSON', 400)

  data = request.get_json()
  job = data.get('job')
  questions = data.get('questions')

  if not job or not questions:
    return _json_error(
        '`job` and `questions` are required in request body', 400)

  try:
    result = generate_feedback_for_answers(job, questions)

    response_data = {
        'success': True,
        **result
    }

    logger.info(
        f"Successfully generated feedback for job: '{job.get('title', 'N/A')}'")
    return jsonify(response_data)

  except ServiceError as e:
    logger.error(f"Service error in feedback endpoint: {str(e)}")
    return _json_error(str(e), e.status_code)
  except Exception as e:
    logger.error(f"Unexpected error in feedback endpoint: {str(e)}")
    return _json_error(f'Internal server error: {str(e)}', 500)
