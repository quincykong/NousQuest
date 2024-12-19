# user_routes.py
from flask import Blueprint, request, jsonify, make_response, current_app, g
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from app.utils.jwt_utils import create_jwt_token, set_tokens_in_cookies
from marshmallow import ValidationError
from app.schemas.user_schemas import ForgotPasswordSchema, LoginSchema
from app.services.user_service import user_service_login, user_service_logout, user_service_forgotpassword
from app.services.authorization_service import get_user_authorizations
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
        success, response = user_service_login(data['userId'], data['password'])
        if success:
            response_data = response.get_json()
            user_data = response_data.get("data")
            access_token, refresh_token = create_jwt_token(
                user_data.get("org_id"),
                user_data.get("id")
            )
            final_response = create_response(
                data=user_data,
                message=response_data.get("message"),
                status=200
            )
            set_tokens_in_cookies(final_response, access_token, refresh_token)
            return response
        return create_response(data=None, message="Invalid credentials", status=401), 401
    except ValidationError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Login error: {str(e)}")

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
    
@user_bp.route('/api/authorizations', methods=['GET'])
@inject_identity
@jwt_required()
def get_authorizations():
    """
        Retrieves all authorizations for the logged-in user and organization, or for specific resources if provided.
        Args:
            resources: Optional list of resource names to filter the authorizations
                        (e.g., ['StudentGroup', 'Quiz']). If not provided, fetch all resources.
        Returns: 
            Dictionary with resources as keys and authorization actions as values
    """
    try:
        # Extract the user_id from the JWT identity
        user_id = g.user_id 
        org_id = g.org_id
        resources = request.args.get('resources')

        result = get_user_authorizations(user_id, org_id, resources)

        return create_response(data=result, message=f"Authorization for resource: {resources} returned.", status=200)
    
    except PermissionError:
        # Raise a specific error if permissions are insufficient
        raise PermissionError("You do not have permission to access authorizations.")

    except Exception as e:
        # Raise a generic error for unexpected issues
        raise Exception(f"Error fetching authorizations: {str(e)}")

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
