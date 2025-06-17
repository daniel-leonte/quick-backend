"""
Main Flask application entry point for job search API.
"""
import os
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask application instance
app = create_app()

# The Flask application instance is created inside the main block
# to ensure it's not globally accessible, which is a good practice
# for preventing accidental use in imported modules.
if __name__ == '__main__':
  # Development server
  port = int(os.environ.get('PORT', 8080))
  host = os.environ.get('HOST', '0.0.0.0')

  logger.info(f"Starting development server on {host}:{port}")
  app.run(
      host=host,
      port=port,
      debug=app.config['DEBUG']
  )
