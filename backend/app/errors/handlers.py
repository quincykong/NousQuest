from flask import request, current_app
from marshmallow import ValidationError
from app.utils.response_utils import create_response
import traceback

def handle_validation_error(err):
    """Handles Marshmallow validation errors."""
    return create_response(
        data=None,
        message="Validation error",
        status=400
    ), 400

def handle_generic_error(err):
    """Handles generic exceptions."""
    # Capture and format the traceback
    error_traceback = traceback.format_exc()
    request_info = f"Request URL: {request.url} | Method: {request.method} | Body: {request.get_data(as_text=True)}"
    current_app.logger.error(f"Unhandled exception: {err}\n{request_info}\n{error_traceback}")

    return create_response(
        data=None,
        message="An unexpected error occurred.",
        status=500
    ), 500

def register_error_handlers(app):
    """Registers global error handlers."""
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(Exception, handle_generic_error)
