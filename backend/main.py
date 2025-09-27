from fastapi import FastAPI
from db.database import engine
from models.base import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Backend is running, DB works"}
