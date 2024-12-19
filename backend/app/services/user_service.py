from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for, jsonify
from app.extensions import db
from app.models.authorization_models import User, Authorization, user_securityroles, securityrole_authorizations
from app.models.resource_models import Resource
from app.models.action_models import Action

from app.models.authorization_models import SecurityRole
from app.constants import USER_ROUTES
from app.config.message_config import send_email
#from app.utils.logging_config import security_logger, app_logger
#from app import app_logger, security_logger
from app.schemas.user_schemas import LoginSchema, ForgotPasswordSchema
from app.utils.response_utils import create_response

def user_service_login(userId, password):
    """
    Handles user login logic, including credential validation, account locking, and logging.

    Args:
        email (str): The user's email address.
        password (str): The user's password.

    Returns:
        tuple: A boolean indicating success, and either JWT tokens (on success) or an error response (on failure).
    """
    schema = LoginSchema()
    current_app.app_logger.debug(f"Login attempt with userId: {userId}, password: {password}")
    errors = schema.validate({"userId": userId, "password": password})
    if errors:
        current_app.app_logger.debug(f"Validation errors: {errors}")
        return False, create_response(message="Failure to pass schema validation.", status=400)
    
    user = User.query.filter_by(email=userId).first()
    current_app.app_logger.debug(f"userId:{userId}")
    if user and not user.locked:
        if user.check_password(password):
            user.last_logon = datetime.now(timezone.utc)
            user.logon_attempt = 0
            db.session.commit()
            current_app.security_logger.info(f'User logged in: {user.username}')
            #return True, access_token, refresh_token, user.id, user.org_id
            return True, create_response(data={user.id, user.org_id}, message="Login successful", status=200)
        else:
            handle_failed_login(user)
            return False, create_response(message="Invalid credentials. Please try again.", status=401)
    elif user and user.locked:
        current_app.security_logger.critical(f'Attempted login to locked account: {user.id}')
        return False, create_response(message="Your account is locked due to too many attempted logins. Please contact the system administrator.", status=403)
    else:
        current_app.security_logger.critical(f'Login attempt with unknown email: {userId}')
        return False, create_response(message="No credentials match.", status=401)

# user_service_login helper
def get_redirect_url(user):
    # current_app.security_logger.debug(f'user.userclass: {user.userclass}')
    if user.userclass == UserClassEnum.ADMIN:
        return USER_ROUTES['admin_home']
    elif user.userclass == UserClassEnum.INSTRUCTOR:
        return USER_ROUTES['instructor_home']
    elif user.userclass == UserClassEnum.STUDENT:
        return USER_ROUTES['student_home']
    return '/home'  # Default fallback 

# user_service_login helper
def handle_failed_login(user):
    user.logon_attempt += 1
    if user.logon_attempt > 5:
        user.locked = True
        db.session.commit()
        current_app.security_logger.critical(f'Account locked for user: {user.id}')
        return 'Too many login attempts. Your account is now locked.'
    else:
        db.session.commit()
        current_app.security_logger.warning(f'Invalid login attempt for user: {user.id}')

def user_service_logout(user_id):
    current_app.security_logger.info(f'User logged out: {user_id}')
    #localStorage.removeItem("access_token");
    return True


def user_service_forgotpassword(email):
    user = User.query.filter_by(email=email).first()
    if user:
        token = generate_reset_token(user)
        subject = "Requet for password reset"
        msgBody = f"""To reset your password, visit the following link:
            {url_for('reset_token', token=token, _external=True)}
            If you did not make this request, simply ignore this email and no changes will be made.
            """
        success = send_email(subject, email, msgBody, organization_id)
        if success:
            return True, "Password reset instructions have been sent to your email."
        else:
            return False, ""
    else:
        return False, "Credential not found."


def generate_reset_token(user, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.Config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')


def user_service_forgotpassword(email):
    """
    Business logic for handling forgot password requests.

    Args:
        email (str): The email address of the user requesting a password reset.

    Returns:
        tuple: A success flag (bool) and a message (str).
    """
    # Simulate checking the database for the email
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return False, "Email address not found."

    # Simulate sending a reset email (or other actions)
    # e.g., send_reset_email(user)
    return True, "If the email is registered, a reset link has been sent."
