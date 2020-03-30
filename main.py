from fastapi import FastAPI
from pydantic import BaseModel
# from typing import Dict

app = FastAPI()

class HelloNameResp(BaseModel):
    message: str

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}', response_model=HelloNameResp)
def hello_name(name: str):
    return HelloNameResp(message=f"hello {name}")
    # return {"message" : }