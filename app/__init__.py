"""
Flask application factory and configuration.
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from models import close_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
  """Application factory pattern for Flask app creation."""
  app = Flask(__name__)

  # Configuration
  app.config['SECRET_KEY'] = os.environ.get(
      'SECRET_KEY', 'dev-secret-key-change-in-production')
  app.config['DEBUG'] = os.environ.get(
      'FLASK_DEBUG', 'False').lower() == 'true'

  # Configure CORS
  CORS(app, origins=[
      'http://localhost:5173',
      'https://quickq-frontend.vercel.app'
  ])

  # Register blueprints
  from app.routes.health import health_bp
  from app.routes.jobs import jobs_bp
  from app.routes.questions import questions_bp
  from app.routes.feedback import feedback_bp

  app.register_blueprint(health_bp)
  app.register_blueprint(jobs_bp)
  app.register_blueprint(questions_bp)
  app.register_blueprint(feedback_bp)

  # Register teardown function
  app.teardown_appcontext(close_client)

  # Error handlers
  @app.errorhandler(404)
  def not_found(error):
    return {'error': 'Endpoint not found'}, 404

  @app.errorhandler(500)
  def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return {'error': 'Internal server error'}, 500

  logger.info("Flask application with job search functionality starting up...")
  logger.info(f"Debug mode: {app.config['DEBUG']}")

  return app
