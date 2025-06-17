"""
Database operations for MongoDB Atlas integration.
"""
import logging
import os
from flask import g
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_client():
  """
  Returns the MongoDB client instance from the Flask global context.
  If it doesn't exist, it creates a new connection and stores it in the context.
  """
  if 'client' not in g:
    try:
      connection_string = os.environ.get('MONGODB_URI')
      if not connection_string:
        raise ValueError("MONGODB_URI environment variable not set.")

      client = MongoClient(
          connection_string,
          serverSelectionTimeoutMS=5000,
          connectTimeoutMS=10000,
          socketTimeoutMS=20000,
      )
      client.admin.command('ping')
      g.client = client
      logger.info("Successfully connected to MongoDB Atlas.")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
      logger.error(f"Failed to connect to MongoDB: {str(e)}")
      raise
    except Exception as e:
      logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
      raise
  return g.client


def get_db(database_name=None):
  """
  Returns a specific database from the client connection.
  If database_name is None, it uses the default from environment variables.
  """
  client = get_client()
  if database_name is None:
    database_name = os.environ.get('DATABASE_NAME', 'job_postings_db')
  return client[database_name]


def close_client(e=None):
  """
  Closes the MongoDB connection if it exists in the Flask global context.
  """
  client = g.pop('client', None)
  if client is not None:
    client.close()
    logger.info("MongoDB connection closed.")
