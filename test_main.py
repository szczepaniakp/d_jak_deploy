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

def test_welcome():
    response = client.get(f"/welcome")
    assert response.status_code == 200
    assert response.json() == {"message" : "Hi there!"}

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
    json = {"name" : f"{patient[0]}", "surename" : f"{patient[1]}"}
    response = client.post("/patient", json=json)

    assert response.status_code == 200
    assert response.json() == {"id" : (len(patients)-1), "patient" : 
    {"name" : f"{patient[0]}", "surename" : f"{patient[1]}"}}

@pytest.mark.parametrize("pk", [0, 2])
def test_get_patient(pk):
    response =  client.get(f"/patient/{pk}")
    assert response.status_code == 200
    assert response.json() == {"name" : f"{patients[pk][name]}", "surename" : f"{patient[pk][surname]}"}

@pytest.mark.parametrize("pk", [-1, -4])
def test_get_patient(pk):
    response =  client.get(f"/patient/{pk}")
    assert response.status_code == 204

@pytest.mark.parametrize("pk", [1.1, -2.1])
def test_get_patient(pk):
    response =  client.get(f"/patient/{pk}")
    assert response.status_code == 400
