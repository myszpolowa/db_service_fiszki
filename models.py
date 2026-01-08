from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Level(Base):
    __tablename__ = "levels"
    level_id = Column(Integer, primary_key=True, index=True)
    level_name = Column(String, nullable=False)

    questions = relationship(
        "Question",
        back_populates="level",
        cascade="all, delete-orphan",
    )

class Question(Base):
    __tablename__ = "questions"
    question_id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.level_id", ondelete="CASCADE"), nullable=False)
    question = Column(String, nullable=False)

    level = relationship("Level", back_populates="questions")
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

class Answer(Base):
    __tablename__ = "answers"
    answer_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), nullable=False)
    answer = Column(String, nullable=False)
    is_good = Column(Integer, nullable=False)  # 0 / 1

    question = relationship("Question", back_populates="answers")

class Login(Base):
    __tablename__ = "logins"
    user_id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    progress = Column(Integer, nullable=False)

class Administrator(Base):
    __tablename__ = "administrators"
    id_admin = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
