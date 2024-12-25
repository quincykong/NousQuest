from app.extensions import db
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from app.models import UserGroup, User, Tag, usergroup_user, usergroup_tag
from app.utils.rbac_utils import has_permission, has_permission_db

RESOURCE_NAME = 'usergroup'

def filter_user_groups(query, org_id, search_term=None, tags=None):
    """
    Filters user groups based on search criteria such as search term or tags.

    Args:
        query (SQLAlchemy Query): The query object to filter.
        org_id (int): ID of the organization.
        search_term (str, optional): Term to filter groups by name or description.
        tags (list, optional): List of tags to filter groups.

    Returns:
        SQLAlchemy Query: The filtered query object.
    """
    # Filter by organization ID
    query = query.filter_by(org_id=org_id)

    # Apply filtering if a search term is provided
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                UserGroup.title.ilike(search_pattern),
                UserGroup.description.ilike(search_pattern)
            )
        )

    # Apply tag filtering if tags are provided
    if tags:
        tag_list = tags.split(',')
        query = query.join(UserGroup.tags).filter(Tag.name.in_(tag_list))

    return {
        'success': True,
        'data': query,
        'message': 'User groups filtered successfully.'
    }

def get_user_groups(org_id, user_id, search_term=None, tags=None, page=1, per_page=25):
    """
    Retrieves a paginated list of user groups for the specified organization and user.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user.
        search_term (str, optional): Term to filter groups by name or description.
        tags (list, optional): List of tags to filter groups.
        page (int, optional): Page number for pagination. Defaults to 1.
        per_page (int, optional): Number of items per page. Defaults to 25.

    Returns:
        dict: A dictionary containing rows of user groups and pagination information.
    """
    current_app.app_logger.debug(f'===== calling get_user_groups =====')
    try:
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'read'):
            raise PermissionError(f'User {user_id} is not authorized to read user groups.')

        # Base query for user groups
        query = UserGroup.query
        query = filter_user_groups(query, org_id, search_term, tags)

        # Apply pagination to the query
        paginated_result = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize the user group data for the response
        user_groups_data = [serialize_user_group(group) for group in paginated_result.items]
        page_info = {
            'currentPage': paginated_result.page,
            'rowsPerPage': paginated_result.per_page,
            'totalRows': paginated_result.total,
        }

        return {
            'success': True,
            'data': {'rows': user_groups_data, 'pageInfo': page_info},
            'message': 'User groups retrieved successfully.'
        }
    
    except PermissionError as pe:
        current_app.app_logger.warning(f"Permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        current_app.app_logger.warning(f"get_user_groups error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error retrieving user groups: {str(e)}'
        }


def get_user_group_by_id(org_id, user_id, group_id, include_students=False, include_tags=False):
    """
    Retrieves detailed information about a specific user group, optionally including students and tags.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user.
        group_id (int): ID of the user group to retrieve.
        include_students (bool, optional): Whether to include student details. Defaults to False.
        include_tags (bool, optional): Whether to include tag details. Defaults to False.

    Returns:
        dict: Serialized information about the user group.
    """
    try:
        current_app.app_logger.debug(f'===== get_user_group: {group_id} include_students:{include_students} include_tags:{include_tags}')

        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'read'):
            raise PermissionError(f'User {user_id} is not authorized to read user groups.')

        # Fetch the user group from the database
        query = UserGroup.query.filter_by(id=group_id)
        query = filter_user_groups(query, org_id)  # Apply common filtering logic
        user_group = query.first()

        if not user_group:
            return None

        # Fetch associated students if required
        students = []
        if include_students:
            students = [
                {
                    "id": student.id,
                    "name": f"{student.firstname} {student.lastname}",
                    "locked": student.locked
                } 
                for student in user_group.users
            ]

        # Fetch associated tags if required
        tags = []
        if include_tags:
            tags = [{"id": tag.id, "name": tag.name} for tag in user_group.tags]

        return {
            'success': True,
            'data': serialize_user_group(user_group, students, tags),
            'message': f'Successfully retrieve usergroup for user: {user_id}.'
        }
        return 

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f'Error to retrieve user group: {str(e)}'
        }

def serialize_user_group(group, students=None, tags=None):
    """Helper function to serialize user group objects into JSON-friendly format."""
    serialized_data = {
        "id": group.id,
        "title": group.title,
        "description": group.description,
        # "studentcount": group.studentcount,
        "status": group.status,
        "created_at": group.created_at.strftime('%Y-%m-%d'),
        "created_by": group.created_by,
        "updated_at": group.updated_at.strftime('%Y-%m-%d'),
        "updated_by": group.updated_by
    }

    # Add students if provided
    if students is not None:
        serialized_data["studentsInGroup"] = students

    # Add tags if provided
    if tags is not None:
        serialized_data["tags"] = tags

    return serialized_data

def mass_status_update_groups(org_id, user_id, group_ids, new_status):
    """
    Updates the status of multiple user groups in bulk.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user performing the update.
        group_ids (list): List of user group IDs to update.
        new_status (str): New status to apply to the groups.

    Returns:
        dict: A dictionary with a success message and the count of updated groups.
    """
    try:
        current_app.app_logger.debug(f"===== mass_status_update_groups_service called =====")
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'update'):
            raise PermissionError(f"User {user_id} is not authorized to update user groups.")

        # Fetch the user groups
        user_groups = UserGroup.query.filter(UserGroup.id.in_(group_ids), UserGroup.org_id == org_id).all()

        if not user_groups:
            raise ValueError("No matching user groups found.")

        # Update the status
        for group in user_groups:
            group.status = new_status
            group.updated_by = user_id
            group.updated_at = db.func.now()

        db.session.commit()

        updated_count = len(user_groups)
        return {
            'success': True,
            'data': {'updated_count': updated_count},
            'message': f'Successfully updated the status of {updated_count} user groups.'
        }
    
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error performing mass update user group statuses: {str(e)}'
        }

def mass_delete_groups(org_id, user_id, group_ids):
    """
    Deletes multiple user groups in bulk.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user performing the deletion.
        group_ids (list): List of user group IDs to delete.

    Returns:
        dict: A dictionary with a success message and the count of deleted groups.
    """
    try:
        current_app.app_logger.debug(f"===== mass_delete_groups_service called =====")
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'delete'):
            raise PermissionError(f"User {user_id} is not authorized to delete user groups.")

        # Fetch the user groups
        user_groups = UserGroup.query.filter(UserGroup.id.in_(group_ids), UserGroup.org_id == org_id).all()

        if not user_groups:
            raise ValueError("No matching user groups found.")

        # Delete the user groups
        for group in user_groups:
            db.session.delete(group)

        db.session.commit()

        updated_count = len(user_groups)
        return {
            'success': True,
            'data': {'updated_count': updated_count},
            'message': f'Successfully updated the status of {updated_count} user groups.'
        }
    
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error updating user group statuses: {str(e)}'
        }
    

def create_user_group(org_id, user_id, title, description=None, status='1', tags=None):
    """
    Creates a new user group within the specified organization.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user creating the group.
        title (str): Title of the user group.
        description (str, optional): Description of the user group.
        status (str, optional): Status of the user group. Defaults to '1'.
        tags (list, optional): List of tags associated with the group.

    Returns:
        dict: A dictionary containing success status, data, and a message.
    """
    try:
        current_app.app_logger.debug(f"===== create_user_group called =====")
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'create'):
            raise PermissionError(f"User {user_id} is not authorized to create user groups.")

        # Create the user group
        new_group = UserGroup(
            org_id=org_id,
            title=title,
            description=description,
            status=status,
            created_by=user_id,
            updated_by=user_id,
        )
        db.session.add(new_group)
        db.session.flush()  # Get the new group ID

        # Associate tags if provided
        if tags:
            tag_objects = Tag.query.filter(Tag.id.in_(tags), Tag.org_id == org_id).all()
            new_group.tags.extend(tag_objects)

        db.session.commit()
        return {
            'success': True,
            'data': serialize_user_group(new_group),
            'message': 'User group created successfully.'
        }
    
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error updating user group statuses: {str(e)}'
        }

def update_user_group(org_id, user_id, group_id, title=None, description=None, status=None, tags=None):
    """
    Updates an existing user group with new information.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user performing the update.
        group_id (int): ID of the user group to update.
        title (str, optional): New title for the user group.
        description (str, optional): New description for the user group.
        status (str, optional): New status for the user group.
        tags (list, optional): Updated list of tags associated with the group.

    Returns:
        dict: Serialized information about the updated user group.
    """
    try:
        current_app.app_logger.debug(f"===== update_user_group called =====")
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'update'):
            raise PermissionError(f"User {user_id} is not authorized to update user groups.")

        user_group = UserGroup.query.filter_by(id=group_id, org_id=org_id).first()
        if not user_group:
            raise ValueError(f"User group with ID {group_id} not found.")

        # Update fields
        if title is not None:
            user_group.title = title
        if description is not None:
            user_group.description = description
        if status is not None:
            user_group.status = status
        user_group.updated_by = user_id

        # Update tags if provided
        if tags is not None:
            tag_objects = Tag.query.filter(Tag.id.in_(tags), Tag.org_id == org_id).all()
            user_group.tags = tag_objects

        db.session.commit()
        return {
            'success': True,
            'data': serialize_user_group(user_group),
            'message': f'User group has updated.'
        }

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error updating user group statuses: {str(ve)}'
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Database error updating user group statuses: {str(e)}'
        }


def delete_user_group(org_id, user_id, group_id):
    """
    Deletes a specific user group.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user performing the deletion.
        group_id (int): ID of the user group to delete.

    Returns:
        dict: A dictionary with a success message.
    """
    try:
        current_app.app_logger.debug(f"===== delete_user_group called =====")
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'delete'):
            raise PermissionError(f"User {user_id} is not authorized to delete user groups.")

        user_group = UserGroup.query.filter_by(id=group_id, org_id=org_id).first()
        if not user_group:
            raise ValueError(f"User group with ID {group_id} not found.")

        db.session.delete(user_group)
        db.session.commit()

        return {
            'success': True,
            'data': None,
            'message': f'User group {group_id} deleted successfully.'
        }
    
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error deleting user group: {str(e)}'
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Database error deleting user group: {str(e)}'
        }

def mass_update_group_status(org_id, user_id, group_ids, new_status):
    """
    Updates the status of multiple user groups in bulk.

    Args:
        org_id (int): ID of the organization.
        user_id (int): ID of the user performing the update.
        group_ids (list): List of user group IDs to update.
        new_status (str): New status to apply to the groups.

    Returns:
        dict: A dictionary with a success message and the count of updated groups.
    """
    try:
        current_app.app_logger.debug(f"===== mass_update_group_status called =====")
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'update'):
            raise PermissionError(f"User {user_id} is not authorized to update user groups.")

        user_groups = UserGroup.query.filter(UserGroup.id.in_(group_ids), UserGroup.org_id == org_id).all()
        if not user_groups:
            raise ValueError("No matching user groups found.")

        for group in user_groups:
            group.status = new_status
            group.updated_by = user_id

        db.session.commit()

        updated_count = len(group_ids)
        return {
            'success': True,
            'data': {'updated_count': updated_count},
            'message': f'Successfully updated the status of {updated_count} user groups.'
        }
    
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error updating user group statuses: {str(e)}'
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Database error updating user group statuses: {str(e)}'
        }
