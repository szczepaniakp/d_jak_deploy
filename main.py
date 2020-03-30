from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HelloNameResp(BaseModel):
    message: str


@app.get('/')
def hello_world():
    return {"message" : "hello world"}

@app.get('/hello/{name}', response_model=HelloNameResp)
def hello_name(name: str):
    return HelloNameResp(message=f"hello {name}")
    # return {"message" : }