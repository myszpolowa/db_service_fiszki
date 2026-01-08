# database.py в db_service
# Подключение к PostgreSQL на Render или SQLite локально

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Получаем DATABASE_URL из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # На Render: PostgreSQL
    # Render использует postgres://, SQLAlchemy требует postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(DATABASE_URL)
else:
    # Локально: SQLite
    DATABASE_URL = "sqlite:///./fiszki.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


# Зависимость для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
