from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for, jsonify
from app import db
from app.models import User, UserClassEnum
from app.routes import API_ROUTES
from app.utils.message_config import send_email
#from app.utils.logging_config import security_logger, app_logger
#from app import app_logger, security_logger
from app.utils.jwt_utils import create_jwt_token

def user_service_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and not user.locked:
        if user.check_password(password):
            user.last_logon = datetime.now(timezone.utc)
            user.logon_attempt = 0
            db.session.commit()

            # Generate JWT tokens (access_token, refresh_token)
            access_token, refresh_token = create_jwt_token(user.org_id, user.id)
            current_app.security_logger.info(f'User logged in: {user.username}')
            
            # # Create the response and set cookies
            # response = make_response(jsonify({
            #     "message": f'Welcome {user.firstname}',
            #     "redirect_url": get_redirect_url(user)  # Return redirect URL in response
            # }))
            
            # # Set the access token as a cookie
            # response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Strict', max_age=24 * 60 * 60)
            # # Set the refresh token as a cookie
            # response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict', max_age=7 * 24 * 60 * 60)

            return True, access_token, refresh_token, user.firstname, get_redirect_url(user)
        else:
            handle_failed_login(user)
            return False, jsonify({"message": "Invalid credentials. Please try again."}), 401
    elif user and user.locked:
        current_app.security_logger.critical(f'Attempted login to locked account: {user.id}')
        return False, jsonify({"message": "Your account is locked due to too many attempted logins. Please contact the system administrator."}), 403
    else:
        current_app.security_logger.critical(f'Login attempt with unknown email: {email}')
        return False, jsonify({"message": "No credentials match."}), 401

# user_service_login helper
def get_redirect_url(user):
    current_app.security_logger.debug(f'user.userclass: {user.userclass}')
    if user.userclass == UserClassEnum.ADMIN:
        return API_ROUTES['admin_home']
    elif user.userclass == UserClassEnum.INSTRUCTOR:
        return API_ROUTES['instructor_home']
    elif user.userclass == UserClassEnum.STUDENT:
        return API_ROUTES['student_home']
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
    return True, "Logout successful"

def user_service_forgotpassword(email, organization_id):
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