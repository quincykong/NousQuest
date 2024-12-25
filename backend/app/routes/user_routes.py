# user_routes.py
from flask import Blueprint, request, jsonify, make_response, current_app, g
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from app.utils.jwt_utils import create_jwt_token, set_tokens_in_cookies
from marshmallow import ValidationError
from app.schemas.user_schemas import ForgotPasswordSchema, LoginSchema
from app.services.user_service import user_service_login, user_service_logout, user_service_forgotpassword
from app.utils.response_utils import create_response
from app.utils.auth_decorators import inject_identity

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/login', methods=['POST'])
def login():
    """
        Perform authentications
        Request Body:
            {
                "userId": "user@example.com",
                "password": "password123"
            }
        Returns:
            Response:
                {
                    "data": {"id": "user_id", "org_id": "org_id"},
                    "message": "Login successful",
                    "status": 200
                }    
    """
    try:
        # Validate the request payload
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Perform login
        success, user_data, message = user_service_login(data['userId'], data['password'])

        if success:
            token_response = create_jwt_token(user_data["org_id"], user_data["id"])
            tokens = token_response.get_json().get("data")
            final_response = create_response(
                data={"user": user_data},
                message=message,
                status=200
            )
            set_tokens_in_cookies(final_response, tokens["access_token"], tokens["refresh_token"])
            return final_response
        
        return create_response(data=None, message=message, status=401)
    
    except ValidationError as ve:
        current_app.logger.error(f"ValueError: {str(ve)}")
        return create_response(data=None, message="Invalid credentials format", status=400)
    
    except Exception as e:
        current_app.logger.error(f"Unhandled exception: {str(e)}")
        return create_response(data=None, message="Server error", status=500)

@user_bp.route('/api/logout', methods=['POST'])
@inject_identity
@jwt_required()
def logout():
    """
        Logout user from system. Cookies are cleared.
        Args:
            None
        Response:
            {
                "data": null,
                "message": "Logout successful",
                "status": 200
            }    """
    try:
        user_id = g.user_id
        
        # Call the service to log out the user
        if not user_service_logout(user_id):
            raise Exception("Logout failed. Unable to clear user session.")
        
        # Create a successful logout response
        response = create_response(message="Logout successful", status=200)
        unset_jwt_cookies(response)
        
        return response
    
    except Exception as e:
        raise Exception(f"Error during logout: {str(e)}")


@user_bp.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    """
    Forgot Password Route

    Validates the incoming payload and triggers the forgot password service.

    Request Body:
        {
            "email": "user@example.com"
        }
    
    Returns:
        Response:
            {
                "data": null,
                "message": "Reset email sent successfully",
                "status": 200
            }
    """
    try:
        # Validate the request payload
        schema = ForgotPasswordSchema()
        data = schema.load(request.json)

        # Trigger the service
        success, message = user_service_forgotpassword(data['email'])

        # Return the response
        if success:
            return jsonify(create_response(message=message, status=200)), 200
        else:
            return jsonify(create_response(message=message, status=404)), 404

    except ValidationError as ve:
        # Validation errors are handled globally
        raise ve
    except Exception as e:
        raise Exception(f"Error during process forgot password: {str(e)}")


@user_bp.route('/api/session', methods=['GET'])
@inject_identity
@jwt_required()
def get_session():
    """
    Get User Session

    Retrieves the current user's session information (user ID and organization ID).

    Returns:
        Response:
            {
                "data": {"id": "user_id", "org_id": "org_id"},
                "message": "Session retrieved successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id

        # Return the session data
        return create_response(
            data={"id": user_id, "org_id": org_id},
            message="Session retrieved successfully",
            status=200
        )

    except Exception as e:
        current_app.app_logger.error(f"Error during session retrieval: {str(e)}")
        raise Exception("Session retrieval error")