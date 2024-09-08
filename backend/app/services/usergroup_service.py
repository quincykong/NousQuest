from app import db
from app.models import UserGroup, User
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logging_config import security_logger, app_logger

def get_user_groups(user_id):
    """Retrieve all user groups for a specific user (e.g., instructor)."""
    try:
        # Filter groups that the user is allowed to view, for now, we'll assume all groups
        user_groups = UserGroup.query.filter_by(created_by=user_id).all()

        return [serialize_user_group(group) for group in user_groups]
    except SQLAlchemyError as e:
        app_logger.warning(f"get_user_groups: {str(e)}")
        return []

def create_user_group(user_id, data):
    """Create a new user group."""
    try:
        new_group = UserGroup(
            org_id=data['org_id'],
            title=data['title'],
            description=data.get('description', ''),
            created_by=user_id,
            updated_by=user_id
        )

        db.session.add(new_group)
        db.session.commit()
        return serialize_user_group(new_group)
    except SQLAlchemyError as e:
        db.session.rollback()
        app_logger.warning(f"create_user_group: {str(e)}")
        return None

def update_user_group(user_id, group_id, data):
    """Update an existing user group."""
    try:
        user_group = UserGroup.query.get(group_id)

        if user_group and user_group.created_by == user_id:
            user_group.title = data['title']
            user_group.description = data.get('description', '')
            user_group.updated_by = user_id
            db.session.commit()

            return serialize_user_group(user_group)
        return None
    except SQLAlchemyError as e:
        db.session.rollback()
        app_logger.warning(f"update_user_group: {str(e)}")
        return None

def delete_user_group(user_id, group_id):
    """Delete an existing user group."""
    try:
        user_group = UserGroup.query.get(group_id)

        if user_group and user_group.created_by == user_id:
            db.session.delete(user_group)
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        app_logger.warning(f"delete_user_groups: {str(e)}")
        return False

def serialize_user_group(group):
    """Helper function to serialize user group objects into JSON-friendly format."""
    return {
        "id": group.id,
        "title": group.title,
        "description": group.description,
        "status": group.status,
        "created_at": group.created_at.strftime('%Y-%m-%d'),
        "updated_at": group.updated_at.strftime('%Y-%m-%d')
    }
