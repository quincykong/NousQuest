import jwt
from flask import current_app, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from jwt import decode as jwt_decode, ExpiredSignatureError, InvalidTokenError
from datetime import timedelta
from app.utils.response_utils import create_response

# Constants for token expiration
ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRES = timedelta(days=7)
JWT_KEY_ORG_ID = 'org_id'


def create_jwt_token(org_id, user_id, access_expires_delta=None):
    """
    Creates JWT access and refresh tokens for a given user and organization.

    Args:
        org_id (str): The organization ID to include in the token.
        user_id (str): The user ID for the token identity.
        access_expires_delta (timedelta, optional): Custom expiration for the access token.
            Defaults to `ACCESS_TOKEN_EXPIRES`.

    Returns:
        dict: A dictionary with access_token and refresh_token.
    """
    current_app.app_logger.debug(f"JWT_SECRET_KEY: {current_app.config.get('JWT_SECRET_KEY')}")

    try:
        access_token = create_token(
            identity=user_id,
            expires_delta=access_expires_delta or ACCESS_TOKEN_EXPIRES,
            org_id=org_id
        )
        refresh_token = create_token(
            identity=user_id,
            expires_delta=REFRESH_TOKEN_EXPIRES,
            org_id=org_id
        )
        return create_response(
            data={"access_token": access_token, "refresh_token": refresh_token},
            message="Tokens generated successfully.",
            status=200
        )
    except Exception as e:
        current_app.app_logger.error(f'Error creating JWT token: {e}')
        return create_response(message="Failed to create tokens.", status=500)


def create_token(identity, expires_delta, org_id=None):
    """
    Generates a JWT token with optional organization ID claims.

    Args:
        identity (str): The identity to include in the token (e.g., user ID).
        expires_delta (timedelta): The expiration duration for the token.
        org_id (str, optional): The organization ID to include as an additional claim.

    Returns:
        str: The generated JWT token.
    """
    additional_claims = {JWT_KEY_ORG_ID: org_id} if org_id else {}
    return create_access_token(identity=identity, additional_claims=additional_claims, expires_delta=expires_delta)


def configure_jwt_callbacks(jwt, app):
    """
    Configures JWT callbacks for the Flask application.

    Args:
        jwt (JWTManager): The Flask-JWT-Extended JWT manager instance.
        app (Flask): The Flask application instance.

    Returns:
        None
    """
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        """
        Handles unauthorized access attempts.

        Args:
            reason (str): The reason for unauthorized access.

        Returns:
            Response: A JSON response indicating unauthorized access.
        """
        headers = dict(request.headers)  # Log headers for unauthorized requests
        current_app.logger.error(f"Unauthorized access - Headers: {headers}")
        return create_response(message=f"Unauthorized access: {reason}", status=401)


def verify_refresh_token(refresh_token):
    """
    Verifies and decodes a refresh token.

    Args:
        refresh_token (str): The JWT refresh token to verify.

    Returns:
        Response: Standardized response with user_id and org_id or error.
    """
    try:
        decoded_token = decode_jwt_token(refresh_token)
        current_user_id = decoded_token.get('sub')
        org_id = decoded_token.get(JWT_KEY_ORG_ID)
        return create_response(
            data={"user_id": current_user_id, "org_id": org_id},
            message="Refresh token verified successfully.",
            status=200
        )
    except Exception as e:
        current_app.security_logger.error(f"Invalid refresh token: {e}")
        return create_response(message="Invalid refresh token.", status=401)


def decode_jwt_token(token):
    """
    Decodes and validates a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded JWT claims.

    Raises:
        Exception: If the token is expired, invalid, or cannot be decoded.
    """
    try:
        return jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
    except ExpiredSignatureError:
        current_app.security_logger.warning("JWT has expired.")
        raise Exception("JWT has expired")
    except InvalidTokenError as e:
        current_app.security_logger.warning(f"Invalid JWT: {e}")
        raise Exception(f"Invalid JWT: {e}")
    except Exception as e:
        current_app.security_logger.error(f"Error decoding JWT: {e}")
        raise Exception(f"Error decoding JWT: {e}")

def set_tokens_in_cookies(response, access_token, refresh_token):
    """
    Set access and refresh tokens as HttpOnly cookies on the response.
    
    Args:
        response (Response): Flask Response object to modify.
        access_token (str): The JWT access token.
        refresh_token (str): The JWT refresh token.
    """
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=current_app.config.get("JWT_COOKIE_SECURE", True),
        samesite=current_app.config.get("JWT_COOKIE_SAMESITE", "Lax"),
        max_age=current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 900),
        path="/api"
    )
    
    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=current_app.config.get("JWT_COOKIE_SECURE", True),
        samesite=current_app.config.get("JWT_COOKIE_SAMESITE", "Lax"),
        max_age=current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES", 86400),
        path="/api/token"
    )