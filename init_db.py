# init_db.py - Initialize database and run seeders

import asyncio
import sys

from database import engine
from models import Base


async def init_database(run_seeders: bool = True):
    """Initialize database tables.

    Args:
        run_seeders: If True, also run seeders after creating tables
    """
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

    if run_seeders:
        print("\nRunning seeders...")
        from seeders.run_seeders import run_all_seeders
        await run_all_seeders(fresh=False)


if __name__ == "__main__":
    run_seeders = "--no-seed" not in sys.argv
    asyncio.run(init_database(run_seeders=run_seeders))
