import pytest
from app.models import User
from flask import g
from app.services import (
    user_service_login,
    user_service_logout,
    user_service_forgotpassword,
    get_user_authorizations,
    get_tags_by_resource,
    create_tag,
    delete_tag,
    get_user_groups,
    create_user_group,
    update_user_group,
    delete_user_group,
)
from app import create_app

# Initialize test app and setup context
app_instance = create_app("testing")

def test_get_usergroups(reset_database, app_instance):
    """Test retrieving user groups with valid filters."""
    with app_instance.app_context():
        result = user_service_login("student@email.com", "123")
        assert isinstance(result, tuple), "The result should be a tuple"

        # Test without filters
        response = get_user_groups(g.org_id, g.user_id)
        assert response['rows']
        assert 'pageInfo' in response

        # Test with a search term
        response = get_user_groups(g.org_id, g.user_id, search_term="User Group")
        assert any("User Group" in group['title'] for group in response['rows'])

        # Test with tags
        response = get_user_groups(g.org_id, g.user_id, tags="tag1,tag2")
        assert all('tags' in group for group in response['rows'])

# def test_create_usergroup(reset_database, app_instance):
#     """Test creating a user group."""
#     org_id = 1
#     user_id = 1
#     title = "New Test Group"
#     description = "This is a test group."
#     status = '1'
#     tags = [1, 2]

#     response = create_user_group(org_id, user_id, title, description, status, tags)
#     assert response['title'] == title
#     assert response['description'] == description
#     assert response['status'] == status
#     assert response['tags']

# def test_update_usergroup(test_client, init_database):
#     """Test updating an existing user group."""
#     org_id = 1
#     user_id = 1
#     group_id = 1
#     new_title = "Updated Test Group"
#     new_description = "Updated description."

#     response = update_user_group(org_id, user_id, group_id, title=new_title, description=new_description)
#     assert response['title'] == new_title
#     assert response['description'] == new_description

# def test_delete_usergroup(test_client, init_database):
#     """Test deleting a user group."""
#     org_id = 1
#     user_id = 1
#     group_id = 2  # Assuming a group with this ID exists

#     response = delete_user_group(org_id, user_id, group_id)
#     assert "Successfully deleted" in response['message']