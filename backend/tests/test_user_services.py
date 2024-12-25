import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.models.authorization_models import User

from app.services import (
    user_service_login,
    user_service_logout,
    user_service_forgotpassword,
    get_user_authorizations,
    get_tags_by_resource,
    create_tag,
    delete_tag,
    create_user_group,
    update_user_group,
    delete_user_group,
)
from app import create_app, db

# Initialize test app and setup context
app_instance = create_app("testing")

# Test User Service Login
def test_user_service_login(reset_database, app_instance):
    with app_instance.app_context():
        result = user_service_login("student@email.com", "123")

        # Assertions
        assert result is not None, "The result should not be None"
        assert isinstance(result, tuple), "The result should be a tuple"
        # Unpack the result tuple
        success, data, message = result
        # Validate the success flag
        assert success is True, "The service should return True for a valid login"
        # Validate the response structure
        assert data is not None
        assert message == "Login successful"

# Test User Service Logout
def test_user_service_logout(reset_database, app_instance):
    with app_instance.app_context():
        # Query the database to get the user ID
        user = User.query.filter_by(email="student@email.com").first()
        
        assert user is not None, "User should exist in the database"
        
        # Pass the user's ID to the service
        result = user_service_logout(user.id)
        
        # Validate the result
        assert result is True, "Logout should return True"


# # Test Forgot Password Service
# @patch("app.services.user_service.send_email")
# def test_user_service_forgotpassword(mock_send_email):
#     mock_send_email.return_value = True
#     with app_instance.app_context():
#         result, message = user_service_forgotpassword(mock_user["email"])
#         assert result is True
#         assert "reset link" in message.lower()

# # Test Create User Group
# @patch("app.services.usergroup_service.db.session.add")
# @patch("app.services.usergroup_service.db.session.commit")
# def test_create_user_group(mock_commit, mock_add):
#     with app_instance.app_context():
#         result = create_user_group(
#             "org_123",
#             "user_123",
#             "New Group",
#             description="Group Description",
#             tags=["tag_id_1", "tag_id_2"],
#         )
#         assert result["title"] == "New Group"

# # Test Update User Group
# @patch("app.services.usergroup_service.db.session.commit")
# def test_update_user_group(mock_commit):
#     with app_instance.app_context():
#         result = update_user_group(
#             "org_123",
#             "user_123",
#             "group_id_123",
#             title="Updated Title",
#             description="Updated Description",
#         )
#         assert result["title"] == "Updated Title"

# # Test Delete User Group
# @patch("app.services.usergroup_service.db.session.commit")
# def test_delete_user_group(mock_commit):
#     with app_instance.app_context():
#         result = delete_user_group("org_123", "user_123", "group_id_123")
#         assert result["message"] == "Successfully deleted user group group_id_123."
