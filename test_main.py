import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app) #klient, ktory gada z app

def test_hello_world():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message" : "hello world"}

@pytest.mark.parametrize("name", ["Ala", "zazółć ", "Patrycja"])
def test_hello_name(name):
    response = client.get(f'/hello/{name}')
    assert response.status_code == 200
    assert response.json() == {"message" : f"hello {name}"}

