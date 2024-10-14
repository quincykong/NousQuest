from flask import request, jsonify, Blueprint, make_response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies
from marshmallow import ValidationError
from app.services.user_service import (
    user_service_login, user_service_logout, user_service_forgotpassword
)
from app.services.usergroup_service import (
    get_user_group_by_id, get_user_groups, get_students_by_user_group, get_tags_by_user_group, 
    create_user_group, update_user_group, delete_user_groups, mass_status_update_groups_service
)
from app.services.tag_service import get_tags_by_resource, create_tag, delete_tag
from app.services.rabbitmq_config import send_to_rabbitmq
#from app.utils.logging_config import app_logger, security_logger
#from app import app_logger, security_logger
from app.utils.jwt_utils import create_jwt_token, get_jwt_identity_with_org, verify_refresh_token, set_tokens_in_cookies
from app.utils.auth_decorators import jwt_required_with_refresh
#from app.utils.rbac_utils import get_user_permissions

# Create blueprint
api_bp = Blueprint('api_bp', __name__)

# Route for home with quiz display
@api_bp.route('/api/home', methods=['GET'])
@jwt_required()
def home():
    current_user_id = get_jwt_identity()
    # try:
    #     quizzes_data = get_open_quizzes(current_user_id)  # Service layer to handle this logic
    #     return jsonify({
    #         "user_name": current_user_id,
    #         "quizzes": quizzes_data,
    #         "app_name": current_app.config['APP_NAME'],
    #         "show_nav": True
    #     })
    # except Exception as e:
    #     current_app.app_logger.error(f"Error loading home data: {str(e)}")
    return jsonify({"error": "Error loading data"}), 500

@api_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    try:
        # Get refresh token from cookies
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            return jsonify({"error": "Refresh token missing"}), 400

        # Verify refresh token
        user_id, org_id = verify_refresh_token(refresh_token)
        if not user_id:
            return jsonify({"error": "Invalid or expired refresh token"}), 401

        # Create new access token
        new_access_token, new_refresh_token = create_jwt_token(org_id, user_id)

        # Set the new access token and refresh token as cookies
        response = make_response(jsonify({"message": "Token refreshed successfully"}))
        set_tokens_in_cookies(response, new_access_token, new_refresh_token)
        #response.set_cookie('access_token', new_access_token, httponly=True, secure=True, samesite='Strict', max_age=24 * 60 * 60)
        #response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, samesite='Strict', max_age=7 * 24 * 60 * 60)

        return response

    except Exception as e:
        current_app.app_logger.error(f"Error during token refresh: {str(e)}")
        return jsonify({"error": "Token refresh error"}), 500
    
# Login route
@api_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        success, access_token, refresh_token, user_firstname, url_to_rediect = user_service_login(data.get('userId'), data.get('password'))
        if success:
            response = make_response(jsonify({
                "message": f'Welcome {user_firstname}',
                "redirect_url": url_to_rediect  # Return redirect URL in response
            }))

            # Use Flask-JWT-Extended helpers to set both JWT tokens and their CSRF tokens in cookies
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
        else:
            return response, 401
    except Exception as e:
        current_app.app_logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": f"Login error {str(e)}"}), 500

# Logout route
@api_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        response = make_response(jsonify({"message": "Logout successful"}))
        # Remove the tokens by clearing the cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    except Exception as e:
        current_app.app_logger.error(f"Error during logout: {str(e)}")
        return jsonify({"error": "Logout error"}), 500

# Forgot password route
@api_bp.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    try:
        email = data.get('email')
        success, message = user_service_forgotpassword(email)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"message": message}), 404
    except Exception as e:
        current_app.app_logger.error(f"Error during forgot password: {str(e)}")
        return jsonify({"error": "Forgot password error"}), 500

# Frontend error logging route
@api_bp.route('/api/frontendlog', methods=['POST'])
def log_frontend_error():
    data = request.json
    try:
        message = data.get('message')
        client_info = data.get('clientInfo', {})
        if message:
            send_to_rabbitmq(message, client_info)
            return jsonify({"message": "Error logged"}), 200
        else:
            return jsonify({"error": "No message provided"}), 400
    except Exception as e:
        current_app.app_logger.error(f"Error logging frontend error: {str(e)}")
        return jsonify({"error": "Frontend logging error"}), 500

# Route to get all user groups
@api_bp.route('/api/usergroups', methods=['GET'])
@api_bp.route('/api/usergroups/<usergroup_id>', methods=['GET'])
#@jwt_required_with_refresh
@jwt_required()
def get_usergroups(usergroup_id=None):
    current_app.app_logger.debug('***** API call: usergroups *****')
    # user_id, org_id, roles, permissions = get_jwt_identity_with_org()
    user_id, org_id = get_jwt_identity_with_org()
    try:
        if usergroup_id:
            # Fetch the specific user group by ID
            user_group = get_user_group_by_id(org_id, user_id, usergroup_id)
            if not user_group:
                return jsonify({"error": f"User group with ID {usergroup_id} not found"}), 404
            response = {
                'rows': [user_group],  # Return as a list for compatibility with the frontend
                'pageInfo': {
                    'currentPage': 1,
                    'rowsPerPage': 1,
                    'totalRows': 1
                }
            }
        else:
            # Fetch all user groups and paginate user groups via service layer
            page = max(1, request.args.get('page', 1, type=int))
            per_page = request.args.get('per_page', 25, type=int)
            search_term = request.args.get('search', None)  # Fetch the search term from query
            tags = request.args.get('tags', None)  # Fetch the tags parameter from the query

            #result = get_user_groups(org_id, user_id, search_term=None, page=page, per_page=per_page) or {}
            result = get_user_groups(org_id, user_id, search_term=search_term, tags=tags, page=page, per_page=per_page) or {}
            user_groups = result.get('rows', [])  # Extract 'rows' from the result
            page_info = result.get('pageInfo', {})  # Extract 'pageInfo' from the result
            total_rows = page_info.get('totalRows', 0)
            #print(f'user_groups returned: {user_groups}')
            response = {
                'rows': user_groups,
                'pageInfo': {
                    'currentPage': page_info.get('currentPage', page),
                    'rowsPerPage': page_info.get('rowsPerPage', per_page),
                    'totalRows': total_rows
                }
            }

        return jsonify(response), 200
    except PermissionError:
        return jsonify({"error": "You don not have permission to retrieve student(s). Please contact system administrator."}), 403
    except Exception as e:
        current_app.app_logger.error(f"Error fetching user groups: {str(e)}. Please contact system administrator.")
        return jsonify({"usergroups error": str(e)}), 500

# Route to get Students for a user group
@api_bp.route('/api/userGroupStudents/<group_id>', methods=['GET'])
@jwt_required()
def get_user_group_students(group_id):
    """Fetch students associated with the given user group"""
    try:
        user_id, org_id = get_jwt_identity_with_org()
        students = get_students_by_user_group(org_id, user_id, group_id)
        return jsonify({"students": students}), 200
    except PermissionError:
        return jsonify({"error": "You don not have permission to retrieve student(s). Please contact system administrator."}), 403
    except Exception as e:
        return jsonify({"userGroupStudents error": str(e)}), 500

# Route to get Tags for a user group
@api_bp.route('/api/userGroupTags/<group_id>', methods=['GET'])
@jwt_required()
def get_user_group_tags(group_id):
    """Fetch tags associated with the given user group"""
    try:
        user_id, org_id = get_jwt_identity_with_org()
        # Add your org_id logic if required
        tags = get_tags_by_user_group(org_id, user_id, group_id)
        return jsonify({"tags": tags}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to create a new user group
@api_bp.route('/api/usergroups', methods=['POST'])
@jwt_required()
def create_usergroup():
    user_id, org_id = get_jwt_identity_with_org()
    data = request.get_json()

    try:
        user_group = create_user_group(org_id, user_id, data)
        return jsonify({"message": "User Group created successfully", "user_group": user_group}), 201
    except ValidationError as ve:
        return jsonify({"API usergroups validation error": str(ve)}), 400
    except PermissionError:
        return jsonify({"API usergroups permission error": "You do not have permission to create user group."}), 403
    except Exception as e:
        current_app.app_logger.error(f"API usergroups error: {str(e)}")
        return jsonify({"API usergroups error": str(e)}), 500

# Route to update an existing user group
@api_bp.route('/api/usergroups/<group_id>', methods=['PUT'])
@jwt_required()
def update_usergroup(group_id):
    user_id, org_id = get_jwt_identity_with_org()
    data = request.get_json()

    try:
        user_group = update_user_group(org_id, user_id, group_id, data)
        if user_group:
            return jsonify({"message": "User Group updated successfully", "user_group": user_group}), 200
        else:
            return jsonify({"error": "Failed to update user group"}), 400
    except ValidationError as ve:
        return jsonify({"API usergroups error": str(ve)}), 400
    except PermissionError:
        return jsonify({"API usergroups error": "Forbidden"}), 403
    except Exception as e:
        current_app.app_logger.error(f"API usergroups updating error: {str(e)}")
        return jsonify({"API usergroups error": str(e)}), 500

# Route to delete an existing user group
@api_bp.route('/api/usergroups/<group_id>', methods=['DELETE'])
@jwt_required()
def delete_usergroup(group_id):
    user_id, org_id = get_jwt_identity_with_org()

    try:
        success = delete_user_groups(org_id, user_id, group_id)
        if success:
            return jsonify({"message": "User Group deleted successfully"}), 200
        else:
            return jsonify({"API usergroups error": "Failed to delete user group"}), 400
    except PermissionError:
        return jsonify({"API usergroups error": "Forbidden"}), 403
    except Exception as e:
        current_app.pp_logger.error(f"API usergroups deleting error: {str(e)}")
        return jsonify({"API usergroups error": str(e)}), 500

# Route for mass updating user groups
@api_bp.route('/api/massUpdateGroupStatus', methods=['PUT'])
@jwt_required()
def mass_update_groups():
    user_id, org_id = get_jwt_identity_with_org()
    data = request.json

    try:
        data = request.get_json()
        group_ids = data.get('groupIds')
        new_status = data.get('status')
        success_message = mass_status_update_groups_service(org_id, user_id, group_ids, new_status)
        return jsonify({"message": success_message}), 200
    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403
    except Exception as e:
        current_app.app_logger.error(f"Error mass updating groups: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Route for mass deleting user groups
@api_bp.route('/api/massDeleteGroups', methods=['POST'])
@jwt_required()
def mass_delete_groups():
    user_id, org_id = get_jwt_identity_with_org()
    data = request.json

    try:
        group_ids = data.get('groupIds')
        success_message = delete_user_groups(org_id, user_id, group_ids)
        return jsonify({"message": success_message}), 200
    except PermissionError:
        return jsonify({"API usergroups error": "Forbidden"}), 403
    except Exception as e:
        current_app.app_logger.error(f"Error mass deleting groups: {str(e)}")
        return jsonify({"API usergroups error": str(e)}), 500

# Route to get all tags for a specific resource
@api_bp.route('/api/tags/<resource_id>', methods=['GET'])
@jwt_required()
def get_tags(resource_id):
    try:
        tags = get_tags_by_resource(resource_id)
        if not tags:
            return jsonify({"message": "No tags found"}), 404
        return jsonify({"tags": tags}), 200
    except Exception as e:
        current_app.app_logger.error(f"Error fetching tags for resource {resource_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Route to create a new tag for a specific resource
@api_bp.route('/api/tags', methods=['POST'])
@jwt_required()
def create_new_tag():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        resource_id = data.get('resource_id')
        org_id = data.get('org_id')
        name = data.get('name')

        if not resource_id or not name:
            return jsonify({"error": "Missing required fields"}), 400

        tag = create_tag(resource_id, org_id, name, current_user_id)
        if tag:
            return jsonify({"message": "Tag created successfully", "tag": tag}), 201
        else:
            return jsonify({"error": "Failed to create tag"}), 400
    except Exception as e:
        current_app.app_logger.error(f"Error creating tag: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Route to delete a tag
@api_bp.route('/api/tags/<tag_id>', methods=['DELETE'])
@jwt_required()
def delete_existing_tag(tag_id):
    try:
        success = delete_tag(tag_id)
        if success:
            return jsonify({"message": "Tag deleted successfully"}), 200
        else:
            return jsonify({"error": f"Tag with ID {tag_id} not found"}), 404
    except Exception as e:
        current_app.app_logger.error(f"Error deleting tag: {str(e)}")
        return jsonify({"error": str(e)}), 500
