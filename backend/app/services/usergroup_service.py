from app import db
from flask import current_app
from app.models import UserGroup, User, Tag, usergroup_user, usergroup_tag
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from marshmallow import Schema, fields, validate, ValidationError
#from app.utils.logging_config import security_logger, app_logger
#from app import app_logger, security_logger
from app.utils.rbac_utils import has_permission, has_permission_db

RESOURCE_NAME = 'usergroup'

# Marshmallow Schemas for validation
class UserGroupSchema(Schema):
    org_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=1000))

def get_user_group_by_id(org_id, user_id, group_id):
    """Fetch a user group by its ID."""
    #if not has_permission(org_id, user_id, RESOURCE_NAME, 'read'):
    current_app.app_logger.info(f"\t===== calling get_user_group_by_id")
    print("entering get_user_group_by_id and calling has_permission_db")
    if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'read'):
        raise PermissionError(f'User {user_id} is not authorized to read user groups.')

    try:
        user_group = UserGroup.query.get((group_id, org_id))
        if user_group:
            return serialize_user_group(user_group)
        return None
    except SQLAlchemyError as e:
        current_app.app_logger.warning(f"get_user_group_by_id error: {str(e)}")
        return None

def get_user_groups(org_id, user_id, search_term=None, tags=None, page=1, per_page=25):
    """
    Retrieve paginated and filtered user groups.
    :param user_id: ID of the requesting user for authorization checks
    :param search_term: Optional search term for filtering user groups
    :param page: The current page (1-based index)
    :param per_page: Number of records per page
    :return: A dictionary with paginated user groups and pagination info
    """
    current_app.app_logger.debug(f'\t===== calling get_user_groups =====')
    try:
        # Check authorization for 'read' action
        if not has_permission_db(org_id, user_id, RESOURCE_NAME, 'read'):
            raise PermissionError(f'User {user_id} is not authorized to read student group.')

        # Base query for user groups
        query = UserGroup.query.filter_by(org_id=org_id)
        current_app.app_logger.debug(f'\t===== UserGroup.Query: {query}')
        
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

        # Apply pagination to the query
        paginated_result = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize the user group data for the response
        user_groups_data = [serialize_user_group(group) for group in paginated_result.items]
        current_app.app_logger.debug(f'\t===== user_groups_data: {user_groups_data}')
        # Pagination info
        page_info = {
            'currentPage': paginated_result.page,
            'rowsPerPage': paginated_result.per_page,
            'totalRows': paginated_result.total,
        }
        current_app.app_logger.debug(f"\t===== completed get_user_groups. Returning data to caller.")

        return {
            'rows': user_groups_data,
            'pageInfo': page_info
        }
    except PermissionError as pe:
        current_app.app_logger.warning(f"Permission error: {str(pe)}")
        raise pe  # Let the calling route handle this
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

def get_students_by_user_group(org_id, user_id, group_id):
    """Fetch all students associated with a specific user group"""
    try:
        if not has_permission(org_id, user_id, RESOURCE_NAME, 'read'):
            raise PermissionError(f'User {user_id} is not authorized to read user groups.')

        students = db.session.query(User).join(usergroup_user).filter(
            usergroup_user.c.group_id == group_id
        ).all()

        return [{"firstname": student.firstname, "lastname": student.lastname} for student in students]
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe  # Let the calling route handle this
    except Exception as e:
        raise Exception(f"get_students_by_user_group error for group_id {group_id}: {str(e)}")

def get_tags_by_user_group(org_id, user_id, group_id):
    """Fetch all tags associated with a specific user group"""
    try:
        if not has_permission(org_id, user_id, RESOURCE_NAME, 'read'):
            raise PermissionError(f'User {user_id} is not authorized to read user groups.')
        
        tags = db.session.query(Tag).join(usergroup_tag).filter(
            usergroup_tag.c.usergroup_id == group_id,
            Tag.org_id == org_id  # Add the org_id filter to ensure the tags belong to the correct organization
        ).all()
        
        return [{"name": tag.name} for tag in tags]
    except PermissionError as pe:
        current_app.security_logger.critical(f"Permission error: {str(pe)}")
        raise pe  # Let the calling route handle this
    except Exception as e:
        raise Exception(f"Error fetching tags for group {group_id}: {str(e)}")

def create_user_group(org_id, user_id, data):
    """Create a new user group."""
    try:
        if not has_permission(org_id, user_id, RESOURCE_NAME, 'create'):
            raise PermissionError(f"User {user_id} is not authorized to create user groups")
        
        # Validate data using schema
        schema = UserGroupSchema()
        validated_data = schema.load(data)

        # Create the new user group
        new_group = UserGroup(
            org_id=validated_data['org_id'],
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            created_by=user_id,
            updated_by=user_id
        )

        db.session.add(new_group)
        db.session.commit()

        current_app.app_logger.info(f"User {user_id} created a new user group {new_group.title}.")
        return serialize_user_group(new_group)
    except ValidationError as ve:
        current_app.app_logger.warning(f"create_user_group validation error: {str(ve)}")
        raise ve
    except PermissionError as pe:
        current_app.security_logger.critical(f"create_user_group Permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"create_user_group error: {str(e)}")
        return None

def update_user_group(org_id, user_id, group_id, data):
    """Update an existing user group."""
    try:
        # Check authorization for 'update' action
        if not has_permission(org_id, user_id, RESOURCE_NAME, 'update'):
            raise PermissionError(f"User {user_id} is not authorized to update user groups")
        
        # Validate data using schema
        schema = UserGroupSchema(partial=True)  # Allow partial updates
        validated_data = schema.load(data)

        # Retrieve the user group and update it
        user_group = UserGroup.query.get(group_id)
        if not user_group:
            raise ValueError(f"User group with ID {group_id} not found.")

        if user_group.created_by != user_id:
            raise PermissionError(f"User {user_id} does not have permission to update group {group_id}.")

        # Update fields
        user_group.title = validated_data.get('title', user_group.title)
        user_group.description = validated_data.get('description', user_group.description)
        user_group.updated_by = user_id

        db.session.commit()

        current_app.app_logger.info(f"User {user_id} updated user group {user_group.title}.")
        return serialize_user_group(user_group)
    except ValidationError as ve:
        current_app.app_logger.warning(f"update_user_group validation error: {str(ve)}")
        raise ve
    except PermissionError as pe:
        current_app.security_logger.critical(f"update_user_group permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"update_user_group error: {str(e)}")
        return None
    except ValueError as ve:
        current_app.app_logger.warning(f"update_user_group value error: {str(ve)}")
        raise ve

def delete_user_groups(org_id, user_id, group_ids):
    """
    Delete one or multiple user groups.
    :param org_id: Organization ID
    :param user_id: ID of the user requesting the delete action
    :param group_ids: List of group IDs to be deleted
    :return: Success message or raise an exception
    """
    try:
        # Ensure group_ids is always treated as a list
        if isinstance(group_ids, str):
            group_ids = [group_ids]

        # Fetch all user groups to delete
        groups_to_delete = UserGroup.query.filter(UserGroup.id.in_(group_ids), UserGroup.org_id == org_id).all()

        if not groups_to_delete:
            raise ValueError(f"No valid user groups found for the provided IDs: {group_ids}")

        # Check permissions and delete each group
        for group in groups_to_delete:
            if not has_permission(group.org_id, user_id, RESOURCE_NAME, 'delete'):
                raise PermissionError(f"User {user_id} is not authorized to delete group {group.id}")

            db.session.delete(group)  # Mark the group for deletion

        # Commit the deletions
        db.session.commit()

        current_app.app_logger.info(f"User {user_id} deleted {len(groups_to_delete)} user group(s).")
        return f"Successfully deleted {len(groups_to_delete)} user group(s)."
    
    except PermissionError as pe:
        current_app.app_logger.warning(f"Permission error in delete_user_groups: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.warning(f"delete_user_groups error: {str(e)}")
        raise e
    except ValueError as ve:
        current_app.app_logger.warning(f"delete_user_groups value error: {str(ve)}")
        raise ve

def serialize_user_group(group):
    """Helper function to serialize user group objects into JSON-friendly format."""
    return {
        "id": group.id,
        "title": group.title,
        "description": group.description,
        "studentcount": group.studentcount,
        "status": group.status,
        "created_at": group.created_at.strftime('%Y-%m-%d'),
        "updated_at": group.updated_at.strftime('%Y-%m-%d')
    }

def mass_status_update_groups_service(org_id, user_id, group_ids, new_status):
    """Mass update the status of user groups."""
    try:
        # Check authorization for 'update' action
        if not has_permission(org_id, user_id, RESOURCE_NAME, 'update'):
            raise PermissionError(f"User {user_id} is not authorized to update user groups")
        
        # Check that group_ids is a list and that new_status is valid
        if not group_ids or not isinstance(group_ids, list):
            raise ValueError("Invalid group_ids provided.")
        if new_status not in [0, 1]:  # Assuming '0' is disabled and '1' is enabled
            raise ValueError("Invalid status value provided.")

        # Fetch all the user groups that need updating
        groups_to_update = UserGroup.query.filter(UserGroup.id.in_(group_ids)).all()

        if not groups_to_update:
            raise ValueError("No valid user groups found for the provided IDs.")

        # Check permissions for each group and update the status
        for group in groups_to_update:            
            group.status = new_status  # Update status
            group.updated_by = user_id  # Record who made the update
            db.session.add(group)  # Mark for update

        # Commit the changes to the database
        db.session.commit()

        return f"Successfully updated {len(groups_to_update)} user group(s)."
    
    except PermissionError as pe:
        current_app.app_logger.warning(f"mass_status_update_groups_service permission error: {str(pe)}")
        raise pe
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.security_logger.critical(f"mass_status_update_groups_service error: {str(e)}")
        raise e
    except Exception as e:
        current_app.app_logger.error(f"mass_status_update_groups_service error: {str(e)}")
        raise e