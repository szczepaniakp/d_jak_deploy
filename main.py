from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict
import logging
import json

app = FastAPI()
patients =[]
counter =0

class HelloNameResp(BaseModel):
    message: str

class MethodResp(BaseModel):
    method: str

class PatientData(BaseModel):
    name: str
    surename: str

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
    patients.append(patient_data)
    id = len(patients) - 1

    return Patient(id=id, patient=patient_data)

@app.get("/patient/{pk}", response_model=PatientData)#, errors=[404])
def get_patient(pk):
    # global patients
    # logging.warning(patients[pk])
    try:
        i = int(pk)
    except:
        raise HTTPException(status_code=404, detail=f"patient with id={pk} not found")

    if(i < 0 or i >= len(patients)):
        raise HTTPException(status_code=404, detail=f"patient with id={pk} not found")

    return PatientData(**patients[int(pk)])
    # except:
        # return 404#, {"message" : f"patient with id={pk} not found"}

# @app.exception_handler(HTTPException, response_model=GenericHTTPError)
# async def generic_error(request, ex):
#     return GenericHTTPError(status_code=ex.status_code, detail=ex.detail)