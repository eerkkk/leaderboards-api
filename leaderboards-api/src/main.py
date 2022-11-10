from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import auth, games, scores


app = FastAPI()

origins = [
    "http://127.0.0.1:9000",
    "http://localhost:9000",
    "http://enclosure.local-dev:9000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(scores.router)
