from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, g, url_for
from app.extensions import db
from app.models.authorization_models import User, Authorization, user_securityroles, securityrole_authorizations
from app.models.resource_models import Resource
from app.models.action_models import Action
from app.models.authorization_models import SecurityRole
from app.constants import USER_ROUTES
from app.config.message_config import send_email
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
    # current_app.app_logger.debug(f"Login attempt with userId: {userId}, password: {password}")
    errors = schema.validate({"userId": userId, "password": password})
    if errors:
        # current_app.app_logger.debug(f"Validation errors: {errors}")
        return False, create_response(message="Failure to pass LoginSchema validation.", status=400)
    
    # current_app.app_logger.debug(f"Database URI: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
    # current_app.app_logger.debug(f"userId:**{userId}**")
    user = User.query.filter_by(email=userId).first()
    # current_app.app_logger.debug(f"user:**{user}**")
    if user and not user.locked:
        if user.check_password(password):

            user.last_logon = datetime.now(timezone.utc)
            user.logon_attempt = 0

            db.session.commit()
            current_app.security_logger.info(f'User logged in: {user.username}')

            # Store user data in g
            g.user_id = user.id
            g.org_id = user.org_id

            # return a message to caller
            user_data = {"id":user.id, "org_id":user.org_id}
            return True, user_data, "Login successful"
        else:
            handle_failed_login(user)
            return False, None, "Invalid credentials."
    elif user and user.locked:
        current_app.security_logger.critical(f'Attempted login to locked account: {user.id}')
        return False, None, "Your account is locked due to too many attempted logins. Please contact the system administrator."
    else:
        current_app.security_logger.critical(f'Login attempt with unknown email: {userId}')
        return False, None,"No credentials match."


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
        success = send_email(subject, email, msgBody, g.org_id)
        if success:
            return True, "Password reset instructions have been sent to your email."
        else:
            return False, ""
    else:
        return False, "Credential not found."


def generate_reset_token(user, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.Config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')

