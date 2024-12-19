from app.extensions import db
from flask import current_app
from app.models.usergroup_models import UserGroup, usergroup_tag
from app.models.tag_models import Tag
from sqlalchemy.exc import SQLAlchemyError

def get_tags_by_resource(resource_id):
    """
    Retrieve tags associated with a resource by the resource ID.
    """
    try:
        # Query the tags associated with the given resource through the usergroup_tag table
        tags = db.session.query(Tag).join(usergroup_tag, usergroup_tag.c.tag_id == Tag.id)\
            .filter(usergroup_tag.c.group_id == resource_id).all()

        return serialize_tags(tags)
    
    except SQLAlchemyError as e:
        current_app.app_logger.error(f"get_tags_by_resource error: {str(e)}")
        return None

def get_tags_by_user_group(org_id, user_id, group_id):
    """
    Retrieves all tags associated with a specific user group.

    Args:
        org_id (str): The organization ID to which the user group belongs.
        user_id (str): The ID of the user requesting the tags.
        group_id (str): The ID of the user group for which tags are being fetched.

    Returns:
        list: A list of serialized tag dictionaries, or an empty list if none found.
    """
    try:
        # Check if the user group exists within the organization
        user_group = UserGroup.query.filter_by(id=group_id, org_id=org_id).first()

        if not user_group:
            current_app.app_logger.warning(f"User group {group_id} not found in org {org_id}")
            return []

        # Fetch all associated tags for the user group using the many-to-many relationship
        tags = (
            Tag.query.join(usergroup_tag, Tag.id == usergroup_tag.c.tag_id)
            .filter(usergroup_tag.c.usergroup_id == group_id)
            .all()
        )

        # Serialize the tags for response
        serialized_tags = [
            {
                "id": tag.id,
                "name": tag.name,
                "created_at": tag.created_at.strftime('%Y-%m-%d'),
                "updated_at": tag.updated_at.strftime('%Y-%m-%d'),
            }
            for tag in tags
        ]

        current_app.app_logger.info(f"Fetched {len(serialized_tags)} tags for group {group_id} in org {org_id}")
        return serialized_tags

    except SQLAlchemyError as e:
        # Handle database errors gracefully
        current_app.app_logger.error(f"Database error fetching tags for group {group_id}: {e}")
        return []
    except Exception as e:
        # Catch any unexpected errors
        current_app.app_logger.error(f"Unexpected error fetching tags for group {group_id}: {e}")
        return []

def create_tag(resource_id, org_id, name, user_id):
    """Create a new tag for a resource."""
    try:
        tag = Tag(
            resource_id=resource_id,
            org_id=org_id,
            name=name,
            created_by=user_id,
            updated_by=user_id
        )
        db.session.add(tag)
        db.session.commit()
        return serialize_tag(tag)
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.error(f"create_tag error: {str(e)}")
        return None

def delete_tag(tag_id):
    """Delete a tag."""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return False
        db.session.delete(tag)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.app_logger.error(f"delete_tag error: {str(e)}")
        return False

# Utility Functions
def serialize_tag(tag):
    """Serialize a single tag object into JSON format."""
    return {
        "id": tag.id,
        "resource_id": tag.resource_id,
        "name": tag.name,
        "created_at": tag.created_at.strftime('%Y-%m-%d'),
        "updated_at": tag.updated_at.strftime('%Y-%m-%d'),
    }

def serialize_tags(tags):
    """Serialize a list of tag objects into JSON format."""
    return [serialize_tag(tag) for tag in tags]
