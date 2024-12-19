import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
# import logging

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
test_app = create_app("testing")

# # Sample data for mocking
# mock_user = {
#     "id": "student@email.com",
#     "email": "student@email.com",
#     "password": "123",
#     "org_id": "org_123",
# }

# mock_tag = {
#     "id": "tag_1",
#     "resource_id": "resource_123",
#     "name": "New Tag",
#     "created_at": datetime.now(),
#     "updated_at": datetime.now(),
# }

# Test User Service Login
# @patch("app.services.user_service.User.query.filter_by")
def test_user_service_login(reset_database, test_app):
    with test_app.app_context():
        result = user_service_login("student@email.com", "123")
        # Print the result
        test_app.app_logger.info(f"Login result: {result}")
        assert result is not None

# # Test User Service Logout
# @patch("app.services.user_service.db.session.commit")
# def test_user_service_logout(mock_commit):
#     with test_app.app_context():
#         result = user_service_logout(mock_user["id"])
#         assert result is True

# # Test Forgot Password Service
# @patch("app.services.user_service.send_email")
# def test_user_service_forgotpassword(mock_send_email):
#     mock_send_email.return_value = True
#     with test_app.app_context():
#         result, message = user_service_forgotpassword(mock_user["email"])
#         assert result is True
#         assert "reset link" in message.lower()

# # Test Get User Authorizations
# @patch("app.services.authorization_service.db.session.query")
# def test_get_user_authorizations(mock_query):
#     mock_query.return_value.all.return_value = [{"resource": "test_resource", "action": "read"}]
#     with test_app.app_context():
#         result = get_user_authorizations(mock_user["id"], mock_user["org_id"])
#         assert "test_resource" in result

# # Test Get Tags by Resource
# @patch("app.services.tag_service.db.session.query")
# def test_get_tags_by_resource(mock_query):
#     mock_query.return_value.filter.return_value.all.return_value = [
#         MagicMock(**mock_tag)
#     ]
#     with test_app.app_context():
#         result = get_tags_by_resource("resource_123")
#         assert result is not None

# # Test Create Tag
# @patch("app.services.tag_service.db.session.add")
# @patch("app.services.tag_service.db.session.commit")
# def test_create_tag(mock_commit, mock_add):
#     with test_app.app_context():
#         result = create_tag("resource_123", "org_123", "New Tag", "user_123")
#         assert result["name"] == "New Tag"

# # Test Delete Tag
# @patch("app.services.tag_service.db.session.commit")
# def test_delete_tag(mock_commit):
#     with test_app.app_context():
#         result = delete_tag("tag_id_123")
#         assert result is True

# # Test Create User Group
# @patch("app.services.usergroup_service.db.session.add")
# @patch("app.services.usergroup_service.db.session.commit")
# def test_create_user_group(mock_commit, mock_add):
#     with test_app.app_context():
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
#     with test_app.app_context():
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
#     with test_app.app_context():
#         result = delete_user_group("org_123", "user_123", "group_id_123")
#         assert result["message"] == "Successfully deleted user group group_id_123."
