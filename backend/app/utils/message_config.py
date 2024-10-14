import smtplib
from flask import current_app
from flask_mail import Mail, Message
#from app import db
from app.models import Organization
#from app.utils.logging_config import app_logger
#from app import app_logger

def get_smtp_settings(organization_id):
    organization = Organization.query.get(organization_id)

    if not organization:
        current_app.app_logger.critical(f"get_smtp_settings: Organization ID [{organization_id}] not found.")
        raise ValueError(f"Organization ID [{organization_id}] not found.")

    # Setup mail config based on organization's SMTP settings
    current_app.config.update(
        MAIL_SERVER=organization.smtp_server,
        MAIL_PORT=organization.smtp_port,
        MAIL_USE_TLS=organization.smtp_use_tls,
        MAIL_USE_SSL=organization.smtp_use_ssl,
        MAIL_USERNAME=organization.smtp_username,
        MAIL_PASSWORD=organization.smtp_password,
        MAIL_DEFAULT_SENDER=(organization.name, organization.smtp_sender)
    )

    # Reinitialize mail instance to use the new configuration
    mail = Mail(current_app)
    return mail

def send_email(subject, recipients, body, organization_id):
    try:
        # Get SMTP settings based on organization
        mail = get_smtp_settings(organization_id)

        # Create and send the email
        msg = Message(subject, recipients=recipients)
        msg.body = body
        mail.send(msg)
        current_app.app_logger.info(f"send_email - Message {subject} to {recipients} has been sent.")
        return True  # Email sent successfully
    except smtplib.SMTPException as e:
        # Handle specific SMTP errors
        current_app.app_logger.critical(f"send_email - SMTP error: {e}")
        return False
    except Exception as e:
        # Handle any other exception
        current_app.app_logger.critical(f"send_email - Failed to send email: {e}")
        return False
