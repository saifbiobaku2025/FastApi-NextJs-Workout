import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, workouts, routines

app = FastAPI()

Base.metadata.create_all(bind=engine)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def health_check():
    return {"message": "API is healthy!"}


app.include_router(auth.router)
app.include_router(workouts.router)
app.include_router(routines.router)
