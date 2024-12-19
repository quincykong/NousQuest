from flask import Blueprint, request, current_app
from app.utils.response_utils import create_response
from app.services.rabbitmq_config import send_to_rabbitmq

logging_bp = Blueprint('logging_bp', __name__)

@logging_bp.route('/api/frontendlog', methods=['POST'])
def log_frontend_error():
    """
    Log Frontend Error

    Logs error messages sent from the frontend.

    Request Body:
        {
            "message": "Error details",
            "clientInfo": {...}
        }

    Returns:
        Response:
            {
                "data": null,
                "message": "Error logged",
                "status": 200
            }
    """
    try:
        data = request.get_json()
        message = data.get('message')
        client_info = data.get('clientInfo', {})
        
        if not message:
            raise ValueError("No error message provided in the request.")
        
        send_to_rabbitmq(message, client_info)

        return create_response(data=None, message="Error logged", status=200)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Error logging frontend error: {str(e)}")
