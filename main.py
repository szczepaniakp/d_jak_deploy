from fastapi import FastAPI, Request, HTTPException, Response, Form, status, Query, Depends, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict
import secrets
from os import environ
from hashlib import sha256
from base64 import b64encode
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi.templating import Jinja2Templates

USERS = "users"
security = HTTPBasic()

app = FastAPI()


hashed_passes = { b64encode("trudnY:PaC13Nt".encode('utf-8')).decode('utf-8') }
sessions = set()

app.secret_key = "very consta and random secret, best 64 characters" 

patients = {}
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

# def if_logged(headers):
#     if "" not in headers:
#         response = Response(headers={'WWW-Authenticate': 'Basic'}, status_code=401)
#         return response        

@app.get('/welcome')
def welcome(request: Request, response: Response):
    if_logged_in(request)
   
    user = request.cookies["username"]

    response = templates.TemplateResponse("index.html", {"request": request, "user": "trudnY"})
    response.status_code = status.HTTP_302_FOUND

    return response

@app.get('/', response_model=HelloResp)
def hello_world(request: Request, response: Response):
    return {"message":"Hello World during the coronavirus pandemic!"}
    #HelloResp(message = "Hello World during the coronavirus pandemic!")

@app.get('/hello/{name}', response_model=HelloResp)
def hello_name(name: str):
    return HelloResp(message=f"hello {name}")

@app.post('/login')
def login(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password

    passes = b64encode(bytes(username + ':' + password, "utf-8")).decode('utf-8')

    if passes not in hashed_passes:  
        raise HTTPException(status_code=401, detail="Unauthorized") 

    session_token = sha256(bytes(f"{username}{password}{app.secret_key}", 'utf-8')).hexdigest()
    sessions.add(session_token)
    response = RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=session_token, expires=300)
    response.set_cookie(key="username", value=username)

    response.headers['Authorization'] = f"Basic {passes}" 

    return response


def if_logged_in(request: Request):
    try:
        auth = request.headers["Authorization"].split(" ")[1]
        if auth not in hashed_passes:  
            raise HTTPException(status_code=401, detail="Unauthorized")
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if "session_token" not in request.cookies.keys():
        raise HTTPException(status_code=440, detail="Session is dead") 


@app.post('/logout')
def logout(request: Request, current_user = Depends(security)):
    if_logged_in(request)

    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND, headers={"Location": "/"})
    response.headers["Authorization"] = ""

    try:
        session = request.cookies["session_token"]
        sessions.remove(session)
    except:
        print("Already removed")

    response.delete_cookie("session_token")
    response.delete_cookie("username")

    return response

# @app.get('/method', response_model=MethodResp)
# @app.put('/method', response_model=MethodResp)
# @app.delete('/method', response_model=MethodResp)
# @app.post('/method', response_model=MethodResp)
# def hello_method(request: Request):
#     method = request.method
#     return MethodResp(method=f"{method}")

@app.post('/patient')
def add_patient(data: PatientData, request: Request):
    if_logged_in(request)

    patient_data = data.dict()
    id = f"id_{len(patients)+1}"
    patients[id] = patient_data
    print()

    # return Patient(id=id, patient=patient_data)
    response = RedirectResponse(url=f"/patient/{id}", status_code=status.HTTP_302_FOUND)


@app.get("/patient/{pk}", response_model=PatientData)
def get_patient(pk, request: Request):
    if_logged_in(request)
    if pk not in patients.keys():
        raise HTTPException(status_code=400)
    
    return PatientData(*patients[pk])

@app.delete("/patient/{pk}")
def delete_patient(pk, request: Request):
    if_logged_in(request)
    if pk not in patients.keys():
        raise HTTPException(status_code=400)

    del patients[pk]
    return RedirectResponse(url=f"/patient")

@app.get("/patient")
def get_patients(request: Request):
    if_logged_in(request)

    return patients
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(jsonable_encoder({"detail": exc.errors(), "body": exc.body}))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )