import os, tempfile, pytest
from fastapi.testclient import TestClient
@pytest.fixture
def client(tmp_path, monkeypatch):
    dbfile=tmp_path/"test.db"
    monkeypatch.setenv("DATABASE_URL",f"sqlite:///{dbfile}")
    # App modules are imported after environment setup in test modules; this fixture uses the configured app.
    from app.main import app
    with TestClient(app) as c: yield c
