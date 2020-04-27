from fastapi import FastAPI, Request, HTTPException, Response, Form, status, Query, Depends, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict
import secrets
# import redis
from os import environ
from hashlib import sha256
from base64 import b64encode

from fastapi.templating import Jinja2Templates

USERS = "users"
security = HTTPBasic()
# basic_auth = BasicAuth(auto_error=False)

app = FastAPI()
# db = redis.Redis(host='localhost', charset="utf-8", decode_responses=True)
# db.sadd(b64encode(b"trudnY:PaC13Nt"))

hashed_passes = { b64encode("trudnY:PaC13Nt".encode('utf-8')) }
sessions = set()

app.secret_key = "very consta and random secret, best 64 characters" #environ.get("DAFT_SECRET_KEY")

patients ={}
templates = Jinja2Templates(directory="templates")


class HelloResp(BaseModel):
    message: str

class MethodResp(BaseModel):
    method: str

class PatientData(BaseModel):
    name: str=""
    surname: str=""

class Patient(BaseModel):
    id: str
    patient: Dict 

def if_logged(headers):
    if "" not in headers:
        response = Response(headers={'WWW-Authenticate': 'Basic'}, status_code=401)
        return response        

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}', response_model=HelloResp)
def hello_name(name: str):
    return HelloResp(message=f"hello {name}")

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
    response = RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    # Request.url_for()
    response.set_cookie(key="session_token", value=session_token, expires=300)
    response.set_cookie(key="username", value=username)

    response.headers['Authorization'] = f"Basic {passes}" 

    return response


def if_logged_in(request: Request):
    # session_token = sha256(bytes(f"{username}{password}{app.secret_key}", 'utf-8')).hexdigest()
    # print(request.headers)
    # auth = request.headers["authorization"]
    # if auth
        
    if "session_token" not in request.cookies.keys():
        raise HTTPException(status_code=401, detail="Session is dead") 


@app.post('/logout')
def logout(request: Request, current_user = Depends(security)):
    if_logged_in(request)

    print(request.headers)
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND, headers={"Location": "/"})
    # response.dele("authorization")
    # response(key="session_token", value="")
    
    try:
        session = request.cookies["session_token"]
        sessions.remove(session)
    except:
        print("Already removed")
    response.delete_cookie("session_token")
    #  if request.headers["authorization"] not in sessions:
    #     raise HTTPException(status_code=401, detail="Session is dead") 

    return response


@app.get('/welcome')
def welcome(request: Request, credentials: HTTPBasicCredentials = Depends(login)):
    # return HelloResp(message="Hi there!")
    # if not if_logged_in(request):
    if_logged_in(request)

    user = request.cookies["username"]

    return templates.TemplateResponse("index.html", {"request": request, "user": user}) 

# @app.get('/login')
# def load_login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request}) 
    

@app.get('/method', response_model=MethodResp)
@app.put('/method', response_model=MethodResp)
@app.delete('/method', response_model=MethodResp)
@app.post('/method', response_model=MethodResp)
def hello_method(request: Request):
    method = request.method
    return MethodResp(method=f"{method}")

@app.post('/patient')#, response_model=Patient)
def add_patient(data: PatientData, request: Request):
    if_logged_in(request)

    patient_data = data.dict()
    id = f"id_{len(patients)+1}"
    patients[id] = patient_data
    print()

    # return Patient(id=id, patient=patient_data)
    response = RedirectResponse(url=f"/patient/{id}", status_code=status.HTTP_302_FOUND)


@app.get("/patient/{pk}", response_model=PatientData)#, errors=[404])
def get_patient(pk, request: Request):
    if_logged_in(request)
    if pk not in patients.keys():
        raise HTTPException(status_code=400)
    
    return PatientData(*patients[pk])

@app.delete("/patient/{pk}")#, errors=[404])
def delete_patient(pk, request: Request):
    if_logged_in(request)
    if pk not in patients.keys():
        raise HTTPException(status_code=400)

    del patients[pk]
    return RedirectResponse(url=f"/patient", status_code=status.HTTP_302_FOUND)

@app.get("/patient")
def get_patients(request: Request):
    if_logged_in(request)
   
    return patients
    