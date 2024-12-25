import pytest
from app.models import User, SecurityRole, Resource, Authorization, Action
from app.services.authorization_service import get_user_authorizations
from app import db
from sqlalchemy.sql import text

from app.services import (
    get_user_authorizations,
)
from app import create_app, db

# Initialize test app and setup context
app_instance = create_app("testing")

def test_get_user_authorizations(reset_database):
    """
    Test the get_user_authorizations function.
    """
    with app_instance.app_context():
        # Query the database to get the user ID
        user = User.query.filter_by(email="student@email.com").first()        
        assert user is not None, "User should exist in the database"

        # Call the service function
        try:
            result = get_user_authorizations(user_id=user.id, org_id=user.org_id)
        except Exception as e:
            pytest.fail(f"get_user_authorizations raised an exception: {e}")

        # Validate the result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "usergroup" in result, "UserGroup resource should be in the result"
        assert "quiz" in result, "Quiz resource should be in the result"
        assert "class" in result, "Class resource should be in the result"

        # Validate permissions for UserGroup
        usergroup_perms = result["usergroup"]
        assert isinstance(usergroup_perms, dict), "Permissions for UserGroup should be a dictionary"
        assert usergroup_perms.get("create") is None, "UserGroup should NOT have 'create' permission"
        assert usergroup_perms.get("update") is None, "UserGroup should NOT have 'update' permission"
        assert usergroup_perms.get("read") is True, "UserGroup should have 'view' permission"
        assert usergroup_perms.get("delete") is None, "UserGroup should NOT have 'delete' permission"

        # Validate permissions for Quiz
        quiz_perms = result["quiz"]
        assert isinstance(quiz_perms, dict), "Permissions for Quiz should be a dictionary"
        assert quiz_perms.get("create") is None, "Quiz should NOT have 'create' permission"
        assert quiz_perms.get("update") is None, "Quiz should NOT have 'update' permission"
        assert quiz_perms.get("read") is True, "Quiz should have 'read' permission"
        assert quiz_perms.get("delete") is None, "Quiz should NOT have 'delete' permission"
        assert quiz_perms.get("attempt") is True, "Quiz should have 'attempt' permission"
    
        # Validate permissions for Class
        class_perms = result["class"]
        assert isinstance(class_perms, dict), "Permissions for Class should be a dictionary"
        assert class_perms.get("create") is True, "Class should have 'create' permission"
        assert class_perms.get("update") is True, "Class should have 'update' permission"
        assert class_perms.get("read") is True, "Class should have 'read' permission"
        assert class_perms.get("delete") is True, "Class should have 'delete' permission"
