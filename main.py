from fastapi import FastAPI
from database import SessionLocal, engine
import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get('/sankey')
async def get_all_sankey():
    return


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
