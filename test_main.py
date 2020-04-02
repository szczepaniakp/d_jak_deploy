import pytest
from fastapi.testclient import TestClient
from main import app, patients
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
    assert response.json() == {"method" : f"{method[0]}"}

@pytest.mark.parametrize("patient", [
    ("Anna", "Minsky"),
    ("Greg", "Chawisz"),
    ("Patty", "Shwash"),
    ("Rina", "Gilbert"),
])
def test_add_patient(patient):
    json = {"name" : f"{patient[0]}", "surname" : f"{patient[1]}"}
    response = client.post('/patient', json=json)

    assert response.status_code == 200
    assert response.json() == {"id" : (len(patients)-1), "patient" : 
    {"name" : f"{patient[0]}", "surname" : f"{patient[1]}"}}