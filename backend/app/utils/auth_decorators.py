from functools import wraps
from flask import request, jsonify, make_response, current_app
from flask_jwt_extended import verify_jwt_in_request, decode_token, set_access_cookies, set_refresh_cookies
from app.utils.jwt_utils import create_jwt_token, set_tokens_in_cookies
from jwt import ExpiredSignatureError
#from flask_jwt_extended.exceptions import JWTDecodeError, ExpiredSignatureError

def jwt_required_with_refresh(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            print('*** Calling jwt_required_with_refresh decorator...')
            verify_jwt_in_request()  # Check if the access token is valid
            return fn(*args, **kwargs)  # If valid, proceed to the original function
        except ExpiredSignatureError:
            # Handle an expired access token
            print(f'\tjwt_required_with_refresh - error catched. Getting refresh_token from cookie: {current_app.config['JWT_REFRESH_COOKIE_NAME']}')
            refresh_token = request.cookies.get(current_app.config['JWT_REFRESH_COOKIE_NAME'])
            print(f'\t\tRefersh_token: {refresh_token}')
            if not refresh_token:
                return jsonify({"error": "Session expired, please log in again"}), 401
            
            try:
                # Decode refresh token and extract user info
                decoded_refresh_token = decode_token(refresh_token)
                print(f'\tDecode_refresh_token: {decoded_refresh_token}')
                user_id = decoded_refresh_token.get('sub')
                org_id = decoded_refresh_token.get(current_app.config.get('JWT_KEY_ORG_ID', 'org_id'))
                print(f'\tuser_id: {user_id} org_id: {org_id}')
                if not user_id or not org_id:
                    return jsonify({"error": "Invalid refresh token"}), 401

                # Create new tokens
                new_access_token, new_refresh_token = create_jwt_token(user_id, org_id)
                print(f'\tnew tokens have gnerated: new_access_token: {new_access_token} new_refresh_token: {new_refresh_token}')

                # Set new tokens in cookies
                #response = make_response(fn(*args, **kwargs))
                response = make_response()
                print(f'\t*** New response object has created ***')
                #set_tokens_in_cookies(response, new_access_token, new_refresh_token)
                set_access_cookies(response, new_access_token)
                set_refresh_cookies(response, new_refresh_token)
                print(f'\t*** Cookies has set ***')
                response.data = fn(*args, **kwargs).get_data()  # Add the function response data
                response.status_code = 200  # Assuming a successful request here
                print(f'\t*** Update response object and return to caller ***')

                return response

            # except ExpiredSignatureError:
                # print(f'\t\t ===== Refresh token expired =====')
                # return jsonify({"error": "Refresh token expired, please log in again"}), 401
            except Exception as e:
                print(f'\t\t ===== Error during token refresh: {str(e)} =====')
                return jsonify({"error": f"Error during token refresh: {str(e)}"}), 500
        except Exception as e:
            print(f'\t\t ===== Unexpected error: {str(e)} =====')
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    return wrapper
