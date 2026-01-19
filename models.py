# models.py - SQLAlchemy ORM models for SQLite database

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Admin(Base):
    __tablename__ = "admins"

    id_admin = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Level(Base):
    __tablename__ = "levels"

    level_id = Column(Integer, primary_key=True, index=True)
    level_name = Column(String, unique=True, nullable=False)

    questions = relationship("Question", back_populates="level", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    level_id = Column(Integer, ForeignKey("levels.level_id"), nullable=False)

    level = relationship("Level", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    answer_id = Column(Integer, primary_key=True, index=True)
    answer = Column(String, nullable=False)
    is_good = Column(Integer, default=0)  # 0 or 1
    question_id = Column(Integer, ForeignKey("questions.question_id"), nullable=False)

    question = relationship("Question", back_populates="answers")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    progress = Column(Integer, default=0)
