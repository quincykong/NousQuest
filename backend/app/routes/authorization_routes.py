from flask import Blueprint, request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, set_access_cookies, set_refresh_cookies
from app.utils.jwt_utils import create_jwt_token, verify_refresh_token #, set_tokens_in_cookies
from app.utils.response_utils import create_response
from app.utils.auth_decorators import inject_identity
from marshmallow import ValidationError

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh Access Token

    Refresh the user's access token using a valid refresh token stored in cookies.

    Returns:
        Response:
            {
                "data": {"access_token": "new_access_token"},
                "message": "Token refreshed successfully",
                "status": 200
            }
    """
    try:
        # Get refresh token from cookies
        refresh_token = request.cookies.get(current_app.config['JWT_REFRESH_COOKIE_NAME'])
        if not refresh_token:
            return create_response(data=None, message="Refresh token missing", status=400), 400

        # Verify refresh token
        user_id, org_id = verify_refresh_token(refresh_token)
        if not user_id:
            return create_response(data=None, message="Invalid or expired refresh token", status=401), 401

        # Create new tokens
        new_access_token, new_refresh_token = create_jwt_token(org_id, user_id)

        # Set the new tokens in cookies
        response = create_response(
            data={"access_token": new_access_token},
            message="Token refreshed successfully",
            status=200
        )
        set_tokens_in_cookies(response, new_access_token, new_refresh_token)

        return response

    except Exception as e:
        current_app.app_logger.error(f"Error during token refresh: {str(e)}")
        raise Exception("Token refresh error")


@auth_bp.route('/api/session', methods=['GET'])
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
