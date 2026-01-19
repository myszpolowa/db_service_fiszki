# seeders/run_seeders.py - Run all seeders to populate database

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text

from database import engine, AsyncSessionLocal
from models import Base, Admin, Level, Question, Answer, User
from seeders.seed_data import (
    hash_password,
    ADMINS_DATA,
    LEVELS_DATA,
    QUESTIONS_DATA,
    ANSWERS_DATA,
    USERS_DATA,
)


async def clear_database():
    """Clear all data from database (preserves tables)."""
    async with AsyncSessionLocal() as session:
        # Disable foreign key checks temporarily
        await session.execute(text("PRAGMA foreign_keys = OFF"))

        # Delete in reverse order of dependencies
        await session.execute(text("DELETE FROM answers"))
        await session.execute(text("DELETE FROM questions"))
        await session.execute(text("DELETE FROM levels"))
        await session.execute(text("DELETE FROM users"))
        await session.execute(text("DELETE FROM admins"))

        # Reset autoincrement counters (if sqlite_sequence exists)
        try:
            await session.execute(text("DELETE FROM sqlite_sequence"))
        except Exception:
            pass  # Table may not exist if AUTOINCREMENT was never used

        # Re-enable foreign key checks
        await session.execute(text("PRAGMA foreign_keys = ON"))

        await session.commit()
    print("Database cleared.")


async def seed_admins():
    """Seed administrators."""
    async with AsyncSessionLocal() as session:
        for admin_data in ADMINS_DATA:
            admin = Admin(
                login=admin_data["login"],
                password=hash_password(admin_data["password"])
            )
            session.add(admin)
        await session.commit()
    print(f"Seeded {len(ADMINS_DATA)} admin(s)")


async def seed_levels():
    """Seed levels."""
    async with AsyncSessionLocal() as session:
        for level_data in LEVELS_DATA:
            level = Level(
                level_id=level_data["level_id"],
                level_name=level_data["level_name"]
            )
            session.add(level)
        await session.commit()
    print(f"Seeded {len(LEVELS_DATA)} level(s)")


async def seed_questions():
    """Seed questions."""
    async with AsyncSessionLocal() as session:
        for q_data in QUESTIONS_DATA:
            question = Question(
                question_id=q_data["question_id"],
                level_id=q_data["level_id"],
                question=q_data["question"]
            )
            session.add(question)
        await session.commit()
    print(f"Seeded {len(QUESTIONS_DATA)} question(s)")


async def seed_answers():
    """Seed answers."""
    async with AsyncSessionLocal() as session:
        for a_data in ANSWERS_DATA:
            answer = Answer(
                answer_id=a_data["answer_id"],
                question_id=a_data["question_id"],
                answer=a_data["answer"],
                is_good=a_data["is_good"]
            )
            session.add(answer)
        await session.commit()
    print(f"Seeded {len(ANSWERS_DATA)} answer(s)")


async def seed_users():
    """Seed test users."""
    async with AsyncSessionLocal() as session:
        for user_data in USERS_DATA:
            user = User(
                login=user_data["login"],
                password=hash_password(user_data["password"]),
                progress=user_data["progress"]
            )
            session.add(user)
        await session.commit()
    print(f"Seeded {len(USERS_DATA)} user(s)")


async def run_all_seeders(fresh: bool = False):
    """Run all seeders.

    Args:
        fresh: If True, clear database before seeding
    """
    print("=" * 50)
    print("Running database seeders")
    print("=" * 50)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if fresh:
        await clear_database()

    # Check if data already exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Admin))
        if result.scalar_one_or_none() and not fresh:
            print("\nDatabase already has data. Use --fresh to clear and reseed.")
            print("Exiting without changes.")
            return

    # Run seeders in order
    await seed_admins()
    await seed_levels()
    await seed_questions()
    await seed_answers()
    await seed_users()

    print("=" * 50)
    print("Seeding complete!")
    print("=" * 50)


if __name__ == "__main__":
    fresh = "--fresh" in sys.argv
    asyncio.run(run_all_seeders(fresh=fresh))
