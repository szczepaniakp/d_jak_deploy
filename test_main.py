import pytest
from fastapi.testclient import TestClient
from main import app
import json
client = TestClient(app) #klient, ktory gada z app

def test_hello_world():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}

@pytest.mark.parametrize("name", ["Ala", "zazółć ", "Patrycja"])
def test_hello_name(name):
    response = client.get(f'/hello/{name}')
    assert response.status_code == 200
    assert response.json() == {"message" : f"hello {name}"}

@pytest.mark.parametrize("method", [
    ("GET", client.get('/method')),
    ("PUT", client.put('/method')),
    ("DELETE", client.delete('/method')),
    ("POST", client.post('/method'))])
def test_hello_method(method):
    response = method[1]
    assert response.status_code == 200
    assert response.json() == {"message" : f"{method[0]}"}

