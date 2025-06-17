"""
Custom exceptions for service layer.
"""


class ServiceError(Exception):
  """Custom exception for service-related errors."""

  def __init__(self, message, status_code=500):
    super().__init__(message)
    self.status_code = status_code
