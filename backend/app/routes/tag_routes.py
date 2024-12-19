from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from app.services.tag_service import (
    get_tags_by_resource,
    create_tag,
    delete_tag,
    get_tags_by_user_group
)
from app.utils.response_utils import create_response
from app.utils.auth_decorators import inject_identity

tag_bp = Blueprint('tag_bp', __name__)

@tag_bp.route('/api/userGroupTags/<group_id>', methods=['GET'])
@inject_identity
@jwt_required()
def get_user_group_tags(group_id):
    """
    Get Tags for User Group

    Fetches tags associated with a user group.

    Args:
        group_id (str): ID of the user group.

    Returns:
        Response:
            {
                "data": {"tags": [...]},
                "message": "Tags fetched successfully",
                "status": 200
            }
    """
    try:
        org_id = g.org_id
        user_id = g.user_id

        tags = get_tags_by_user_group(org_id, user_id, group_id)
        return create_response(data={"tags": tags}, message="Tags fetched successfully", status=200)
    except Exception as e:
        raise Exception(f"Error fetching tags for user group: {str(e)}")


@tag_bp.route('/api/tags/<resource_id>', methods=['GET'])
@jwt_required()
def get_tags(resource_id):
    """
    Get Tags for Resource

    Fetches tags associated with a specific resource.

    Args:
        resource_id (str): ID of the resource.

    Returns:
        Response:
            {
                "data": {"tags": [...]},
                "message": "Tags fetched successfully",
                "status": 200
            }
    """
    try:
        tags = get_tags_by_resource(resource_id)
        if not tags:
            return create_response(data=None, message="No tags found", status=404)
        return create_response(data={"tags": tags}, message="Tags fetched successfully", status=200)
    except Exception as e:
        raise Exception(f"Error fetching tags for resource: {str(e)}")


@tag_bp.route('/api/tags', methods=['POST'])
@inject_identity
@jwt_required()
def create_new_tag():
    """
    Create New Tag

    Creates a new tag for a specific resource.

    Request Body:
        {
            "resource_id": "resource_id",
            "name": "tag_name"
        }

    Returns:
        Response:
            {
                "data": {"tag": {...}},
                "message": "Tag created successfully",
                "status": 201
            }
    """
    try:
        data = request.get_json()
        resource_id = data.get("resource_id")
        name = data.get("name")
        org_id = g.org_id
        user_id = g.user_id

        if not resource_id or not name:
            raise ValueError("Missing 'resource_id' or 'name' in the request.")

        tag = create_tag(resource_id, org_id, name, user_id)
        if tag:
            return create_response(data={"tag": tag}, message="Tag created successfully", status=201)
        return create_response(data=None, message="Failed to create tag", status=400)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Error creating tag: {str(e)}")


@tag_bp.route('/api/tags/<tag_id>', methods=['DELETE'])
@inject_identity
@jwt_required()
def delete_existing_tag(tag_id):
    """
    Delete Tag

    Deletes a tag by its ID.

    Args:
        tag_id (str): ID of the tag to delete.

    Returns:
        Response:
            {
                "data": null,
                "message": "Tag deleted successfully",
                "status": 200
            }
    """
    try:
        success = delete_tag(tag_id)
        if success:
            return create_response(data=None, message="Tag deleted successfully", status=200)
        return create_response(data=None, message=f"Tag with ID {tag_id} not found", status=404)
    except Exception as e:
        raise Exception(f"Error deleting tag: {str(e)}")
