# migrate_data.py - Migrate data from fiszki.db to database.sqlite

import asyncio
import sqlite3
import bcrypt
from sqlalchemy import select

from database import engine, AsyncSessionLocal
from models import Base, Admin, Level, Question, Answer, User


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def migrate_data():
    """Migrate all data from fiszki.db to database.sqlite."""

    # Connect to source database (fiszki.db)
    source_conn = sqlite3.connect("fiszki.db")
    source_conn.row_factory = sqlite3.Row
    source_cursor = source_conn.cursor()

    # Create all tables in target database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Migrate administrators -> admins
        print("Migrating administrators...")
        source_cursor.execute("SELECT * FROM administrators")
        for row in source_cursor.fetchall():
            admin = Admin(
                id_admin=row["id_admin"],
                login=row["login"],
                password=hash_password(row["password"])  # Hash the plain text password
            )
            session.add(admin)
        await session.flush()
        print(f"  - Migrated administrators")

        # 2. Migrate levels
        print("Migrating levels...")
        source_cursor.execute("SELECT * FROM levels")
        for row in source_cursor.fetchall():
            level = Level(
                level_id=row["level_id"],
                level_name=row["level_name"]
            )
            session.add(level)
        await session.flush()
        print(f"  - Migrated levels")

        # 3. Migrate questions
        print("Migrating questions...")
        source_cursor.execute("SELECT * FROM questions")
        for row in source_cursor.fetchall():
            question = Question(
                question_id=row["question_id"],
                level_id=row["level_id"],
                question=row["question"]
            )
            session.add(question)
        await session.flush()
        print(f"  - Migrated questions")

        # 4. Migrate answers
        print("Migrating answers...")
        source_cursor.execute("SELECT * FROM answers")
        for row in source_cursor.fetchall():
            answer = Answer(
                answer_id=row["answer_id"],
                question_id=row["question_id"],
                answer=row["answer"],
                is_good=row["is_good"]
            )
            session.add(answer)
        await session.flush()
        print(f"  - Migrated answers")

        # 5. Migrate logins -> users
        print("Migrating users...")
        source_cursor.execute("SELECT * FROM logins")
        for row in source_cursor.fetchall():
            user = User(
                user_id=row["user_id"],
                login=row["login"],
                password=hash_password(row["password"]),  # Hash the plain text password
                progress=row["progress"]
            )
            session.add(user)
        await session.flush()
        print(f"  - Migrated users")

        await session.commit()

    source_conn.close()
    print("\nMigration complete!")
    print("Note: All passwords have been hashed with bcrypt.")


if __name__ == "__main__":
    asyncio.run(migrate_data())
