import sys
sys.path.append("..")

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import delete
from pydantic import BaseModel
import datetime
import models
from database import engine, SessionLocal
from .auth import get_current_user, get_user_exception

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/scores",
    tags=["scores"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Score(BaseModel):
    score: int
    game_modifier: int
    game_mode_slug: str
    game_content_slug: str


@router.get("/all")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Scores).all()


@router.get("/high_score")
async def get_user_high_score(game_modifier: int,
                              game_mode_slug: str,
                              game_content_slug: str,
                              db: Session = Depends(get_db),
                              user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    game_mode_model = db.query(models.GameModes)\
        .filter(models.GameModes.slug == game_mode_slug)\
        .first()
    game_mode_id = game_mode_model.id

    game_content_model = db.query(models.GameContents)\
        .filter(models.GameContents.slug == game_content_slug)\
        .first()
    game_content_id = game_content_model.id

    user_high_score = db.query(
        models.Scores
    ).filter(
        models.Scores.game_mode_id == game_mode_id,
        models.Scores.game_content_id == game_content_id,
        models.Scores.game_modifier == game_modifier,
        models.Scores.user_id == user.get("id")
    ).order_by(
        models.Scores.score.desc()
    ).first()
    # Test the response below
    return user_high_score.score


@router.get("/high_scores")
async def get_high_scores_for_game(game_modifier: int,
                                   game_mode_slug: str,
                                   game_content_slug: str,
                                   db: Session = Depends(get_db)):
    query_results = db.query(
        models.Scores,
        models.GameModes,
        models.GameContents,
        models.Users
    ).filter(
        models.Scores.game_mode_id == models.GameModes.id,
        models.GameModes.slug == game_mode_slug,
        models.Scores.game_content_id == models.GameContents.id,
        models.GameContents.slug == game_content_slug,
        models.Scores.game_modifier == game_modifier
    ).order_by(
        models.Scores.score.desc()
        # Also order by date so the earliest high score shows between multiple users
    ).all()

    rank = 0
    high_scores = [build_score_from_response(high_score, idx) for idx, high_score in enumerate(query_results, start=1)]

    return high_scores


@router.post("/")
async def post_score(score: Score,
                     user: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    # Finds the game mode id using slug
    game_mode_model = db.query(models.GameModes)\
        .filter(models.GameModes.slug == score.game_mode_slug)\
        .first()
    game_mode_id = game_mode_model.id
    # Finds the game content id using slug
    game_content_model = db.query(models.GameContents)\
        .filter(models.GameContents.slug == score.game_content_slug)\
        .first()
    game_content_id = game_content_model.id

    user_high_score = db.query(
        models.Scores
    ).filter(
        models.Scores.game_mode_id == game_mode_id,
        models.Scores.game_content_id == game_content_id,
        models.Scores.game_modifier == score.game_modifier,
        models.Scores.user_id == user.get("id")
    ).order_by(
        models.Scores.score.desc()
    ).first()
    highest_score = user_high_score.score if user_high_score is not None else 0

    if highest_score >= score.score:
        return highest_score

    score_model = models.Scores()
    score_model.score = score.score
    score_model.date = datetime.date.today()
    score_model.game_modifier = score.game_modifier
    score_model.user_id = user.get("id")
    score_model.game_mode_id = game_mode_id
    score_model.game_content_id = game_content_id

    # Deletes previous high scores for the specific game type
    delete_statement = delete(models.Scores).where(models.Scores.user_id == user['id'])\
                                            .where(models.Scores.game_modifier == score.game_modifier)\
                                            .where(models.Scores.game_content_id == game_content_id)\
                                            .where(models.Scores.game_mode_id == game_mode_id)
    db.execute(delete_statement)
    # Submits the new high score
    db.add(score_model)
    db.commit()

    return score.score


def build_score_from_response(high_score, rank):
    score_id = high_score['Scores'].id
    score_date = high_score['Scores'].date
    score = high_score['Scores'].score
    modifier = high_score['Scores'].game_modifier
    user = high_score['Users'].username
    content = high_score['GameContents'].name
    mode = high_score['GameModes'].name

    return {
        'id': score_id,
        'rank': rank,
        'score': score,
        'date': score_date,
        'username': user,
        'game_mode': mode,
        'game_content': content,
        'game_modifier': modifier
    }


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }
