import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="Test@1234",
        organization="UNA",
        role="user"
    )
    return user

@pytest.mark.django_db
def test_password_reset_request_valid_email(api_client, create_user):
    url = reverse('password_reset')
    response = api_client.post(url, {"email": create_user.email}, format='json')
    assert response.status_code == 200
    assert "message" in response.data

@pytest.mark.django_db
def test_password_reset_request_invalid_email(api_client):
    url = reverse('password_reset')
    response = api_client.post(url, {"email": "notfound@example.com"}, format='json')
    assert response.status_code == 404
    assert response.data["error"] == "User not found."

@pytest.mark.django_db
def test_password_reset_request_missing_email(api_client):
    url = reverse('password_reset')
    response = api_client.post(url, {}, format='json')
    assert response.status_code == 400
    assert response.data["error"] == "Email required."

@pytest.mark.django_db
def test_password_reset_confirm_valid_token(api_client, create_user):
    uid = urlsafe_base64_encode(force_bytes(create_user.pk))
    token = default_token_generator.make_token(create_user)
    url = reverse('password_reset_confirm_api', kwargs={"uidb64": uid, "token": token})
    response = api_client.post(url, {"password": "NewSecurePass123"}, format='json')
    assert response.status_code == 200
    assert response.data["message"] == "Password has been reset successfully."

@pytest.mark.django_db
def test_password_reset_confirm_invalid_uid(api_client):
    url = reverse('password_reset_confirm_api', kwargs={"uidb64": "invalid", "token": "sometoken"})
    response = api_client.post(url, {"password": "NewPass123"}, format='json')
    assert response.status_code == 400
    assert response.data["error"] == "Invalid UID"

@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(api_client, create_user):
    uid = urlsafe_base64_encode(force_bytes(create_user.pk))
    url = reverse('password_reset_confirm_api', kwargs={"uidb64": uid, "token": "invalid-token"})
    response = api_client.post(url, {"password": "NewPass123"}, format='json')
    assert response.status_code == 400
    assert response.data["error"] == "Invalid or expired token"

@pytest.mark.django_db
def test_password_reset_confirm_missing_password(api_client, create_user):
    uid = urlsafe_base64_encode(force_bytes(create_user.pk))
    token = default_token_generator.make_token(create_user)
    url = reverse('password_reset_confirm_api', kwargs={"uidb64": uid, "token": token})
    response = api_client.post(url, {}, format='json')
    assert response.status_code == 400
    assert response.data["error"] == "Password is required"
