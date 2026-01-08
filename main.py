# db_service/main.py
# Точка входа FastAPI + эндпоинты под телефон и админку (DB Service)

import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db  # локальная БД (SQLite локально, Postgres на Render)
from models import Level, Question, Answer, Administrator, Login
from schemas import (
    LevelOut, QuestionOut, AnswerOut,
    LevelCreate, LevelUpdate,
    QuestionCreate, QuestionUpdate,
    AnswerCreate, AnswerUpdate,
    UserOut, UserCreate, UserLoginIn,
    UserChangePasswordIn, UserChangeLoginIn, UserResetPasswordIn, AdminLevelOut,
)

app = FastAPI()

# CORS - разрешаем запросы от backend
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8002"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# JWT и конфиг из окружения
# -------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
RESET_CODE = os.getenv("RESET_CODE", "1111")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_admin(db: Session, login: str, password: str) -> Administrator | None:
    admin = db.query(Administrator).filter(Administrator.login == login).first()
    if not admin:
        return None
    if admin.password != password:
        return None
    return admin


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Administrator:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if admin_id is None or role != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin = db.query(Administrator).filter(Administrator.id_admin == int(admin_id)).first()
    if admin is None:
        raise credentials_exception
    return admin

# -------------------------------------------------
# Публичные эндпоинты (DB Service)
# -------------------------------------------------


@app.get("/levels", response_model=list[LevelOut])
async def get_levels(db: Session = Depends(get_db)):
    return db.query(Level).all()


@app.get("/levels/{level_id}/questions", response_model=list[QuestionOut])
async def get_questions(level_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.level_id == level_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Level not found")
    return questions


@app.get("/user/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Login).filter(Login.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/user/{user_id}/progress", response_model=UserOut)
async def update_user_progress_by_id(
    user_id: int,
    new_progress: int,
    db: Session = Depends(get_db),
):
    user = db.query(Login).filter(Login.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.progress = new_progress
    db.commit()
    db.refresh(user)
    return user


@app.post("/user/register", response_model=UserOut)
async def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Login).filter(Login.login == data.login).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = Login(login=data.login, password=data.password, progress=0)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/user/login", response_model=UserOut)
async def login_user(data: UserLoginIn, db: Session = Depends(get_db)):
    user = (
        db.query(Login)
        .filter(Login.login == data.login, Login.password == data.password)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@app.put("/user/{user_id}/change-password", response_model=UserOut)
async def change_password(
    user_id: int,
    data: UserChangePasswordIn,
    db: Session = Depends(get_db),
):
    user = db.query(Login).filter(Login.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = data.new_password
    db.commit()
    db.refresh(user)
    return user


@app.put("/user/{user_id}/change-login", response_model=UserOut)
async def change_login(
    user_id: int,
    data: UserChangeLoginIn,
    db: Session = Depends(get_db),
):
    user = db.query(Login).filter(Login.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(Login).filter(Login.login == data.new_login).first()
    if existing and existing.user_id != user_id:
        raise HTTPException(status_code=400, detail="Login already taken")

    user.login = data.new_login
    db.commit()
    db.refresh(user)
    return user


@app.post("/user/reset-password", response_model=UserOut)
async def reset_password(
    data: UserResetPasswordIn,
    db: Session = Depends(get_db),
):
    if data.code != RESET_CODE:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    user = db.query(Login).filter(Login.login == data.login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = data.new_password
    db.commit()
    db.refresh(user)
    return user

# -------------------------------------------------
# Админка
# -------------------------------------------------


@app.post("/admin/login")
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(admin.id_admin), "role": "admin"},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/admin/levels", response_model=list[AdminLevelOut])
async def admin_get_levels(
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            Level.level_id,
            Level.level_name,
            func.count(Question.question_id).label("questions_count"),
        )
        .outerjoin(Question, Question.level_id == Level.level_id)
        .group_by(Level.level_id, Level.level_name)
        .all()
    )

    return [
        {
            "level_id": r.level_id,
            "level_name": r.level_name,
            "questions_count": r.questions_count,
        }
        for r in rows
    ]


@app.post("/admin/levels", response_model=LevelOut)
async def admin_create_level(
    data: LevelCreate,
    db: Session = Depends(get_db),
):
    new_level = Level(level_name=data.level_name)
    db.add(new_level)
    db.commit()
    db.refresh(new_level)
    return new_level


@app.put("/admin/levels/{level_id}", response_model=LevelOut)
async def admin_update_level(
    level_id: int,
    data: LevelUpdate,
    db: Session = Depends(get_db),
):
    level = db.query(Level).filter(Level.level_id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    level.level_name = data.level_name
    db.commit()
    db.refresh(level)
    return level


@app.delete("/admin/levels/{level_id}")
async def admin_delete_level(
    level_id: int,
    db: Session = Depends(get_db),
):
    level = db.query(Level).filter(Level.level_id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    db.delete(level)
    db.commit()
    return {"detail": "Level deleted"}


@app.get("/admin/questions", response_model=list[QuestionOut])
async def admin_get_questions(
    db: Session = Depends(get_db),
):
    return db.query(Question).all()


@app.post("/admin/questions", response_model=QuestionOut)
async def admin_create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
):
    level = db.query(Level).filter(Level.level_id == data.level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    q = Question(level_id=data.level_id, question=data.question)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@app.put("/admin/questions/{question_id}", response_model=QuestionOut)
async def admin_update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
):
    q = db.query(Question).filter(Question.question_id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    q.question = data.question
    db.commit()
    db.refresh(q)
    return q


@app.delete("/admin/questions/{question_id}")
async def admin_delete_question(
    question_id: int,
    db: Session = Depends(get_db),
):
    q = db.query(Question).filter(Question.question_id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(q)
    db.commit()
    return {"detail": "Question deleted"}


@app.get("/admin/answers", response_model=list[AnswerOut])
async def admin_get_answers(
    db: Session = Depends(get_db),
):
    return db.query(Answer).all()


@app.post("/admin/answers", response_model=AnswerOut)
async def admin_create_answer(
    data: AnswerCreate,
    db: Session = Depends(get_db),
):
    q = db.query(Question).filter(Question.question_id == data.question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    a = Answer(
        question_id=data.question_id,
        answer=data.answer,
        is_good=data.is_good,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@app.put("/admin/answers/{answer_id}", response_model=AnswerOut)
async def admin_update_answer(
    answer_id: int,
    data: AnswerUpdate,
    db: Session = Depends(get_db),
):
    a = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Answer not found")

    a.answer = data.answer
    a.is_good = data.is_good
    db.commit()
    db.refresh(a)
    return a


@app.delete("/admin/answers/{answer_id}")
async def admin_delete_answer(
    answer_id: int,
    db: Session = Depends(get_db),
):
    a = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Answer not found")

    db.delete(a)
    db.commit()
    return {"detail": "Answer deleted"}


@app.get("/admin/users", response_model=list[UserOut])
async def admin_get_users(
    db: Session = Depends(get_db),
):
    return db.query(Login).all()


@app.put("/admin/users/{user_id}/reset-progress", response_model=UserOut)
async def admin_reset_progress(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(Login).filter(Login.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.progress = 0
    db.commit()
    db.refresh(user)
    return user


@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(Login).filter(Login.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


@app.get("/health")
def health():
    return {"status": "ok"}


from models import Base, Administrator
from database import engine, SessionLocal


# Создаём таблицы при старте
@app.on_event("startup")
def startup_event():
    # Создаём все таблицы
    Base.metadata.create_all(bind=engine)

    # Создаём первого админа
    db = SessionLocal()
    try:
        admin = db.query(Administrator).filter(Administrator.login == "admin").first()
        if not admin:
            new_admin = Administrator(
                login="admin",
                password="admin"
            )
            db.add(new_admin)
            db.commit()
            print("default admin created")
    finally:
        db.close()

