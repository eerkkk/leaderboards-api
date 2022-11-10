import sys
sys.path.append("..")

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/modes")
async def get_modes(db: Session = Depends(get_db)):
    return db.query(models.GameModes).all()


@router.get("/contents")
async def get_modes(db: Session = Depends(get_db)):
    return db.query(models.GameContents).all()
