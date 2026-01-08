# database.py
# подключение к существующему fiszki.db через SQLAlchemy (когда база из папки общей)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# универсальный путь: ../baza_danych/fiszki.db
BASE_DIR = Path(__file__).parent  # корень (html/)
DB_PATH = BASE_DIR.parent / "baza_danych" / "fiszki.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}?check_same_thread=False"

# engine — объект подключения к SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# # файл fiszki.db должен лежать в этой же папке
# SQLALCHEMY_DATABASE_URL = "sqlite:///./fiszki.db"
#
# # engine — объект подключения к SQLite
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False}  # нужно для SQLite в многопоточном режиме
# )

# фабрика сессий для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# базовый класс для всех моделей
Base = declarative_base()

# зависимость для FastAPI: даёт сессию БД в эндпоинт и потом закрывает её
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
