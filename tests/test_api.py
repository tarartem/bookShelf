import pytest

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "stats" in data

def test_get_books_empty(client):
    response = client.get("/api/books/")
    assert response.status_code == 200
    assert response.json() == []

def test_auth_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_submit_feedback(client):
    msg = "Great app!"
    response = client.post("/api/feedback/", json={"message": msg})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == msg
    assert "id" in data

from backend.services.auth_service import create_verification_token
from backend.models import Book

def test_unlock_book(client, db):
    # 1. Create a user and login
    email = "unlock@example.com"
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
    token = create_verification_token(email)
    client.get(f"/api/auth/verify?token={token}")
    
    login_res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    auth_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 2. Create a book
    book = Book(title="Test Book", author="Test Author", epub_filepath="test.epub", status="approved")
    db.add(book)
    db.commit()
    db.refresh(book)
    
    # 3. Unlock book
    response = client.post(f"/api/books/{book.id}/unlock", headers=headers)
    assert response.status_code == 200
    
    # 4. Check credits
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.json()["credits"] == 2 # Initial 3 - 1
