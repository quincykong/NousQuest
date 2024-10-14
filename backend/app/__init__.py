import os
import inspect
from datetime import datetime, timezone, timedelta
from flask import Flask, request
from flask_cors import CORS
from jwt import ExpiredSignatureError
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, verify_jwt_in_request, decode_token
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.utils.jwt_utils import create_jwt_token, set_tokens_in_cookies

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config.from_object(Config)
    #   security-related settings from Config.SECURITY dictionary
    app.config.update(Config.SECURITY)

    # Create uploads folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize the other components
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize the loggers
    with app.app_context():
        from app.utils.logging_config import initialize_loggers, get_app_logger, get_security_logger, get_frontend_logger
        initialize_loggers(app)
        # Assign global loggers
        #global app_logger, security_logger, frontend_logger
        app.app_logger = get_app_logger()
        app.security_logger = get_security_logger()
        app.frontend_logger = get_frontend_logger()

    # CORS configuration
    CORS(app, 
        resources={r"/api/*": {"origins": ["http://127.0.0.1:3000", "http://localhost:3000"]}},
        supports_credentials=True)
    #CORS(app, origins=["http://127.0.0.1:3000", "http://localhost:3000"], supports_credentials=True)

    # Register API blueprints
    from app.api.backend_api import api_bp
    app.register_blueprint(api_bp, strict_slashes=False)

    # Refresh the token if access_token expires but refresh_token is still valid
    @app.after_request
    def refresh_expiring_access_token(response):
        app.app_logger.debug('***** Entering refresh_expiring_access_token after API call ...')
        try:
            #verify_jwt_in_request(optional=True)  # This will verify if there's a JWT present
            verify_jwt_in_request()
            app.app_logger.debug(f'\t***** Completed verify_jwt_in_request. Going to check if new token is required...')

            #get exp 
            jwt_data = get_jwt()
            access_token_exp = jwt_data["exp"]
            access_token_exp_datetime = datetime.fromtimestamp(access_token_exp, tz=timezone.utc)
            app.app_logger.debug(f'\t***** access_token [exp]: {access_token_exp_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")}')
            refresh_token_cookie = request.cookies.get(app.config["JWT_REFRESH_COOKIE_NAME"])
            refresh_token_decoded = decode_token(refresh_token_cookie)
            refresh_token_exp_timestamp = refresh_token_decoded["exp"]
            refresh_token_exp_datetime = datetime.fromtimestamp(refresh_token_exp_timestamp, tz=timezone.utc)
            app.app_logger.debug(f'\t***** refresh_token [exp]: {refresh_token_exp_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")}')

            if datetime.now(timezone.utc) > refresh_token_exp_datetime:
                app.app_logger.debug("\t***** Refresh token expired, cannot refresh access token.")
                # add logic to logging out the user.
                return
            
            access_token_threshold = app.config.get('JWT_ACCESS_TOKEN_EXPIRES').total_seconds()
            #app.app_logger.debug(f"\t***** access_token_threshold: {access_token_threshold}")
            #app.app_logger.debug(f"\t{(access_token_exp_datetime - datetime.now(timezone.utc)).total_seconds()}")
            if (access_token_exp_datetime - datetime.now(timezone.utc)).total_seconds() < access_token_threshold:
                app.app_logger.debug(f'\t***** Token close to expiry - refreshing access_token ...')
                # Extract user_id and org_id from JWT for new token generation
                user_id = get_jwt_identity()
                org_id = get_jwt().get(app.config.get('JWT_KEY_ORG_ID', 'org_id'))

                # Calculate the remaining time for the refresh token to expire
                remaining_refresh_time = (refresh_token_exp_datetime - datetime.now(timezone.utc)).total_seconds()
                app.app_logger.debug(f'\t***** remaining_refresh_time: {remaining_refresh_time} ...')
                access_token_config_expiry = access_token_threshold
                # Take the smallest value from threshold value or remaining time of refresh_token 
                #   to ensure new access_token exp won't exceed refresh_token exp
                new_access_token_expiry_seconds = min(remaining_refresh_time, access_token_config_expiry)
                app.app_logger.debug(f'\t***** new_access_token_expiry_seconds: {new_access_token_expiry_seconds} ...')

                access_expires_delta = timedelta(seconds=new_access_token_expiry_seconds)
                new_access_token, _ = create_jwt_token(org_id, user_id, access_expires_delta=access_expires_delta)

                # Set the new access and refresh tokens in cookies
                set_tokens_in_cookies(response, new_access_token)   # not to update refresh_token
                app.app_logger.debug('\t***** access_token has been refreshed and set to cookies')
            else:
                app.app_logger.debug('\t***** access_token is still valid. Exiting refresh_expiring_access_token *****')
            return response
        
        except (RuntimeError, KeyError) as e:
            # Handle cases when no JWT is present (e.g., accessing static files or public endpoints)
            app.app_logger.warning(f'__init__ refresh_expiring_access_token - RuntimeError or KeyError: {str(e)}')
            return response
        except Exception as e:
            # Log unexpected errors during the refresh process
            # Consider adding the token to a denylist if needed
            app.app_logger.warning(f'__init__ refresh_expiring_access_token - Unexpected error during JWT refresh: {str(e)}')
            return response

    return app

app = create_app()
