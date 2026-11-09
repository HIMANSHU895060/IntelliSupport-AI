from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def account():
    import uuid
    email=f"test-{uuid.uuid4().hex[:8]}@example.com"
    r=client.post("/api/auth/register",json={"name":"Test User","email":email,"password":"StrongPass123"})
    assert r.status_code==200
    return r.json()["access_token"]
def test_health():
    assert client.get("/api/health").json()["status"]=="ok"
def test_register_and_me():
    token=account()
    r=client.get("/api/auth/me",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
def test_chat_creates_workflow_response():
    token=account()
    r=client.post("/api/chat",headers={"Authorization":f"Bearer {token}"},json={"message":"I get HTTP 429 errors from the API"})
    assert r.status_code==200
    data=r.json()
    assert data["category"]=="technical"
    assert len(data["events"])==7
def test_rag_search():
    token=account()
    r=client.get("/api/knowledge/search?q=password%20reset",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert r.json()
def test_customer_cannot_access_admin_users():
    token=account()
    r=client.get("/api/admin/users",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==403
