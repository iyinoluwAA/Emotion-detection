"""
Structured error handling for API responses.
"""
from flask import jsonify
from typing import Dict, Any


class APIError(Exception):
    """Base exception for API errors."""
    status_code = 500
    message = "An error occurred"
    
    def __init__(self, message: str = None, status_code: int = None, details: Dict[str, Any] = None):
        super().__init__()
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.message,
            **self.details,
        }


class ValidationError(APIError):
    """Validation error (400)."""
    status_code = 400
    message = "Validation error"


class NotFoundError(APIError):
    """Resource not found (404)."""
    status_code = 404
    message = "Resource not found"


class ServiceUnavailableError(APIError):
    """Service unavailable (503)."""
    status_code = 503
    message = "Service unavailable"


def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500
