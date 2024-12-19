from flask import Blueprint, request, current_app, g
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.utils.response_utils import create_response
from app.utils.auth_decorators import inject_identity
from app.services.usergroup_service import (
    get_user_groups,
    get_user_group_by_id,
    # get_students_by_user_group,
    create_user_group,
    update_user_group,
    delete_user_group,
    mass_update_group_status,
    mass_delete_groups,
)
from app.utils.pagination_utils import get_pagination_params

usergroup_bp = Blueprint("usergroup_bp", __name__)

@usergroup_bp.route("/api/usergroups", methods=["GET"])
@inject_identity
@jwt_required()
def get_usergroups():
    """
    Get User Groups

    Retrieves a paginated list of user groups for the logged-in user and organization.

    Query Parameters:
        - search: Filter by search term.
        - tags: Filter by tags.
        - page: Page number for pagination.
        - per_page: Number of records per page.

    Returns:
        Response:
            {
                "data": {
                    "rows": [...],
                    "pageInfo": {
                        "currentPage": ...,
                        "rowsPerPage": ...,
                        "totalRows": ...
                    }
                },
                "message": "User groups fetched successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id
        search_term = request.args.get("search")
        tags = request.args.get("tags")
        page, per_page = get_pagination_params(request)

        result = get_user_groups(org_id, user_id, search_term, tags, page, per_page)

        return create_response(
            data=result,
            message="User groups fetched successfully",
            status=200,
        )
    except Exception as e:
        raise Exception(f"Error fetching user groups: {str(e)}")


@usergroup_bp.route("/api/usergroups/<usergroup_id>", methods=["GET"])
@inject_identity
@jwt_required()
def get_usergroup_by_id(usergroup_id):
    """
    Get User Group by ID

    Retrieves details of a specific user group, optionally including associated students and tags.

    Query Parameters:
        - include_students: Whether to include student details (true/false).
        - include_tags: Whether to include tag details (true/false).

    Returns:
        Response:
            {
                "data": {...},
                "message": "User group fetched successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id
        include_students = request.args.get("include_students", "false").lower() == "true"
        include_tags = request.args.get("include_tags", "false").lower() == "true"

        result = get_user_group_by_id(org_id, user_id, usergroup_id, include_students, include_tags)

        if not result:
            return create_response(
                data=None,
                message=f"User group with ID {usergroup_id} not found",
                status=404,
            )
        return create_response(
            data=result,
            message="User group fetched successfully",
            status=200,
        )
    except Exception as e:
        raise Exception(f"Error fetching user group: {str(e)}")


@usergroup_bp.route("/api/usergroups", methods=["POST"])
@inject_identity
@jwt_required()
def create_usergroup():
    """
    Create User Group

    Creates a new user group for the logged-in user and organization.

    Request Body:
        {
            "name": "Group Name",
            "description": "Optional description"
        }

    Returns:
        Response:
            {
                "data": {...},
                "message": "User group created successfully",
                "status": 201
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id
        data = request.get_json()

        result = create_user_group(org_id, user_id, data)

        return create_response(
            data=result,
            message="User group created successfully",
            status=201,
        )
    except ValidationError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Error creating user group: {str(e)}")


@usergroup_bp.route("/api/usergroups/<usergroup_id>", methods=["PUT"])
@inject_identity
@jwt_required()
def update_usergroup(usergroup_id):
    """
    Update User Group

    Updates an existing user group.

    Request Body:
        {
            "name": "Updated Group Name",
            "description": "Updated description"
        }

    Returns:
        Response:
            {
                "data": {...},
                "message": "User group updated successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id
        data = request.get_json()

        result = update_user_group(org_id, user_id, usergroup_id, data)

        if not result:
            return create_response(
                data=None,
                message="Failed to update user group",
                status=400,
            )
        return create_response(
            data=result,
            message="User group updated successfully",
            status=200,
        )
    except ValidationError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Error updating user group: {str(e)}")


@usergroup_bp.route("/api/usergroups/<usergroup_id>", methods=["DELETE"])
@inject_identity
@jwt_required()
def delete_usergroup(usergroup_id):
    """
    Delete User Group

    Deletes an existing user group.

    Returns:
        Response:
            {
                "data": null,
                "message": "User group deleted successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id

        if not delete_user_group(org_id, user_id, usergroup_id):
            raise Exception("Failed to delete user group")

        return create_response(
            data=None,
            message="User group deleted successfully",
            status=200,
        )
    except Exception as e:
        raise Exception(f"Error deleting user group: {str(e)}")


@usergroup_bp.route('/api/massUpdateGroupStatus', methods=['PUT'])
@inject_identity
@jwt_required()
def mass_update_groups():
    """
    Mass Update User Group Status

    Updates the status of multiple user groups.

    Request Body:
        {
            "groupIds": [1, 2, 3],
            "status": "active"
        }

    Returns:
        Response:
            {
                "data": null,
                "message": "User group statuses updated successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id
        data = request.get_json()

        if not data or not isinstance(data.get("groupIds"), list) or not data.get("status"):
            raise ValidationError("Invalid request payload. 'groupIds' must be a list and 'status' is required.")

        group_ids = data.get("groupIds")
        new_status = data.get("status")

        success_message = mass_status_update_groups(org_id, user_id, group_ids, new_status)

        return create_response(
            data=None,
            message=success_message,
            status=200,
        )
    except ValidationError as ve:
        raise ve
    except PermissionError:
        raise PermissionError("You do not have permission to update user group statuses.")
    except Exception as e:
        raise Exception(f"Error mass updating groups: {str(e)}")


@usergroup_bp.route('/api/massDeleteGroups', methods=['POST'])
@inject_identity
@jwt_required()
def mass_delete_groups():
    """
    Mass Delete User Groups

    Deletes multiple user groups.

    Request Body:
        {
            "groupIds": [1, 2, 3]
        }

    Returns:
        Response:
            {
                "data": null,
                "message": "User groups deleted successfully",
                "status": 200
            }
    """
    try:
        user_id = g.user_id
        org_id = g.org_id
        data = request.get_json()

        if not data or not isinstance(data.get("groupIds"), list):
            raise ValidationError("Invalid request payload. 'groupIds' must be a list.")

        group_ids = data.get("groupIds")

        success_message = mass_delete_groups(org_id, user_id, group_ids)

        return create_response(
            data=None,
            message=success_message,
            status=200,
        )
    except ValidationError as ve:
        raise ve
    except PermissionError:
        raise PermissionError("You do not have permission to delete user groups.")
    except Exception as e:
        raise Exception(f"Error mass deleting groups: {str(e)}")
