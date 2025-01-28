import requests

def test_initial_state():

    resp = requests.get("http://host.docker.internal:8197/state")
    assert resp.text == 'INIT'

    #resp = requests.put("http://localhost:8197/state", data="INIT")
    #assert resp.status_code == 200


