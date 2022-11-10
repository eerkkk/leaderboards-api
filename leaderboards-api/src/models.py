import uuid

from sqlalchemy import Boolean, Column, Date, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    scores = relationship("Scores", back_populates="owner")


class Scores(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    game_modifier = Column(Integer)
    score = Column(Integer)
    date = Column(Date)

    game_mode_id = Column(UUID(as_uuid=True), ForeignKey("game_modes.id"))
    game_content_id = Column(UUID(as_uuid=True), ForeignKey("game_contents.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    modes = relationship("GameModes", back_populates="scores")
    contents = relationship("GameContents", back_populates="scores")
    owner = relationship("Users", back_populates="scores")


class GameModes(Base):
    __tablename__ = "game_modes"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    description = Column(String)

    scores = relationship("Scores", back_populates="modes")


class GameContents(Base):
    __tablename__ = "game_contents"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    slug = Column(String)
    name = Column(String)
    description = Column(String)

    scores = relationship("Scores", back_populates="contents")
