from fastapi import FastAPI, Request, HTTPException, Response, Form, status, Query, Depends, APIRouter, Cookie
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
import logging
from fastapi.templating import Jinja2Templates
from routers import tracks

USERS = "users"
security = HTTPBasic()

app = FastAPI()
app.include_router(tracks.router)

hashed_passes = { b64encode("trudnY:PaC13Nt".encode('utf-8')).decode('utf-8') }
sessions = {}

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


def check_creds(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password

    passes = b64encode(bytes(username + ':' + password, "utf-8")).decode('utf-8')

    if passes not in hashed_passes:  
        raise HTTPException(status_code=401, detail="Unauthorized") 

    session_token = sha256(bytes(f"{username}{password}{app.secret_key}", encoding='utf8')).hexdigest()
    sessions[session_token] = username

    return passes, session_token

@app.get('/welcome')
def welcome(request: Request, response: Response):
    if_logged_in(request)

    user = sessions[request.cookies["session_token"]]
    response = templates.TemplateResponse("index.html", {"request": request, "user": user})

    return response

@app.get('/', response_model=HelloResp)
def hello_world(request: Request, response: Response):
    return {"message":"Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}', response_model=HelloResp)
def hello_name(name: str):
    return HelloResp(message=f"hello {name}")

@app.post('/login')
def login(user_data: (str, str) = Depends(check_creds)):
   
    passes = user_data[0]
    session_token = user_data[1]

    response = RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    response.headers["Location"] = "/welcome"
    response.set_cookie(key="session_token", value=session_token)
    # response.set_cookie(key="username", value=username)

    response.headers['Authorization'] = f"Basic {passes}" 

    return response


def if_logged_in(request: Request, session_token: str = Cookie(None)):
    # try:
    #     auth = request.headers["Authorization"].split(" ")[1]
    #     if auth not in hashed_passes:  
    #         raise HTTPException(status_code=401, detail="Unauthorized")
    # except:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    if "session_token" not in request.cookies.keys():
        raise HTTPException(status_code=401, detail="Session is dead") 
    if request.cookies["session_token"] not in sessions.keys():
        raise HTTPException(status_code=401, detail="Unauthorized") 


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

@app.get('/method', response_model=MethodResp)
@app.put('/method', response_model=MethodResp)
@app.delete('/method', response_model=MethodResp)
@app.post('/method', response_model=MethodResp)
def hello_method(request: Request):
    method = request.method
    return MethodResp(method=f"{method}")

@app.post('/patient')
def add_patient(data: PatientData, request: Request):
    if_logged_in(request)

    patient_data = data.dict()
    id = f"id_{len(patients)+1}"
    patients[id] = patient_data

    return RedirectResponse(url=f"/patient/{id}", status_code=status.HTTP_302_FOUND)

@app.get("/patient")
def get_patients(request: Request):
    if_logged_in(request)

    return patients

@app.get("/patient/{pk}", response_model=PatientData)
def get_patient(pk, request: Request):
    if_logged_in(request)
    if pk not in patients.keys():
        raise HTTPException(status_code=400)
    
    return PatientData(**patients[pk])

@app.delete("/patient/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(pk, request: Request):
    if_logged_in(request)
    if pk not in patients.keys():
        raise HTTPException(status_code=400)

    del patients[pk]
    # return RedirectResponse(url=f"/welcome", status_code=status.HTTP_302_FOUND, headers={"Location":"/welcome"})
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(jsonable_encoder({"detail": exc.errors(), "body": exc.body}))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

    