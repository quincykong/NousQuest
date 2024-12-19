from functools import wraps
from flask import g, request, jsonify, make_response, current_app
from flask_jwt_extended import (
    verify_jwt_in_request,
    decode_token,
    set_access_cookies,
    set_refresh_cookies,
)
from app.utils.jwt_utils import create_jwt_token

def inject_identity(f):
    """
    Decorator to inject user_id and org_id into the `g` context variable.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()  # Verify the access token
        identity = decode_token(request.cookies.get(current_app.config["JWT_ACCESS_COOKIE_NAME"]))  # Decode the JWT
        g.user_id = identity.get("sub")
        g.org_id = identity.get(current_app.config.get("JWT_KEY_ORG_ID", "org_id"))
        current_app.logger.debug(f"Authenticated user: {g.user_id}, org: {g.org_id}")
        return f(*args, **kwargs)
    return wrapper


def jwt_required_with_refresh(fn):
    """
    Decorator to handle refreshing tokens if the access token is expired.
    Assumes `inject_identity` is used to extract user/org IDs.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Attempt to verify access token
            verify_jwt_in_request()
            return fn(*args, **kwargs)  # Proceed to the original function if valid
        except Exception as access_token_error:
            current_app.logger.debug(f"Access token error: {access_token_error}")
            
            # Handle an expired or invalid access token
            refresh_token = request.cookies.get(current_app.config["JWT_REFRESH_COOKIE_NAME"])
            if not refresh_token:
                return jsonify({"error": "Session expired, please log in again"}), 401
            
            try:
                # Decode refresh token
                decoded_refresh_token = decode_token(refresh_token)
                g.user_id = decoded_refresh_token.get("sub")
                g.org_id = decoded_refresh_token.get(current_app.config.get("JWT_KEY_ORG_ID", "org_id"))
                
                if not g.user_id or not g.org_id:
                    return jsonify({"error": "Invalid refresh token"}), 401

                # Create new tokens
                new_access_token, new_refresh_token = create_jwt_token(g.user_id, g.org_id)
                response = make_response(fn(*args, **kwargs))  # Call the original function
                
                # Set new tokens in cookies
                set_access_cookies(response, new_access_token)
                set_refresh_cookies(response, new_refresh_token)
                return response
            
            except Exception as refresh_error:
                current_app.logger.error(f"Refresh token error: {refresh_error}")
                return jsonify({"error": "Unable to refresh token. Please log in again."}), 401
    
    return wrapper
