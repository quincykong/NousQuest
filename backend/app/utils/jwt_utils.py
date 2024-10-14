import jwt
from functools import wraps
from flask import current_app, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, decode_token, verify_jwt_in_request
from datetime import timedelta
#from app.utils.logging_config import app_logger, security_logger
#from app import app_logger, security_logger
from app.utils.rbac_utils import get_user_roles, get_user_permissions
from jwt import decode as jwt_decode, ExpiredSignatureError, InvalidTokenError

# Constants for token expiration
ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRES = timedelta(days=7)
JWT_KEY_ORG_ID = 'org_id'
JWT_KEY_ROLES = 'roles'
JWT_KEY_PERMISSIONS = 'permissions'

def create_jwt_token(org_id, user_id, access_expires_delta=None):
    roles = get_user_roles(org_id, user_id)
    permissions = get_user_permissions(org_id, user_id)

    try:
        additional_claims = {
            JWT_KEY_ORG_ID: org_id,
            JWT_KEY_ROLES: roles,
            JWT_KEY_PERMISSIONS: permissions
        }
        access_token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims,
            expires_delta=access_expires_delta or current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', ACCESS_TOKEN_EXPIRES)
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            #additional_claims=additional_claims,
            expires_delta=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', REFRESH_TOKEN_EXPIRES)
        )
    except Exception as e:
        current_app.app_logger.critical(f'create_jwt_token error: {e}')
        raise e
    
    return access_token, refresh_token

def get_jwt_identity_with_org(token=None):
    """
    Extracts user_id, org_id, and permissions from the JWT token stored in cookies.
    :return: user_id, org_id
    """

    if token is None:
        token = request.cookies.get(current_app.config['JWT_ACCESS_COOKIE_NAME'])
        if not token:
            raise Exception("JWT not found in cookies")

    try:
        current_app.app_logger.debug(f"\t----- calling get_jwt_identity_with_org access token retrieved from cookies")
        decoded_token = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token.get('sub')  # Assuming 'sub' contains user_id
        org_id = decoded_token.get(JWT_KEY_ORG_ID)
        current_app.app_logger.debug(f"\t----- after decoded. user_id: {user_id} org_id: {org_id}")
        return user_id, org_id
    
    except ExpiredSignatureError:
        print("JWT has expired.")
        raise Exception("JWT has expired")
    except InvalidTokenError as e:
        print(f"Invalid JWT: {e}")
        raise Exception(f"Invalid JWT: {e}")
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        raise Exception(f"Error decoding JWT: {e}")
    # except Exception as e:
    #     security_logger.critical(f"get_jwt_identity_with_org error: {str(e)}")
    #     return None, None

def verify_refresh_token(refresh_token):
    try:
        # Decode token
        current_user_id, org_id = get_jwt_identity_with_org(refresh_token)
        payload = decode_token(refresh_token)
        refresh_token_user_id = payload.get('sub')
        if refresh_token_user_id == current_user_id:
            return current_user_id, org_id
        else:
            return None, None
    except jwt.ExpiredSignatureError:
        current_app.security_logger.critical("Refresh token expired.")
        return False  
    except jwt.InvalidTokenError:
        current_app.security_logger.critical("Invalid refresh token.")
        return False

def set_tokens_in_cookies(response, access_token, refresh_token=None):
    response.set_cookie(current_app.config['JWT_ACCESS_COOKIE_NAME'], access_token, httponly=True, secure=True, samesite='Strict', max_age=24 * 60 * 60)
    if refresh_token:
        response.set_cookie(current_app.config['JWT_REFRESH_COOKIE_NAME'], refresh_token, httponly=True, secure=True, samesite='Strict', max_age=7 * 24 * 60 * 60)
