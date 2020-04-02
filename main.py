from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict

app = FastAPI()
patients =[]

class HelloNameResp(BaseModel):
    message: str

class MethodResp(BaseModel):
    method: str

class PatientData(BaseModel):
    name: str
    surname: str

class Patient(BaseModel):
    id: int 
    patient: Dict 

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}', response_model=HelloNameResp)
def hello_name(name: str):
    return HelloNameResp(message=f"hello {name}")

@app.get('/method', response_model=MethodResp)
@app.put('/method', response_model=MethodResp)
@app.delete('/method', response_model=MethodResp)
@app.post('/method', response_model=MethodResp)
def hello_method(request: Request):
    method = request.method
    return MethodResp(method=f"{method}")

@app.post('/patient', response_model=Patient)
def add_patient(data: PatientData):
    patient_data = data.dict()
    id = len(patients) 
    patients.append(patient_data)

    return Patient(id=id, patient=patient_data)