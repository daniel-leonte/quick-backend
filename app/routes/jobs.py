"""
Job search routes.
"""
import logging
from flask import Blueprint, jsonify, request
from app.services.job_service import search_jobs

logger = logging.getLogger(__name__)

# Create Blueprint
jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/jobs', methods=['POST'])
def search_jobs_endpoint():
  """
  Job search endpoint using AI-enhanced search.

  Expected JSON payload:
  {
      "query": "mobile developer",
      "tech_skills": ["Java", "Kotlin"],
      "job_level": "senior",
      "limit": 10
  }
  """
  try:
    # Validate request
    if not request.is_json:
      return jsonify({
          'error': 'Request must be JSON',
          'success': False
      }), 400

    data = request.get_json()
    query = data.get('query')

    if not query:
      return jsonify({
          'error': 'Query is required in request body',
          'success': False
      }), 400

    tech_skills = data.get('tech_skills')
    job_level = data.get('job_level')
    limit = data.get('limit', 10)

    # Search for jobs
    result = search_jobs(query, tech_skills=tech_skills, job_level=job_level, limit=limit)

    if 'error' in result:
      return jsonify({
          'success': False,
          'error': result['error'],
          'query': query
      }), 500

    # Prepare response
    response_data = {
        'success': True,
        'query': result['query'],
        'jobs': result['jobs'],
        'total': result['total'],
        'ai_generated': result.get('ai_generated', True)
    }

    logger.info(
        f"Jobs search completed for query: '{query}', returned {len(result['jobs'])} jobs")
    return jsonify(response_data)

  except Exception as e:
    logger.error(f"Unexpected error in jobs endpoint: {str(e)}")
    return jsonify({
        'error': f'Internal server error: {str(e)}',
        'success': False
    }), 500
