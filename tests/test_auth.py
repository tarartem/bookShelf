import pytest
from backend.services.auth_service import create_verification_token

def test_signup_and_login(client, db):
    # 1. Signup
    signup_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/api/auth/signup", json=signup_data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert response.json()["is_verified"] is False
    
    # 2. Verify email
    token = create_verification_token("test@example.com")
    response = client.get(f"/api/auth/verify?token={token}")
    assert response.status_code == 200
    assert response.json()["message"] == "Account successfully verified."
    
    # 3. Login
    login_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 4. Get me
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["is_verified"] is True

def test_login_invalid_password(client, db):
    # Create user first
    signup_data = {"email": "wrong@example.com", "password": "password123"}
    client.post("/api/auth/signup", json=signup_data)
    
    # Login with wrong password
    login_data = {"email": "wrong@example.com", "password": "wrongpassword"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

def test_login_unverified(client, db):
    # Signup but don't verify
    signup_data = {"email": "unverified@example.com", "password": "password123"}
    client.post("/api/auth/signup", json=signup_data)
    
    # Login
    login_data = {"email": "unverified@example.com", "password": "password123"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 403
