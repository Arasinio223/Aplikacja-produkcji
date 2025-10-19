import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_login_invalid_login_format():
    response = client.post("/login", json={"login": "1234", "haslo": "123456"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Login musi zawierać dokładnie 4 litery"}
