from app import db
from flask import current_app
from app.models import Tag, usergroup_tag
from sqlalchemy.exc import SQLAlchemyError
#from app.utils.logging_config import app_logger

def get_tags_by_resource(usergroup_id):
    """
    Retrieve tags associated with a user group by the group ID.
    """
    try:
        # Query the tags associated with the given user group through the usergroup_tag table
        tags = db.session.query(Tag).join(usergroup_tag, usergroup_tag.c.tag_id == Tag.id)\
            .filter(usergroup_tag.c.group_id == usergroup_id).all()

        return [serialize_tag(tag) for tag in tags]
    
    except SQLAlchemyError as e:
        current_app.app_logger.error(f"get_tags_by_usergroup error: {str(e)}")
        return None

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

def serialize_tag(tag):
    """Helper function to serialize a tag object into JSON format."""
    return {
        "id": tag.id,
        "resource_id": tag.resource_id,
        "name": tag.name,
        "created_at": tag.created_at.strftime('%Y-%m-%d'),
        "updated_at": tag.updated_at.strftime('%Y-%m-%d'),
    }
