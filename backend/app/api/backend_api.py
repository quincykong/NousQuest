from datetime import datetime
from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
# from app.models import User, Quiz, QuizOption, QuizQuestion
# from app.utils.helper_auth import handle_login, handle_logout, send_password_reset_email
# from app.utils.helper_logging import create_logger_instance
from app.services.rabbitmq_config import send_to_rabbitmq
from app.services.user_service import user_service_login, user_service_logout, user_service_forgotpassword
from app.services.usergroup_service import (get_user_groups, create_user_group, update_user_group, delete_user_group,)
from app.utils.logging_config import app_logger, frontend_logger

# Create blueprint
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/api/home', methods=['GET'])
@login_required
def home():
    open_quizzes = Quiz.query.filter(Quiz.end_date >= datetime.utcnow()).all()
    quizzes_data = [{"id": quiz.id, "title": quiz.title, "description": quiz.description, "end_date": quiz.end_date} for quiz in open_quizzes]
    return jsonify({"user_name": current_user.username, "quizzes": quizzes_data, "app_name": current_app.config['APP_NAME'], "show_nav": True})

#def load_user(user_id):
#    return User.query.get(str(user_id))

@api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_token), 200

@api_bp.route('/api/login', methods=['GET', 'POST'])
def login():
    data = request.json
    success, message = user_service_login(data.get('userId'), data.get('password'))
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 401

@api_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    data = request.json
    user_id = current_user.get_id()
    success, message = user_service_logout(data.get('userId'))
    return jsonify({"message": message}), 200

@api_bp.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    success, message = user_service_forgotpassword(email)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 404

@api_bp.route('/api/frontendlog', methods=['POST'])
def log_frontend_error():
    data = request.json
    message = data.get('message')
    client_info = data.get('clientInfo', {})
    if message:
        app_logger.info("Calling RabbitMQ *****")
        send_to_rabbitmq(message, client_info)
        return jsonify({"message": "Error posting to message queue"}), 200
    else:
        return jsonify({"error": "No message provided"}), 400

# Route to get all user groups
@api_bp.route('/api/usergroups', methods=['GET'])
@jwt_required()
def get_usergroups():
    # Get the current user identity from JWT
    current_user_id = get_jwt_identity()

    # Check authorization for 'read' action
    if not authorize_action(current_user_id, 'read', 'usergroup'):
        return jsonify({"error": "Forbidden"}), 403

    user_groups = get_user_groups(current_user_id)
    return jsonify(user_groups), 200

# Route to create a new user group
@api_bp.route('/api/usergroups', methods=['POST'])
@jwt_required()
def create_usergroup():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    # Check authorization for 'create' action
    if not authorize_action(current_user_id, 'create', 'usergroup'):
        return jsonify({"error": "Forbidden"}), 403

    # Use service layer to create the user group
    user_group = create_user_group(current_user_id, data)
    if user_group:
        return jsonify({"message": "User Group created successfully", "user_group": user_group}), 201
    return jsonify({"error": "Failed to create user group"}), 400

# Route to update an existing user group
@api_bp.route('/api/usergroups/<group_id>', methods=['PUT'])
@jwt_required()
def update_usergroup(group_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()

    # Check authorization for 'update' action
    if not authorize_action(current_user_id, 'update', 'usergroup'):
        return jsonify({"error": "Forbidden"}), 403

    user_group = update_user_group(current_user_id, group_id, data)
    if user_group:
        return jsonify({"message": "User Group updated successfully", "user_group": user_group}), 200
    return jsonify({"error": "Failed to update user group"}), 400

# Route to delete an existing user group
@api_bp.route('/api/usergroups/<group_id>', methods=['DELETE'])
@jwt_required()
def delete_usergroup(group_id):
    current_user_id = get_jwt_identity()

    # Check authorization for 'delete' action
    if not authorize_action(current_user_id, 'delete', 'usergroup'):
        return jsonify({"error": "Forbidden"}), 403

    result = delete_user_group(current_user_id, group_id)
    if result:
        return jsonify({"message": "User Group deleted successfully"}), 200
    return jsonify({"error": "Failed to delete user group"}), 400

