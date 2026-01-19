# main.py — Backend API for Vue admin panel with SQLite database

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import os

from database import get_db, init_db
from models import Admin, Level, Question, Answer, User
from schemas import (
    LevelOut, QuestionOut, AnswerOut,
    LevelCreate, LevelUpdate,
    QuestionCreate, QuestionUpdate,
    AnswerCreate, AnswerUpdate,
    UserOut, UserCreate, UserLoginIn,
    UserChangePasswordIn, UserChangeLoginIn, UserResetPasswordIn, AdminLevelOut,
    Token,
)


# -------------------------------------------------
# Lifespan - database initialization
# -------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


# -------------------------------------------------
# Application and CORS
# -------------------------------------------------

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fiszkiadminpanelfrontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# JWT for admin authentication
# -------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "jnUubi5NNKDkRd2neldQRikDcOeQ5MagGnRvsxki7sQ")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
RESET_CODE = os.getenv("RESET_CODE", "1111")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=12))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
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

    return {"id_admin": int(admin_id), "role": role}


# -------------------------------------------------
# Health check
# -------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


# -------------------------------------------------
# Public endpoints
# -------------------------------------------------

@app.get("/levels", response_model=list[LevelOut])
async def get_levels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Level))
    levels = result.scalars().all()
    return levels


@app.get("/levels/{level_id}/questions", response_model=list[QuestionOut])
async def get_questions(level_id: int, db: AsyncSession = Depends(get_db)):
    # Check if level exists
    level = await db.get(Level, level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    result = await db.execute(
        select(Question)
        .where(Question.level_id == level_id)
        .options(selectinload(Question.answers))
    )
    questions = result.scalars().all()
    return questions


# -------------------------------------------------
# User endpoints
# -------------------------------------------------

@app.get("/user/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/user/{user_id}/progress", response_model=UserOut)
async def update_user_progress_by_id(
    user_id: int,
    new_progress: int,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.progress = new_progress
    await db.commit()
    await db.refresh(user)
    return user


@app.post("/user/register", response_model=UserOut)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    result = await db.execute(select(User).where(User.login == data.login))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(data.password)
    new_user = User(login=data.login, password=hashed_password, progress=0)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.post("/user/login", response_model=UserOut)
async def login_user(data: UserLoginIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.login == data.login))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


@app.put("/user/{user_id}/change-password", response_model=UserOut)
async def change_password(
    user_id: int,
    data: UserChangePasswordIn,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    user.password = get_password_hash(data.new_password)
    await db.commit()
    await db.refresh(user)
    return user


@app.put("/user/{user_id}/change-login", response_model=UserOut)
async def change_login(
    user_id: int,
    data: UserChangeLoginIn,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # Check if new login is already taken
    result = await db.execute(select(User).where(User.login == data.new_login))
    existing = result.scalar_one_or_none()
    if existing and existing.user_id != user_id:
        raise HTTPException(status_code=400, detail="Login already taken")

    user.login = data.new_login
    await db.commit()
    await db.refresh(user)
    return user


@app.post("/user/reset-password", response_model=UserOut)
async def reset_password(data: UserResetPasswordIn, db: AsyncSession = Depends(get_db)):
    if data.code != RESET_CODE:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    result = await db.execute(select(User).where(User.login == data.login))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = get_password_hash(data.new_password)
    await db.commit()
    await db.refresh(user)
    return user


# -------------------------------------------------
# Admin login
# -------------------------------------------------

@app.post("/admin/login", response_model=Token)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Admin).where(Admin.login == form_data.username))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(form_data.password, admin.password):
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

    return Token(access_token=access_token, token_type="bearer")


# -------------------------------------------------
# Admin CRUD - Levels
# -------------------------------------------------

@app.get("/admin/levels", response_model=list[AdminLevelOut])
async def admin_get_levels(
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            Level.level_id,
            Level.level_name,
            func.count(Question.question_id).label("questions_count")
        )
        .outerjoin(Question, Level.level_id == Question.level_id)
        .group_by(Level.level_id)
    )
    levels = result.all()
    return [
        AdminLevelOut(level_id=l.level_id, level_name=l.level_name, questions_count=l.questions_count)
        for l in levels
    ]


@app.post("/admin/levels", response_model=LevelOut)
async def admin_create_level(
    data: LevelCreate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    new_level = Level(level_name=data.level_name)
    db.add(new_level)
    await db.commit()
    await db.refresh(new_level)
    return new_level


@app.put("/admin/levels/{level_id}", response_model=LevelOut)
async def admin_update_level(
    level_id: int,
    data: LevelUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    level = await db.get(Level, level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    level.level_name = data.level_name
    await db.commit()
    await db.refresh(level)
    return level


@app.delete("/admin/levels/{level_id}")
async def admin_delete_level(
    level_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    level = await db.get(Level, level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    await db.delete(level)
    await db.commit()
    return {"detail": "Level deleted"}


# -------------------------------------------------
# Admin CRUD - Questions
# -------------------------------------------------

@app.get("/admin/questions", response_model=list[QuestionOut])
async def admin_get_questions(
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Question).options(selectinload(Question.answers))
    )
    questions = result.scalars().all()
    return questions


@app.post("/admin/questions", response_model=QuestionOut)
async def admin_create_question(
    data: QuestionCreate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Check if level exists
    level = await db.get(Level, data.level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    new_question = Question(question=data.question, level_id=data.level_id)
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)

    # Load answers relationship for response
    result = await db.execute(
        select(Question)
        .where(Question.question_id == new_question.question_id)
        .options(selectinload(Question.answers))
    )
    return result.scalar_one()


@app.put("/admin/questions/{question_id}", response_model=QuestionOut)
async def admin_update_question(
    question_id: int,
    data: QuestionUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.question = data.question
    await db.commit()

    # Load with answers
    result = await db.execute(
        select(Question)
        .where(Question.question_id == question_id)
        .options(selectinload(Question.answers))
    )
    return result.scalar_one()


@app.delete("/admin/questions/{question_id}")
async def admin_delete_question(
    question_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(question)
    await db.commit()
    return {"detail": "Question deleted"}


# -------------------------------------------------
# Admin CRUD - Answers
# -------------------------------------------------

@app.get("/admin/answers", response_model=list[AnswerOut])
async def admin_get_answers(
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Answer))
    answers = result.scalars().all()
    return answers


@app.post("/admin/answers", response_model=AnswerOut)
async def admin_create_answer(
    data: AnswerCreate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Check if question exists
    question = await db.get(Question, data.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    new_answer = Answer(
        answer=data.answer,
        is_good=data.is_good,
        question_id=data.question_id
    )
    db.add(new_answer)
    await db.commit()
    await db.refresh(new_answer)
    return new_answer


@app.put("/admin/answers/{answer_id}", response_model=AnswerOut)
async def admin_update_answer(
    answer_id: int,
    data: AnswerUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    answer = await db.get(Answer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    answer.answer = data.answer
    answer.is_good = data.is_good
    await db.commit()
    await db.refresh(answer)
    return answer


@app.delete("/admin/answers/{answer_id}")
async def admin_delete_answer(
    answer_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    answer = await db.get(Answer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    await db.delete(answer)
    await db.commit()
    return {"detail": "Answer deleted"}


# -------------------------------------------------
# Admin CRUD - Users
# -------------------------------------------------

@app.get("/admin/users", response_model=list[UserOut])
async def admin_get_users(
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@app.put("/admin/users/{user_id}/reset-progress", response_model=UserOut)
async def admin_reset_progress(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.progress = 0
    await db.commit()
    await db.refresh(user)
    return user


@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted"}
