import pytest
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://host.docker.internal:8197"
AUTH = HTTPBasicAuth("admin", "secret")
TIMEOUT = 5

def test_initial_state():

    resp = requests.get(f"{BASE_URL}/state")
    assert resp.text == 'INIT'

def test_ex4_functionality():
    response = requests.get(f"{BASE_URL}/api", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /api endpoint"
    data = response.json()
    assert "Service" in data, "Expected 'Service' in the response JSON"
    assert "Service2" in data, "Expected 'Service2' in the response JSON"


