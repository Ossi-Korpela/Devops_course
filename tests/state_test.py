import pytest
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://host.docker.internal:8197"
AUTH = HTTPBasicAuth("admin", "secret")
TIMEOUT = 5

def test_state_change_no_auth():
    """
    Corresponds to:
      it('should not allow state change without login (401)', ...)
    """
    states_to_test = ["PAUSED", "RUNNING"]
    for state in states_to_test:
        # try changing state without auth
        response = requests.put(
            f"{BASE_URL}/state",
            params={"state": state},
            timeout=TIMEOUT
        )
        # we expect a 401 status
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated state change to {state}, "
            f"got {response.status_code}"
        )
        assert "401" in response.text or "Unauthorized" in response.text, (
            "Expected error page to contain '401' or 'Unauthorized'"
        )