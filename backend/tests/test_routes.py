import pytest

def test_login_success(test_client, reset_database):
    """
    Tests successful login with valid credentials.
    """
    response = test_client.post('/api/login', json={
        'userId': 'student@email.com',
        'password': '123'
    })
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['message'] == 'Login successful'
    # check tokens in cookies
    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token=" in cookie for cookie in cookies)
    assert any("refresh_token=" in cookie for cookie in cookies)


def test_login_invalid_credentials(test_client, reset_database):
    """
    Tests login with invalid credentials.
    """
    response = test_client.post('/api/login', json={
        'userId': 'student@email.com',
        'password': 'wrong_password'
    })
    assert response.status_code == 401
    response_data = response.get_json()
    assert response_data['message'] == 'Invalid credentials.'


def test_login_missing_fields(test_client, reset_database):
    """
    Tests login with missing fields in the request.
    """
    response = test_client.post('/api/login', json={'userId': 'test_user@email.com'})
    assert response.status_code == 400  # Assuming your app handles validation
    response_data = response.get_json()
    assert response_data['message'] == 'Invalid credentials format'
