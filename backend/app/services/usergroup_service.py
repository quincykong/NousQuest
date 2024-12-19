from app.extensions import db
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from app.models import UserGroup, User, Tag, usergroup_user, usergroup_tag
from app.utils.rbac_utils import has_permission, has_permission_db

RESOURCE_NAME = 'usergroup'

def filter_user_groups(query, org_id, search_term=None, tags=None):
    """
    Apply common filtering logic to a user group query.
    :param query: The base query object.
    :param org_id: Organization ID for filtering.
    :param search_term: Optional search term for filtering.
    :param tags: Optional list of tags for filtering.
    :return: Filtered query.
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

    return query


def get_user_groups(org_id, user_id, search_term=None, tags=None, page=1, per_page=25):
    """
    Retrieve paginated and filtered user groups.
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
            'rows': user_groups_data,
            'pageInfo': page_info
        }
    except PermissionError as pe:
        current_app.app_logger.warning(f"Permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        current_app.app_logger.warning(f"get_user_groups error: {str(e)}")
        return {
            'rows': [],
            'pageInfo': {
                'currentPage': 1,
                'rowsPerPage': per_page,
                'totalRows': 0
            }
        }


def get_user_group_by_id(org_id, user_id, group_id, include_students=False, include_tags=False):
    """Fetch a user group by ID, optionally including students and tags."""
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

        return serialize_user_group(user_group, students, tags)

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except Exception as e:
        raise Exception(f"Error fetching user group for ID {group_id}: {str(e)}")


def serialize_user_group(group, students=None, tags=None):
    """Helper function to serialize user group objects into JSON-friendly format."""
    serialized_data = {
        "id": group.id,
        "title": group.title,
        "description": group.description,
        "studentcount": group.studentcount,
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
    Update the status of multiple user groups.
    :param org_id: Organization ID.
    :param user_id: ID of the user performing the operation.
    :param group_ids: List of group IDs to update.
    :param new_status: New status to set for the user groups.
    :return: Success message or error details.
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

        return {"message": f"Successfully updated the status of {len(user_groups)} user groups."}

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        raise e


def mass_delete_groups(org_id, user_id, group_ids):
    """
    Delete multiple user groups.
    :param org_id: Organization ID.
    :param user_id: ID of the user performing the operation.
    :param group_ids: List of group IDs to delete.
    :return: Success message or error details.
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

        return {"message": f"Successfully deleted {len(user_groups)} user groups."}

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        raise e

def create_user_group(org_id, user_id, title, description=None, status='1', tags=None):
    """
    Create a new user group.
    :param org_id: Organization ID.
    :param user_id: ID of the user performing the operation.
    :param title: Title of the user group.
    :param description: Optional description of the group.
    :param status: Status of the group (default: '1').
    :param tags: Optional list of tag IDs to associate with the group.
    :return: Created user group.
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
        return serialize_user_group(new_group)

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        raise e


def update_user_group(org_id, user_id, group_id, title=None, description=None, status=None, tags=None):
    """
    Update an existing user group.
    :param org_id: Organization ID.
    :param user_id: ID of the user performing the operation.
    :param group_id: ID of the group to update.
    :param title: New title of the group (optional).
    :param description: New description of the group (optional).
    :param status: New status of the group (optional).
    :param tags: List of tag IDs to associate with the group (optional).
    :return: Updated user group.
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
        return serialize_user_group(user_group)

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        raise e


def delete_user_group(org_id, user_id, group_id):
    """
    Delete a user group.
    :param org_id: Organization ID.
    :param user_id: ID of the user performing the operation.
    :param group_id: ID of the group to delete.
    :return: Success message or error details.
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

        return {"message": f"Successfully deleted user group {group_id}."}

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        raise e


def mass_update_group_status(org_id, user_id, group_ids, new_status):
    """
    Update the status of multiple user groups.
    :param org_id: Organization ID.
    :param user_id: ID of the user performing the operation.
    :param group_ids: List of group IDs to update.
    :param new_status: New status to set for the user groups.
    :return: Success message or error details.
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

        return {"message": f"Successfully updated the status of {len(user_groups)} user groups."}

    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe
    except ValueError as ve:
        current_app.app_logger.warning(f"Value error: {str(ve)}")
        return {"error": str(ve)}
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"Database error: {str(e)}")
        raise e
