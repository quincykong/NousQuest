from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token
from app import db
from app.models import User
from app.utils.message_config import send_email
from app.utils.logging_config import security_logger, app_logger

def user_service_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and not user.locked:
        if user.check_password(password):
            login_user(user)
            user.last_logon = datetime.now(timezone.utc)
            #user.last_logon = datetime.now(datetime.utc)
            user.logon_attempt = 0
            db.session.commit()
            access_token = create_access_token(identity=user.id, additional_claims={"roles": [role.name for role in user.roles]})
            security_logger.info(f'User {user.firstname} logged in.')
            return True, {"message": f'Welcome {user.firstname}', "access_token": access_token}
        else:
            user.logon_attempt += 1
            if user.logon_attempt > 5:
                user.locked = True
                db.session.commit()
                security_logger.critical(f'Account locked for user: {user.id}')
                return False, 'Too many login attempts. Your account is now locked. Please contact the system administrator to follow up.'
            else:
                db.session.commit()
                security_logger.warning(f'Invalid login attempt for user: {user.id}')
                return False, 'Invalid credentials. Please try again.'
    elif user and user.locked:
        security_logger.critical(f'Attempted login to locked account: {user.id}')
        return False, 'Your account is locked due to too many attempted. Please contact the system administrator to follow up.'
    else:
        security_logger.critical(f'Login attempt with unknown email: {email}')
        return False, 'No credentials match.'

def user_service_logout(user_id):
    security_logger.info(f'User logged out: {user_id}')
    logout_user()
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
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')