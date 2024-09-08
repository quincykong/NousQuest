import logging
from app import db
from logging.handlers import RotatingFileHandler
from flask_login import login_user
from app.models import User
from datetime import datetime

# Setup logger
def setup_security_logger():
    logger = logging.getLogger('security_logger')
    logger.setLevel(logging.INFO)

    # Ensure that only one handler is attached to the logger to avoid duplicates
    if not logger.hasHandlers():
        handler = RotatingFileHandler('log/security.log', maxBytes=10000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

security_logger = setup_security_logger()

def handle_login(email, password):
    user = User.query.filter_by(email=email).first()

    if user and not user.locked:
        if user.check_password(password):
            login_user(user)
            user.last_logon = datetime.utcnow()
            user.logon_attempt = 0
            db.session.commit()
            security_logger.info(f'User logged in: {user.id}')
            return True, None
        else:
            user.logon_attempt += 1
            if user.logon_attempt > 5:
                user.locked = True
                db.session.commit()
                security_logger.warning(f'Account locked for user: {user.id}')
                return False, 'Too many login attempts. Your account is now locked. Please contact the system administrator.'
            else:
                db.session.commit()
                security_logger.warning(f'Invalid login attempt for user: {user.id}')
                return False, 'Invalid credentials. Please try again.'
    elif user and user.locked:
        security_logger.warning(f'Attempted login to locked account: {user.id}')
        return False, 'Your account is locked due to too many attempted. Please contact the system administrator.'
    else:
        security_logger.warning(f'Login attempt with unknown email: {email}')
        return False, 'No credentials match.'

def handle_logout(user):
    security_logger.info(f'User logged out: {user}')

def send_password_reset_email(user):
    token = generate_reset_token(user)
    msg = Message("Password Reset Request", sender="noreply@domain.com", recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
        {url_for('reset_token', token=token, _external=True)}
        If you did not make this request, simply ignore this email and no changes will be made.
        """
    mail.send(msg)

def generate_reset_token(user, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')