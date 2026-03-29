import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.mark.django_db
def test_login_returns_access_token_and_refresh_cookie(client):
    User.objects.create_user(username='alice', password='StrongPassword123!')

    response = client.post(
        '/api/v1/auth/login/',
        data=json.dumps({'username': 'alice', 'password': 'StrongPassword123!'}),
        content_type='application/json',
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload['access'], str)
    assert payload['user']['username'] == 'alice'
    assert 'igar_refresh_token' in response.cookies


@pytest.mark.django_db
def test_login_returns_rfc7807_on_invalid_credentials(client):
    User.objects.create_user(username='alice', password='StrongPassword123!')

    response = client.post(
        '/api/v1/auth/login/',
        data=json.dumps({'username': 'alice', 'password': 'wrong'}),
        content_type='application/json',
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload['type'] == 'https://igar.dev/errors/invalid_credentials'
    assert payload['status'] == 401
    assert payload['detail'] == 'Identifiants invalides.'


@pytest.mark.django_db
def test_refresh_renews_access_token_using_refresh_cookie(client):
    User.objects.create_user(username='alice', password='StrongPassword123!')

    login_response = client.post(
        '/api/v1/auth/login/',
        data=json.dumps({'username': 'alice', 'password': 'StrongPassword123!'}),
        content_type='application/json',
    )
    assert login_response.status_code == 200

    refresh_response = client.post('/api/v1/auth/refresh/', data=json.dumps({}), content_type='application/json')

    assert refresh_response.status_code == 200
    payload = refresh_response.json()
    assert isinstance(payload['access'], str)
    assert payload['user']['username'] == 'alice'


@pytest.mark.django_db
def test_logout_clears_refresh_cookie(client):
    User.objects.create_user(username='alice', password='StrongPassword123!')

    login_response = client.post(
        '/api/v1/auth/login/',
        data=json.dumps({'username': 'alice', 'password': 'StrongPassword123!'}),
        content_type='application/json',
    )
    assert login_response.status_code == 200

    logout_response = client.post('/api/v1/auth/logout/', data=json.dumps({}), content_type='application/json')

    assert logout_response.status_code == 204
    assert logout_response.cookies['igar_refresh_token'].value == ''


@pytest.mark.django_db
def test_login_requires_csrf_when_csrf_checks_enabled():
    User.objects.create_user(username='alice', password='StrongPassword123!')
    csrf_client = Client(enforce_csrf_checks=True)

    csrf_client.get('/api/v1/auth/csrf/')

    response_without_token = csrf_client.post(
        '/api/v1/auth/login/',
        data=json.dumps({'username': 'alice', 'password': 'StrongPassword123!'}),
        content_type='application/json',
    )
    assert response_without_token.status_code == 403

    csrf_token = csrf_client.cookies['csrftoken'].value
    response_with_token = csrf_client.post(
        '/api/v1/auth/login/',
        data=json.dumps({'username': 'alice', 'password': 'StrongPassword123!'}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response_with_token.status_code == 200
