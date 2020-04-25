from fastapi import FastAPI, Request, HTTPException, Response, Form, status, Query, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict
# import redis
from os import environ
from hashlib import sha256
from base64 import b64encode


# import logging
# import json
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

USERS = "users"
security = HTTPBasic()

app = FastAPI()
# db = redis.Redis(host='localhost', charset="utf-8", decode_responses=True)
# db.sadd(b64encode(b"trudnY:PaC13Nt"))
hashed_passes = { b64encode("trudnY:PaC13Nt".encode('utf-8')) }
sessions = set()

app.secret_key = "very consta and random secret, best 64 characters" #environ.get("DAFT_SECRET_KEY")

patients =[]
templates = Jinja2Templates(directory="templates")


class HelloResp(BaseModel):
    message: str

class MethodResp(BaseModel):
    method: str

class PatientData(BaseModel):
    name: str=""
    surename: str=""

class Patient(BaseModel):
    id: int
    patient: Dict 

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}', response_model=HelloResp)
def hello_name(name: str):
    return HelloResp(message=f"hello {name}")

@app.get('/welcome', response_model=HelloResp)
def welcome():
    return HelloResp(message="Hi there!")

@app.get('/login')
def load_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request}) 

# @app.post('/login')
async def login(request: Request, *, username: str = Form(...), password: str = Form(...)): #login: str = Query("login"), password: str = Query("pass")):#
    # print(username)
    # await request.form()
    # print(request.form())
    # username = request.form()["login"]
    # password = request.form()["pass"]
    # print(request.query_params)

    # login = request.query_params["login"] 
    # password = "jdjd"
    # print(request.headers)
    # print(login)
    passes = b64encode(bytes(username + ':' + password, "utf-8"))

    if passes not in hashed_passes:  #db.smembers(USERS):
        raise HTTPException(status_code=401, detail="Unauthorized") 

    session_token = sha256(bytes(f"{username}{password}{app.secret_key}", 'utf-8')).hexdigest()
    #db.set(session_token, "session will expire in 5 minutes", ex=300)
    sessions.add(session_token)
    response = RedirectResponse(url="/hello", status_code=status.HTTP_302_FOUND) 
    response.set_cookie(key="session_token", value=session_token, expires=300)
    response.headers['Authorization'] = f"Basic {passes}" 

    return response
    
@app.post('/login')
def login(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password

    passes = b64encode(bytes(username + ':' + password, "utf-8"))

    if passes not in hashed_passes:  #db.smembers(USERS):
        raise HTTPException(status_code=401, detail="Unauthorized") 

    session_token = sha256(bytes(f"{username}{password}{app.secret_key}", 'utf-8')).hexdigest()
    #db.set(session_token, "session will expire in 5 minutes", ex=300)
    sessions.add(session_token)
    response = RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)#, headers={"Location": "/hello"}) 
    response.set_cookie(key="session_token", value=session_token, expires=300)
    response.headers['Authorization'] = f"Basic {passes}" 

    return response

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
    try:
        i = int(pk)

    except:
        raise HTTPException(status_code=400)

    if(i < 0 or i >= len(patients)):
        raise HTTPException(status_code=204)
    
    return PatientData(**patients[i])
    