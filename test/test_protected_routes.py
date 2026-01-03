import pytest
from httpx import AsyncClient
from starlette import status
from unittest.mock import patch

@pytest.mark.asyncio
async def test_protected_document_route_unauthorized(client: AsyncClient):
    """Test that accessing documents without a token is blocked."""
    # We use a route that actually exists in your app
    response = await client.post("/api/v1/documents/upload") 
    
    # Check if your app returns 401 or 403 when no token is present
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

@pytest.mark.asyncio
async def test_access_with_valid_token(client: AsyncClient):
    """Test login and then accessing a real route."""
    # 1. Setup
    user_email = "test_protected@example.com"
    password = "password123"
    await client.post("/api/v1/auth/register", json={"email": user_email, "password": password})
    
    # 2. Login (Using 'email' as your API expects)
    login_res = await client.post("/api/v1/auth/login", json={"email": user_email, "password": password})
    assert login_res.status_code == 200
    
    # Debug print if this fails again
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.json()}")
        
    token = login_res.json()["access_token"]
    files = {"file": ("test.pdf", b"%PDF-1.4\n%test content", "application/pdf")}
    headers = {"Authorization": f"Bearer {token}"}


    # We patch the 'queue_processing' function where it is USED (in the routes file)
    with patch("app.api.v1.routes.documents.queue_processing") as mock_queue:
        # Give it a fake return value so the code continues
        mock_queue.return_value = {
            "task_id": "mock-task-id-123",
            "document_id": "mock-doc-id",
            "trace_id": "mock-trace"
        }

        # 3. Access a real route
        response = await client.post("/api/v1/documents/upload", headers=headers, files=files)
        
        assert response.status_code == 201
        assert response.json()["task_id"] == "mock-task-id-123"